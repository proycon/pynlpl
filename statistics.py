###############################################################
#  PyNLPp - Statistics & Information Theory Library
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#       Also contains MIT licensed code from
#        AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
#        Peter Norvig
#
#       Licensed under GPLv3
#
###############################################################


"""This is a Python library containing classes for Statistic and Information Theoretical computations. It also contains some code from Peter Norvig, AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import u, isstring
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout
import io

import math
import random
import operator
from collections import Counter



class FrequencyList(object):
    """A frequency list (implemented using dictionaries)"""

    def __init__(self, tokens = None, casesensitive = True, dovalidation = True):
        self._count = Counter()
        self._ranked = {}
        self.total = 0 #number of tokens
        self.casesensitive = casesensitive
        self.dovalidation = dovalidation
        if tokens: self.append(tokens)


    def load(self, filename):
        """Load a frequency list from file (in the format produced by the save method)"""
        f = io.open(filename,'r',encoding='utf-8')
        for line in f:
            data = line.strip().split("\t")
            type, count = data[:2]
            self.count(type,count)
        f.close()


    def save(self, filename, addnormalised=False):
        """Save a frequency list to file, can be loaded later using the load method"""
        f = io.open(filename,'w',encoding='utf-8')
        for line in self.output("\t", addnormalised):
            f.write(line + '\n')
        f.close()

    def _validate(self,type):
        if isinstance(type,list):
            type = tuple(type)
        if isinstance(type,tuple):
            if not self.casesensitive:
                return tuple([x.lower() for x in type])
            else:
                return type
        else:
            if not self.casesensitive:
                return type.lower()
            else:
                return type

    def append(self,tokens):
        """Add a list of tokens to the frequencylist. This method will count them for you."""
        for token in tokens:
            self.count(token)


    def count(self, type, amount = 1):
        """Count a certain type. The counter will increase by the amount specified (defaults to one)"""
        if self.dovalidation: type = self._validate(type)
        if self._ranked: self._ranked = None
        if type in self._count:
            self._count[type] += amount
        else:
            self._count[type] = amount
        self.total += amount

    def sum(self):
        """Returns the total amount of tokens"""
        return self.total

    def _rank(self):
        if not self._ranked: self._ranked = self._count.most_common()

    def __iter__(self):
        """Iterate over the frequency lists, in order (frequent to rare). This is a generator that yields (type, count) pairs. The first time you iterate over the FrequencyList, the ranking will be computed. For subsequent calls it will be available immediately, unless the frequency list changed in the meantime."""
        self._rank()
        for type, count in self._ranked:
            yield type, count

    def items(self):
        """Returns an *unranked* list of (type, count) pairs. Use this only if you are not interested in the order."""
        for type, count in  self._count.items():
            yield type, count

    def __getitem__(self, type):
        if self.dovalidation: type = self._validate(type)
        try:
            return self._count[type]
        except KeyError:
            return 0

    def __setitem__(self, type, value):
        """alias for count, but can only be called once"""
        if self.dovalidation: type = self._validate(type)
        if not type in self._count:
            self.count(type,value)
        else:
            raise ValueError("This type is already set!")

    def __delitem__(self, type):
        if self.dovalidation: type = self._validate(type)
        del self._count[type]
        if self._ranked: self._ranked = None


    def typetokenratio(self):
        """Computes the type/token ratio"""
        return len(self._count) / float(self.total)

    def __len__(self):
        """Returns the total amount of types"""
        return len(self._count)

    def tokens(self):
        """Returns the total amount of tokens"""
        return self.total

    def mode(self):
        """Returns the type that occurs the most frequently in the frequency list"""
        self._rank()
        return self._ranked[0][0]


    def p(self, type):
        """Returns the probability (relative frequency) of the token"""
        if self.dovalidation: type = self._validate(type)
        return self._count[type] / float(self.total)


    def __eq__(self, otherfreqlist):
        return (self.total == otherfreqlist.total and self._count == otherfreqlist._count)

    def __contains__(self, type):
        """Checks if the specified type is in the frequency list"""
        if self.dovalidation: type = self._validate(type)
        return type in self._count

    def __add__(self, otherfreqlist):
        """Multiple frequency lists can be added together"""
        assert isinstance(otherfreqlist,FrequencyList)
        product = FrequencyList(None,)
        for type, count in self.items():
            product.count(type,count)
        for type, count in otherfreqlist.items():
            product.count(type,count)
        return product

    def output(self,delimiter = '\t', addnormalised=False):
        """Print a representation of the frequency list"""
        for type, count in self:
            if isinstance(type,tuple) or isinstance(type,list):
                if addnormalised:
                    yield " ".join((u(x) for x in type)) + delimiter + str(count) + delimiter + str(count/self.total)
                else:
                    yield " ".join((u(x) for x in type)) + delimiter + str(count)
            elif isstring(type):
                if addnormalised:
                    yield type + delimiter + str(count) + delimiter + str(count/self.total)
                else:
                    yield type + delimiter + str(count)
            else:
                if addnormalised:
                    yield str(type) + delimiter + str(count) + delimiter + str(count/self.total)
                else:
                    yield str(type) + delimiter + str(count)

    def __repr__(self):
        return repr(self._count)

    def __unicode__(self): #Python 2
        return str(self)

    def __str__(self):
        return "\n".join(self.output())

    def values(self):
        return self._count.values()

    def dict(self):
        return self._count


#class FrequencyTrie:
#    def __init__(self):
#        self.data = Tree()
#
#    def count(self, sequence):
#
#
#        self.data.append( Tree(item) )




class Distribution(object):
    """A distribution can be created over a FrequencyList or a plain dictionary with numeric values. It will be normalized automatically. This implemtation uses dictionaries/hashing"""

    def __init__(self, data, base = 2):
        self.base = base #logarithmic base: can be set to 2, 10 or math.e (or anything else). when set to None, it's set to e automatically
        self._dist = {}
        if isinstance(data, FrequencyList):
            for type, count in data.items():
                self._dist[type] = count / data.total
        elif isinstance(data, dict) or isinstance(data, list):
            if isinstance(data, list):
                self._dist = {}
                for key,value in data:
                    self._dist[key] = float(value)
            else:
                self._dist = data
            total = sum(self._dist.values())
            if total < 0.999 or total > 1.000:
                #normalize again
                for key, value in self._dist.items():
                    self._dist[key] = value / total
        else:
            raise Exception("Can't create distribution")
        self._ranked = None



    def _rank(self):
        if not self._ranked: self._ranked = sorted(self._dist.items(),key=lambda x: x[1], reverse=True )

    def information(self, type):
        """Computes the information content of the specified type: -log_e(p(X))"""
        if not self.base:
            return -math.log(self._dist[type])
        else:
            return -math.log(self._dist[type], self.base)

    def poslog(self, type):
        """alias for information content"""
        return self.information(type)

    def entropy(self, base = 2):
        """Compute the entropy of the distribution"""
        entropy = 0
        if not base and self.base: base = self.base
        for type in self._dist:
            if not base:
                entropy += self._dist[type] * -math.log(self._dist[type])
            else:
                entropy += self._dist[type] * -math.log(self._dist[type], base)
        return entropy

    def perplexity(self, base=2):
        return base ** self.entropy(base)

    def mode(self):
        """Returns the type that occurs the most frequently in the probability distribution"""
        self._rank()
        return self._ranked[0][0]

    def maxentropy(self, base = 2):
        """Compute the maximum entropy of the distribution: log_e(N)"""
        if not base and self.base: base = self.base
        if not base:
            return math.log(len(self._dist))
        else:
            return math.log(len(self._dist), base)

    def __len__(self):
        """Returns the number of types"""
        return len(self._dist)

    def __getitem__(self, type):
        """Return the probability for this type"""
        return self._dist[type]

    def __iter__(self):
        """Iterate over the *ranked* distribution, returns (type, probability) pairs"""
        self._rank()
        for type, p in self._ranked:
            yield type, p

    def items(self):
        """Returns an *unranked* list of (type, prob) pairs. Use this only if you are not interested in the order."""
        for type, count in  self._dist.items():
            yield type, count

    def output(self,delimiter = '\t', freqlist = None):
        """Generator yielding formatted strings expressing the time and probabily for each item in the distribution"""
        for type, prob in self:
            if freqlist:
                if isinstance(type,list) or isinstance(type, tuple):
                    yield " ".join(type) + delimiter + str(freqlist[type]) + delimiter + str(prob)
                else:
                    yield type + delimiter + str(freqlist[type]) + delimiter + str(prob)
            else:
                if isinstance(type,list) or isinstance(type, tuple):
                    yield " ".join(type) + delimiter + str(prob)
                else:
                    yield type + delimiter + str(prob)


    def __unicode__(self):
        return str(self)

    def __str__(self):
        return "\n".join(self.output())

    def __repr__(self):
        return repr(self._dist)

    def keys(self):
        return self._dist.keys()

    def values(self):
        return self._dist.values()


class MarkovChain(object):
    def __init__(self, startstate, endstate = None):
        self.nodes = set()
        self.edges_out = {}
        self.startstate = startstate
        self.endstate = endstate

    def settransitions(self, state, distribution):
        self.nodes.add(state)
        if not isinstance(distribution, Distribution):
            distribution = Distribution(distribution)
        self.edges_out[state] = distribution
        self.nodes.update(distribution.keys())

    def __iter__(self):
        for state, distribution in self.edges_out.items():
            yield state, distribution

    def __getitem__(self, state):
        for distribution in self.edges_out[state]:
            yield distribution

    def size(self):
        return len(self.nodes)

    def accessible(self,fromstate, tostate):
        """Is state tonode directly accessible (in one step) from state fromnode? (i.e. is there an edge between the nodes). If so, return the probability, else zero"""
        if (not (fromstate in self.nodes)) or (not (tostate in self.nodes)) or not (fromstate in self.edges_out):
            return 0
        if tostate in self.edges_out[fromstate]:
            return self.edges_out[fromstate][tostate]
        else:
            return 0


    def communicates(self,fromstate, tostate, maxlength=999999):
        """See if a node communicates (directly or indirectly) with another. Returns the probability of the *shortest* path (probably, but not necessarily the highest probability)"""
        if (not (fromstate in self.nodes)) or (not (tostate in self.nodes)):
            return 0
        assert (fromstate != tostate)


        def _test(node,length,prob):
            if length > maxlength:
                return 0
            if node == tostate:
                prob *= self.edges_out[node][tostate]
                return True

            for child in self.edges_out[node].keys():
                if not child in visited:
                    visited.add(child)
                    if child == tostate:
                        return prob * self.edges_out[node][tostate]
                    else:
                        r = _test(child, length+1, prob * self.edges_out[node][tostate])
                        if r:
                            return r
            return 0

        visited = set(fromstate)
        return _test(fromstate,1,1)

    def p(self, sequence, subsequence=True):
        """Returns the probability of the given sequence or subsequence (if subsequence=True, default)."""
        if sequence[0] != self.startstate:
            if isinstance(sequence, tuple):
                sequence = (self.startstate,) + sequence
            else:
                sequence = (self.startstate,) + tuple(sequence)
        if self.endstate:
            if sequence[-1] != self.endstate:
                if isinstance(sequence, tuple):
                    sequence = sequence + (self.endstate,)
                else:
                    sequence = tuple(sequence) + (self.endstate,)

        prevnode = None
        prob = 1
        for node in sequence:
            if prevnode:
                try:
                    prob *= self.edges_out[prevnode][node]
                except:
                    return 0
        return prob


    def __contains__(self, sequence):
        """Is the given sequence generated by the markov model? Does not work for subsequences!"""
        return bool(self.p(sequence,False))



    def reducible(self):
        #TODO: implement
        raise NotImplementedError




class HiddenMarkovModel(MarkovChain):
    def __init__(self, startstate, endstate = None):
        self.observablenodes = set()
        self.edges_toobservables = {}
        super(HiddenMarkovModel, self).__init__(startstate,endstate)

    def setemission(self, state, distribution):
        self.nodes.add(state)
        if not isinstance(distribution, Distribution):
            distribution = Distribution(distribution)
        self.edges_toobservables[state] = distribution
        self.observablenodes.update(distribution.keys())

    def print_dptable(self, V):
        print("    ",end="",file=stdout)
        for i in range(len(V)): print("%7s" % ("%d" % i),end="",file=stdout)
        print(file=stdout)

        for y in V[0].keys():
            print("%.5s: " % y, end="",file=stdout)
            for t in range(len(V)):
                print("%.7s" % ("%f" % V[t][y]),end="",file=stdout)
            print(file=stdout)

    #Adapted from: http://en.wikipedia.org/wiki/Viterbi_algorithm
    def viterbi(self,observations, doprint=False):
        #states, start_p, trans_p, emit_p):

        V = [{}] #Viterbi matrix
        path = {}

        # Initialize base cases (t == 0)
        for node in self.edges_out[self.startstate].keys():
            try:
                V[0][node] = self.edges_out[self.startstate][node] * self.edges_toobservables[node][observations[0]]
                path[node] = [node]
            except KeyError:
                pass #will be 0, don't store

        # Run Viterbi for t > 0
        for t in range(1,len(observations)):
            V.append({})
            newpath = {}

            for node in self.nodes:
                column = []
                for prevnode in V[t-1].keys():
                    try:
                        column.append( (V[t-1][prevnode] * self.edges_out[prevnode][node] * self.edges_toobservables[node][observations[t]],  prevnode ) )
                    except KeyError:
                        pass #will be 0

                if column:
                    (prob, state) = max(column)
                    V[t][node] = prob
                    newpath[node] = path[state] + [node]

            # Don't need to remember the old paths
            path = newpath

        if doprint: self.print_dptable(V)

        if not V[len(observations) - 1]:
            return (0,[])
        else:
            (prob, state) = max([(V[len(observations) - 1][node], node) for node in V[len(observations) - 1].keys()])
            return (prob, path[state])



# ********************* Common Functions ******************************

def product(seq):
    """Return the product of a sequence of numerical values.
    >>> product([1,2,6])
    12
    """
    if len(seq) == 0:
        return 0
    else:
        product = 1
        for x in seq:
            product *= x
        return product



# All below functions are mathematical functions from  AI: A Modern Approach, see: http://aima.cs.berkeley.edu/python/utils.html

def histogram(values, mode=0, bin_function=None): #from AI: A Modern Appproach
    """Return a list of (value, count) pairs, summarizing the input values.
    Sorted by increasing value, or if mode=1, by decreasing count.
    If bin_function is given, map it over values first."""
    if bin_function: values = map(bin_function, values)
    bins = {}
    for val in values:
        bins[val] = bins.get(val, 0) + 1
    if mode:
        return sorted(bins.items(), key=lambda v: v[1], reverse=True)
    else:
        return sorted(bins.items())

def log2(x):  #from AI: A Modern Appproach
    """Base 2 logarithm.
    >>> log2(1024)
    10.0
    """
    return math.log(x, 2)

def mode(values):  #from AI: A Modern Appproach
    """Return the most common value in the list of values.
    >>> mode([1, 2, 3, 2])
    2
    """
    return histogram(values, mode=1)[0][0]

def median(values):  #from AI: A Modern Appproach
    """Return the middle value, when the values are sorted.
    If there are an odd number of elements, try to average the middle two.
    If they can't be averaged (e.g. they are strings), choose one at random.
    >>> median([10, 100, 11])
    11
    >>> median([1, 2, 3, 4])
    2.5
    """
    n = len(values)
    values = sorted(values)
    if n % 2 == 1:
        return values[n/2]
    else:
        middle2 = values[(n/2)-1:(n/2)+1]
        try:
            return mean(middle2)
        except TypeError:
            return random.choice(middle2)

def mean(values):  #from AI: A Modern Appproach
    """Return the arithmetic average of the values."""
    return sum(values) / len(values)

def stddev(values, meanval=None):  #from AI: A Modern Appproach
    """The standard deviation of a set of values.
    Pass in the mean if you already know it."""
    if meanval == None: meanval = mean(values)
    return math.sqrt( sum([(x - meanval)**2 for x in values]) / (len(values)-1) )

def dotproduct(X, Y):  #from AI: A Modern Appproach
    """Return the sum of the element-wise product of vectors x and y.
    >>> dotproduct([1, 2, 3], [1000, 100, 10])
    1230
    """
    return sum([x * y for x, y in zip(X, Y)])

def vector_add(a, b):  #from AI: A Modern Appproach
    """Component-wise addition of two vectors.
    >>> vector_add((0, 1), (8, 9))
    (8, 10)
    """
    return tuple(map(operator.add, a, b))



def normalize(numbers, total=1.0):  #from AI: A Modern Appproach
    """Multiply each number by a constant such that the sum is 1.0 (or total).
    >>> normalize([1,2,1])
    [0.25, 0.5, 0.25]
    """
    k = total / sum(numbers)
    return [k * n for n in numbers]

###########################################################################################

def levenshtein(s1, s2, maxdistance=9999):
    """Computes the levenshtein distance between two strings. Adapted from:  http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python"""
    l1 = len(s1)
    l2 = len(s2)
    if l1 < l2:
        return levenshtein(s2, s1)
    if not s1:
        return len(s2)

    #If the words differ too much in length,  (if  we have a low maxdistance) , we needn't bother compute distance:
    if l1 > l2 + maxdistance:
        return maxdistance+1

    previous_row = list(range(l2 + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        if current_row[-1] > maxdistance:
            return current_row[-1]
        previous_row = current_row

    return previous_row[-1]



