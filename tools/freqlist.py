#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################
#  PyNLPl - Frequency List Generator
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
###############################################################


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import getopt
import sys
import codecs

from pynlpl.statistics import FrequencyList, Distribution
from pynlpl.textprocessors import Windower, crude_tokenizer

def usage():
    print("freqlist.py -n 1  file1 (file2) etc..",file=sys.stderr)
    print("\t-n number   n-gram size (default: 1)",file=sys.stderr)
    print("\t-i          case-insensitve",file=sys.stderr)
    print("\t-e encoding (default: utf-8)",file=sys.stderr)

def main():
    try:
        opts, files = getopt.getopt(sys.argv[1:], "hn:ie:", ["help"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err),file=sys.stderr)
        usage()
        sys.exit(2)

    testsetsize = devsetsize = 0
    casesensitive = True
    encoding = 'utf-8'
    n = 1

    for o, a in opts:
        if o == "-n":
            n = int(a)
        elif o == "-i":
            casesensitive =  False
        elif o == "-e":
            encoding = a
        else:
            print("ERROR: Unknown option:",o,file=sys.stderr)
            sys.exit(1)

    if not files:
        print >>sys.stderr, "No files specified"
        sys.exit(1)

    freqlist = FrequencyList(None, casesensitive)
    for filename in files:
        f = codecs.open(filename,'r',encoding)
        for line in f:
            if n > 1:
                freqlist.append(Windower(crude_tokenizer(line),n))
            else:
                freqlist.append(crude_tokenizer(line))

        f.close()

    dist = Distribution(freqlist)
    for type, count in freqlist:
        if isinstance(type,tuple) or isinstance(type,list):
            type = " ".join(type)
        s =  type + "\t" + str(count) + "\t" + str(dist[type]) + "\t" + str(dist.information(type))
        print(s)

    print("Tokens:           ", freqlist.tokens(),file=sys.stderr)
    print("Types:            ", len(freqlist),file=sys.stderr)
    print("Type-token ratio: ", freqlist.typetokenratio(),file=sys.stderr)
    print("Entropy:          ", dist.entropy(),file=sys.stderr)

if __name__ == '__main__':
    main()

