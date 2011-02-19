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

try:
    from itertools import permutations
except ImportError: #python too old, include function explicitly (code from from Python Documentation)
    def permutations(iterable, r=None): 
        # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
        # permutations(range(3)) --> 012 021 102 120 201 210
        pool = tuple(iterable)
        n = len(pool)
        r = n if r is None else r
        if r > n:
            return
        indices = range(n)
        cycles = range(n, n-r, -1)
        yield tuple(pool[i] for i in indices[:r])
        while n:
            for i in reversed(range(r)):
                cycles[i] -= 1
                if cycles[i] == 0:
                    indices[i:] = indices[i+1:] + indices[i:i+1]
                    cycles[i] = n - i
                else:
                    j = cycles[i]
                    indices[i], indices[-j] = indices[-j], indices[i]
                    yield tuple(pool[i] for i in indices[:r])
                    break
            else:
                return
            
            
class Windower:
    """Moves a sliding window over a list of tokens, returning all windows"""

    def __init__(self, tokens, n=1, beginmarker = "<begin>", endmarker = "<end>"):
        if isinstance(tokens, str) or  isinstance(unicode, str):
            self.tokens = tuple(tokens.split())
        else:
            self.tokens = tuple(tokens)
        self.n = n
        self.beginmarker = beginmarker
        self.endmarker = endmarker

    def __iter__(self):
        l = len(self.tokens)

        if self.beginmarker:
            beginmarker = (self.beginmarker),  #tuple
        if self.endmarker:
            endmarker = (self.endmarker),  #tuple

        for i in xrange(-(self.n - 1),l):
            begin = i
            end = i + self.n
            if begin >= 0 and end <= l:
                yield tuple(self.tokens[begin:end])
            elif begin < 0 and end > l:
                if not self.beginmarker or not self.endmarker:
                    continue
                else:
                   yield tuple(((begin * -1) * beginmarker  ) + self.tokens + ((end - l) * endmarker ))
            elif begin < 0:
                if not self.beginmarker: 
                   continue   
                else: 
                   yield tuple(((begin * -1) * beginmarker ) + self.tokens[0:end])
            elif end > l:
                if not self.endmarker:
                   continue
                else:
                   yield tuple(self.tokens[begin:] + ((end - l) * endmarker))


def calculate_overlap(haystack, needle, allowpartial=True):
    """Calculate the overlap between two sequences. Yields (overlap, placement) tuples (multiple because there may be multiple overlaps!). The former is the part of the sequence that overlaps, and the latter is -1 if the overlap is on the left side, 0 if it is a subset, 1 if it overlaps on the right side, 2 if its an identical match"""    
    needle = tuple(needle)
    haystack = tuple(haystack)
    solutions = []
    
    #equality check    
    if needle == haystack:
        return [(needle, 2)]

    if allowpartial: 
        minl =1
    else:
        minl = len(needle)
        
    for l in range(minl,min(len(needle), len(haystack))+1):    
        #print "LEFT-DEBUG", l,":", needle[-l:], " vs ", haystack[:l]
        #print "RIGHT-DEBUG", l,":", needle[:l], " vs ", haystack[-l:]
        #Search for overlap left (including partial overlap!)
        if needle[-l:] == haystack[:l]:
            #print "LEFT MATCH"
            solutions.append( (needle[-l:], -1) )
        #Search for overlap right (including partial overlap!)
        if needle[:l] == haystack[-l:]:
            #print "RIGHT MATCH"
            solutions.append( (needle[:l], 1) )

    if len(needle) <= len(haystack):
        options = list(iter(Windower(haystack,len(needle),beginmarker=None,endmarker=None)))
        for option in options[1:-1]:
            if option == needle:
                #print "SUBSET MATCH"
                solutions.append( (needle, 0) )

    return solutions
            
    

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

def extract_sentences(text):
    """Crude sentence tokeniser"""
    

def strip_accents(s, encoding= 'utf-8'):
      if isinstance(s,unicode):
          return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')
      else:
          return unicodedata.normalize('NFKD', unicode(s,encoding)).encode('ASCII', 'ignore')



def swap(tokens, maxdist=2):
    assert maxdist >= 2
    tokens = list(tokens)
    if maxdist > len(tokens):
        maxdist = len(tokens)
    l = len(tokens)
    for i in range(0,l - 1):
        for permutation in permutations(tokens[i:i+maxdist]):
            if permutation != tuple(tokens[i:i+maxdist]):
                newtokens = tokens[:i]
                newtokens += permutation
                newtokens += tokens[i+maxdist:]
                yield newtokens
        if maxdist == len(tokens):
            break
        
