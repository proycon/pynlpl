#!/usr/bin/env python
#-*- coding:utf-8 -*-

from pynlpl.formats.sonar import CorpusX, CorpusDocumentX, ns
from pynlpl.clients.frogclient import FrogClient
import sys
import os.path

sonardir = sys.argv[1]

#Starting temporary Frog server
os.system("frog --skip=tmp -S 7551 &")


time.sleep(3)
frogclient = FrogClient('localhost',7551)

for doc in CorpusX(sonardir,'tok',"", lambda f: not os.path.exists(f + '.pos') ): #read the *.tok files, on condition there are no *.pos equivalents (will not overwrite)
    processed_doc = False
    print doc.filename + '\tPROCESSING'
    for sentence in doc.sentences():
            words = " ".join([ x.text for x in sentence ])

            process_sentence = False
            for x in sentence:
                if not ns('dcoi') + 'pos' in x.attrib or not ns('dcoi') + 'lemma' in x.attrib:
                    process_sentence = True
            if process_sentence:
                processed_doc = True
                for i, (word, lemma, morph, pos) in enumerate(frogclient.process(words)):
                    try:
                        word_id = sentence[i].attrib[ns('xml') + 'id']
                    except: 
                        print >>sys.stderr, "ERROR: words out of sync in " + sentence.attrib[ns('xml') + 'id']
                        break
                    if pos:
                        doc[word_id].attrib[ns('dcoi') + 'pos'] = pos
                    if lemma:
                        doc[word_id].attrib[ns('dcoi') + 'lemma'] = lemma
    if processed_doc:
        doc.save(doc.filename+'.pos', 'iso-8859-15') #write .tok.pos files

