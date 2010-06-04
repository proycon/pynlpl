###############################################################
#  PyNLPl - Text Processors
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
# 
# This is a Python library containing text processors
#
###############################################################

import unicodedata
import string

class Windower:
    """Moves a sliding window over a list of tokens, returning all windows"""

    def __init__(self, tokens, n=1, beginmarker = "<begin>", endmarker = "<end>"):
        if isinstance(tokens, str) or  isinstance(unicode, str):
            self.tokens = tokens.split()
        else:
            self.tokens = tokens
        self.n = n
        self.beginmarker = beginmarker
        self.endmarker = endmarker

    def __iter__(self):
        l = len(self.tokens)

        for i in xrange(-(self.n - 1),l):
            begin = i
            end = i + self.n
            if begin >= 0 and end <= l:
                yield self.tokens[begin:end] 
            elif begin < 0 and end > l:
                if not self.beginmarker or not self.endmarker:
                    continue
                else:
                   yield ((begin * -1) * [self.beginmarker]) + self.tokens + ((end - l) * [self.endmarker])
            elif begin < 0:
                if not self.beginmarker: 
                   continue   
                else: 
                   yield ((begin * -1) * [self.beginmarker]) + self.tokens[0:end] 
            elif end > l:
                if not self.endmarker:
                   continue
                else:
                   yield self.tokens[begin:] + ((end - l) * [self.endmarker])

def crude_tokenizer(line):
    """This is a very crude tokenizer"""
    tokens = []
    buffer = ''
    for c in line.strip():
        if c == ' ' or c in string.punctuation:
            if buffer:
                tokens.append(buffer)
                buffer = ''
        else:
            buffer += c          
    if buffer: tokens.append(buffer)  
    return tokens

def strip_accents(s, encoding= 'utf-8'):
      if isinstance(s,unicode):
          return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')
      else:
          return unicodedata.normalize('NFKD', unicode(s,encoding)).encode('ASCII', 'ignore')


