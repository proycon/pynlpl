#!/usr/bin/env python3
#-*- coding:utf-8 -*-


from pynlpl.textprocessors import ClassDecoder
import sys
import os
import argparse



def main():
    """pynlpl-classdecoder
    by Maarten van Gompel (proycon)
    Centre for Language Studies, Radboud University Nijmegen
    2013 - Licensed under GPLv3

    This tool decodes files from a  more compressed binary format, in which each word-type gets assigned a numeric class value, back to plain text.

    Usage: pynlpl-classdecoder [files]
    """

    parser = argparse.ArgumentParser(prog="pynlpl-classdecoder", description='This tool converts one or more tokenised plain text files, with one sentence per line, to a more compressed binary format in which each word-type gets assigned a numeric class value.  Instead of plain text files, FoLiA XML files are also supported as valid input. Certain other NLP tools may make use of this format to conserve memory and attain higher performance.')
    parser.add_argument("-s","--singleoutput", type=str, help="Decode all files to a single file, set filename to - to decode to standard output")
    parser.add_argument("--encoding",type=str,default="utf-8",help="Encoding of plain-text input files")
    parser.add_argument("-u","--unknown",action='store_true',default=False,help="Unknown classes will be assigned a special 'unknown' class (used with -c)")

    parser.add_argument('classfile', type=str, help="Class file (*.cls)")
    parser.add_argument('files', nargs='+', help="The encoded corpus files (*.clsenc)")
    args = parser.parse_args()

    classdecoder = ClassDecoder(args.classfile, args.unknown)

    if args.singleoutput:
        print("Decoding all files to " + args.singleoutput+"...", file=sys.stderr)
        classdecoder.decodefile(args.files, args.singleoutput if args.singleoutput != '-' else None, args.encoding)
    else:
        for filename in args.files:
            targetfile = os.path.basename(filename).replace('.clsenc','') + '.txt'
            print("Decoding " + filename + " to " + targetfilename+"...", file=sys.stderr)
            classdecoder.decodefile(filename, targetfile)

