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

import argparse
import sys
import io

from pynlpl.statistics import FrequencyList, Distribution
from pynlpl.textprocessors import Windower, crude_tokenizer

def main():
    parser = argparse.ArgumentParser(description="Generate an n-gram frequency list", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n','--ngramsize', help="N-gram size", type=int, action='store',default=1)
    parser.add_argument('-i','--caseinsensitive', help="Case insensitive", action="store_true")
    parser.add_argument('-e','--encoding', help="Character encoding", type=str, action='store',default='utf-8')
    parser.add_argument('files', type=str, nargs='+', help="The data sets to sample from, must be of equal size (i.e., same number of lines)")


    args = parser.parse_args()

    if not args.files:
        print("No files specified", file=sys.stderr)
        sys.exit(1)

    freqlist = FrequencyList(None, args.caseinsensitive)
    for filename in args.files:
        f = io.open(filename,'r',encoding=args.encoding)
        for line in f:
            if args.ngramsize > 1:
                freqlist.append(Windower(crude_tokenizer(line),args.ngramsize))
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

