#!/usr/bin/env python3
#-*- coding:utf-8 -*-


from __future__ import print_function, unicode_literals, division, absolute_import

import glob
import sys
import os


if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

from pynlpl.formats import folia
from pynlpl.formats import cgn
import lxml.etree

def process(target):
    print("Processing " + target)
    if os.path.isdir(target):
        print("Descending into directory " + target)
        for f in glob.glob(target + '/*'):
            process(f)
    elif os.path.isfile(target) and target[-4:] == '.xml':            
        print("Loading " + target)
        try:
            doc = folia.Document(file=target)
        except lxml.etree.XMLSyntaxError:
            print("UNABLE TO LOAD " + target + " (XML SYNTAX ERROR!)",file=sys.stderr)
            return None
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
                print("WARNING: INVALID TAG " + pos.cls,file=sys.stderr)
                continue
        if changed:
            print("Saving...")
            doc.save()

target = sys.argv[1]
process(target)
   
