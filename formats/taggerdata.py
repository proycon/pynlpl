#-*- coding:utf-8 -*-

###############################################################
#  PyNLPl - Read tagger data
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
#
#
###############################################################

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import    

import io

class Taggerdata(object):
    def __init__(self,filename, encoding = 'utf-8', mode ='r'):
        self.filename = filename
        self.encoding = encoding
        assert (mode == 'r' or mode == 'w')
        self.mode = mode
        self.reset()
        self.firstiter = True
        self.indexed = False
        self.writeindex = 0

    def __iter__(self):
        words = []
        lemmas = []
        postags = []
        for line in self.f:
            line = line.strip()
            if self.firstiter:
                self.indexed = (line == "#0")
                self.firstiter = False
            if not line and not self.indexed:
                yield (words, lemmas, postags)
                words = []
                lemmas = []
                postags = []
            elif self.indexed and len(line) > 1 and line[0] == '#' and line[1:].isdigit():
                if line != "#0":
                    yield (words, lemmas, postags)
                    words = []
                    lemmas = []
                    postags = []
            elif line:
                try:
                    word, lemma, pos = line.split("\t")
                except:
                    word = lemma = pos = "NONE"
                if word == "NONE": word = None
                if lemma == "NONE": lemma = None
                if pos == "NONE": pos = None
                words.append(word)
                lemmas.append(lemma)
                postags.append(pos)
        if words:
            yield (words, lemmas, postags)

    def next(self):
        words = []
        lemmas = []
        postags = []
        while True:
            try:
                line = self.f.next().strip()
            except StopIteration:
                if words:
                    return (words, lemmas, postags)
                else:
                    raise
            if self.firstiter:
                self.indexed = (line == "#0")
                self.firstiter = False
            if not line and not self.indexed:
                return (words, lemmas, postags)
            elif self.indexed and len(line) > 1 and line[0] == '#' and line[1:].isdigit():
                if line != "#0":
                    return (words, lemmas, postags)
            elif line:
                try:
                    word, lemma, pos = line.split("\t")
                except:
                    word = lemma = pos = "NONE"
                if word == "NONE": word = None
                if lemma == "NONE": lemma = None
                if pos == "NONE": pos = None
                words.append(word)
                lemmas.append(lemma)
                postags.append(pos)

    def align(self, referencewords, datatuple):
        """align the reference sentence with the tagged data"""
        targetwords = []
        for i, (word,lemma,postag) in enumerate(zip(datatuple[0],datatuple[1],datatuple[2])):
            if word:
                subwords = word.split("_")
                for w in subwords: #split multiword expressions
                    targetwords.append( (w, lemma, postag, i, len(subwords) > 1 ) ) #word, lemma, pos, index, multiword? 

        referencewords = [ w.lower() for w in referencewords ]          
        alignment = []
        for i, referenceword in enumerate(referencewords):
            found = False
            best = 0  
            distance = 999999          
            for j, (targetword, lemma, pos, index, multiword) in enumerate(targetwords):
                if referenceword == targetword and abs(i-j) < distance:
                    found = True
                    best = j
                    distance = abs(i-j)

            if found:
                alignment.append(targetwords[best])
            else:                
                alignment.append((None,None,None,None,False)) #no alignment found        
        
        return alignment   

    def reset(self):
        self.f = io.open(self.filename,self.mode, encoding=self.encoding)


    def write(self, sentence):
        self.f.write("#" + str(self.writeindex)+"\n")
        for word, lemma, pos in sentence:
           if not word: word = "NONE"
           if not lemma: lemma = "NONE"
           if not pos: pos = "NONE"
           self.f.write( word + "\t" + lemma + "\t" + pos + "\n" )                
        self.writeindex += 1

    def close(self):
        self.f.close()

