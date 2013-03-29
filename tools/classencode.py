#!/usr/bin/env python
#-*- coding:utf-8 -*-


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import  

from pynlpl.textprocessors import Classer
from pynlpl.statistics import FrequencyList
import sys

filename = sys.argv[1]

print >>sys.stderr, "Counting tokens"
f = open(filename)
freqlist = FrequencyList()
for i, line in enumerate(f):            
    if (i % 10000 == 0): 
        print("\tLine " + str(i+1),file=sys.stderr)
    line = ['<s>'] + line.strip().split(' ') + ['</s>']
    
    freqlist.append(line)
f.close()

print >>sys.stderr, "Building classer"
classer = Classer(freqlist, filesupport=True )
classer.save(filename + '.cls')

print >>sys.stderr, "Encoding data"
classer.encodefile(filename, filename + '.clsenc')
