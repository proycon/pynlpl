#! /usr/bin/env python
# -*- coding: utf8 -*-

import codecs
import sys
import os
import getopt

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

from pynlpl.textprocessors import ReflowText


try:
    opts, args = getopt.getopt(sys.argv[1:], "to:")
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    self.usage()
    sys.exit(2)
                
for filename in sys.argv[1:]: 
    f = codecs.open(filename, 'r', 'utf-8')
    for line in ReflowText(f):
        print line.encode('utf-8')
    f.close()
