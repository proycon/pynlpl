#---------------------------------------------------------------
# PyNLPl - Language Models
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import math
import sys

from pynlpl.statistics import FrequencyList, product
from pynlpl.textprocessors import Windower

if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout


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

    """Full back-off language model, loaded from file in ARPA format.

    This class does not build the model but allows you to use a pre-computed one.
    You can use the tool ngram-count from for instance SRILM to actually build the model.

    """

    class NgramsProbs(object):
        """Store Ngrams with their probabilities and backoffs.

        This class is used in order to abstract the physical storage layout,
        and enable memory/speed tradeoffs.

        """

        def __init__(self, data, mode='simple', delim=' '):
            """Create an ngrams storage with the given method:

            'simple' method is a Python dictionary (quick, takes much memory).
            'trie' method is more space-efficient (~35% reduction) but slower.
            data is a dictionary of ngram-tuple => (probability, backoff).
            delim is the strings which converts ngrams between tuple and
            unicode string (for saving in trie mode).

            """
            self.delim = delim
            self.mode = mode
            if mode == 'simple':
                self._data = data
            elif mode == 'trie':
                import marisa_trie
                self._data = marisa_trie.RecordTrie("@dd", [(self.delim.join(k), v) for k, v in data.items()])
            else:
                raise ValueError("mode {} is not supported for NgramsProbs".format(mode))

        def prob(self, ngram):
            """Return probability of given ngram tuple"""
            return self._data[ngram][0] if self.mode == 'simple' else self._data[self.delim.join(ngram)][0][0]

        def backoff(self, ngram):
            """Return backoff value of a given ngram tuple"""
            return self._data[ngram][1] if self.mode == 'simple' else self._data[self.delim.join(ngram)][0][1]

        def __len__(self):
            return len(self._data)


    def __init__(self, filename, encoding='utf-8', encoder=None, base_e=True, dounknown=True, debug=False, mode='simple'):
        # parameters
        self.encoder = (lambda x: x) if encoder is None else encoder
        self.base_e = base_e
        self.dounknown = dounknown
        self.debug = debug
        self.mode = mode
        # other attributes
        self.total = {}

        data = {}

        with io.open(filename, 'rt', encoding=encoding) as f:
            order = None
            for line in f:
                line = line.strip()
                if line == '\\data\\':
                    order = 0
                elif line == '\\end\\':
                    break
                elif line.startswith('\\') and line.endswith(':'):
                    for i in range(1, 10):
                        if line == '\\{}-grams:'.format(i):
                            order = i
                            break
                    else:
                        raise ValueError("Order of n-gram is not supported!")
                elif line:
                    if order == 0:  # still in \data\ section
                        if line.startswith('ngram'):
                            n = int(line[6])
                            v = int(line[8:])
                            self.total[n] = v
                    elif order > 0:
                        fields = line.split('\t')
                        logprob = float(fields[0])
                        if base_e:  # * log(10) does log10 to log_e conversion
                            logprob *= math.log(10)
                        ngram = self.encoder(tuple(fields[1].split()))
                        if len(fields) > 2:
                            backoffprob = float(fields[2])
                            if base_e:  # * log(10) does log10 to log_e conversion
                                backoffprob *= math.log(10)
                            if self.debug:
                                msg = "Adding to LM: {}\t{}\t{}"
                                print(msg.format(ngram, logprob, backoffprob), file=stderr)
                        else:
                            backoffprob = 0.0
                            if self.debug:
                                msg = "Adding to LM: {}\t{}"
                                print(msg.format(ngram, logprob), file=stderr)
                        data[ngram] = (logprob, backoffprob)
                    elif self.debug:
                        print("Unable to parse ARPA LM line: " + line, file=stderr)
        self.order = order
        self.ngrams = self.NgramsProbs(data, mode)

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
            return self.ngrams.prob(lookup)
        except KeyError:  # not found, back off
            if not history:
                if self.dounknown:
                    try:
                        return self.ngrams.prob(('<unk>',))
                    except KeyError:
                        msg = "Word {} not found. And no history specified and model has no <unk>."
                        raise KeyError(msg.format(word))
                else:
                    msg = "Word {} not found. And no history specified."
                    raise KeyError(msg.format(word))
            else:
                try:
                    backoffweight = self.ngrams.backoff(history)
                except KeyError:
                    backoffweight = 0  # backoff weight will be 0 if not found
                return backoffweight + self.scoreword(word, history[1:])

    def __len__(self):
        return len(self.ngrams)
