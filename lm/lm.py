#---------------------------------------------------------------
# PyNLPl - Language Models
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
##
#   Licensed under GPLv3
#
#----------------------------------------------------------------

from pynlpl.statistics import FrequencyList, product
from pynlpl.textprocessors import Windower
import codecs

class SimpleLanguageModel:
    """This is a very simple unsmoothed language model"""
    def __init__(self, n, beginmarker = "<begin>", endmarker = "<end>"):
        self.freqlistN = FrequencyList()
        self.freqlistNm1 = FrequencyList()

        assert n >= 2
        self.n = n
        self.beginmarker = beginmarker
        self.endmarker = endmarker

    def append(self, sentence):
        for ngram in Windower(sentence,self.n):
            self.freqlistN.count(ngram)
        for ngram in Windower(sentence,self.n-1):
            self.freqlistNm1.count(ngram)        
        
    def load(self, filename):
        self.freqlistN = FrequencyList()
        self.freqlistNm1 = FrequencyList()
        f = codecs.open(filename,'r','utf-8')
        mode = False
        for line in f.readlines():        
            line = line.strip()
            if line:
                if not mode:
                    if line != "[simplelanguagemodel]":
                        raise Exception("File is not a SimpleLanguageModel")
                    else:
                        mode = 1
                elif mode == 1:
                    if line[:2] == 'n=':
                        self.n = int(line[2:])
                    elif line[:12] == 'beginmarker=':
                        self.beginmarker = line[:12]
                    elif line[:10] == 'endmarker=':
                        self.beginmarker = line[:10]            
                    mode = 2
                elif mode == 2:
                    if line == "[freqlistN]":
                        mode = 3
                    else:
                        raise Exception("Syntax error in language model file: ", line)
                elif mode == 3:
                    if line == "[freqlistNm1]":
                        mode = 4
                    else:
                        type, count = line.split("\t")
                        self.freqlistN.count(type,count)
                elif mode == 4:
                        type, count = line.split("\t")
                        self.freqlistNm1.count(type,count)

    def save(self, filename):
        f = codecs.open(filename,'w','utf-8')
        f.write("[simplelanguagemodel]\n")
        f.write("n="+str(self.n)+"\n")
        f.write("beginmarker="+self.beginmarker+"\n")
        f.write("endmarker="+self.endmarker+"\n")
        f.write("\n")
        f.write("[freqlistN]\n")
        for line in self.freqlistN.output():
            f.write(line+"\n")
        f.write("[freqlistNm1]\n")
        for line in self.freqlistNm1.output():
            f.write(line+"\n")
        f.close()


    def scoresentence(self, sentence):
        return product([self.__getitem(x) for x in Windower(sentence, self.n, self.beginmarker, self.endmarker)])
            

    def __getitem__(self, ngram):
        assert len(ngram) == self.n

        nm1gram = ngram[:-1]

        return self.freqlistN.p(ngram) / self.freqlistN.p(nm1gram)
            
        
    

