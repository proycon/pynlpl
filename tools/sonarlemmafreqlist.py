#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

from pynlpl.formats.sonar import CorpusFiles, Corpus
from pynlpl.statistics import FrequencyList

sonardir = sys.argv[1]

freqlist = FrequencyList()

for i, doc in enumerate(Corpus(sonardir)):
    print >>sys.stderr, "#" + str(i) + " Processing " + doc.filename
    for word, id, pos, lemma in doc:
        if lemma and pos:
            poshead = pos.split('(')[0]
            freqlist.count(lemma+'.'+poshead)

freqlist.save('sonarlemmafreqlist.txt')
            
print freqlist.encode('utf-8')
