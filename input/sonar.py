#---------------------------------------------------------------
# PyNLPl - Simple Read library for D-Coi/SoNaR format
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
# This library facilitates parsing and reading corpora in
# the SoNaR/D-Coi format.
#
#----------------------------------------------------------------


import codecs
import re
import glob
import os.path

class CorpusDocument:
    """This class represent one document/text of the Corpus"""

    def __init__(self, filename, encoding = 'iso-8859-15'):
        self.filename = filename
        self.id = os.path.basename(filename).split(".")[0]
        self.f = codecs.open(filename,'r', encoding)

    def __iter__(self):
        r = re.compile('<w.*xml:id="([^"]*)"(.*)>(.*)</w>')
        for line in self.f.readlines():
            matches = r.findall(line)
            for id, attribs, word in matches:
                pos = lemma = None
                m = re.findall('pos="([^"]+)"', attribs)
                if m: pos = m[0]

                m = re.findall('lemma="([^"]+)"', attribs)
                if m: lemma = m[0]
        
                yield word, id, pos, lemma       

    def sentences(self):
        prevp = 0
        prevs = 0
        prevw = 0
        sentence = [];
        sentence_id = ""
        for word, id, pos, lemma in iter(self):
            doc_id, ptype, p, s, w = re.findall('([\w\d-]+)\.(p|head)\.(\d+)\.s\.(\d+)\.w\.(\d+)',id)[0]
            if ((p != prevp) or (s != prevs)) and sentence:
                yield sentence_id, sentence
                sentence = []
                sentence_id = doc_id + '.' + ptype + '.' + str(p) + '.s.' + str(s)
            sentence.append( (word,id,pos,lemma) )     
            prevp = p
            prevs = s
            prevw = w
        if sentence:
            yield sentence_id, sentence 
            
    def paragraphs(self, with_id = False):
        """Extracts paragraphs, returns list of plain-text paragraphs"""
        prevp = 0
        partext = []
        for word, id, pos, lemma in iter(self):
            doc_id, ptype, p, s, w = re.findall('([\w\d-]+)\.(p|head)\.(\d+)\.s\.(\d+)\.w\.(\d+)',id)[0]
            if prevp != p and partext:
                    yield ( doc_id + "." + ptype + "." + prevp , " ".join(partext) )
                    partext = []
            partext.append(word)
            prevp = p   
        if partext:
            yield (doc_id + "." + ptype + "." + prevp, " ".join(partext) )
                
class Corpus:
    def __init__(self,corpusdir, extension = 'pos', restrict_to_collection = ""):
        self.corpusdir = corpusdir
        self.extension = extension
        self.restrict_to_collection = restrict_to_collection

    def __iter__(self):
        for d in glob.glob(self.corpusdir+"/*"):
            if (not self.restrict_to_collection or self.restrict_to_collection == d) and (os.path.isdir(d)):
                for f in glob.glob(d+ "/*." + self.extension):
                    yield CorpusDocument(f)
            
      
    
        
        
        

