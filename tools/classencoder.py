#!/usr/bin/env python3
#-*- coding:utf-8 -*-


#Python 3 by definition

from pynlpl.textprocessors import ClassEncoder
from pynlpl.statistics import FrequencyList
from pynlpl.formats import folia
import argparse
import sys
import os
assert sys.version > '3'

def main():
    """pynlpl-classencoder
    by Maarten van Gompel (proycon)
    Centre for Language Studies, Radboud University Nijmegen
    2013 - Licensed under GPLv3

    This tool converts one or more tokenised plain text files, with one sentence per line, to a more compressed binary format in which each word-type gets assigned a numeric class value.
    Instead of plain text files, FoLiA XML files are also supported as valid input. Certain other NLP tools may make use of this format to conserve memory and attain higher performance.

    Usage: pynlpl-classencoder [files]
    """

    parser = argparse.ArgumentParser(prog="pynlpl-classencoder", description='This tool converts one or more tokenised plain text files, with one sentence per line, to a more compressed binary format in which each word-type gets assigned a numeric class value.  Instead of plain text files, FoLiA XML files are also supported as valid input. Certain other NLP tools may make use of this format to conserve memory and attain higher performance.')
    parser.add_argument("-x","--xml", help="Input is FoLiA XML instead of plain-text")
    parser.add_argument("-c","--classfile", type=str,help="Load and use existing class model instead of building a new one")
    parser.add_argument("-o","--output", type=str, default="classes.cls", help="Filename of the class file")
    parser.add_argument("-s","--singleoutput", type=str, help="Encode all files to a single file")
    parser.add_argument("-e","--extend",action='store_true',default=False,help="Extend existing class model with (used with -c)")
    parser.add_argument("-a","--autoadd",action='store_true',default=False,help="Automatically add newly found classes to existing class file (used with -c)")
    parser.add_argument("-u","--unknown",action='store_true',default=False,help="Unknown classes will be assigned a special 'unknown' class (used with -c)")
    parser.add_argument("--encoding",type=str,default="utf-8",help="Encoding of plain-text input files")

    parser.add_argument('files', nargs='+')
    args = parser.parse_args()


    if args.classfile:
        classencoder = ClassEncoder(args.classfile, args.autoadd or args.extend, args.unknown)
    else:
        classencoder = ClassEncoder(None, args.autoadd or args.extend, args.unknown)

    if not args.classfile or args.extend:
        if args.xml:
            for filename in args.files:
                doc = folia.Document(file=filename)

        else:
            print("Building classes...", file=sys.stderr)
            if args.xml:
                classencoder.buildfromfolia(args.files)
            else:
                classencoder.buildfromtext(args.files)

    if not args.classfile:
        print("Writing classes to ", args.output, file=sys.stderr)
        classencoder.save(args.output)

    if args.singleoutput:
        print("Encoding all files in " + args.singleoutput + "...", file=sys.stderr)
        classencoder.encodefile(args.files, args.singleoutput, args.encoding)
    else:
        for filename in args.files:
            targetfilename = os.path.basename(filename).replace('.txt','').replace('.xml','') + '.clsenc'
            print("Encoding " + filename + " in " + targetfilename + "...",file=sys.stderr)
            classencoder.encodefile(filename, targetfilename)

    if args.classfile and args.autoadd:
        print("Writing classes to ", args.classfile, file=sys.stderr)
        classencoder.save(args.classfile)



if __name__ == '__main__':
    main()
