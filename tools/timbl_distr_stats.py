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

from pynlpl.format.timbl import TimblOutput
from pynlpl.statistics import mean,mode, median
import sys
import os

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'


print "Filename          \tmax\tmin\tmean\tmedian\tmode"
for filename in sys.argv[1:]:
    observations = []
    for _,_,_,distribution in TimblOutput(filename):
        observations.append(len(distribution))
    print filename + "\t" + max(observations) + "\t" + min(observations) + "\t"  + mean(observations) + "\t" + median(observations) + "\t" + mode(observations)
