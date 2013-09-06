#! /usr/bin/env python
# -*- coding: utf8 -*-


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import sys
import io
import getopt

from pynlpl.textprocessors import ReflowText


def main():
    for filename in sys.argv[1:]:
        f = io.open(filename, 'r', encoding='utf-8')
        for line in ReflowText(f):
            print(line)
        f.close()

if __name__ == '__main__':
    main()
