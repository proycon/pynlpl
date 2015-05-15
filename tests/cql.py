#!/usr/bin/env python
#-*- coding:utf-8 -*-

#---------------------------------------------------------------
# PyNLPl - Test Units for CQL using Finite State Automata
#   by Maarten van Gompel, Radboud University Nijmegen
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#----------------------------------------------------------------


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout

import sys
import unittest
from pynlpl.formats import cql

tokens = [
    {
        'word': 'This',
        'lemma': 'this',
        'pos': 'det',
    },
    {
        'word': 'is',
        'lemma': 'be',
        'pos': 'v',
    },
    {
        'word': 'a',
        'lemma': 'a',
        'pos': 'det',
    },
    {
        'word': 'first',
        'lemma': 'first',
        'pos': 'a',
    },
    {
        'word': 'test',
        'lemma': 'test',
        'pos': 'n',
    },
    {
        'word': 'of',
        'lemma': 'dit',
        'pos': 'prep',
    },
    {
        'word': 'the',
        'lemma': 'the',
        'pos': 'det',
    },
    {
        'word': 'new',
        'lemma': 'new',
        'pos': 'a',
    },
    {
        'word': 'module',
        'lemma': 'module',
        'pos': 'n',
    },
    {
        'word': '.',
        'lemma': '.',
        'pos': 'punc',
    },
]


class Test1(unittest.TestCase):

    def test1(self):
        q = cql.Query("\"the\"")
        result = q(tokens)
        self.assertEqual(len(result),1) #one result
        self.assertEqual(len(result[0]),1) #result 1 consists of one word
        self.assertEqual(result[0][0]['word'],"the")

if __name__ == '__main__':
    unittest.main()
