#---------------------------------------------------------------
# PyNLPl - SRILM Language Model
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Adapted from code by Sander Canisius
#
#   Licensed under GPLv3
#
#
# This library enables using SRILM as language model
#
#----------------------------------------------------------------


import srilmcc

from collections import deque
from pynlpl.statistics import product
from pynlpl.textprocessors import Windower

class SRILM:
    def __init__(self, filename, n):
        self.model = srilmcc.LanguageModel(filename, n)
        self.n = n

    def scoresentence(self, sentence):
        return product([self[x] for x in Windower(sentence, self.n, "<s>", "</s>")])

    def __getitem__(self, ngram):
        return 10**self.logscore(ngram)

    def logscore(self, ngram):
        #expand underscore-delimited phrases in the n-grams (proycon)
        #ngram = sum([ x.split("_") for x in ngram if x != "__" ],[]) 
        n = len(ngram)
        if n < self.n:
            ngram = (self.order - n) * ["<s>"] + ngram
            n = len(ngram)

        #Bug work-around
        if "" in ngram or "_" in ngram or "__" in ngram:
            print >> sys.stderr, "WARNING: Invalid word in n-gram! Ignoring", ngram 
            return -999.9

        if n == self.n:
            #no phrases, basic trigram, compute directly
            return self.model.wordProb(*ngram)
        else: 
            #we have phrases, estimate probability of phrases:
            #print ngram[0:3]            
            #print self.model.wordProb(*ngram[0:3])
            score = self.model.wordProb(*ngram[0:3])
            for i in range(1,n - 2):
                score += self.model.wordProb(*ngram[i:i+3]) 
            return score

