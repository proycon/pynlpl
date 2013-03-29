#!/usr/bin/env python
#-*- coding:utf-8 -*-


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import  

from pynlpl.textprocessors import Classer
import sys

classer = Classer(sys.argv[1])
for line in classer.decodefile(sys.argv[2]):
    print(" ".join(line))
