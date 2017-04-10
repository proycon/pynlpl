#!/usr/bin/env python
#-*- coding:utf-8 -*-

#---------------------------------------------------------------
# PyNLPl - Conversion script for converting SoNaR/D-Coi from D-Coi XML to FoLiA XML
#   by Maarten van Gompel, ILK, Tilburg University
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

# Usage: sonar2folia.py sonar-input-dir output-dir nr-of-threads

from __future__ import print_function, unicode_literals, division, absolute_import

import sys
import os

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

import pynlpl.formats.folia as folia
import pynlpl.formats.sonar as sonar
from multiprocessing import Pool, Process
import datetime
import codecs


def process(data):
    i, filename = data
    category = os.path.basename(os.path.dirname(filename))
    progress = round((i+1) / float(len(index)) * 100,1)    
    print("#" + str(i+1) + " " + filename + ' ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' +  str(progress) + '%',file=sys.stderr)
    try:
        doc = folia.Document(file=filename)
    except Exception as e:
        print("ERROR loading " + filename + ":" + str(e),file=sys.stderr)
        return False
    filename = filename.replace(sonardir,'')
    if filename[0] == '/':
        filename = filename[1:]
    if filename[-4:] == '.pos':
        filename = filename[:-4]
    if filename[-4:] == '.tok':
        filename = filename[:-4]    
    if filename[-4:] == '.ilk':
        filename = filename[:-4]    
    #Load document prior to tokenisation
    try:
        pretokdoc = folia.Document(file=sonardir + '/' + filename)
    except:
        print("WARNING unable to load pretokdoc " + filename,file=sys.stderr)
        pretokdoc = None
    if pretokdoc:
        for p2 in pretokdoc.paragraphs():
            try:
                p = doc[p2.id]        
            except:
                print("ERROR: Paragraph " + p2.id + " not found. Tokenised and pre-tokenised versions out of sync?",file=sys.stderr)
                continue
            if p2.text:
                p.text = p2.text                     
    try:
        os.mkdir(foliadir + os.path.dirname(filename))
    except:
        pass
        
    try:        
        doc.save(foliadir + filename)
    except:
        print("ERROR saving " + foliadir + filename,file=sys.stderr)
    
    try:
        f = codecs.open(foliadir + filename.replace('.xml','.tok.txt'),'w','utf-8')
        f.write(unicode(doc))    
        f.close()        
    except:
        print("ERROR saving " + foliadir + filename.replace('.xml','.tok.txt'),file=sys.stderr)

            
    sys.stdout.flush()
    sys.stderr.flush()
    return True
    
def outputexists(filename, sonardir, foliadir):
    filename = filename.replace(sonardir,'')
    if filename[0] == '/':
        filename = filename[1:]
    if filename[-4:] == '.pos':
        filename = filename[:-4]
    if filename[-4:] == '.tok':
        filename = filename[:-4]    
    if filename[-4:] == '.ilk':
        filename = filename[:-4]     
    return os.path.exists(foliadir + filename)


if __name__ == '__main__':    
    sonardir = sys.argv[1]
    foliadir = sys.argv[2]
    threads = int(sys.argv[3])
    if foliadir[-1] != '/': foliadir += '/'
    try:
        os.mkdir(foliadir[:-1])
    except:
        pass
            
    print("Building index...")
    index = list(enumerate([ x for x in sonar.CorpusFiles(sonardir,'pos', "", lambda x: True, True) if not outputexists(x, sonardir, foliadir) ]))

    print("Processing...")
    p = Pool(threads)
    p.map(process, index )

