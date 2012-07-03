# -*- coding: utf8 -*-

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
import codecs
import array
from statistics import FrequencyList
from datatypes import intarraytobytearray, bytearraytoint, containsnullbyte

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
    """Moves a sliding window over a list of tokens, returning all ngrams"""

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

class MultiWindower(object):
    "Extract n-grams of various configurations from a sequence"
    
    def __init__(self,tokens, min_n = 1, max_n = 9, beginmarker=None, endmarker=None):
        if isinstance(tokens, str) or  isinstance(unicode, str):
            self.tokens = tuple(tokens.split())
        else:
            self.tokens = tuple(tokens)
        self.min_n = min_n
        self.max_n = max_n
        self.beginmarker = beginmarker
        self.endmarker = endmarker        
        
    def __iter__(self):
        for n in range(self.min_n, self.max_n + 1):
            for ngram in Windower(self.tokens,n, self.beginmarker, self.endmarker):
                yield ngram        


class ReflowText(object):
    def __init__(self, stream, filternontext=True):
        self.stream = stream
        self.filternontext = filternontext
        
    def __iter__(self):
        eosmarkers = ('.',':','?','!','"',"'",u"„",u"”",u"’")
        emptyline = 0
        pagebreak = False
        niceeos = True
        buffer = ""
        for line in self.stream:
            
            line = line.strip()
            if line:
                if emptyline:
                    if buffer:
                        yield buffer
                        yield ""
                        emptyline = 0
                        buffer = ""
                    
                if buffer: buffer += ' '                
                if (line[-1] in eosmarkers):
                    buffer += line
                    yield buffer
                    buffer = ""
                    emptyline = 0
                elif len(line) > 2 and line[-1] == '-' and line[-2].isalpha():
                    #undo hyphenisation
                    buffer += line[:-1]
                else:    
                    if self.filternontext:
                        hastext = False
                        for c in line:
                            if c.isalpha():
                                hastext = True
                                break
                    else:                                
                        hastext = True
                        
                    if hastext:
                        buffer += line
            else:                    
                emptyline += 1
              
            #print "BUFFER=[" + buffer.encode('utf-8') + "] emptyline=" + str(emptyline)
            
        if buffer:
            yield buffer
            


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
    

def strip_accents(s, encoding= 'utf-8'):
    """Strip characters with diacritics and return a flat ascii representation"""
    if isinstance(s,unicode):
       return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')
    else:
       return unicodedata.normalize('NFKD', unicode(s,encoding)).encode('ASCII', 'ignore')



def swap(tokens, maxdist=2):
    """Perform a swap operation on a sequence of tokens, exhaustively swapping all tokens up to the maximum specified distance. This is a subset of all permutations."""
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
        


class Classer(object):
    """The Classer can encode and decode tokens to an integer representation. It is constructed using a frequency list."""
    
    def __init__(self, f, **kwargs):
        """Pass either a filename of a plain text data file or a pre-computed frequency list.
        
        Keyword arguments:
            decoder = True/False   Enable decoder? Default: True
            encoder = True/False   Enable encoder? Default: True
            encoding = (str)       The encoding of your data (None for encoding-agnostic, default)
        """
        
        if 'decoder' in kwargs:
            self.decoder = bool(kwargs['decoder'])
        else:
            self.decoder = True
        
        if 'encoder' in kwargs:
            self.encoder = bool(kwargs['encoder'])
        else:
            self.encoder = True

        self.newestclass = 0
            
        if self.decoder:
            self.class2word = {} 
        if self.encoder:    
            self.word2class = {}

        if 'encoding' in kwargs and kwargs['encoding']:
            self.encoding = kwargs['encoding']
        else:
            self.encoding = None
            
        if 'filesupport' in kwargs:
            self.filesupport = bool(kwargs['filesupport'])
        else:
            self.filesupport = False
            
        if self.filesupport:
            self.newestclass = 1 #0 and 1 are reserved for space and newline
                    
        if isinstance(f, FrequencyList):                        
            for word, _ in f:  
                self.newestclass += 1
                if self.filesupport:
                    while containsnullbyte(self.newestclass): 
                        self.newestclass += 1
                print self.newestclass, word
                if self.decoder:
                    self.class2word[self.newestclass] = word  
                if self.encoder:
                    self.word2class[word] = self.newestclass
            if not self.decoder:
                del self.class2word
        elif isinstance(f, str):
            f = codecs.open(f,'r','utf-8')      
            for line in f:
                cls, word = line.strip().split('\t',2)
                if self.decoder: self.class2word[int(cls)] = word
                if self.encoder: self.word2class[word] = int(cls)
            f.close()
        else: 
            raise Exception("Expected FrequencyList or filename, got " + str(type(f)))
        
        

    def save(self, filename):
        """Save to a class file"""
        if not self.decoder: raise Exception("Decoder not enabled!")
        if self.encoding:
            f = codecs.open(filename,'w',self.encoding)   
        else:
            f = open(filename,'w')
        for cls, word in sorted(self.class2word.items()):
            if cls:
                f.write( str(cls) + '\t' + word + '\n')
        f.close()
                    
    def decode(self, x):
        """Encode a class integer, return string token"""
        try:
            return self.class2word[x]
        except:
            if not self.decoder: 
                raise Exception("Decoder not enabled!")
            else:
                raise
            
    def encode(self, x):        
        """Encode a string token, return class integer"""
        try:
            return self.word2class[x]
        except:
            if not self.encoder:
                raise Exception("Encoder not enabled!")
            else:
                raise
                        
    def decodeseq(self, sequence):
        """Decode a sequence, converting class integers to strings"""
        return tuple( self.decode(x) for x in sequence  )
        
    def encodeseq(self, sequence):
        """Encode a sequence of string tokens to class integers"""
        return tuple( self.encode(x) for x in sequence  )
        
    def __len__(self):
        try:
            return len(self.class2word)
        except:
            return len(self.word2class)
        
    def encodefile(self, fromfile, tofile):
        """Encode a file, converting word tokens to class integers"""
        assert self.filesupport
        ffrom = open(fromfile,'r')  
        fto = open(tofile,'w')
        for line in ffrom:
            a = intarraytobytearray( self.encodeseq( line.strip().split(' ') ))
            a.append(0) #delimiter
            a.append(1) #newline
            a.append(0) #delimiter
            a.tofile(fto)            
        fto.close()
        ffrom.close()
        
    def decodefile(self, filename):
        """Decode a file, converting class integers to token strings"""
        f = open(filename)
        buffer = array.array('B')
        line = []
        b = chr(0)
        nullbyte = chr(0)
        while b != "":
            b = f.read(1)
            if b == "": break
            if b == nullbyte:
                cls = bytearraytoint(buffer)
                if cls == 1:
                    yield line
                    line = []
                else:
                    line.append( self.decode(cls) )
                buffer = array.array('B')
            else:
                buffer.append(ord(b))
        f.close()
        
            

    
    
        
