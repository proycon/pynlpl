#!/usr/bin/env python
#-*- coding:utf-8 -*-

import glob
import sys
import os

from pynlpl.formats import folia
from pynlpl.formats import cgn

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

def process(target):
    if os.path.isdir(target):
        for f in glob.glob(target + '/*'):
            process(target)
    elif os.path.isfile(target) and target[-4] == '.xml':            
        doc = folia.Document(file=target)
        changed = False
        for word in doc.words():
            try:
                pos = word.annotation(folia.PosAnnotation)                
            except folia.NoSuchAnnotation:
                continue
            try:
                word.replace( cgn.parse_cgn_postag(pos.cls) )
                changed = True
            except cgn.InvalidTagException:
                continue
        if changed:
            doc.save()

target = sys.argv[1]
process(target)
doc.save()
   
