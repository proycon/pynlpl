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

    def test2(self):
        q = cql.Query("[ pos = \"det\" ]")
        result = q(tokens)
        self.assertEqual(len(result),3)
        self.assertEqual(result[0][0]['word'],"This")
        self.assertEqual(result[1][0]['word'],"a")
        self.assertEqual(result[2][0]['word'],"the")

    def test3(self):
        q = cql.Query("[ pos = \"det\" ] [ pos = \"a\" ] [ pos = \"n\" ]")
        result = q(tokens)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0][0]['word'],"a")
        self.assertEqual(result[0][1]['word'],"first")
        self.assertEqual(result[0][2]['word'],"test")
        self.assertEqual(result[1][0]['word'],"the")
        self.assertEqual(result[1][1]['word'],"new")
        self.assertEqual(result[1][2]['word'],"module")

    def test4(self):
        q = cql.Query("[ pos = \"det\" ] [ pos = \"a\" ]? [ pos = \"n\" ]")
        result = q(tokens)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0][0]['word'],"a")
        self.assertEqual(result[0][1]['word'],"first")
        self.assertEqual(result[0][2]['word'],"test")
        self.assertEqual(result[1][0]['word'],"the")
        self.assertEqual(result[1][1]['word'],"new")
        self.assertEqual(result[1][2]['word'],"module")

    def test5(self):
        q = cql.Query("[ pos = \"det\" ] []? [ pos = \"n\" ]")
        result = q(tokens)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0][0]['word'],"a")
        self.assertEqual(result[0][1]['word'],"first")
        self.assertEqual(result[0][2]['word'],"test")
        self.assertEqual(result[1][0]['word'],"the")
        self.assertEqual(result[1][1]['word'],"new")
        self.assertEqual(result[1][2]['word'],"module")

    def test6(self):
        q = cql.Query("[ pos = \"det\" ] []+ [ pos = \"n\" ]")
        result = q(tokens)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0][0]['word'],"a")
        self.assertEqual(result[0][1]['word'],"first")
        self.assertEqual(result[0][2]['word'],"test")
        self.assertEqual(result[1][0]['word'],"the")
        self.assertEqual(result[1][1]['word'],"new")
        self.assertEqual(result[1][2]['word'],"module")

    def test7(self):
        q = cql.Query("[ pos = \"det\" ] []* [ pos = \"n\" ]")
        result = q(tokens)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0][0]['word'],"a")
        self.assertEqual(result[0][1]['word'],"first")
        self.assertEqual(result[0][2]['word'],"test")
        self.assertEqual(result[1][0]['word'],"the")
        self.assertEqual(result[1][1]['word'],"new")
        self.assertEqual(result[1][2]['word'],"module")

if __name__ == '__main__':
    unittest.main()
