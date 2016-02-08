# -*- coding: utf8 -*-

###############################################################
#  PyNLPl - Text Processors
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#       Licensed under GPLv3
#
# This is a Python library containing text processors
#
###############################################################


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import isstring
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout

import unicodedata
import string
import io
import array
import re
from itertools import permutations
from pynlpl.statistics import FrequencyList
from pynlpl.formats import folia
from pynlpl.algorithms import bytesize

WHITESPACE = [" ", "\t", "\n", "\r","\v","\f"]
EOSMARKERS = ('.','?','!','。',';','؟','｡','？','！','।','։','՞','።','᙮','។','៕')
REGEXP_URL = re.compile(r"^(?:(?:https?):(?:(?://)|(?:\\\\))|www\.)(?:[\w\d:#@%/;$()~_?\+-=\\\.&](?:#!)?)*")
REGEXP_MAIL = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+(?:\.[a-zA-Z]+)+") #email
TOKENIZERRULES = (REGEXP_URL, REGEXP_MAIL)


class Windower(object):
    """Moves a sliding window over a list of tokens, upon iteration in yields all n-grams of specified size in a tuple.

    Example without markers:

    >>> for ngram in Windower("This is a test .",3, None, None):
    ...     print(" ".join(ngram))
    This is a
    is a test
    a test .

    Example with default markers:

    >>> for ngram in Windower("This is a test .",3):
    ...     print(" ".join(ngram))
    <begin> <begin> This
    <begin> This is
    This is a
    is a test
    a test .
    test . <end>
    . <end> <end>
    """

    def __init__(self, tokens, n=1, beginmarker = "<begin>", endmarker = "<end>"):
        """
        Constructor for Windower

        :param tokens: The tokens to iterate over. Should be an itereable. Strings will be split on spaces automatically.
        :type tokens: iterable
        :param n: The size of the n-grams to extract
        :type n: integer
        :param beginmarker: The marker for the beginning of the sentence, defaults to "<begin>". Set to None if no markers are desired.
        :type beginmarker: string or None
        :param endmarker: The marker for the end of the sentence, defaults to "<end>". Set to None if no markers are desired.
        :type endmarker: string or None
        """


        if isinstance(tokens, str) or (sys.version < '3' and isinstance(tokens, unicode)):
            self.tokens = tuple(tokens.split())
        else:
            self.tokens = tuple(tokens)
        assert isinstance(n, int)
        self.n = n
        self.beginmarker = beginmarker
        self.endmarker = endmarker

    def __len__(self):
        """Returns the number of n-grams in the data (quick computation without iteration)

        Without markers:

        >>> len(Windower("This is a test .",3, None, None))
        3

        >>> len(Windower("This is a test .",2, None, None))
        4

        >>> len(Windower("This is a test .",1, None, None))
        5

        With default markers:

        >>> len(Windower("This is a test .",3))
        7

        """

        c = (len(self.tokens) - self.n) + 1
        if self.beginmarker: c += self.n-1
        if self.endmarker: c += self.n-1
        return c


    def __iter__(self):
        """Yields an n-gram (tuple) at each iteration"""
        l = len(self.tokens)

        if self.beginmarker:
            beginmarker = (self.beginmarker),  #tuple
        if self.endmarker:
            endmarker = (self.endmarker),  #tuple

        for i in range(-(self.n - 1),l):
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
        if isinstance(tokens, str) or (sys.version < '3' and isinstance(tokens, unicode)):
            self.tokens = tuple(tokens.split())
        else:
            self.tokens = tuple(tokens)
        assert isinstance(min_n, int)
        assert isinstance(max_n, int)
        self.min_n = min_n
        self.max_n = max_n
        self.beginmarker = beginmarker
        self.endmarker = endmarker

    def __iter__(self):
        for n in range(self.min_n, self.max_n + 1):
            for ngram in Windower(self.tokens,n, self.beginmarker, self.endmarker):
                yield ngram


class ReflowText(object):
    """Attempts to re-flow a text that has arbitrary line endings in it. Also undoes hyphenisation"""

    def __init__(self, stream, filternontext=True):
        self.stream = stream
        self.filternontext = filternontext

    def __iter__(self):
        eosmarkers = ('.',':','?','!','"',"'","„","”","’")
        emptyline = 0
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




class Tokenizer(object):
    """A tokenizer and sentence splitter, which acts on a file/stream-like object and when iterating over the object it yields
    a lists of tokens (in case the sentence splitter is active (default)), or a token (if the sentence splitter is deactivated).
    """

    def __init__(self, stream, splitsentences=True, onesentenceperline=False, regexps=TOKENIZERRULES):
        """
        Constructor for Tokenizer

        :param stream: An iterable or file-object containing the data to tokenize
        :type stream: iterable or file-like object
        :param splitsentences: Enable sentence splitter? (default=_True_)
        :type splitsentences: bool
        :param onesentenceperline: Assume input has one sentence per line? (default=_False_)
        :type onesentenceperline: bool
        :param regexps: Regular expressions to use as tokeniser rules in tokenisation (default=_pynlpl.textprocessors.TOKENIZERRULES_)
        :type regexps:  Tuple/list of regular expressions to use in tokenisation
        """

        self.stream = stream
        self.regexps = regexps
        self.splitsentences=splitsentences
        self.onesentenceperline = onesentenceperline

    def __iter__(self):
        buffer = ""
        for line in self.stream:
            line = line.strip()
            if line:
                if buffer: buffer += "\n"
                buffer += line

            if (self.onesentenceperline or not line) and buffer:
                if self.splitsentences:
                    yield split_sentences(tokenize(buffer))
                else:
                    for token in tokenize(buffer, self.regexps):
                        yield token
                buffer = ""

        if buffer:
            if self.splitsentences:
                yield split_sentences(tokenize(buffer))
            else:
                for token in tokenize(buffer, self.regexps):
                    yield token




def tokenize(text, regexps=TOKENIZERRULES):
    """Tokenizes a string and returns a list of tokens

    :param text: The text to tokenise
    :type text: string
    :param regexps: Regular expressions to use as tokeniser rules in tokenisation (default=_pynlpl.textprocessors.TOKENIZERRULES_)
    :type regexps:  Tuple/list of regular expressions to use in tokenisation
    :rtype: Returns a list of tokens

    Examples:

    >>> for token in tokenize("This is a test."):
    ...    print(token)
    This
    is
    a
    test
    .


    """

    for i,regexp in list(enumerate(regexps)):
        if isstring(regexp):
            regexps[i] = re.compile(regexp)

    tokens = []
    begin = 0
    for i, c in enumerate(text):
        if begin > i:
            continue
        elif i == begin:
            m = False
            for regexp in regexps:
                m = regexp.findall(text[i:i+300])
                if m:
                    tokens.append(m[0])
                    begin = i + len(m[0])
                    break
            if m: continue

        if c in string.punctuation or c in WHITESPACE:
            prev = text[i-1] if i > 0 else ""
            next = text[i+1] if i < len(text)-1 else ""

            if (c == '.' or c == ',') and prev.isdigit() and next.isdigit():
                #punctuation in between numbers, keep as one token
                pass
            elif (c == "'" or c == "`") and prev.isalpha() and next.isalpha():
                #quote in between chars, keep...
                pass
            elif c not in WHITESPACE and next == c: #group clusters of identical punctuation together
                continue
            elif c == '\r' and prev == '\n':
                #ignore
                begin = i+1
                continue
            else:
                token = text[begin:i]
                if token: tokens.append(token)

                if c not in WHITESPACE:
                    tokens.append(c) #anything but spaces and newlines (i.e. punctuation) counts as a token too
                begin = i + 1 #set the begin cursor

    if begin <= len(text) - 1:
        token = text[begin:]
        tokens.append(token)

    return tokens


def crude_tokenizer(text):
    """Replaced by tokenize(). Alias"""
    return tokenize(text) #backwards-compatibility, not so crude anymore

def tokenise(text, regexps=TOKENIZERRULES): #for the British
    """Alias for the British"""
    return tokenize(text)

def is_end_of_sentence(tokens,i ):
    # is this an end-of-sentence marker? ... and is this either
    # the last token or the next token is NOT an end of sentence
    # marker as well? (to deal with ellipsis etc)
    return tokens[i] in EOSMARKERS and (i == len(tokens) - 1 or not tokens[i+1] in EOSMARKERS)

def split_sentences(tokens):
    """Split sentences (based on tokenised data), returns sentences as a list of lists of tokens, each sentence is a list of tokens"""
    begin = 0
    for i, token in enumerate(tokens):
        if is_end_of_sentence(tokens, i):
            yield tokens[begin:i+1]
            begin = i+1
    if begin <= len(tokens)-1:
        yield tokens[begin:]



def strip_accents(s, encoding= 'utf-8'):
    """Strip characters with diacritics and return a flat ascii representation"""
    if sys.version < '3':
        if isinstance(s,unicode):
           return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')
        else:
           return unicodedata.normalize('NFKD', unicode(s,encoding)).encode('ASCII', 'ignore')
    else:
        if isinstance(s,bytes): s = str(s,encoding)
        return str(unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore'),'ascii')

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


def find_keyword_in_context(tokens, keyword, contextsize=1):
    """Find a keyword in a particular sequence of tokens, and return the local context. Contextsize is the number of words to the left and right. The keyword may have multiple word, in which case it should to passed as a tuple or list"""
    if isinstance(keyword,tuple) and isinstance(keyword,list):
        l = len(keyword)
    else:
        keyword = (keyword,)
        l = 1
    n = l + contextsize*2
    focuspos = contextsize + 1
    for ngram in Windower(tokens,n,None,None):
        if ngram[focuspos:focuspos+l] == keyword:
            yield ngram[:focuspos], ngram[focuspos:focuspos+l],ngram[focuspos+l+1:]



if __name__ == "__main__":
    import doctest
    doctest.testmod()

