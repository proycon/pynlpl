#! /usr/bin/env python
# -*- coding: utf8 -*-


###############################################################
#  PyNLPl - FreeLing Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Radboud University Nijmegen
#       
#       Licensed under GPLv3
# 
# Generic Tagger interface for PoS-tagging and lemmatisation,
# offers an interface to various software
#
###############################################################

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import u
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout

import io
import codecs
import json
import getopt
import subprocess
    
class Tagger(object):    
     def __init__(self, *args):        
        global WSDDIR
        self.tagger = None
        self.mode = args[0]
        if args[0] == "file":
            if len(args) != 2:
                raise Exception("Syntax: file:[filename]")            
            self.tagger = codecs.open(args[1],'r','utf-8') 
        elif args[0] == "frog":
            if len(args) != 3:
                raise Exception("Syntax: frog:[host]:[port]")
            from pynlpl.clients.frogclient import FrogClient
            port = int(args[2])
            self.tagger = FrogClient(args[1],port)                
        elif args[0] == "freeling":
            if len(args) != 3:
                raise Exception("Syntax: freeling:[host]:[port]")
            from pynlpl.clients.freeling import FreeLingClient
            host = args[1]
            port = int(args[2])
            self.tagger = FreeLingClient(host,port)            
        elif args[0] == "corenlp":
            if len(args) != 1:
                raise Exception("Syntax: corenlp")
            import corenlp
            print("Initialising Stanford Core NLP",file=stderr)
            self.tagger = corenlp.StanfordCoreNLP()
        elif args[0] == 'treetagger':                        
            if not len(args) == 2:
                raise Exception("Syntax: treetagger:[treetagger-bin]")
            self.tagger = args[1]            
        elif args[0] == "durmlex":
            if not len(args) == 2:
                raise Exception("Syntax: durmlex:[filename]")
            print("Reading durm lexicon: ", args[1],file=stderr)
            self.mode = "lookup"
            self.tagger = {}
            f = codecs.open(args[1],'r','utf-8')
            for line in f:
                fields = line.split('\t')
                wordform = fields[0].lower()
                lemma = fields[4].split('.')[0]
                self.tagger[wordform] = (lemma, 'n')
            f.close()
            print("Loaded ", len(self.tagger), " wordforms",file=stderr)
        elif args[0] == "oldlex":
            if not len(args) == 2:
                raise Exception("Syntax: oldlex:[filename]")
            print("Reading OLDLexique: ", args[1],file=stderr)
            self.mode = "lookup"
            self.tagger = {}
            f = codecs.open(args[1],'r','utf-8')
            for line in f:
                fields = line.split('\t')
                wordform = fields[0].lower()                
                lemma = fields[1]
                if lemma == '=': 
                    lemma == fields[0]
                pos = fields[2][0].lower()
                self.tagger[wordform] = (lemma, pos)
                print("Loaded ", len(self.tagger), " wordforms",file=stderr)
            f.close()        
        else:
            raise Exception("Invalid mode: " + args[0])
        
     def __iter__(self):
        if self.mode != 'file':
            raise Exception("Iteration only possible in file mode")
        line = self.tagger.next()
        newwords = []
        postags = []
        lemmas = []    
        for item in line:            
            word,lemma,pos = item.split('|')
            newwords.append(word)
            postags.append(pos)
            lemmas.append(lemma)
        yield newwords, postags, lemmas        
        
     def reset(self):
        if self.mode == 'file':
            self.tagger.seek(0)
        
        
     def process(self, words, debug=False):
        if self.mode == 'file':
            line = self.tagger.next()
            newwords = []
            postags = []
            lemmas = []    
            for item in line.split(' '):                            
                if item.strip():
                    try:
                        word,lemma,pos = item.split('|')
                    except:
                        raise Exception("Unable to parse word|lemma|pos in " + item)
                    newwords.append(word)
                    postags.append(pos)
                    lemmas.append(lemma)
            return newwords, postags, lemmas
        elif self.mode == "frog":
            newwords = []
            postags = []
            lemmas = []             
            for fields in self.tagger.process(' '.join(words)):
                word,lemma,morph,pos = fields[:4]
                newwords.append(word)
                postags.append(pos)
                lemmas.append(lemma)
            return newwords, postags, lemmas                
        elif self.mode == "freeling":
            postags = []
            lemmas = []
            for fields in self.tagger.process(words, debug):
                word, lemma,pos = fields[:3]
                postags.append(pos)
                lemmas.append(lemma)
            return words, postags, lemmas            
        elif self.mode == "corenlp":            
            data = json.loads(self.tagger.parse(" ".join(words)))
            words = []
            postags = []
            lemmas = []
            for sentence in data['sentences']:
                for word, worddata in sentence['words']:
                    words.append(word)
                    lemmas.append(worddata['Lemma'])
                    postags.append(worddata['PartOfSpeech'])
            return words, postags, lemmas
        elif self.mode == 'lookup':
            postags = []
            lemmas = []
            for word in words:
                try:
                    lemma, pos = self.tagger[word.lower()]
                    lemmas.append(lemma)
                    postags.append(pos)
                except KeyError: 
                    lemmas.append(word)
                    postags.append('?')
            return words, postags, lemmas
        elif self.mode == 'treetagger':
            s = " ".join(words)
            s = u(s)
            
            p = subprocess.Popen([self.tagger], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)            
            (out, err) = p.communicate(s.encode('utf-8'))

            newwords = []
            postags = []
            lemmas = []
            for line in out.split('\n'):
                line = line.strip()
                if line:
                    fields = line.split('\t')
                    newwords.append( unicode(fields[0],'utf-8') )
                    postags.append( unicode(fields[1],'utf-8') )
                    lemmas.append( unicode(fields[2],'utf-8') )
                                        
            if p.returncode != 0:
                print(err,file=stderr)
                raise OSError('TreeTagger failed')
        
            return newwords, postags, lemmas
        else:
            raise Exception("Unknown mode")
    
    
     
    
     def treetagger_tag(self, f_in, f_out,oneperline=False, debug=False):
        
        def flush(sentences):
            if sentences:
                print("Processing " + str(len(sentences)) + " lines",file=stderr)                
                for sentence in sentences:
                    out = ""
                    p = subprocess.Popen([self.tagger], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (results, err) = p.communicate("\n".join(sentences).encode('utf-8'))
                    for line in results.split('\n'):
                        line = line.strip()
                        if line:
                            fields = line.split('\t')
                            word = fields[0]
                            pos = fields[1]
                            lemma = fields[2]
                            if oneperline:
                                if out: out += "\n"
                                out += word + "\t" + lemma + "\t" + pos
                            else: 
                                if out: out += " "
                                if '|' in word:
                                    word = word.replace('|','_')
                                if '|' in lemma:
                                    lemma = lemma.replace('|','_') 
                                if '|' in pos:
                                    pos = pos.replace('|','_') 
                            out += word + "|" + lemma + "|" + pos
                            if pos[0] == '$':
                                out = u(out)
                                f_out.write(out + "\n")        
                                if oneperline: f_out.write("\n")
                                out = ""
                            
                if out:
                   out = u(out)
                   f_out.write(out + "\n")   
                   if oneperline: f_out.write("\n")
                

        #buffered tagging
        sentences = []
        linenum = 0
        
        for line in f_in:                        
            linenum += 1
            print(" Buffering input @" + str(linenum),file=stderr)
            line = line.strip()
            if not line or ('.' in line[:-1] or '?' in line[:-1] or '!' in line[:-1]) or (line[-1] != '.' and line[-1] != '?' and line[-1] != '!'): 
                flush(sentences)
                sentences = []
                if not line.strip():
                    f_out.write("\n")
                    if oneperline: f_out.write("\n") 
            sentences.append(line)
        flush(sentences)
                        
    
     def tag(self, f_in, f_out,oneperline=False, debug=False):
        if self.mode == 'treetagger':
            self.treetagger_tag(f_in, f_out,oneperline=False, debug=False) 
        else:
            linenum = 0
            for line in f_in:
                linenum += 1
                print(" Tagger input @" + str(linenum),file=stderr)
                if line.strip():
                    words = line.strip().split(' ')
                    words, postags, lemmas = self.process(words, debug)
                    out = ""
                    for word, pos, lemma in zip(words,postags, lemmas):
                       if word is None: word = ""
                       if lemma is None: lemma = "?"
                       if pos is None: pos = "?"                    
                       if oneperline:
                            if out: out += "\n"
                            out += word + "\t" + lemma + "\t" + pos
                       else: 
                            if out: out += " "
                            if '|' in word:
                                word = word.replace('|','_')
                            if '|' in lemma:
                                lemma = lemma.replace('|','_') 
                            if '|' in pos:
                                pos = pos.replace('|','_') 
                            out += word + "|" + lemma + "|" + pos
                    if not isinstance(out, unicode):
                        out = unicode(out, 'utf-8')
                    f_out.write(out + "\n")
                    if oneperline:
                        f_out.write("\n")
                else:
                    f_out.write("\n")

def usage():
    print("tagger.py -c [conf] -f [input-filename] -o [output-filename]",file=stderr) 

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:c:o:D")
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err),file=stderr)
        usage()
        sys.exit(2)   
    
    taggerconf = None
    filename = None
    outfilename = None        
    oneperline = False
    debug = False
        
    for o, a in opts:
        if o == "-c":	
            taggerconf = a
        elif o == "-f":	
            filename = a
        elif o == '-o':
            outfilename =a
        elif o == '-l':
            oneperline = True
        elif o == '-D':
            debug = True
        else: 
            print >>sys.stderr,"Unknown option: ", o
            sys.exit(2)
    

    if not taggerconf:
        print("ERROR: Specify a tagger configuration with -c",file=stderr)
        sys.exit(2)
    if not filename:
        print("ERROR: Specify a filename with -f",file=stderr)
        sys.exit(2)
    
        
    if outfilename: 
        f_out = io.open(outfilename,'w',encoding='utf-8')
    else:
        f_out = stdout;
        
    f_in = io.open(filename,'r',encoding='utf-8')
    
    tagger = Tagger(*taggerconf.split(':'))
    tagger.tag(f_in, f_out, oneperline, debug)
    
    f_in.close()
    if outfilename:
        f_out.close()
    
      
            
        
