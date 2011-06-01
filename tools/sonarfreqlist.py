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
lemmapos_freqlist = FrequencyList()
poshead_freqlist = FrequencyList()
pos_freqlist = FrequencyList()

for i, doc in enumerate(Corpus(sonardir)):
    print >>sys.stderr, "#" + str(i) + " Processing " + doc.filename
    for word, id, pos, lemma in doc:
        freqlist.count(word)
        if lemma and pos:
            poshead = pos.split('(')[0]
            lemmapos_freqlist.count(lemma+'.'+poshead)
            poshead_freqlist.count(poshead)
            pos_freqlist.count(pos)

freqlist.save('sonarfreqlist.txt')
lemmapos_freqlist.save('sonarlemmaposfreqlist.txt')
poshead_freqlist.save('sonarposheadfreqlist.txt')
pos_freqlist.save('sonarposfreqlist.txt')

            
print unicode(freqlist).encode('utf-8')
