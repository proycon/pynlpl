#!/usr/bin/env python3


from __future__ import print_function, unicode_literals, division, absolute_import

import argparse
import sys
from math import log

from collections import defaultdict

def pmi(sentences1, sentences2,discount = 0):
    jointcount = len(sentences1 & sentences2) - discount
    if jointcount <= 0: return None
    return log( jointcount / (len(sentences1) * len(sentences2))), jointcount+discount

def npmi(sentences1, sentences2,discount=0):
    jointcount = len(sentences1 & sentences2) - discount
    if jointcount <= 0: return None
    return log( jointcount / (len(sentences1) * len(sentences2))) / -log(jointcount), jointcount+discount

def main():
    parser = argparse.ArgumentParser(description="Simple cooccurence computation", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f','--inputtext', type=str,help="Input file (plaintext, tokenised, utf-8, one sentence per line)", action='store',default="",required=True)
    parser.add_argument('-s','--sorted', help="Output sorted by co-occurrence score", action='store_true',default=False)
    parser.add_argument('-t','--threshold', help="Joined occurrence threshold, do not consider words occuring less than this", type=int, action='store',default=1)
    parser.add_argument('-a','--adjacency', help="Compute the adjacency fraction (how many co-occurrence are immediate bigrams)", action='store_true',default=False)
    parser.add_argument('-A','--discountadjacency', help="Do not take immediately adjacent fragments (bigrams) into account when computing mutual information (requires -a)", action='store_true',default=False)
    parser.add_argument('--pmi',help="Compute pointwise mutual information", action='store_true',default=False)
    parser.add_argument('--npmi',help="Compute normalised pointwise mutual information", action='store_true',default=False)
    parser.add_argument('--jaccard',help="Compute jaccard similarity coefficient", action='store_true',default=False)
    parser.add_argument('--dice',help="Compute dice coefficient", action='store_true',default=False)

    args = parser.parse_args()
    if not args.pmi and not args.npmi and not args.jaccard and not args.dice:
        args.pmi = True

    count = defaultdict(int)
    cooc = defaultdict(lambda: defaultdict(int))
    adjacent = defaultdict(lambda: defaultdict(int))
    total = 0

    f = open(args.inputtext,'r',encoding='utf-8')
    for i, line in enumerate(f):
        sentence = i + 1
        if sentence % 1000 == 0: print("Indexing @" + str(sentence),file=sys.stderr)
        if line:
            words = list(enumerate(line.split()))
            for pos, word in words:
                count[word] += 1
                total += 1
                for pos2, word2 in words:
                    if pos2 > pos:
                        cooc[word][word2] += 1
                        if args.adjacency and pos2 == pos + len(word.split()):
                            adjacent[word][word2] += 1
    f.close()


    l = len(cooc)
    output = []
    for i, (word, coocdata) in enumerate(cooc.items()):
        print("Computing mutual information @" + str(i+1) + "/" + str(l) + ": \"" + word + "\" , co-occurs with " + str(len(coocdata)) + " words",file=sys.stderr)
        for word2, jointcount in coocdata.items():
            if jointcount> args.threshold:
                if args.adjacency and word in adjacent and word2 in adjacent[word]:
                    adjcount = adjacent[word][word2]
                else:
                    adjcount = 0

                if args.discountadjacency:
                    discount = adjcount
                else:
                    discount = 0

                if args.pmi:
                    score = log( ((jointcount-discount)/total)  / ((count[word]/total) * (count[word2]/total)))
                elif args.npmi:
                    score = log( ((jointcount-discount)/total) / ((count[word]/total) * (count[word2]/total))) / -log((jointcount-discount)/total)
                elif args.jaccard or args.dice:
                    score = (jointcount-discount) / (count[word] + count[word2] - (jointcount - discount) )
                    if args.dice:
                        score = 2*score / (1+score)

                if args.sorted:
                    outputdata = (word,word2,score, jointcount, adjcount, adjcount / jointcount if args.adjacency else None)
                    output.append(outputdata)
                else:
                    if args.adjacency:
                        print(word + "\t" + word2 + "\t" + str(score) + "\t" + str(jointcount) + "\t" + str(adjcount) + "\t" + str(adjcount / jointcount))
                    else:
                        print(word + "\t" + word2 + "\t" + str(score) + "\t" + str(jointcount))


    if args.sorted:
        print("Outputting " + str(len(output)) + " pairs",file=sys.stderr)
        if args.adjacency:
            print("#WORD\tWORD2\tSCORE\tJOINTCOUNT\tBIGRAMCOUNT\tBIGRAMRATIO")
        else:
            print("#WORD\tWORD2\tSCORE\tJOINTCOUNT\tBIGRAMCOUNT\tBIGRAMRATIO")
        if args.npmi:
            sign = 1
        else:
            sign = -1
        for word,word2,score,jointcount,adjcount, adjratio in sorted(output, key=lambda x: sign * x[2]):
            if args.adjacency:
                print(word + "\t" + word2 + "\t" + str(score) + "\t" + str(jointcount) + "\t" + str(adjcount) + "\t" + str(adjratio) )
            else:
                print(word + "\t" + word2 + "\t" + str(score) + "\t" + str(jointcount))




if __name__ == '__main__':
    main()

