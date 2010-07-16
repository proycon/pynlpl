#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################
#  PyNLPl - Frequency List Generator
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
###############################################################   

import getopt
import sys
import os
import codecs

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

from pynlpl.statistics import FrequencyList, Distribution
from pynlpl.textprocessors import Windower, crude_tokenizer

def usage():
    print >>sys.stderr,"freqlist.py -n 1  file1 (file2) etc.."
    print >>sys.stderr,"\t-n number   n-gram size (default: 1)"
    print >>sys.stderr,"\t-i          case-insensitve"
    print >>sys.stderr,"\t-e encoding (default: utf-8)"


try:
    opts, files = getopt.getopt(sys.argv[1:], "hn:ie:", ["help"])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err)
    usage()
    sys.exit(2)

testsetsize = devsetsize = 0
casesensitive = True
encoding = 'utf-8'
n = 1

for o, a in opts:
    if o == "-n":
        n = int(a)
    elif o == "-i":
        casesensitive =  False
    elif o == "-e":
        encoding = a
    else:
        print >>sys.stderr, "ERROR: Unknown option:",o
        sys.exit(1)

if not files:
    print >>sys.stderr, "No files specified"
    sys.exit(1)

freqlist = FrequencyList(None, casesensitive)
for filename in files:
    f = codecs.open(filename,'r',encoding)
    for line in f:
        if n > 1:
            freqlist.append(Windower(crude_tokenizer(line),n))
        else:
            freqlist.append(crude_tokenizer(line))

    f.close()

dist = Distribution(freqlist)
for type, count in freqlist:
    if isinstance(type,tuple) or isinstance(type,list):
        type = " ".join(type)
    s =  type + "\t" + str(count) + "\t" + str(dist[type]) + "\t" + str(dist.information(type))
    print s.encode('utf-8')

print >>sys.stderr, "Tokens:           ", freqlist.tokens()
print >>sys.stderr, "Types:            ", len(freqlist)
print >>sys.stderr, "Type-token ratio: ", freqlist.typetokenratio()
print >>sys.stderr, "Entropy:          ", dist.entropy()


