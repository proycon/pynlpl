#---------------------------------------------------------------
# PyNLPl - Data Types
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Based in large part on MIT licensed code from
#    AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
#    Peter Norvig
#
#   Licensed under GPLv3
#
# This library contains various extra data types
#
#----------------------------------------------------------------

import bisect

class Queue: #from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """Queue is an abstract class/interface. There are three types:
        Python List: A Last In First Out Queue.
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(lt): Queue where items are sorted by lt, (default <).
    Each type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())
    Note that isinstance(Stack(), Queue) is false, because we implement stacks
    as lists.  If Python ever gets interfaces, Queue will be an interface."""

    def extend(self, items):
        for item in items: self.append(item)

    
#note: A Python list is a LIFOQueue / Stack

class FIFOQueue(Queue): #adapted from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """A First-In-First-Out Queue."""
    def __init__(self, data = []):
        self.data = data
        self.start = 0

    def append(self, item):
        self.data.append(item)

    def __len__(self):
        return len(self.data) - self.start

    def extend(self, items):
        self.data.extend(items)

    def pop(self):
        e = self.data[self.start]
        self.start += 1
        if self.start > 5 and self.start > len(self.data)/2:
            self.data = self.data[self.start:]
            self.start = 0
        return e

class PriorityQueue(Queue): #adapted from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """A queue in which the maximum (or minumum) element is return first, 
    as determined by either an external score function f (by default calling
    the objects score() method). If minimize=True, the item with minimum f(x) is
    returned first; otherwise is the item with maximum f(x) or x.score()."""
    def __init__(self, data =[], f = lambda x: x.score, minimize=False):
        self.data=data
        self.f = f
        self.minimize=False #minimize instead of maximize?

    def append(self, item):
        bisect.insort(self.data, (self.f(item), item))

    def __len__(self):
        return len(self.data)

    def pop(self):
        if self.minimize:
            return self.data.pop(0)[1]
        else:
            return self.data.pop()[1]

    def prune(self, n):
        #prune all but the first n items
        self.data = self.data[:n]

