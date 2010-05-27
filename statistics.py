###############################################################
#  PyNLPp - Statistics Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
# 
# This is a Python library containing classes for Statistic and
# Information Theoretical computations.
#
###############################################################

from math import log

class FrequencyList:
    def __init__(self, tokens = None, casesensitive = True):
        self._count = {}
        self._ranked = {}
        self.total = 0
        self.casesensitive = casesensitive
        if tokens: self.append(tokens)


    def _validate(self,type):
        if not self.casesensitive: 
            return tuple([x.lower() for x in type])
        else:
            return tuple(type)

    def append(self,tokens):
        for token in tokens:
            self.count(token)
        

    def count(self, type, amount = 1):
        type = self._validate(type)
        if self._ranked: self._ranked = None
        if type in self._count:
            self._count[type] += amount
        else:
            self._count[type] = amount
        self.total += amount

    def sum(self):
        """alias"""
        return self._total

    def _rank(self):
        if not self._ranked: self._ranked = sorted(self._count.items(),key=lambda x: x[1], reverse=True )

    def __iter__(self):
        """Returns a ranked list of (type, count) pairs. The first time you iterate over the FrequencyList, the ranking will be computed. For subsequent calls it will be available immediately, unless the frequency list changed in the meantime."""
        self._rank()
        for type, count in self._ranked:
            yield type, count

    def items(self):
        """Returns an *unranked* list of (type, count) pairs. Use this only if you are not interested in the order."""
        for type, count in  self._count.items():
            yield type, count

    def __getitem__(self, type):
        type = self._validate(type)
        return self._count[type]

    def __setitem__(self, type, value):
        """alias for count, but can only be called once"""
        type = self._validate(type)
        if not type in self._count:
            self.count(type,value)     
        else:
            raise ValueError("This type is already set!")
    
    def typetokenratio(self):
        """Computes the type/token ratio"""
        return len(self._total) / float(self._total)


    def mode(self):
        """Returns the type that occurs the most frequently in the frequency list"""
        self._rank()
        return self._ranked[0][0]


    def p(self, type): 
        """Returns the probability (relative frequency) of the token"""
        type = self._validate(type)
        return self._count[type] / float(self._total)


    def __eq__(self, otherfreqlist):
        return (self.total == otherfreqlist.total and self._count == otherfreqlist._count)

    def __contains__(self, type):
        type = self._validate(type)
        return type in self._count

    def __add__(self, otherfreqlist):
        product = FrequencyList(None, )
        for type, count in self.items():
            product.count(type,count)        
        for type, count in otherfreqlist.items():
            product.count(type,count)        
        return product

    def output(self,delimiter = '\t'):
        for type, count in self:    
            yield " ".join(type) + delimiter + str(count)

class Distribution:
    def __init__(self, data):
        self._dist = {}
        if isinstance(data, FrequencyList):
            for type, count in data.items():
                self._dist[type] = count / float(data.total)
        elif isinstance(data, dict):
            self._dist = data                    
        self._ranked = None
        

    def _validate(self,type):
        return tuple(type)

    def _rank(self):
        if not self._ranked: self._ranked = sorted(self._dist.items(),key=lambda x: x[1], reverse=True )

    def information(self, type):
        """Computes the information content of the specified type: -log(p(X))"""
        type = self._validate(type)
        return -log(self._dist[type])

    def poslog(self, type):
        """alias for information content"""
        type = self._validate(type)
        return self.information(type)

    def entropy(self):
        """Compute the entropy of the distribution"""
        entropy = 0
        for type in self._dist:
            entropy += self._dist[type] * -log(self._dist[type])     
        return entropy

    def mode(self):
        """Returns the type that occurs the most frequently in the probability distribution"""
        self._rank()
        return self._ranked[0][0]

    def maxentropy(self):     
        """Compute the maximum entropy of the distribution: log(N)"""   
        return log(len(self._dist))

    def __getitem__(self, type):
        """Return the probability for this type"""
        type = self._validate(type)
        return self._dist[type]

    def __iter__(self):
        """Iterate over the ranked distribution, returns (type, probability) pairs"""       
        self._rank()
        for type, p in self._ranked:
            yield type, p

    def items(self):
        """Returns an *unranked* list of (type, prob) pairs. Use this only if you are not interested in the order."""
        for type, count in  self._dist.items():
            yield type, count

    def output(self,delimiter = '\t'):
        for type, prob in self:    
            yield " ".join(type) + delimiter + str(prob)

