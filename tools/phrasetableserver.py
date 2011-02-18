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

from pynlpl.formats.moses import PhraseTable, PhraseTableServer

import sys

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

if len(sys.argv) != 3:
    print >>sys.stderr,"Syntax: phrasetableserver.py phrasetable port"
    sys.exit(2)
else:    
    PhraseTableServer(PhraseTable(sys.argv[0]), sys.argv[1])
