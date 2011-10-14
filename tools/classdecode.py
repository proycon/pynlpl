#!/usr/bin/env python
#-*- coding:utf-8 -*-

from pynlpl.textprocessors import Classer
import sys

classer = Classer(sys.argv[1])
for line in classer.decodefile(sys.argv[2]):
    print " ".join(line).encode('utf-8')
