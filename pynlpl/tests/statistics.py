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
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import sys
import os
import unittest

from pynlpl.statistics import FrequencyList, HiddenMarkovModel
from pynlpl.textprocessors import Windower


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

class BigramFrequencyListTest(unittest.TestCase):
    def test_freqlist_casesens(self):
        """Bigram Frequency List (case sensitive)"""
        global sentences
        f= FrequencyList()
        for sentence in sentences:
            f.append(Windower(sentence,2))
        self.assertTrue(( f[('is','a')] == 2 and  f[('This','is')] == 1))

    def test_freqlist_caseinsens(self):
        """Bigram Frequency List (case insensitive)"""
        global sentences
        f= FrequencyList(None, False)
        for sentence in sentences:
            f.append(Windower(sentence,2))
        self.assertTrue(( f[('is','a')] == 2 and  f[('this','is')] == 1))

class HMMTest(unittest.TestCase):
    def test_viterbi(self):
        """Viterbi decode run on Hidden Markov Model"""
        hmm = HiddenMarkovModel('start')
        hmm.settransitions('start',{'rainy':0.6,'sunny':0.4})
        hmm.settransitions('rainy',{'rainy':0.7,'sunny':0.3})
        hmm.settransitions('sunny',{'rainy':0.4,'sunny':0.6}) 
        hmm.setemission('rainy', {'walk': 0.1, 'shop': 0.4, 'clean': 0.5})
        hmm.setemission('sunny', {'walk': 0.6, 'shop': 0.3, 'clean': 0.1})
        observations = ['walk', 'shop', 'clean']
        prob, path = hmm.viterbi(observations)
        self.assertEqual( path, ['sunny', 'rainy', 'rainy'])
        self.assertEqual( prob, 0.01344)
        
if __name__ == '__main__':
    unittest.main()
