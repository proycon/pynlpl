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
    

    def __contains__(self, key):
        return self.model.exists( key )

    def logscore(self, ngram):
        n = len(ngram)

        #Bug work-around
        #if "" in ngram or "_" in ngram or "__" in ngram:
        #    print >> sys.stderr, "WARNING: Invalid word in n-gram! Ignoring", ngram 
        #    return -999.9

        if len(ngram) == self.n:
            if all( (self.model.exists(x) for x in ngram) ):
                #no phrases, basic trigram, compute directly
                return self.model.wordProb(*ngram)
            else:
                raise KeyError
        else:
            raise Exception("Not an " + str(self.n) + "-gram")

