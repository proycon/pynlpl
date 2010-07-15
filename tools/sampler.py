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

import getopt
import sys
import os

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

from pynlpl.evaluation import filesampler


def usage():
    print >>sys.stderr,"sampler.py [ -t testsetsize ] [ -d devsetsize ] file1 (file2) etc.."
    print >>sys.stderr,"\tNote: testsetsize and devsetsize may be fractions (< 1) or absolute (>=1)"

try:
    opts, args = getopt.getopt(sys.argv[1:], "ht:d:", ["help"])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err)
    usage()
    sys.exit(2)

testsetsize = devsetsize = 0

for o, a in opts:
    if o == "-t":
        try:
            testsetsize = int(a)
        except:
            testsetsize = float(a)

    elif o == "-d":
        try:
            devsetsize = int(a)
        except:
            devsetsize = float(a)

    elif o == "-h":
        usage()
        sys.exit(0)
    else:
        print >>sys.stderr,"ERROR: No such option: ",o
        sys.exit(2)

if testsetsize == 0:
    print >>sys.stderr,"ERROR: Specify at least a testset size!"
    usage()
    sys.exit(2)
elif len(args) == 0:
    print >>sys.stderr,"ERROR: Specify at least one file!"
    usage()
    sys.exit(2)

filesampler(args, testsetsize, devsetsize)


