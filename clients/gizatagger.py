#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################
#  PyNLPl - FreeLing/Tadpole-based PoS tagger and Lemmatiser
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
# 
# This is a FreeLing/Tadpole based tokeniser, PoS-tagger and lemmatiser that processes
# A3 giza files. It produces two data files that can be read with 
# pynlpl.input.taggerdata.Taggerdata
#
###############################################################

import sys
import getopt
import os.path
from pynlpl.giza import WordAlignment, MultiWordAlignment
from pynlpl.clients.freeling import FreeLingClient
from pynlpl.clients.tadpoleclient import TadpoleClient
from pynlpl.formats.taggerdata import Taggerdata
import codecs
from datetime import datetime


def usage():
    print >> sys.stderr,"Syntax for usage with GIZA A3 alignment files:"    
    print >> sys.stderr,"\t-a [A3 file]           Alignment file, this may be a source-target.A3.final (direction: s2t) file or a target-source.A3.final file (direction: t2s), please set the direction accordingly using the -d flag."
    print >> sys.stderr,"\t-d (s2t|t2s)           Direction: Set to t2s (target-to-source, default) or s2t (source-to-target). In the former case, each word is aligned with only one target word, and multiple source words may point to the same target word. In the latter case, a source word may align to multiple target words."
    print >> sys.stderr,"\t--Sfreeling=channel    Use FreeLing to tokenise and lemmatise source-language sentences on-the-fly, channel points to the named pipe created by FreeLing analyze, without the .in or .out extension. Required for being PoS-aware"
    print >> sys.stderr,"\t--Tfreeling=channel    Use FreeLing to tokenise and lemmatise target-language sentences on-the-fly, channel points to the named pipe created by FreeLing analyze, without the .in or .out extension. Required for proper lemmatised output."
    print >> sys.stderr,"\t--Stadpole=port        Use Tadpole to tokenise and lemmatise source-language sentences on-the-fly, points to a Tadpole server port. Required for being PoS-aware"
    print >> sys.stderr,"\t--Ttadpole=port        Use Tadpole to tokenise and lemmatise target-language sentences on-the-fly, points to a Tadpole server port. Required for being PoS-aware"
    print >> sys.stderr,"\t--shortpos             Use only the head of the PoS tag, remove the features (only works for Tadpole!) "

try:
	opts, args = getopt.getopt(sys.argv[1:], "a:o:", ["Sfreeling=","Tfreeling=","Stadpole=","Ttadpole=","help","encoding=","shortpos"])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err)
	usage()
	sys.exit(1)         

alignfilename = None
Sfreeling = None
Tfreeling = None
Stadpole = None
Ttadpole = None
multiwordalignment = False
encoding = "utf-8"
outputdir = "."
shortpos = False

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit(0)
    elif o == "-o":
        outputdir = a
        if not os.path.exists(outputdir):
                print >> sys.stderr, "Output directory %s does not exist" % outputdir
                sys.exit()
    elif o == "-a":
        alignfilename = a
    elif o == "--Sfreeling":
        Sfreeling = FreeLingClient(a)
    elif o == "--Tfreeling":
        Tfreeling = FreeLingClient(a)
    elif o == "--Stadpole":
        Stadpole = TadpoleClient('localhost',int(a))
    elif o == "--Ttadpole":
        Ttadpole = TadpoleClient('localhost',int(a))
    elif o == "--encoding":
        encoding = a
    elif o == "--shortpos":
        shortpos = True
    elif o == "-d":
        if a == "s2t":       
            multiwordalignment = True
        elif a == "t2s":
            multiwordalignment = False
        else:
            print >> sys.stderr, "ERROR: Invalid direction specified"
            usage()
            sys.exit(1)
    else:
        assert False, "ERROR: Unknown option: %s" % o    
    

if not alignfilename:
    print usage()
    sys.exit(1)


if multiwordalignment:
    wordalignment = MultiWordAlignment(alignfilename,encoding)
else:
    wordalignment = WordAlignment(alignfilename,encoding)

fsource = Taggerdata(outputdir + '/source.toklempos','w',encoding)
ftarget = Taggerdata(outputdir + '/target.toklempos','w',encoding)

if alignfilename:

    for line, (source, target, alignment) in enumerate(wordalignment):    
        if line % 100 == 0: 
            d = datetime.now()
            print "@", line, "--",d.strftime("%Y-%m-%d %H:%M:%S")
            sys.stdout.flush()

        if Sfreeling:
            sentence = [ (w[0], w[1], w[2]) for w in Sfreeling.process(source) ]
            fsource.write(sentence, line)
        elif Stadpole:
            # 0: sourceword 1: lemma: 2: morph 3: pos
            if shortpos:
                sentence = [ (w[0], w[1], w[3].split("(")[0] for w in Stadpole.process(" ".join(source)) if len(w) >= 4 ]
            else:
                sentence = [ (w[0], w[1], w[3] for w in Stadpole.process(" ".join(source)) if len(w) >= 4 ]
            fsource.write(sentence, line)

        if Tfreeling:
            sentence = [ (w[0], w[1], w[2]) for w in Tfreeling.process(target) ]
            ftarget.write(sentence, line)
        elif Ttadpole:
            if shortpos:
                sentence = [ (w[0], w[1], w[3].split("(")[0] for w in Ttadpole.process(" ".join(target)) if len(w) >= 4 ]
            else:
                sentence = [ (w[0], w[1], w[3] for w in Ttadpole.process(" ".join(target)) if len(w) >= 4 ]
            ftarget.write(sentence, line)

