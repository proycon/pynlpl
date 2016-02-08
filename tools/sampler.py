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

import argparse
import sys

import random
from pynlpl.evaluation import filesampler

def main():
    parser = argparse.ArgumentParser(description="Extracts random samples from datasets, supports multiple parallel datasets (such as parallel corpora), provided that corresponding data is on the same line.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t','--testsetsize', help="Test set size (lines)", type=float, action='store',default=0)
    parser.add_argument('-d','--devsetsize', help="Development set size (lines)", type=float, action='store',default=0)
    parser.add_argument('-T','--trainsetsize', help="Training set size (lines), leave unassigned (0) to automatically use all of the remaining data", type=float, action='store',default=0)
    parser.add_argument('-S','--seed', help="Seed for random number generator", type=int, action='store',default=0)
    parser.add_argument('files', type=str, nargs='+', help="The data sets to sample from, must be of equal size (i.e., same number of lines)")

    args = parser.parse_args()
    if args.seed:
        random.seed(args.seed)

    if args.testsetsize == 0:
        print("ERROR: Specify at least a testset size!",file=sys.stderr)
        sys.exit(2)

    try:
        if not args.files:
            print("ERROR: Specify at least one file!",file=sys.stderr)
            sys.exit(2)
    except:
        print("ERROR: Specify at least one file!",file=sys.stderr)
        sys.exit(2)

    filesampler(args.files, args.testsetsize, args.devsetsize, args.trainsetsize)

if __name__ == '__main__':
    main()
