#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################
#  PyNLPl - Sampler
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
# This tool can be used to split a file (or multiple interdependent
# files, such as a parallel corpus) into a train, test and development
# set.
#
###############################################################


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import getopt
import sys

import random
from pynlpl.evaluation import filesampler


def usage():
    print("sampler.py [ -t testsetsize ] [ -d devsetsize ] [ -S seed] file1 (file2) etc..",file=sys.stderr)
    print("\tNote: testsetsize and devsetsize may be fractions (< 1) or absolute (>=1)",file=sys.stderr)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:d:S:T:", ["help"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err),file=sys.stderr)
        usage()
        sys.exit(2)

    trainsetsize = testsetsize = devsetsize = 0

    for o, a in opts:
        if o == "-t":
            try:
                testsetsize = int(a)
            except:
                try:
                    testsetsize = float(a)
                except:
                    print("ERROR: Invalid testsize",file=sys.stderr)
                    sys.exit(2)
        elif o == "-d":
            try:
                devsetsize = int(a)
            except:
                try:
                    devsetsize = float(a)
                except:
                    print("ERROR: Invalid devsetsize",file=sys.stderr)
                    sys.exit(2)
        elif o == '-T':
            try:
                trainsetsize = int(a)
            except:
                try:
                    trainsetsize = float(a)
                except:
                    print("ERROR: Invalid trainsetsize",file=sys.stderr)
                    sys.exit(2)
        elif o == "-S":
            random.seed(int(a))
        elif o == "-h":
            usage()
            sys.exit(0)
        else:
            print("ERROR: No such option: ",o,file=sys.stderr)
            sys.exit(2)

    if testsetsize == 0:
        print("ERROR: Specify at least a testset size!",file=sys.stderr)
        usage()
        sys.exit(2)
    elif len(args) == 0:
        print("ERROR: Specify at least one file!",file=sys.stderr)
        usage()
        sys.exit(2)

    filesampler(args, testsetsize, devsetsize, trainsetsize)

if __name__ == '__main__':
    main()
