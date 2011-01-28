#!/usr/bin/env python
#-*- coding:utf-8 -*-

#Create a language model based on SoNaR

import sys
import os
sys.path.append(sys.path[0] + '/../..')
os.environ['PYTHONPATH'] = sys.path[0] + '/../..'


from pynlpl.formats.sonar import Corpus
from pynlpl.lm.lm import SimpleLanguageModel

#syntax: ./make_sonar_lm.py sonar_dir output_file n

outputfile = sys.argv[2]

try:
    n = int(sys.argv[3])
except:
    n = 3

lm = SimpleLanguageModel(n)

for doc in Corpus(sys.argv[1],'tok'):
    for sentence_id, sentence in doc.sentences():
	print sentence_id
        words = [ word for word, id, pos, lemma in sentence ]
        lm.append(words)
lm.save(outputfile)




