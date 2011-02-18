#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################
#  PyNLPl - Phrase Table Server
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
###############################################################   


import sys
import os

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'
    
from pynlpl.formats.moses import PhraseTable, PhraseTableServer




if len(sys.argv) != 3:
    print >>sys.stderr,"Syntax: phrasetableserver.py phrasetable port"
    sys.exit(2)
else:    
    port = int(sys.argv[2])
    PhraseTableServer(PhraseTable(sys.argv[1]), port)
