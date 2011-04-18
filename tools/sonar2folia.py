#!/usr/bin/env python
#-*- coding:utf-8 -*-



import sys
import os

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

import pynlpl.formats.folia as folia
import pynlpl.formats.sonar as sonar

sonardir = sys.argv[1]
foliadir = sys.argv[2]
if foliadir[-1] != '/': foliadir += '/'
try:
    os.mkdir(foliadir[:-1])
except:
    pass
        
print "Building index..."
index = list(sonar.CorpusFiles(sonardir,'pos', "", lambda x: True, True))

print "Processing..."
for i, filename in enumerate(index):
    progress = round((i+1) / float(len(index)) * 100,1)    
    print "#" + str(i+1) + " " + filename + " " + str(progress) + '%'
    doc = folia.Document(file=filename)
    filename = filename.replace(sonardir,'')
    if filename[0] == '/':
        filename = filename[1:]
    if filename[-4:] == '.pos':
        filename == filename[:-4]
    if filename[-4:] == '.tok':
        filename == filename[:-4]    
    if filename[-4:] == '.ilk':
        filename == filename[:-4]    
    #Load document prior to tokenisation
    pretokdoc = folia.Document(file=sonardir + '/' + filename)
    for p2 in pretokdoc.paragraphs():
        try:
            p = doc[p2.id]        
        except:
            print >> sys.stderr,"ERROR: Paragraph " + p2.id + " not found. Tokenised and pre-tokenised versions out of sync?"
            continue
        p.text = p2.text                        
    try:
        os.mkdir(foliadir + os.path.dirname(filename))
    except:
        pass
    doc.save(foliadir + filename)
    
    
