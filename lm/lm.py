#---------------------------------------------------------------
# PyNLPl - Language Models
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
#from pynlpl.common import u
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout

from pynlpl.statistics import FrequencyList, product
from pynlpl.textprocessors import Windower
import math
import io



class SimpleLanguageModel:
    """This is a simple unsmoothed language model. This class can both hold and compute the model."""

    def __init__(self, n=2, casesensitive = True, beginmarker = "<begin>", endmarker = "<end>"):
        self.casesensitive = casesensitive
        self.freqlistN = FrequencyList(None, self.casesensitive)
        self.freqlistNm1 = FrequencyList(None, self.casesensitive)

        assert isinstance(n,int) and n >= 2
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
        f = io.open(filename,'r',encoding='utf-8')
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
                            print("Warning, could not parse line whilst loading frequency list: ", line,file=stderr)
                elif mode == 3:
                        try:
                            type, count = line.split("\t")
                            self.freqlistNm1.count(type.split(' '),int(count))
                        except:
                            print("Warning, could not parse line whilst loading frequency list: ", line,file=stderr)

        if self.beginmarker:
            self._begingram = [self.beginmarker] * (self.n-1)
        if self.endmarker:
            self._endgram = [self.endmarker] * (self.n-1)


    def save(self, filename):
        f = io.open(filename,'w',encoding='utf-8')
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


class ARPALanguageModel(object):
    """Full back-off language model, loaded from file in ARPA format. This class does not build the model but allows you to use a pre-computed one. You can use the tool ngram-count from for instance SRILM to actually build the model. """

    def __init__(self, filename, encoding = 'utf-8', encoder=None, base_e=True, dounknown=True,debug=False):
        self.ngrams = {}
        self.backoff = {}
        self.total = {}
        self.base_e = base_e
        self.dounknown = dounknown
        self.debug = False

        if encoder is None:
            self.encoder = lambda x: x
        else:
            self.encoder = encoder

        with io.open(filename,'r',encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if line == '\\data\\':
                    order = 0
                elif line == '\\end\\':
                    break
                elif line and line[0] == '\\' and line[-1] == ':':
                    for i in range(1,10):
                        if line == '\\' + str(i) + '-grams:':
                            order = i
                elif line:
                    if order == 0:
                        if line[0:6] == "ngram":
                            n = int(line[6])
                            v = int(line[8])
                            self.total[n] = v
                    elif order > 0:
                        fields = line.split('\t')
                        if base_e:
                            logprob = float(fields[0]) * math.log(10)   # * log(10) does log10 to log_e conversion
                        else:
                            logprob = float(fields[0])
                        ngram = self.encoder(tuple(fields[1].split()))
                        self.ngrams[ngram] = logprob
                        if len(fields) > 2:
                            if base_e:
                                backoffprob = float(fields[2]) * math.log(10)
                            else:
                                backoffprob = float(fields[2])
                            self.backoff[ngram] = backoffprob
                            if self.debug:
                                print("Adding to LM: " + str(ngram) + "\t" << str(logprob) + "\t" + str(backoffprob), file=stderr)
                        elif self.debug:
                            print("Adding to LM: " + str(ngram) + "\t" << str(logprob), file=stderr)
                    elif self.debug:
                        print("Unable to parse ARPA LM line: " + line, file=stderr)

        self.order = order

    def score(self, data, history=None):
        result = 0
        for word in data:
            result += self.scoreword(word, history)
            if history:
                history += (word,)
            else:
                history = (word,)
        return result

    def scoreword(self, word, history=None):
        if isinstance(word, str) or (sys.version < '3' and isinstance(word, unicode)):
            word = (word,)
        if history:
            lookup = history + word
        else:
            lookup = word

        if len(lookup) > self.order:
            lookup = lookup[-self.order:]

        try:
            return self.ngrams[lookup]
        except KeyError:
            #not found, back off
            if not history:
                if self.dounknown:
                    try:
                        return self.ngrams[('<unk>',)]
                    except KeyError:
                        raise KeyError("Word " + str(word) + " not found. And no history specified and model has no <unk>")
                else:
                    raise KeyError("Word " + str(word) + " not found. And no history specified")

            try:
                backoffweight = self.backoff[history]
            except KeyError:
                backoffweight = 0 #backoff weight will be 0 if not found
            return backoffweight + self.scoreword(word, history[1:])



    def __len__(self):
        return len(self.ngrams)




