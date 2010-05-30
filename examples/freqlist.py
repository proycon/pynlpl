#!/usr/bin/env python
#-*- coding:utf-8 -*-

from pynlpl.textprocessors import Windower, crude_tokenizer
from pynlpl.statistics import FrequencyList, Distribution

import sys
import codecs

with codecs.open(sys.argv[1],'r','utf-8') as file:
    freqlist = FrequencyList()
    for line in file:
        freqlist.append(Windower(crude_tokenizer(line),2))


print "Type/Token Ratio: ", freqlist.typetokenratio()

### uncomment if you want to output the full frequency list:
#for line in freqlist.output():
#    print line.encode('utf-8')

dist = Distribution(freqlist)
for line in dist.output():
    print line.encode('utf-8')

