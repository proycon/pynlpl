# -*- coding: utf-8 -*-

###############################################################
#  PyNLPl - WordAlignment Library for reading GIZA++ A3 files
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       In part using code by Sander Canisius
#       
#       Licensed under GPLv3
# 
#
# This library reads GIZA++ A3 files. It contains three classes over which
# you can iterate to obtain (sourcewords,targetwords,alignment) pairs.
#
#   - WordAlignment  - Reads target-source.A3.final files, in which each source word is aligned to one target word
#   - MultiWordAlignment  - Reads source-target.A3.final files, in which each source word may be aligned to multiple target target words
#   - IntersectionAlignment  - Computes the intersection between the above two alignments
#
#
###############################################################


import bz2
from itertools import izip


def parseAlignment(tokens): #by Sander Canisius
    assert tokens.pop(0) == "NULL"
    while tokens.pop(0) != "})":
        pass

    while tokens:
        word = tokens.pop(0)
        assert tokens.pop(0) == "({"
        positions = []
        token = tokens.pop(0)
        while token != "})":
            positions.append(int(token))
            token = tokens.pop(0)

        yield word, positions


class WordAlignment: 
    """Target to Source alignment: reads target-source.A3.final files, in which each source word is aligned to one target word"""

    def __init__(self,filename, encoding=False):
        """Open a target-source GIZA++ A3 file. The file may be bzip2 compressed. If an encoding is specified, proper unicode strings will be returned"""

        if filename.split(".")[-1] == "bz2":
            self.stream = bz2.BZ2File(filename,'r')
        else:
            self.stream = open(filename)
        self.encoding = encoding


    def __del__(self):
        self.stream.close()

    def __iter__(self): #by Sander Canisius
        line = self.stream.readline()
        while line:
            assert line.startswith("#")
            src = self.stream.readline().split()
            trg = []
            alignment = [None for i in xrange(len(src))]

            for i, (targetWord, positions) in enumerate(parseAlignment(self.stream.readline().split())):

                trg.append(targetWord)
                
                for pos in positions:
                    assert alignment[pos - 1] is None
                    alignment[pos - 1] = i

            if self.encoding: 
                yield [ unicode(w,self.encoding) for w in src ], [ unicode(w,self.encoding) for w in trg ], alignment
            else:
                yield src, trg, alignment

            line = self.stream.readline()


    def targetword(self, index, targetwords, alignment):
        """Return the aligned targetword for a specified index in the source words"""
        if alignment[index]:
            return targetwords[alignment[index]]
        else:
            return None

    def reset(self):
        self.stream.seek(0)

class MultiWordAlignment:
    """Source to Target alignment: reads source-target.A3.final files, in which each source word may be aligned to multiple target words (adapted from code by Sander Canisius)"""

    def __init__(self,filename, encoding = False):
        """Load a target-source GIZA++ A3 file. The file may be bzip2 compressed. If an encoding is specified, proper unicode strings will be returned"""

        if filename.split(".")[-1] == "bz2":
            self.stream = bz2.BZ2File(filename,'r')
        else:
            self.stream = open(filename)
        self.encoding = encoding

    def __del__(self):
        self.stream.close()

    def __iter__(self):
        line = self.stream.readline()
        while line:
            assert line.startswith("#")
            trg = self.stream.readline().split()
            src = []
            alignment = []

            for i, (word, positions) in enumerate(parseAlignment(self.stream.readline().split())):
                src.append(word)
                alignment.append( [ p - 1 for p in positions ] )


            if self.encoding: 
                yield [ unicode(w,self.encoding) for w in src ], [ unicode(w,self.encoding) for w in trg ], alignment
            else:
                yield src, trg, alignment

            line = self.stream.readline()

    def targetword(self, index, targetwords, alignment):
        """Return the aligned targeword for a specified index in the source words. Multiple words are concatenated together with a space in between"""
        return " ".join(targetwords[alignment[index]])

    def targetwords(self, index, targetwords, alignment):
        """Return the aligned targetwords for a specified index in the source words"""
        return [ targetwords[x] for x in alignment[index] ]

    def reset(self):
        self.stream.seek(0)


class IntersectionAlignment:          

    def __init__(self,source2target,target2source,encoding=False):
        self.s2t = MultiWordAlignment(source2target, encoding)
        self.t2s = WordAlignment(target2source, encoding)
        self.encoding = encoding

    def __iter__(self):
        for (src, trg, alignment), (revsrc, revtrg, revalignment) in izip(self.s2t,self.t2s):
            if src != revsrc or trg != revtrg:
                raise Exception("Files are not identical!")
            else:                
                #keep only those alignments that are present in both
                intersection = []                
                for i, x in enumerate(alignment):
                    if revalignment[i] and revalignment[i] in x:
                        intersection.append(revalignment[i])
                    else:
                        intersection.append(None)

                yield src, trg, intersection

    def reset(self):
        self.s2t.reset()
        self.t2s.reset()

