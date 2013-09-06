#!/usr/bin/env python3


from __future__ import print_function, unicode_literals, division, absolute_import

import argparse
import sys
import os
from math import log

from collections import defaultdict

def pmi(sentences1, sentences2):
    jointcount = len(sentences1 & sentences2)
    if jointcount == 0: return None
    return log( jointcount / (len(sentences1) * len(sentences2)))

def npmi(sentences1, sentences2):
    jointcount = len(sentences1 & sentences2)
    if jointcount == 0: return None
    return log( jointcount / (len(sentences1) * len(sentences2))) / -log(jointcount)

def main():
    parser = argparse.ArgumentParser(description="Simple cooccurence computation", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f','--inputtext', type=str,help="Input file (plaintext, tokenised, utf-8, one sentence per line)", action='store',default="",required=True)
    parser.add_argument('-u','--unidirectional', help="Compute unidirectionally, i.e. the left word will always occur before the right word", action='store_true',default=False)
    parser.add_argument('-s','--sorted', help="Output sorted by co-occurrence score", action='store_true',default=False)
    parser.add_argument('--pmi',help="Compute pointwise mutual information", action='store_true',default=False)
    parser.add_argument('--npmi',help="Compute normalised pointwise mutual information", action='store_true',default=False)

    args = parser.parse_args()
    if not args.pmi and not args.npmi:
        args.pmi = True

    index = defaultdict(set)
    reverseindex = defaultdict(set)

    f = open(args.inputtext,'r',encoding='utf-8')
    for i, line in enumerate(f):
        sentence = i + 1
        print("Indexing @" + str(sentence),file=sys.stderr)
        if line:
            for pos, word in enumerate(line.split()):
                if word:
                    index[(pos,word)].add(sentence)
                    reverseindex[sentence].add((pos,word))
    f.close()

    output = []
    #compute co-occurence
    l = len(index)
    for i, (pos, word) in enumerate(index):
        print("Computing cooc @" + str(i+1) + "/" + str(l),file=sys.stderr)
        for sentence in index[(pos,word)]:
            for pos2, word2 in reverseindex[sentence]:
                if args.unidirectional and pos2 < pos:
                    continue
                if (pos != pos2) or (word != word2):
                    if args.pmi:
                        score = pmi(index[(pos,word)], index[(pos2,word2)])
                    elif args.npmi:
                        score = npmi(index[(pos,word)], index[(pos2,word2)])
                    if not (score is None):
                        if args.sorted:
                            output.append((word,word2,score))
                        else:
                            print(word + "\t" + word2 + "\t" + str(score))

    if args.sorted:
        for word,word2,score in sorted(output, key=lambda x: x[2]):
            print(word + "\t" + word2 + "\t" + str(score))


if __name__ == '__main__':
    main()

