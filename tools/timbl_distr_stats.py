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

from pynlpl.formats.timbl import TimblOutput
from pynlpl.statistics import mean,mode,median
import sys
import os


print "Filename          \tmax\tmin\tmean\tmedian\tmode"
for filename in sys.argv[1:]:
    observations = []
    for _,_,_,distribution in TimblOutput(open(filename,'r')):
        observations.append(len(distribution))
    print os.path.basename(filename) + "\t" + str(max(observations)) + "\t" + str(min(observations)) + "\t"  + str(mean(observations)) + "\t" + str(median(observations)) + "\t" + str(mode(observations))
