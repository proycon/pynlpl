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
        for ngram in Windower(sentence,n):
            self.freqlistN.count(ngram)
        for ngram in Windower(sentence,n-1):
            self.freqlistNm1.count(ngram)        
        
    def load(self):
        pass

    def save(self):
        pass        


    def scoresentence(self, sentence):
        return product([self.__getitem(x) for x in Windower(sentence, self.n, self.beginmarker, self.endmarker)]
            

    def __getitem__(self, ngram):
        assert len(ngram) == self.n

        nm1gram = ngram[:-1]

        return self.freqlistN.p(ngram) / self.freqlistN.p(nm1gram)
            
        
    

