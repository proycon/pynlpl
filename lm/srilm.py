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

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import    

import srilmcc
from pynlpl.textprocessors import Windower

class SRILM:
    def __init__(self, filename, n):
        self.model = srilmcc.LanguageModel(filename, n)
        self.n = n

    def scoresentence(self, sentence, unknownwordprob=-12):
        score = 0
        for ngram in Windower(sentence, self.n, "<s>", "</s>"):
            try:
               score += self.logscore(ngram)
            except KeyError:
               score += unknownwordprob
        return 10**score

    def __getitem__(self, ngram):
        return 10**self.logscore(ngram)

    def __contains__(self, key):
        return self.model.exists( key )

    def logscore(self, ngram):
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

