#---------------------------------------------------------------
# PyNLPl - Language Models
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

from pynlpl.statistics import FrequencyList, product
from pynlpl.textprocessors import Windower
import codecs
from sys import stderr


class SimpleLanguageModel:
    """This is a very simple unsmoothed language model"""
    def __init__(self, n=2, casesensitive = True, beginmarker = "<begin>", endmarker = "<end>"):
        self.casesensitive = casesensitive
        self.freqlistN = FrequencyList(None, self.casesensitive)
        self.freqlistNm1 = FrequencyList(None, self.casesensitive)

        assert n >= 2
        self.n = n
        self.beginmarker = beginmarker
        self.endmarker = endmarker
        self.sentences = 0

        if self.beginmarker:
            self._begingram = tuple([self.beginmarker] * (n-1))
        if self.endmarker:
            self._endgram = tuple([self.endmarker] * (n-1))

    def append(self, sentence):
        if isinstance(sentence, str) or isinstance(sentence, unicode):
            sentence = sentence.strip().split(' ')
        self.sentences += 1
        for ngram in Windower(sentence,self.n, self.beginmarker, self.endmarker):
            self.freqlistN.count(ngram)
        for ngram in Windower(sentence,self.n-1, self.beginmarker, self.endmarker):
            self.freqlistNm1.count(ngram)  


    def load(self, filename):
        self.freqlistN = FrequencyList(None, self.casesensitive)
        self.freqlistNm1 = FrequencyList(None, self.casesensitive)
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
                        self.beginmarker = line[12:]
                    elif line[:10] == 'endmarker=':
                        self.endmarker = line[10:]   
                    elif line[:10] == 'sentences=':
                        self.sentences = int(line[10:])
                    elif line[:14] == 'casesensitive=':
                        self.casesensitive = bool(int(line[14:]))
                        self.freqlistN = FrequencyList(None, self.casesensitive)
                        self.freqlistNm1 = FrequencyList(None, self.casesensitive)
                    elif line == "[freqlistN]":
                        mode = 2
                    else:
                        raise Exception("Syntax error in language model file: ", line)
                elif mode == 2:
                    if line == "[freqlistNm1]":
                        mode = 3
                    else:
                        try:
                            type, count = line.split("\t")
                            self.freqlistN.count(type.split(' '),int(count))
                        except:
                            print >>stderr,"Warning, could not parse line whilst loading frequency list: ", line
                elif mode == 3:
                        try:
                            type, count = line.split("\t")
                            self.freqlistNm1.count(type.split(' '),int(count))
                        except:
                            print >>stderr,"Warning, could not parse line whilst loading frequency list: ", line

        if self.beginmarker:
            self._begingram = [self.beginmarker] * (self.n-1)
        if self.endmarker:
            self._endgram = [self.endmarker] * (self.n-1)


    def save(self, filename):
        f = codecs.open(filename,'w','utf-8')
        f.write("[simplelanguagemodel]\n")
        f.write("n="+str(self.n)+"\n")
        f.write("sentences="+str(self.sentences)+"\n")
        f.write("beginmarker="+self.beginmarker+"\n")
        f.write("endmarker="+self.endmarker+"\n")
        f.write("casesensitive="+str(int(self.casesensitive))+"\n")
        f.write("\n")
        f.write("[freqlistN]\n")
        for line in self.freqlistN.output():
            f.write(line+"\n")
        f.write("[freqlistNm1]\n")
        for line in self.freqlistNm1.output():
            f.write(line+"\n")
        f.close()


    def scoresentence(self, sentence):
        return product([self[x] for x in Windower(sentence, self.n, self.beginmarker, self.endmarker)])
            

    def __getitem__(self, ngram):
        assert len(ngram) == self.n

        nm1gram = ngram[:-1]

        if (self.beginmarker and nm1gram == self._begingram) or (self.endmarker and nm1gram == self._endgram):
            return self.freqlistN[ngram] / float(self.sentences)
        else:   
            return self.freqlistN[ngram] / float(self.freqlistNm1[nm1gram])





