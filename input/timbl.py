#by Sander Canisius
#TODO: Completely redesign

from itertools import imap
from sys import stderr

class Any:

	def __eq__(self, other):
		return True


ANY = Any()


class Distribution:

	def __init__(self, items):
		self.dist = dict(items)
		normFactor = float(sum(self.dist.itervalues()))
		for cls, weight in self.dist.iteritems():
			self.dist[cls] = weight / normFactor

	def max(self):
		return max(self.dist, key=self.dist.__getitem__)

	def maxscore(self):
		return max(self.dist.values())

	def topN(self, n):
		return sorted(self.dist, key=self.dist.__getitem__, reverse=True)[:n]

	def score(self, symbol):
		if ANY not in symbol:
			return self.dist[symbol]
		else:
			return sum(self.dist[sym] for sym in self.dist if sym == symbol)

	def __eq__(self, other):
		return (self.dist == other.dist)


def timblOutput(stream): #obsolete?
	first = stream.readline().split()
	start = first.index("{")

	yield first[:start], parseDistribution(first, start)

	for instance in imap(str.split, stream):
		yield instance[:start], parseDistribution(instance, start)

def read_timblOutput(stream):
	line = stream.readline()
	if not line:
		return False
	segments = [ x for x in line.split() if x != "^" and not (len(x) == 3 and x[0:2] == "n=") ]  #obtain segments, and filter null fields and "n=?" feature (in fixed-feature configuration)

	start = segments.index("{")
	return segments[:start], parseDistribution(segments, start)


def parseDistribution(instance, start):
	dist = {}
	i = start + 1

	l = len(instance)
	
	if instance[l-1] == "}":
		while i <= l - 2:  #instance[i] != "}":
			label = instance[i]
			try:
				score = float(instance[i+1].rstrip(","))
				key = tuple(label.split("^"))
				dist[key] = score
			except:
				print >>stderr, "ERROR: Could not fetch score for class '" + label + "', expected float, but found '"+instance[i+1].rstrip(",")+"'. Attempting to compensate..."
				del dist[key]
				i = i - 1
			i += 2

	if not dist:
		print >>stderr, "ERROR: Did not find class distribution for ", instance

	return Distribution(dist)
