#!/usr/bin/env python
#-*- coding:utf-8 -*-

#---------------------------------------------------------------
# PyNLPl - Test Units for Statistics and Information Theory
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

import sys
import os
import unittest

sys.path.append(sys.path[0] + '/../../')
os.environ['PYTHONPATH'] = sys.path[0] + '/../../'

from pynlpl.statistics import FrequencyList

sentences = ["This is a sentence .".split(' '),"Moreover , this sentence is a test .".split(' ')]

class FrequencyListTest(unittest.TestCase):
    def test_freqlist_casesens(self):
        """Frequency List (case sensitive)"""
        global sentences
        f= FrequencyList()
        for sentence in sentences:
            f.append(sentence)
        self.assertTrue(( f['sentence'] == 2 and  f['this'] == 1 and f['test'] == 1 )) 

    def test_freqlist_caseinsens(self):
        """Frequency List (case insensitive)"""
        global sentences
        f= FrequencyList(None, False)
        for sentence in sentences:
            f.append(sentence)
        self.assertTrue(( f['sentence'] == 2 and  f['this'] == 2 and f['Test'] == 1 )) 

    def test_freqlist_tokencount(self):
        """Frequency List (count tokens)"""
        global sentences
        f= FrequencyList()
        for sentence in sentences:
            f.append(sentence)
        self.assertEqual(f.total,13) 

    def test_freqlist_typecount(self):
        """Frequency List (count types)"""
        global sentences
        f= FrequencyList()
        for sentence in sentences:
            f.append(sentence)
        self.assertEqual(len(f),9) 

if __name__ == '__main__':
    unittest.main()
