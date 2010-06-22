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


try:
	opts, args = getopt.getopt(sys.argv[1:], "a:o:", ["Sfreeling=","Tfreeling=","Stadpole=","Ttadpole=","help","encoding="])
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

fsource = codecs.open(outputdir + '/source.toklempos','w',encoding)
ftarget = codecs.open(outputdir + '/target.toklempos','w',encoding)

if alignfilename:

    for line, (source, target, alignment) in enumerate(wordalignment):    
        if line % 100 == 0: 
            d = datetime.now()
            print "@", line, "--",d.strftime("%Y-%m-%d %H:%M:%S")
            sys.stdout.flush()

        fsource.write( "#" + str(line) + "\n")                
        if Sfreeling:
            taggedwords = Sfreeling.process(source)
            # 0: sourceword, 1: lemma, 2: pos        
            for w in taggedwords:
                word = lemma = pos = "NONE"
                if w[0]: word = w[0]
                if w[1]: lemma = w[1]        
                if w[2]: pos = w[2]        
                fsource.write( word + "\t" + lemma + "\t" + pos + "\n" )                
            fsource.write("\n")           
        elif Stadpole:
            # 0: sourceword 1: lemma: 2: morph 3: pos
            taggedwords = Stadpole.process(" ".join(source))
            for w in taggedwords:
                word = lemma = pos = "NONE"
                if len(w) >= 4:
                    if w[0]: word = w[0]
                    if w[1]: lemma = w[1]        
                    if w[3]: pos = w[3].split("(")[0]  #filter out extra features
                fsource.write( word + "\t" + lemma + "\t" + pos + "\n" )                
            fsource.write("\n")           

        ftarget.write( "#" + str(line) + "\n")                
        if Tfreeling:
            taggedwords = Tfreeling.process(target)
            # 1: source word, 2: lemma, 3: pos        
            for w in taggedwords:
                word = lemma = pos = "NONE"
                if w[0]: word = w[0]
                if w[1]: lemma = w[1]        
                if w[2]: pos = w[2]        
                ftarget.write( word + "\t" + lemma + "\t" + pos + "\n" )   
            ftarget.write("\n")     
        elif Ttadpole:
            # 0: sourceword 1: lemma: 2: morph 3: pos
            taggedwords = Ttadpole.process(" ".join(target))
            for w in taggedwords:
                word = lemma = pos = "NONE"
                if len(w) >= 4:
                    if w[0]: word = w[0]
                    if w[1]: lemma = w[1]        
                    if w[3]: pos = w[3].split("(")[0]  #filter out extra features
                ftarget.write( word + "\t" + lemma + "\t" + pos + "\n" )                
            ftarget.write("\n")    
           

