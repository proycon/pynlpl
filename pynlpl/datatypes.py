#---------------------------------------------------------------
# PyNLPl - Data Types
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#   Based in large part on MIT licensed code from
#    AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
#    Peter Norvig
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

"""This library contains various extra data types, based to a certain extend on MIT-licensed code from Peter Norvig, AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import u

import random
import bisect
import array
from sys import version as PYTHONVERSION


class Queue(object): #from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """Queue is an abstract class/interface. There are three types:
        Python List: A Last In First Out Queue (no Queue object necessary).
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(lt): Queue where items are sorted by lt, (default <).
    Each type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())."""

    def extend(self, items):
        """Append all elements from items to the queue"""
        for item in items: self.append(item)


#note: A Python list is a LIFOQueue / Stack

class FIFOQueue(Queue): #adapted from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """A First-In-First-Out Queue"""
    def __init__(self, data = []):
        self.data = data
        self.start = 0

    def append(self, item):
        self.data.append(item)

    def __len__(self):
        return len(self.data) - self.start

    def extend(self, items):
        """Append all elements from items to the queue"""
        self.data.extend(items)

    def pop(self):
        """Retrieve the next element in line, this will remove it from the queue"""
        e = self.data[self.start]
        self.start += 1
        if self.start > 5 and self.start > len(self.data)//2:
            self.data = self.data[self.start:]
            self.start = 0
        return e

class PriorityQueue(Queue): #Heavily adapted/extended, originally from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """A queue in which the maximum (or minumum) element is returned first,
    as determined by either an external score function f (by default calling
    the objects score() method). If minimize=True, the item with minimum f(x) is
    returned first; otherwise is the item with maximum f(x) or x.score().

    length can be set to an integer > 0. Items will only be added to the queue if they're better or equal to the worst scoring item. If set to zero, length is unbounded.
    blockworse can be set to true if you want to prohibit adding worse-scoring items to the queue. Only items scoring better than the *BEST* one are added.
    blockequal can be set to false if you also want to prohibit adding equally-scoring items to the queue.
    (Both parameters default to False)
    """
    def __init__(self, data =[], f = lambda x: x.score, minimize=False, length=0, blockworse=False, blockequal=False,duplicates=True):
        self.data = []
        self.f = f
        self.minimize=minimize
        self.length = length
        self.blockworse=blockworse
        self.blockequal=blockequal
        self.duplicates= duplicates
        self.bestscore = None
        for item in data:
            self.append(item)

    def append(self, item):
        """Adds an item to the priority queue (in the right place), returns True if successfull, False if the item was blocked (because of a bad score)"""
        f = self.f(item)
        if callable(f):
            score = f()
        else:
            score = f

        if not self.duplicates:
            for s, i in self.data:
                if s == score and item == i:
                    #item is a duplicate, don't add it
                    return False

        if self.length and len(self.data) == self.length:
                #Fixed-length priority queue, abort when queue is full and new item scores worst than worst scoring item.
                if self.minimize:
                    worstscore = self.data[-1][0]
                    if score >= worstscore:
                        return False
                else:
                    worstscore = self.data[0][0]
                    if score <= worstscore:
                        return False

        if self.blockworse and self.bestscore != None:
            if self.minimize:
                if score > self.bestscore:
                    return False
            else:
                if score < self.bestscore:
                    return False
        if self.blockequal and self.bestscore != None:
            if self.bestscore == score:
                return False
        if (self.bestscore == None) or (self.minimize and score < self.bestscore) or (not self.minimize and score > self.bestscore):
            self.bestscore = score
        bisect.insort(self.data, (score, item))
        if self.length:
            #fixed length queue: queue is now too long, delete worst items
            while len(self.data) > self.length:
                if self.minimize:
                    del self.data[-1]
                else:
                    del self.data[0]
        return True

    def __exists__(self, item):
        return (item in self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        """Iterate over all items, in order from best to worst!"""
        if self.minimize:
            f = lambda x: x
        else:
            f = reversed
        for score, item in f(self.data):
            yield item

    def __getitem__(self, i):
        """Item 0 is always the best item!"""
        if isinstance(i, slice):
            indices = i.indices(len(self))
            if self.minimize:
                return PriorityQueue([ self.data[j][1] for j in range(*indices) ],self.f, self.minimize, self.length, self.blockworse, self.blockequal)
            else:
                return PriorityQueue([ self.data[(-1 * j) - 1][1] for j in range(*indices) ],self.f, self.minimize, self.length, self.blockworse, self.blockequal)
        else:
            if self.minimize:
                return self.data[i][1]
            else:
                return self.data[(-1 * i) - 1][1]

    def pop(self):
        """Retrieve the next element in line, this will remove it from the queue"""
        if self.minimize:
            return self.data.pop(0)[1]
        else:
            return self.data.pop()[1]


    def score(self, i):
        """Return the score for item x (cheap lookup), Item 0 is always the best item"""
        if self.minimize:
            return self.data[i][0]
        else:
            return self.data[(-1 * i) - 1][0]

    def prune(self, n):
        """prune all but the first (=best) n items"""
        if self.minimize:
            self.data = self.data[:n]
        else:
            self.data = self.data[-1 * n:]


    def randomprune(self,n):
        """prune down to n items at random, disregarding their score"""
        self.data = random.sample(self.data, n)

    def stochasticprune(self,n):
        """prune down to n items, chance of an item being pruned is reverse proportional to its score"""
        raise NotImplemented


    def prunebyscore(self, score, retainequalscore=False):
        """Deletes all items below/above a certain score from the queue, depending on whether minimize is True or False. Note: It is recommended (more efficient) to use blockworse=True / blockequal=True instead! Preventing the addition of 'worse' items."""
        if retainequalscore:
            if self.minimize:
                f = lambda x: x[0] <= score
            else:
                f = lambda x: x[0] >= score
        else:
            if self.minimize:
                f = lambda x: x[0] < score
            else:
                f = lambda x: x[0] > score
        self.data = filter(f, self.data)

    def __eq__(self, other):
        return (self.data == other.data) and (self.minimize == other.minimize)


    def __repr__(self):
        return repr(self.data)

    def __add__(self, other):
        """Priority queues can be added up, as long as they all have minimize or maximize (rather than mixed). In case of fixed-length queues, the FIRST queue in the operation will be authorative for the fixed lengthness of the result!"""
        assert (isinstance(other, PriorityQueue) and self.minimize == other.minimize)
        return PriorityQueue(self.data + other.data, self.f, self.minimize, self.length, self.blockworse, self.blockequal)

class Tree(object):
    """Simple tree structure. Nodes are themselves trees."""

    def __init__(self, value = None, children = None):
        self.parent = None
        self.value = value
        if not children:
            self.children = None
        else:
            for c in children:
                self.append(c)

    def leaf(self):
        """Is this a leaf node or not?"""
        return not self.children

    def __len__(self):
        if not self.children:
            return 0
        else:
            return len(self.children)

    def __bool__(self):
        return True

    def __iter__(self):
        """Iterate over all items in the tree"""
        for c in self.children:
            return c

    def append(self, item):
        """Add an item to the Tree"""
        if not isinstance(item, Tree):
            return ValueError("Can only append items of type Tree")
        if not self.children: self.children = []
        item.parent = self
        self.children.append(item)

    def __getitem__(self, index):
        """Retrieve a specific item, by index, from the Tree"""
        assert isinstance(index,int)
        try:
            return self.children[index]
        except:
            raise

    def __str__(self):
        return str(self.value)

    def __unicode__(self): #Python 2.x
        return u(self.value)




class Trie(object):
    """Simple trie structure. Nodes are themselves tries, values are stored on the edges, not the nodes."""

    def __init__(self, sequence = None):
        self.parent = None
        self.children = None
        self.value = None
        if sequence:
            self.append(sequence)

    def leaf(self):
        """Is this a leaf node or not?"""
        return not self.children

    def root(self):
        """Returns True if this is the root of the Trie"""
        return not self.parent

    def __len__(self):
        if not self.children:
            return 0
        else:
            return len(self.children)

    def __bool__(self):
        return True

    def __iter__(self):
        if self.children:
            for key in self.children.keys():
                yield key

    def items(self):
        if self.children:
            for key, trie in self.children.items():
                yield key, trie

    def __setitem__(self, key, subtrie):
        if not isinstance(subtrie, Trie):
            return ValueError("Can only set items of type Trie, got " + str(type(subtrie)))
        if not self.children: self.children = {}
        subtrie.value = key
        subtrie.parent = self
        self.children[key] = subtrie

    def append(self, sequence):
        if not sequence:
            return self
        if not self.children:
            self.children = {}
        if not (sequence[0] in self.children):
            self.children[sequence[0]] = Trie()
            return self.children[sequence[0]].append( sequence[1:] )
        else:
            return self.children[sequence[0]].append( sequence[1:] )

    def find(self, sequence):
        if not sequence:
            return self
        elif self.children and sequence[0] in self.children:
            return self.children[sequence[0]].find(sequence[1:])
        else:
            return False

    def __contains__(self, key):
        return (key in self.children)


    def __getitem__(self, key):
        try:
            return self.children[key]
        except:
            raise


    def size(self):
        """Size is number of nodes under the trie, including the current node"""
        if self.children:
            return sum( ( c.size() for c in self.children.values() ) ) + 1
        else:
            return 1

    def path(self):
        """Returns the path to the current node"""
        if self.parent:
            return (self,) + self.parent.path()
        else:
            return (self,)

    def depth(self):
        """Returns the depth of the current node"""
        if self.parent:
            return 1 + self.parent.depth()
        else:
            return 1

    def sequence(self):
        if self.parent:
            if self.value:
                return (self.value,) + self.parent.sequence()
            else:
                return self.parent.sequence()
        else:
            return (self,)


    def walk(self, leavesonly=True, maxdepth=None, _depth = 0):
        """Depth-first search, walking through trie, returning all encounterd nodes (by default only leaves)"""
        if self.children:
            if not maxdepth or (maxdepth and _depth < maxdepth):
                for key, child in self.children.items():
                    if child.leaf():
                        yield child
                    else:
                        for results in child.walk(leavesonly, maxdepth, _depth + 1):
                            yield results


FIXEDGAP = 128
DYNAMICGAP = 129

if PYTHONVERSION > '3':
    #only available for Python 3

    class Pattern:
        def __init__(self, data, classdecoder=None):
            assert isinstance(data, bytes)
            self.data = data
            self.classdecoder = classdecoder

        @staticmethod
        def fromstring(s, classencoder): #static
            data = b''
            for s in s.split():
                data += classencoder[s]
            return Pattern(data)

        def __str__(self):
            s = ""
            for cls in self:
                s += self.classdecoder[int.from_bytes(cls)]

        def iterbytes(self, begin=0, end=0):
            i = 0
            l = len(self.data)
            n = 0
            if (end != begin):
                slice = True
            else:
                slice = False

            while i < l:
                size = self.data[i]
                if (size < 128): #everything from 128 onward is reserved for markers
                    if not slice:
                        yield self.data[i+1:i+1+size]
                    else:
                        n += 1
                        if n >= begin and n < end:
                            yield self.data[i+1:i+1+size]
                    i += 1 + size
                else:
                    raise ValueError("Size >= 128")


        def __iter__(self):
            for b in self.iterbytes():
                yield Pattern(b, self.classdecoder)

        def __bytes__(self):
            return self.data

        def __len__(self):
            """Return n"""
            i = 0
            l = len(self.data)
            n = 0
            while i < l:
                size = self.data[i]
                if (size < 128):
                    n += 1
                    i += 1 + size
                else:
                    raise ValueError("Size >= 128")

        def __getitem__(self, index):
            assert isinstance(index, int)
            for b in self.iterbytes(index,index+1):
                return Pattern(b, self.classdecoder)

        def __getslice__(self, begin, end):
            slice = b''
            for b in self.iterbytes(begin,end):
                slice += b
            return slice

        def __add__(self, other):
            assert isinstance(other, Pattern)
            return Pattern(self.data + other.data, self.classdecoder)

        def __eq__(self, other):
            return self.data == other.data

    class PatternSet:
        def __init__(self):
            self.data = set()

        def add(self, pattern):
            self.data.add(pattern.data)

        def remove(self, pattern):
            self.data.remove(pattern.data)

        def __len__(self):
            return len(self.data)

        def __bool__(self):
            return len(self.data) > 0

        def __contains__(self, pattern):
            return pattern.data in self.data

        def __iter__(self):
            for patterndata in self.data:
                yield Pattern(patterndata)


    class PatternMap:
        def __init__(self, default=None):
            self.data = {}
            self.default = default

        def __getitem__(self, pattern):
            assert isinstance(pattern, Pattern)
            if not self.default is None:
                try:
                    return self.data[pattern.data]
                except KeyError:
                    return self.default
            else:
                return self.data[pattern.data]

        def __setitem__(self, pattern, value):
            self.data[pattern.data] = value

        def __delitem__(self, pattern):
            del self.data[pattern.data]

        def __len__(self):
            return len(self.data)

        def __bool__(self):
            return len(self.data) > 0

        def __contains__(self, pattern):
            return pattern.data in self.data

        def __iter__(self):
            for patterndata in self.data:
                yield Pattern(patterndata)

        def items(self):
            for patterndata, value in self.data.items():
                yield Pattern(patterndata), value




#class SuffixTree(object):
#   def __init__(self):
#       self.data = {}
#
#
#   def append(self, seq):
#       if len(seq) > 1:
#           for item in seq:
#                self.append(item)
#        else:
#
#
#    def compile(self, s):
