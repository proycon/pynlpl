#!/usr/bin/env python
#-*- coding:utf-8 -*-


#---------------------------------------------------------------
# PyNLPl - Test Units for Text Processors
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

from pynlpl.textprocessors import Windower, tokenise, strip_accents, calculate_overlap

text = "This is a test .".split(" ")

class WindowerTest(unittest.TestCase):
    def test_unigrams(self):
        """Windower (unigrams)"""
        global text
        result = list(iter(Windower(text,1)))
        self.assertEqual(result,[("This",),("is",),("a",),("test",),(".",)])

    def test_bigrams(self):
        """Windower (bigrams)"""
        global text
        result = list(iter(Windower(text,2)))
        self.assertEqual(result,[("<begin>","This"),("This","is"),("is","a"),("a","test"),("test","."),(".","<end>")])

    def test_trigrams(self):
        """Windower (trigrams)"""
        global text
        result = list(iter(Windower(text,3)))
        self.assertEqual(result,[('<begin>', '<begin>', 'This'), ('<begin>', 'This', 'is'), ('This', 'is', 'a'), ('is', 'a', 'test'), ('a', 'test', '.'), ('test', '.', '<end>'), ('.', '<end>', '<end>')])


    def test_trigrams_word(self):
        """Windower (trigrams) (on single word)"""
        global text
        result = list(iter(Windower(["hi"],3)))
        self.assertEqual(result,[('<begin>', '<begin>', 'hi'), ('<begin>', 'hi', '<end>'), ('hi', '<end>', '<end>')])



        
class TokenizerTest(unittest.TestCase):
    def test_tokenize(self):
        """Tokeniser - One sentence"""
        self.assertEqual(tokenise("This is a test."),"This is a test .".split(" "))    
    
    def test_tokenize_sentences(self):
        """Tokeniser - Multiple sentences"""
        self.assertEqual(tokenise("This, is the first sentence! This is the second sentence."),"This , is the first sentence ! This is the second sentence .".split(" "))     
    
    def test_tokenize_noeos(self):
        """Tokeniser - Missing EOS Marker"""
        self.assertEqual(tokenise("This is a test"),"This is a test".split(" "))
    
    def test_tokenize_url(self):
        """Tokeniser - URL"""
        global text
        self.assertEqual(tokenise("I go to http://www.google.com when I need to find something."),"I go to http://www.google.com when I need to find something .".split(" "))        

    def test_tokenize_mail(self):
        """Tokeniser - Mail"""
        global text
        self.assertEqual(tokenise("Write me at proycon@anaproy.nl."),"Write me at proycon@anaproy.nl .".split(" "))        

    def test_tokenize_numeric(self):
        """Tokeniser - numeric"""
        global text
        self.assertEqual(tokenise("I won € 300,000.00!"),"I won € 300,000.00 !".split(" "))        

    def test_tokenize_quotes(self):
        """Tokeniser - quotes"""
        global text
        self.assertEqual(tokenise("Hij zegt: \"Wat een lief baby'tje is dat!\""),"Hij zegt : \" Wat een lief baby'tje is dat ! \"".split(" "))     


class StripAccentTest(unittest.TestCase):
    def test_strip_accents(self):
        """Strip Accents"""        
        self.assertEqual(strip_accents("áàâãāĝŭçñßt"),"aaaaagucnt")

class OverlapTest(unittest.TestCase):
    def test_overlap_subset(self):
        """Overlap - Subset"""
        h = [4,5,6,7]
        n = [5,6]
        self.assertEqual(calculate_overlap(h,n),  [((5,6),0)])
        
    def test_overlap_equal(self):
        """Overlap - Equal"""
        h = [4,5,6,7]
        n = [4,5,6,7]
        self.assertEqual(calculate_overlap(h,n),  [((4,5,6,7),2)])        
        
    def test_overlap_none(self):
        """Overlap - None"""
        h = [4,5,6,7]
        n = [8,9,10]
        self.assertEqual(calculate_overlap(h,n),  [])            
    
    def test_overlap_leftpartial(self):
        """Overlap - Left partial"""
        h = [4,5,6,7]
        n = [1,2,3,4,5]
        self.assertEqual(calculate_overlap(h,n),  [((4,5),-1)] ) 
        
    def test_overlap_rightpartial(self):
        """Overlap - Right partial"""
        h = [4,5,6,7]
        n = [6,7,8,9]
        self.assertEqual(calculate_overlap(h,n),  [((6,7),1)] )        
        
    def test_overlap_leftpartial2(self):
        """Overlap - Left partial (2)"""
        h = [1,2,3,4,5]
        n = [0,1,2]
        self.assertEqual(calculate_overlap(h,n),  [((1,2),-1)] ) 
        
    def test_overlap_rightpartial2(self):
        """Overlap - Right partial (2)"""
        h = [1,2,3,4,5]
        n = [4,5,6]
        self.assertEqual(calculate_overlap(h,n),  [((4,5),1)] )        
    
    
    def test_overlap_leftfull(self):
        """Overlap - Left full"""
        h = [1,2,3,4,5]
        n = [1,2]
        self.assertEqual(calculate_overlap(h,n),  [((1,2),-1)] ) 
        
    def test_overlap_rightfull(self):
        """Overlap - Right full"""
        h = [1,2,3,4,5]
        n = [4,5]
        self.assertEqual(calculate_overlap(h,n),  [((4,5),1)] )        
    

if __name__ == '__main__':
    unittest.main()
