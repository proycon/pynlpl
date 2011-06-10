#!/usr/bin/env python
#-*- coding:utf-8 -*-

import glob
import sys
import os


if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

from pynlpl.formats import folia
from pynlpl.formats import cgn

def process(target):
    print "Processing " + target
    if os.path.isdir(target):
        print "Descending into directory " + target
        for f in glob.glob(target + '/*'):
            process(f)
    elif os.path.isfile(target) and target[-4:] == '.xml':            
        print "Loading " + target
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
	    print "Saving..."
            doc.save()

target = sys.argv[1]
process(target)
   
