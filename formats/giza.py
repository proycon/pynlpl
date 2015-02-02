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

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from pynlpl.common import u

import bz2
import gzip
import copy
import io
from sys import stderr

class GizaSentenceAlignment(object):

    def __init__(self, sourceline, targetline, index):
        self.index = index
        self.alignment = []
        if sourceline:
            self.source = self._parsesource(sourceline.strip())
        else:
            self.source = []
        self.target = targetline.strip().split(' ')

    def _parsesource(self, line):
        cleanline = ""

        inalignment = False
        begin = 0
        sourceindex = 0

        for i in range(0,len(line)):
            if line[i] == ' ' or i == len(line) - 1:
                if i == len(line) - 1:
                    offset = 1
                else:
                    offset = 0

                word = line[begin:i+offset]
                if word == '})':
                    inalignment = False
                    begin = i + 1
                    continue
                elif word == "({":
                    inalignment = True
                    begin = i + 1
                    continue
                if word.strip() and word != 'NULL':
                    if not inalignment:
                        sourceindex += 1
                        if cleanline: cleanline += " "
                        cleanline += word
                    else:
                        targetindex = int(word)
                        self.alignment.append( (sourceindex-1, targetindex-1) )
                begin = i + 1

        return cleanline.split(' ')


    def intersect(self,other):
        if other.target != self.source:
            print("GizaSentenceAlignment.intersect(): Mismatch between self.source and other.target: " + repr(self.source) + " -- vs -- " + repr(other.target),file=stderr)
            return None

        intersection = copy.copy(self)
        intersection.alignment = []

        for sourceindex, targetindex in self.alignment:
            for targetindex2, sourceindex2 in other.alignment:
                if targetindex2 == targetindex and sourceindex2 == sourceindex:
                    intersection.alignment.append( (sourceindex, targetindex) )

        return intersection

    def __repr__(self):
        s = " ".join(self.source)+ " ||| "
        s += " ".join(self.target) + " ||| "
        for S,T in sorted(self.alignment):
            s += self.source[S] + "->" + self.target[T] + " ; "
        return s


    def getalignedtarget(self, index):
        """Returns target range only if source index aligns to a single consecutive range of target tokens."""
        targetindices = []
        target = None
        foundindex = -1
        for sourceindex, targetindex in self.alignment:
            if sourceindex == index:
                targetindices.append(targetindex)
        if len(targetindices) > 1:
            for i in range(1,len(targetindices)):
                if abs(targetindices[i] - targetindices[i-1]) != 1:
                    break  # not consecutive
            foundindex = (min(targetindices), max(targetindices))
            target = ' '.join(self.target[min(targetindices):max(targetindices)+1])
        elif targetindices:
            foundindex = targetindices[0]
            target = self.target[foundindex]

        return target, foundindex

class GizaModel(object):
    def __init__(self, filename, encoding= 'utf-8'):
        if filename.split(".")[-1] == "bz2":
            self.f = bz2.BZ2File(filename,'r')
        elif filename.split(".")[-1] == "gz":
            self.f = gzip.GzipFile(filename,'r')
        else:
            self.f = io.open(filename,'r',encoding=encoding)
        self.nextlinebuffer = None


    def __iter__(self):
        self.f.seek(0)
        nextlinebuffer = u(next(self.f))
        sentenceindex = 0

        done = False
        while not done:
            sentenceindex += 1
            line = nextlinebuffer
            if line[0] != '#':
                raise Exception("Error parsing GIZA++ Alignment at sentence " +  str(sentenceindex) + ", expected new fragment, found: " + repr(line))

            targetline = u(next(self.f))
            sourceline = u(next(self.f))

            yield GizaSentenceAlignment(sourceline, targetline, sentenceindex)

            try:
                nextlinebuffer = u(next(self.f))
            except StopIteration:
                done = True


    def __del__(self):
        if self.f: self.f.close()


#------------------ OLD -------------------

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
                yield [ u(w,self.encoding) for w in src ], [ u(w,self.encoding) for w in trg ], alignment
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
        for (src, trg, alignment), (revsrc, revtrg, revalignment) in zip(self.s2t,self.t2s): #will take unnecessary memory in Python 2.x, optimal in Python 3
            if src != revsrc or trg != revtrg:
                raise Exception("Files are not identical!")
            else:
                #keep only those alignments that are present in both
                intersection = []
                for i, x in enumerate(alignment):
                    if revalignment[i] in x:
                        intersection.append(revalignment[i])
                    else:
                        intersection.append(None)

                yield src, trg, intersection

    def reset(self):
        self.s2t.reset()
        self.t2s.reset()

