#!/usr/bin/env python
#-*- coding:utf-8 -*-


#---------------------------------------------------------------
# PyNLPl - Test Units for FoLiA
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
from pynlpl.common import u, isstring
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout

import sys
import os
import unittest
import io
import gzip
import bz2
import re


FOLIARELEASE = "v1.3.2.52"

if os.path.exists('../../FoLiA'):
    FOLIAPATH = '../../FoLiA/'
elif os.path.exists('../FoLiA'):
    FOLIAPATH = '../FoLiA/'
else:
    FOLIAPATH = 'FoLiA'
    print("Downloading FoLiA",file=sys.stderr)
    os.system("git clone https://github.com/proycon/folia.git FoLiA && cd FoLiA && git checkout tags/" + FOLIARELEASE + ' && cd ..')

if 'TMPDIR' in os.environ:
    TMPDIR = os.environ['TMPDIR']
else:
    TMPDIR = '/tmp/'

if sys.version < '3':
    from StringIO import StringIO
else:
    from io import StringIO, BytesIO
from datetime import datetime
import lxml.objectify
from pynlpl.formats import folia
if folia.LXE:
    from lxml import etree as ElementTree
else:
    import xml.etree.cElementTree as ElementTree


def xmlcheck(xml,expect):
    #obj1 = lxml.objectify.fromstring(expect)
    #expect = lxml.etree.tostring(obj1)
    f = io.open(os.path.join(TMPDIR, 'foliatest.fragment.expect.xml'),'w',encoding='utf-8')
    f.write(expect)
    f.close()
    f = io.open(os.path.join(TMPDIR , 'foliatest.fragment.out.xml'),'w', encoding='utf-8')
    f.write(xml)
    f.close()

    retcode = os.system('xmldiff -c ' + os.path.join(TMPDIR, 'foliatest.fragment.expect.xml') + ' ' + os.path.join(TMPDIR,'foliatest.fragment.out.xml'))
    passed = (retcode == 0)

    #obj2 = lxml.objectify.fromstring(xml)
    #xml = lxml.etree.tostring(obj2)
    #passed = (expect == xml)
    if not passed:
        print("XML fragments don't match:",file=stderr)
        print("--------------------------REFERENCE-------------------------------------",file=stderr)
        print(expect,file=stderr)
        print("--------------------------ACTUAL RESULT---------------------------------",file=stderr)
        print(xml,file=stderr)
        print("------------------------------------------------------------------------",file=stderr)
    return passed


class Test1Read(unittest.TestCase):

    def test1_readfromfile(self):
        """Reading from file"""
        global FOLIAEXAMPLE
        #write example to file
        f = io.open(os.path.join(TMPDIR,'foliatest.xml'),'w',encoding='utf-8')
        f.write(FOLIAEXAMPLE)
        f.close()

        doc = folia.Document(file=os.path.join(TMPDIR,'foliatest.xml'))
        self.assertTrue(isinstance(doc,folia.Document))

        #sanity check: reading from file must yield the exact same data as reading from string
        doc2 = folia.Document(string=FOLIAEXAMPLE)
        self.assertEqual( doc, doc2)

    def test1a_readfromfile(self):
        """Reading from GZ file"""
        global FOLIAEXAMPLE
        #write example to file
        f = gzip.GzipFile(os.path.join(TMPDIR,'foliatest.xml.gz'),'w')
        f.write(FOLIAEXAMPLE.encode('utf-8'))
        f.close()

        doc = folia.Document(file=os.path.join(TMPDIR,'foliatest.xml.gz'))
        self.assertTrue(isinstance(doc,folia.Document))

        #sanity check: reading from file must yield the exact same data as reading from string
        doc2 = folia.Document(string=FOLIAEXAMPLE)
        self.assertEqual( doc, doc2)


    def test1b_readfromfile(self):
        """Reading from BZ2 file"""
        global FOLIAEXAMPLE
        #write example to file
        f = bz2.BZ2File(os.path.join(TMPDIR,'foliatest.xml.bz2'),'w')
        f.write(FOLIAEXAMPLE.encode('utf-8'))
        f.close()

        doc = folia.Document(file=os.path.join(TMPDIR,'foliatest.xml.bz2'))
        self.assertTrue(isinstance(doc,folia.Document))

        #sanity check: reading from file must yield the exact same data as reading from string
        doc2 = folia.Document(string=FOLIAEXAMPLE)
        self.assertEqual( doc, doc2)


    def test2_readfromstring(self):
        """Reading from string (unicode)"""
        global FOLIAEXAMPLE
        doc = folia.Document(string=FOLIAEXAMPLE)
        self.assertTrue(isinstance(doc,folia.Document))

    def test2_readfromstring(self):
        """Reading from string (bytes)"""
        global FOLIAEXAMPLE
        doc = folia.Document(string=FOLIAEXAMPLE.encode('utf-8'))
        self.assertTrue(isinstance(doc,folia.Document))

    def test3_readfromstring(self):
        """Reading from pre-parsed XML tree (as unicode(Py2)/str(Py3) obj)"""
        global FOLIAEXAMPLE
        if sys.version < '3':
            doc = folia.Document(tree=ElementTree.parse(StringIO(FOLIAEXAMPLE.encode('utf-8'))))
        else:
            doc = folia.Document(tree=ElementTree.parse(BytesIO(FOLIAEXAMPLE.encode('utf-8'))))
        self.assertTrue(isinstance(doc,folia.Document))


    def test4_readdcoi(self):
        """Reading D-Coi file"""
        global DCOIEXAMPLE
        doc = folia.Document(string=DCOIEXAMPLE)
        #doc = folia.Document(tree=lxml.etree.parse(StringIO(DCOIEXAMPLE.encode('iso-8859-15'))))
        self.assertTrue(isinstance(doc,folia.Document))
        self.assertEqual(len(list(doc.words())),1465)

class Test2Sanity(unittest.TestCase):

    def setUp(self):
        self.doc = folia.Document(string=FOLIAEXAMPLE)

    def test000_count_text(self):
        """Sanity check - One text """
        self.assertEqual( len(self.doc), 1)
        self.assertTrue( isinstance( self.doc[0], folia.Text ))

    def test001_count_paragraphs(self):
        """Sanity check - Paragraph count"""
        self.assertEqual( len(list(self.doc.paragraphs())) , 3)

    def test002_count_sentences(self):
        """Sanity check - Sentences count"""
        self.assertEqual( len(list(self.doc.sentences())) , 17)

    def test003a_count_words(self):
        """Sanity check - Word count"""
        self.assertEqual( len(list(self.doc.words())) , 190)

    def test003b_iter_words(self):
        """Sanity check - Words"""
        self.assertEqual( [x.id for x in self.doc.words() ], ['WR-P-E-J-0000000001.head.1.s.1.w.1', 'WR-P-E-J-0000000001.p.1.s.1.w.1', 'WR-P-E-J-0000000001.p.1.s.1.w.2', 'WR-P-E-J-0000000001.p.1.s.1.w.3', 'WR-P-E-J-0000000001.p.1.s.1.w.4', 'WR-P-E-J-0000000001.p.1.s.1.w.5', 'WR-P-E-J-0000000001.p.1.s.1.w.6', 'WR-P-E-J-0000000001.p.1.s.1.w.7', 'WR-P-E-J-0000000001.p.1.s.1.w.8', 'WR-P-E-J-0000000001.p.1.s.2.w.1', 'WR-P-E-J-0000000001.p.1.s.2.w.2', 'WR-P-E-J-0000000001.p.1.s.2.w.3', 'WR-P-E-J-0000000001.p.1.s.2.w.4', 'WR-P-E-J-0000000001.p.1.s.2.w.5', 'WR-P-E-J-0000000001.p.1.s.2.w.6', 'WR-P-E-J-0000000001.p.1.s.2.w.7', 'WR-P-E-J-0000000001.p.1.s.2.w.8', 'WR-P-E-J-0000000001.p.1.s.2.w.9', 'WR-P-E-J-0000000001.p.1.s.2.w.10', 'WR-P-E-J-0000000001.p.1.s.2.w.11', 'WR-P-E-J-0000000001.p.1.s.2.w.12', 'WR-P-E-J-0000000001.p.1.s.2.w.13', 'WR-P-E-J-0000000001.p.1.s.2.w.14', 'WR-P-E-J-0000000001.p.1.s.2.w.15', 'WR-P-E-J-0000000001.p.1.s.2.w.16', 'WR-P-E-J-0000000001.p.1.s.2.w.17', 'WR-P-E-J-0000000001.p.1.s.2.w.18', 'WR-P-E-J-0000000001.p.1.s.2.w.19', 'WR-P-E-J-0000000001.p.1.s.2.w.20', 'WR-P-E-J-0000000001.p.1.s.2.w.21', 'WR-P-E-J-0000000001.p.1.s.2.w.22', 'WR-P-E-J-0000000001.p.1.s.2.w.23', 'WR-P-E-J-0000000001.p.1.s.2.w.24-25', 'WR-P-E-J-0000000001.p.1.s.2.w.26', 'WR-P-E-J-0000000001.p.1.s.2.w.27', 'WR-P-E-J-0000000001.p.1.s.2.w.28', 'WR-P-E-J-0000000001.p.1.s.2.w.29', 'WR-P-E-J-0000000001.p.1.s.3.w.1', 'WR-P-E-J-0000000001.p.1.s.3.w.2', 'WR-P-E-J-0000000001.p.1.s.3.w.3', 'WR-P-E-J-0000000001.p.1.s.3.w.4', 'WR-P-E-J-0000000001.p.1.s.3.w.5', 'WR-P-E-J-0000000001.p.1.s.3.w.6', 'WR-P-E-J-0000000001.p.1.s.3.w.7', 'WR-P-E-J-0000000001.p.1.s.3.w.8', 'WR-P-E-J-0000000001.p.1.s.3.w.9', 'WR-P-E-J-0000000001.p.1.s.3.w.10', 'WR-P-E-J-0000000001.p.1.s.3.w.11', 'WR-P-E-J-0000000001.p.1.s.3.w.12', 'WR-P-E-J-0000000001.p.1.s.3.w.13', 'WR-P-E-J-0000000001.p.1.s.3.w.14', 'WR-P-E-J-0000000001.p.1.s.3.w.15', 'WR-P-E-J-0000000001.p.1.s.3.w.16', 'WR-P-E-J-0000000001.p.1.s.3.w.17', 'WR-P-E-J-0000000001.p.1.s.3.w.18', 'WR-P-E-J-0000000001.p.1.s.3.w.19', 'WR-P-E-J-0000000001.p.1.s.3.w.20', 'WR-P-E-J-0000000001.p.1.s.3.w.21', 'WR-P-E-J-0000000001.p.1.s.4.w.1', 'WR-P-E-J-0000000001.p.1.s.4.w.2', 'WR-P-E-J-0000000001.p.1.s.4.w.3', 'WR-P-E-J-0000000001.p.1.s.4.w.4', 'WR-P-E-J-0000000001.p.1.s.4.w.5', 'WR-P-E-J-0000000001.p.1.s.4.w.6', 'WR-P-E-J-0000000001.p.1.s.4.w.7', 'WR-P-E-J-0000000001.p.1.s.4.w.8', 'WR-P-E-J-0000000001.p.1.s.4.w.9', 'WR-P-E-J-0000000001.p.1.s.4.w.10', 'WR-P-E-J-0000000001.p.1.s.5.w.1', 'WR-P-E-J-0000000001.p.1.s.5.w.2', 'WR-P-E-J-0000000001.p.1.s.5.w.3', 'WR-P-E-J-0000000001.p.1.s.5.w.4', 'WR-P-E-J-0000000001.p.1.s.5.w.5', 'WR-P-E-J-0000000001.p.1.s.5.w.6', 'WR-P-E-J-0000000001.p.1.s.5.w.7', 'WR-P-E-J-0000000001.p.1.s.5.w.8', 'WR-P-E-J-0000000001.p.1.s.5.w.9', 'WR-P-E-J-0000000001.p.1.s.5.w.10', 'WR-P-E-J-0000000001.p.1.s.5.w.11', 'WR-P-E-J-0000000001.p.1.s.5.w.12', 'WR-P-E-J-0000000001.p.1.s.5.w.13', 'WR-P-E-J-0000000001.p.1.s.5.w.14', 'WR-P-E-J-0000000001.p.1.s.5.w.15', 'WR-P-E-J-0000000001.p.1.s.5.w.16', 'WR-P-E-J-0000000001.p.1.s.5.w.17', 'WR-P-E-J-0000000001.p.1.s.5.w.18', 'WR-P-E-J-0000000001.p.1.s.5.w.19', 'WR-P-E-J-0000000001.p.1.s.5.w.20', 'WR-P-E-J-0000000001.p.1.s.5.w.21', 'WR-P-E-J-0000000001.p.1.s.6.w.1', 'WR-P-E-J-0000000001.p.1.s.6.w.2', 'WR-P-E-J-0000000001.p.1.s.6.w.3', 'WR-P-E-J-0000000001.p.1.s.6.w.4', 'WR-P-E-J-0000000001.p.1.s.6.w.5', 'WR-P-E-J-0000000001.p.1.s.6.w.6', 'WR-P-E-J-0000000001.p.1.s.6.w.7', 'WR-P-E-J-0000000001.p.1.s.6.w.8', 'WR-P-E-J-0000000001.p.1.s.6.w.9', 'WR-P-E-J-0000000001.p.1.s.6.w.10', 'WR-P-E-J-0000000001.p.1.s.6.w.11', 'WR-P-E-J-0000000001.p.1.s.6.w.12', 'WR-P-E-J-0000000001.p.1.s.6.w.13', 'WR-P-E-J-0000000001.p.1.s.6.w.14', 'WR-P-E-J-0000000001.p.1.s.6.w.15', 'WR-P-E-J-0000000001.p.1.s.6.w.16', 'WR-P-E-J-0000000001.p.1.s.6.w.17', 'WR-P-E-J-0000000001.p.1.s.6.w.18', 'WR-P-E-J-0000000001.p.1.s.6.w.19', 'WR-P-E-J-0000000001.p.1.s.6.w.20', 'WR-P-E-J-0000000001.p.1.s.6.w.21', 'WR-P-E-J-0000000001.p.1.s.6.w.22', 'WR-P-E-J-0000000001.p.1.s.6.w.23', 'WR-P-E-J-0000000001.p.1.s.6.w.24', 'WR-P-E-J-0000000001.p.1.s.6.w.25', 'WR-P-E-J-0000000001.p.1.s.6.w.26', 'WR-P-E-J-0000000001.p.1.s.6.w.27', 'WR-P-E-J-0000000001.p.1.s.6.w.28', 'WR-P-E-J-0000000001.p.1.s.6.w.29', 'WR-P-E-J-0000000001.p.1.s.6.w.30', 'WR-P-E-J-0000000001.p.1.s.6.w.31', 'WR-P-E-J-0000000001.p.1.s.6.w.32', 'WR-P-E-J-0000000001.p.1.s.6.w.33', 'WR-P-E-J-0000000001.p.1.s.6.w.34', 'WR-P-E-J-0000000001.p.1.s.7.w.1', 'WR-P-E-J-0000000001.p.1.s.7.w.2', 'WR-P-E-J-0000000001.p.1.s.7.w.3', 'WR-P-E-J-0000000001.p.1.s.7.w.4', 'WR-P-E-J-0000000001.p.1.s.7.w.5', 'WR-P-E-J-0000000001.p.1.s.7.w.6', 'WR-P-E-J-0000000001.p.1.s.7.w.7', 'WR-P-E-J-0000000001.p.1.s.7.w.8', 'WR-P-E-J-0000000001.p.1.s.7.w.9', 'WR-P-E-J-0000000001.p.1.s.7.w.10', 'WR-P-E-J-0000000001.p.1.s.8.w.1', 'WR-P-E-J-0000000001.p.1.s.8.w.2', 'WR-P-E-J-0000000001.p.1.s.8.w.3', 'WR-P-E-J-0000000001.p.1.s.8.w.4', 'WR-P-E-J-0000000001.p.1.s.8.w.5', 'WR-P-E-J-0000000001.p.1.s.8.w.6', 'WR-P-E-J-0000000001.p.1.s.8.w.7', 'WR-P-E-J-0000000001.p.1.s.8.w.8', 'WR-P-E-J-0000000001.p.1.s.8.w.9', 'WR-P-E-J-0000000001.p.1.s.8.w.10', 'WR-P-E-J-0000000001.p.1.s.8.w.11', 'WR-P-E-J-0000000001.p.1.s.8.w.12', 'WR-P-E-J-0000000001.p.1.s.8.w.13', 'WR-P-E-J-0000000001.p.1.s.8.w.14', 'WR-P-E-J-0000000001.p.1.s.8.w.15', 'WR-P-E-J-0000000001.p.1.s.8.w.16', 'WR-P-E-J-0000000001.p.1.s.8.w.17', 'entry.1.term.1.w.1', 'sandbox.list.1.listitem.1.s.1.w.1', 'sandbox.list.1.listitem.1.s.1.w.2', 'sandbox.list.1.listitem.2.s.1.w.1', 'sandbox.list.1.listitem.2.s.1.w.2', 'sandbox.figure.1.caption.s.1.w.1', 'sandbox.figure.1.caption.s.1.w.2', 'WR-P-E-J-0000000001.sandbox.2.s.1.w.1', 'WR-P-E-J-0000000001.sandbox.2.s.1.w.2', 'WR-P-E-J-0000000001.sandbox.2.s.1.w.3', 'WR-P-E-J-0000000001.sandbox.2.s.1.w.4', 'WR-P-E-J-0000000001.sandbox.2.s.1.w.5', 'WR-P-E-J-0000000001.sandbox.2.s.1.w.6', 'WR-P-E-J-0000000001.sandbox.2.s.2.w.1', 'WR-P-E-J-0000000001.sandbox.2.s.2.w.2', 'WR-P-E-J-0000000001.sandbox.2.s.2.w.3', 'WR-P-E-J-0000000001.sandbox.2.s.2.w.4', 'WR-P-E-J-0000000001.sandbox.2.s.2.w.5', 'WR-P-E-J-0000000001.sandbox.2.s.2.w.6', 'WR-P-E-J-0000000001.sandbox.2.s.2.w.7', 'WR-P-E-J-0000000001.sandbox.2.s.2.w.8', 'WR-P-E-J-0000000001.sandbox.2.s.3.w.1', 'WR-P-E-J-0000000001.sandbox.2.s.3.w.2', 'WR-P-E-J-0000000001.sandbox.2.s.3.w.3', 'WR-P-E-J-0000000001.sandbox.2.s.3.w.4', 'WR-P-E-J-0000000001.sandbox.2.s.3.w.6', 'example.table.1.w.1', 'example.table.1.w.2', 'example.table.1.w.3', 'example.table.1.w.4', 'example.table.1.w.5', 'example.table.1.w.6', 'example.table.1.w.7', 'example.table.1.w.8', 'example.table.1.w.9', 'example.table.1.w.10', 'example.table.1.w.11', 'example.table.1.w.12', 'example.table.1.w.13', 'example.table.1.w.14'] )

    def test004_first_word(self):
        """Sanity check - First word"""
        #grab first word
        w = self.doc.words(0) # shortcut for doc.words()[0]
        self.assertTrue( isinstance(w, folia.Word) )
        self.assertEqual( w.id , 'WR-P-E-J-0000000001.head.1.s.1.w.1' )
        self.assertEqual( w.text() , "Stemma" )
        self.assertEqual( str(w) , "Stemma" ) #should be unicode object also in Py2!
        if sys.version < '3':
            self.assertEqual( unicode(w) , "Stemma" )


    def test005_last_word(self):
        """Sanity check - Last word"""
        #grab last word
        w = self.doc.words(-1) # shortcut for doc.words()[0]
        self.assertTrue( isinstance(w, folia.Word) )
        self.assertEqual( w.id , "example.table.1.w.14" )
        self.assertEqual( w.text() , "University" )
        self.assertEqual( str(w) , "University" )

    def test006_second_sentence(self):
        """Sanity check - Sentence"""
        #grab second sentence
        s = self.doc.sentences(1)
        self.assertTrue( isinstance(s, folia.Sentence) )
        self.assertEqual( s.id, 'WR-P-E-J-0000000001.p.1.s.1' )
        self.assertFalse( s.hastext() )
        self.assertEqual( str(s), "Stemma is een ander woord voor stamboom ." )

    def test006b_sentencetest(self):
        """Sanity check - Sentence text (including retaining tokenisation)"""
        #grab second sentence
        s = self.doc['WR-P-E-J-0000000001.p.1.s.5']
        self.assertTrue( isinstance(s, folia.Sentence) )
        self.assertFalse( s.hastext() )
        self.assertEqual( s.text(), "De andere handschriften krijgen ook een letter die verband kan houden met hun plaats van oorsprong óf plaats van bewaring.")
        self.assertEqual( s.text('current',True), "De andere handschriften krijgen ook een letter die verband kan houden met hun plaats van oorsprong óf plaats van bewaring .") #not detokenised
        self.assertEqual( s.toktext(), "De andere handschriften krijgen ook een letter die verband kan houden met hun plaats van oorsprong óf plaats van bewaring .") #just an alias for the above

    def test007_index(self):
        """Sanity check - Index"""
        #grab something using the index
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7']
        self.assertTrue( isinstance(w, folia.Word) )
        self.assertEqual( self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7'] , self.doc.index['WR-P-E-J-0000000001.p.1.s.2.w.7'] )
        self.assertEqual( w.id , 'WR-P-E-J-0000000001.p.1.s.2.w.7' )
        self.assertEqual( w.text() , "stamboom" )

    def test008_division(self):
        """Sanity check - Division + head"""

        #grab something using the index
        div = self.doc['WR-P-E-J-0000000001.div0.1']
        self.assertTrue( isinstance(div, folia.Division) )
        self.assertEqual( div.head() , self.doc['WR-P-E-J-0000000001.head.1'] )
        self.assertEqual( len(div.head()) ,1 ) #Head contains one element (one sentence)

    def test009_pos(self):
        """Sanity check - Token Annotation - Pos"""
        #grab first word
        w = self.doc.words(0)


        self.assertEqual( w.annotation(folia.PosAnnotation), next(w.select(folia.PosAnnotation)) ) #w.annotation() selects the single first annotation of that type, select is the generic method to retrieve pretty much everything
        self.assertTrue( isinstance(w.annotation(folia.PosAnnotation), folia.PosAnnotation) )
        self.assertTrue( issubclass(folia.PosAnnotation, folia.AbstractTokenAnnotation) )

        self.assertEqual( w.annotation(folia.PosAnnotation).cls, 'N(soort,ev,basis,onz,stan)' ) #cls is used everywhere instead of class, since class is a reserved keyword in python
        self.assertEqual( w.pos(),'N(soort,ev,basis,onz,stan)' ) #w.pos() is just a direct shortcut for getting the class
        self.assertEqual( w.annotation(folia.PosAnnotation).set, 'cgn-combinedtags' )
        self.assertEqual( w.annotation(folia.PosAnnotation).annotator, 'tadpole' )
        self.assertEqual( w.annotation(folia.PosAnnotation).annotatortype, folia.AnnotatorType.AUTO )


    def test010_lemma(self):
        """Sanity check - Token Annotation - Lemma"""
        #grab first word
        w = self.doc.words(0)

        self.assertEqual( w.annotation(folia.LemmaAnnotation), w.annotation(folia.LemmaAnnotation) ) #w.lemma() is just a shortcut
        self.assertEqual( w.annotation(folia.LemmaAnnotation), next(w.select(folia.LemmaAnnotation)) ) #w.annotation() selects the single first annotation of that type, select is the generic method to retrieve pretty much everything
        self.assertTrue( isinstance(w.annotation(folia.LemmaAnnotation), folia.LemmaAnnotation))

        self.assertEqual( w.annotation(folia.LemmaAnnotation).cls, 'stemma' )
        self.assertEqual( w.lemma(),'stemma' ) #w.lemma() is just a direct shortcut for getting the class
        self.assertEqual( w.annotation(folia.LemmaAnnotation).set, 'lemmas-nl' )
        self.assertEqual( w.annotation(folia.LemmaAnnotation).annotator, 'tadpole' )
        self.assertEqual( w.annotation(folia.LemmaAnnotation).annotatortype, folia.AnnotatorType.AUTO )

    def test011_tokenannot_notexist(self):
        """Sanity check - Token Annotation - Non-existing element"""
        #grab first word
        w = self.doc.words(0)

        self.assertEqual( w.count(folia.SenseAnnotation), 0)  #list
        self.assertRaises( folia.NoSuchAnnotation, w.annotation, folia.SenseAnnotation) #exception



    def test012_correction(self):
        """Sanity check - Correction - Text"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.6.w.31']
        c = w.annotation(folia.Correction)

        self.assertEqual( len(list(c.new())), 1)
        self.assertEqual( len(list(c.original())), 1)

        self.assertEqual( w.text(), 'vierkante')
        self.assertEqual( c.new(0), 'vierkante')
        self.assertEqual( c.original(0) , 'vierkant')

    def test013_correction(self):
        """Sanity check - Correction - Token Annotation"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.6.w.32']
        c = w.annotation(folia.Correction)

        self.assertEqual( len(list(c.new())), 1)
        self.assertEqual( len(list(c.original())), 1)

        self.assertEqual( w.annotation(folia.LemmaAnnotation).cls , 'haak')
        self.assertEqual( c.new(0).cls, 'haak')
        self.assertEqual( c.original(0).cls, 'haaak')


    def test014_correction(self):
        """Sanity check - Correction - Suggestions (text)"""
        #grab first word
        w = self.doc['WR-P-E-J-0000000001.p.1.s.8.w.14']
        c = w.annotation(folia.Correction)
        self.assertTrue( isinstance(c, folia.Correction) )
        self.assertEqual( len(list(c.suggestions())), 2 )
        self.assertEqual( str(c.suggestions(0).text()), 'twijfelachtige' )
        self.assertEqual( str(c.suggestions(1).text()), 'ongewisse' )

    def test015_parenttest(self):
        """Sanity check - Checking if all elements know who's their daddy"""

        def check(parent, indent = ''):

            for child in parent:
                if isinstance(child, folia.AbstractElement) and not (isinstance(parent, folia.AbstractSpanAnnotation) and (isinstance(child, folia.Word) or isinstance(child, folia.Morpheme))): #words and morphemes are exempted in abstractspanannotation
                    #print indent + repr(child), child.id, child.cls
                    self.assertTrue( child.parent is parent)
                    check(child, indent + '  ')
            return True

        self.assertTrue( check(self.doc.data[0],'  ') )

    def test016a_description(self):
        """Sanity Check - Description"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.1.w.6']
        self.assertEqual( w.description(), 'Dit woordje is een voorzetsel, het is maar dat je het weet...')

    def test016b_description(self):
        """Sanity Check - Error on non-existing description"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.1.w.7']
        self.assertRaises( folia.NoSuchAnnotation,  w.description)

    def test017_gap(self):
        """Sanity Check - Gap"""
        gap = self.doc["WR-P-E-J-0000000001.gap.1"]
        self.assertEqual( gap.content().strip()[:11], 'De tekst is')
        self.assertEqual( gap.cls, 'backmatter')
        self.assertEqual( gap.description(), 'Backmatter')

    def test018_subtokenannot(self):
        """Sanity Check - Subtoken annotation (part of speech)"""
        w= self.doc['WR-P-E-J-0000000001.p.1.s.2.w.5']
        p = w.annotation(folia.PosAnnotation)
        self.assertEqual( p.feat('role'), 'pv' )
        self.assertEqual( p.feat('tense'), 'tgw' )
        self.assertEqual( p.feat('form'), 'met-t' )

    def test019_alignment(self):
        """Sanity Check - Alignment in same document"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.3.w.10']
        a = w.annotation(folia.Alignment)
        target = next(a.resolve())
        self.assertEqual( target, self.doc['WR-P-E-J-0000000001.p.1.s.3.w.5'] )



    def test020a_spanannotation(self):
        """Sanity Check - Span Annotation (Syntax)"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.1']
        l = s.annotation(folia.SyntaxLayer)

        self.assertTrue( isinstance(l[0], folia.SyntacticUnit ) )
        self.assertEqual( l[0].cls,  'sentence' )
        self.assertEqual( l[0][0].cls,  'subject' )
        self.assertEqual( l[0][0].text(),  'Stemma' )
        self.assertEqual( l[0][1].cls,  'verb' )
        self.assertEqual( l[0][2].cls,  'predicate' )
        self.assertEqual( l[0][2][0].cls,  'np' )
        self.assertEqual( l[0][2][1].cls,  'pp' )
        self.assertEqual( l[0][2][1].text(),  'voor stamboom' )
        self.assertEqual( l[0][2].text(),  'een ander woord voor stamboom' )

    def test020b_spanannotation(self):
        """Sanity Check - Span Annotation (Chunking)"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.1']
        l = s.annotation(folia.ChunkingLayer)

        self.assertTrue( isinstance(l[0], folia.Chunk ) )
        self.assertEqual( l[0].text(),  'een ander woord' )
        self.assertEqual( l[1].text(),  'voor stamboom' )

    def test020c_spanannotation(self):
        """Sanity Check - Span Annotation (Entities)"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.1']
        l = s.annotation(folia.EntitiesLayer)

        self.assertTrue( isinstance(l[0], folia.Entity) )
        self.assertEqual( l[0].text(),  'ander woord' )


    def test020d_spanannotation(self):
        """Sanity Check - Span Annotation (Dependencies)"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.1']
        l = s.annotation(folia.DependenciesLayer)

        self.assertTrue( isinstance(l[0], folia.Dependency) )
        self.assertEqual( l[0].head().text(),  'is' )
        self.assertEqual( l[0].dependent().text(),  'Stemma' )
        self.assertEqual( l[0].cls,  'su' )

        self.assertTrue( isinstance(l[1], folia.Dependency) )
        self.assertEqual( l[1].head().text(),  'is' )
        self.assertEqual( l[1].dependent().text(),  'woord' )
        self.assertEqual( l[1].cls,'predc' )

        self.assertTrue( isinstance(l[2], folia.Dependency) )
        self.assertEqual( l[2].head().text(),  'woord' )
        self.assertEqual( l[2].dependent().text(),  'een' )
        self.assertEqual( l[2].cls,'det' )

        self.assertTrue( isinstance(l[3], folia.Dependency) )
        self.assertEqual( l[3].head().text(),  'woord' )
        self.assertEqual( l[3].dependent().text(),  'ander' )
        self.assertEqual( l[3].cls,'mod' )

        self.assertTrue( isinstance(l[4], folia.Dependency) )
        self.assertEqual( l[4].head().text(),  'woord' )
        self.assertEqual( l[4].dependent().text(),  'voor' )
        self.assertEqual( l[4].cls,'mod' )

        self.assertTrue( isinstance(l[5], folia.Dependency) )
        self.assertEqual( l[5].head().text(),  'voor' )
        self.assertEqual( l[5].dependent().text(),  'stamboom' )
        self.assertEqual( l[5].cls,'obj1' )

    def test020e_spanannotation(self):
        """Sanity Check - Span Annotation (Timedevent)"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.1']
        l = s.annotation(folia.TimingLayer)

        self.assertTrue( isinstance(l[0], folia.TimeSegment ) )
        self.assertEqual( l[0].text(),  'een ander woord' )
        self.assertEqual( l[1].cls, 'cough' )
        self.assertEqual( l[2].text(),  'voor stamboom' )

    def test020f_spanannotation(self):
        """Sanity Check - Co-Reference"""
        div = self.doc["WR-P-E-J-0000000001.div0.1"]
        deplayer = div.annotation(folia.DependenciesLayer)
        deps = list(deplayer.annotations(folia.Dependency))

        self.assertEqual( deps[0].cls,  'su' )
        self.assertEqual( deps[1].cls,  'predc' )
        self.assertEqual( deps[2].cls,  'det' )
        self.assertEqual( deps[3].cls,  'mod' )
        self.assertEqual( deps[4].cls,  'mod' )
        self.assertEqual( deps[5].cls,  'obj1' )

        self.assertEqual( deps[2].head().wrefs(0), self.doc['WR-P-E-J-0000000001.p.1.s.1.w.5'] )
        self.assertEqual( deps[2].dependent().wrefs(0), self.doc['WR-P-E-J-0000000001.p.1.s.1.w.3'] )


    def test020g_spanannotation(self):
        """Sanity Check - Semantic Role Labelling"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.7']
        semrolelayer = s.annotation(folia.SemanticRolesLayer)
        predicate = semrolelayer.annotation(folia.Predicate)
        self.assertEqual( predicate.cls,  'aanduiden' )

        roles = list(predicate.annotations(folia.SemanticRole))

        self.assertEqual( roles[0].cls,  'actor' )
        self.assertEqual( roles[1].cls,  'patient' )

        self.assertEqual( roles[0].wrefs(0), self.doc['WR-P-E-J-0000000001.p.1.s.7.w.3'] )
        self.assertEqual( roles[1].wrefs(0), self.doc['WR-P-E-J-0000000001.p.1.s.7.w.4'] )
        self.assertEqual( roles[1].wrefs(1), self.doc['WR-P-E-J-0000000001.p.1.s.7.w.5'] )


    def test021_previousword(self):
        """Sanity Check - Obtaining previous word"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7']
        prevw = w.previous()
        self.assertTrue( isinstance(prevw, folia.Word) )
        self.assertEqual( prevw.text(),  "zo'n" )

    def test021b_previousword_noscope(self):
        """Sanity Check - Obtaining previous word without scope constraint"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.4.w.1']
        prevw = w.previous(folia.Word, None)
        self.assertTrue( isinstance(prevw, folia.Word) )
        self.assertEqual( prevw.text(),  "." )

    def test022_nextword(self):
        """Sanity Check - Obtaining next word"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7']
        nextw = w.next()
        self.assertTrue( isinstance(nextw, folia.Word) )
        self.assertEqual( nextw.text(),  "," )

    def test023_leftcontext(self):
        """Sanity Check - Obtaining left context"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7']
        context = w.leftcontext(3)
        self.assertEqual( [ x.text() for x in context ], ['wetenschap','wordt',"zo'n"] )

    def test024_rightcontext(self):
        """Sanity Check - Obtaining right context"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7']
        context = w.rightcontext(3)
        self.assertEqual( [ x.text() for x in context ], [',','onder','de'] )

    def test025_fullcontext(self):
        """Sanity Check - Obtaining full context"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7']
        context = w.context(3)
        self.assertEqual( [ x.text() for x in context ], ['wetenschap','wordt',"zo'n",'stamboom',',','onder','de'] )

    def test026_feature(self):
        """Sanity Check - Features"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.6.w.1']
        pos = w.annotation(folia.PosAnnotation)
        self.assertTrue( isinstance(pos, folia.PosAnnotation) )
        self.assertEqual(pos.cls,'WW(vd,prenom,zonder)')
        self.assertEqual( len(pos),  1)
        features = list(pos.select(folia.Feature))
        self.assertEqual( len(features),  1)
        self.assertTrue( isinstance(features[0], folia.Feature))
        self.assertEqual( features[0].subset, 'head')
        self.assertEqual( features[0].cls, 'WW')

    def test027_datetime(self):
        """Sanity Check - Time stamp"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.8.w.15']

        pos = w.annotation(folia.PosAnnotation)
        self.assertEqual( pos.datetime, datetime(2011, 7, 20, 19, 0, 1) )

        self.assertTrue( xmlcheck(pos.xmlstring(), '<pos xmlns="http://ilk.uvt.nl/folia" class="N(soort,ev,basis,zijd,stan)" datetime="2011-07-20T19:00:01"/>') )

    def test028_wordparents(self):
        """Sanity Check - Finding parents of word"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.8.w.15']

        s = w.sentence()
        self.assertTrue( isinstance(s, folia.Sentence) )
        self.assertEqual( s.id, 'WR-P-E-J-0000000001.p.1.s.8')

        p = w.paragraph()
        self.assertTrue( isinstance(p, folia.Paragraph) )
        self.assertEqual( p.id, 'WR-P-E-J-0000000001.p.1')

        div = w.division()
        self.assertTrue( isinstance(div, folia.Division) )
        self.assertEqual( div.id, 'WR-P-E-J-0000000001.div0.1')

        self.assertEqual( w.incorrection(), None)

    def test0029_quote(self):
        """Sanity Check - Quote"""
        q = self.doc['WR-P-E-J-0000000001.p.1.s.8.q.1']
        self.assertTrue( isinstance(q, folia.Quote) )
        self.assertEqual(q.text(), 'volle lijn')

        s = self.doc['WR-P-E-J-0000000001.p.1.s.8']
        self.assertEqual(s.text(), 'Een volle lijn duidt op een verwantschap , terweil een stippelijn op een onzekere verwantschap duidt .') #(spelling errors are present in sentence)

        #a word from the quote
        w = self.doc['WR-P-E-J-0000000001.p.1.s.8.w.2']
        #check if sentence matches
        self.assertTrue( (w.sentence() is s) )

    def test030_textcontent(self):
        """Sanity check - Text Content"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.4']

        self.assertEqual( s.text(), 'De hoofdletter A wordt gebruikt voor het originele handschrift .')
        self.assertEqual( s.stricttext(), 'De hoofdletter A wordt gebruikt voor het originele handschrift.')
        self.assertEqual( s.textcontent().text(), 'De hoofdletter A wordt gebruikt voor het originele handschrift.')
        self.assertEqual( s.textcontent('original').text(), 'De hoofdletter A wordt gebruikt voor het originele handschrift.')
        self.assertRaises( folia.NoSuchText, s.text, 'BLAH' )


        w = self.doc['WR-P-E-J-0000000001.p.1.s.4.w.2']
        self.assertEqual( w.text(), 'hoofdletter')

        self.assertEqual( w.textcontent().text(), 'hoofdletter')
        self.assertEqual( w.textcontent().offset, 3)

        w2 = self.doc['WR-P-E-J-0000000001.p.1.s.6.w.31']
        self.assertEqual( w2.text(), 'vierkante')
        self.assertEqual( w2.stricttext(), 'vierkante')


    def test030b_textcontent(self):
        """Sanity check - Text Content (2)"""
        s = self.doc['sandbox.3.head']
        t = s.textcontent()
        self.assertEqual( len(t), 3)
        self.assertEqual( t.text(), "De FoLiA developers zijn:")
        self.assertEqual( t[0], "De ")
        self.assertTrue( isinstance(t[1], folia.TextMarkupString) )
        self.assertEqual( t[1].text(), "FoLiA developers")
        self.assertEqual( t[2], " zijn:")


    def test031_sense(self):
        """Sanity Check - Lexical Semantic Sense Annotation"""
        w = self.doc['sandbox.list.1.listitem.1.s.1.w.1']
        sense = w.annotation(folia.SenseAnnotation)

        self.assertEqual( sense.cls , 'some.sense.id')
        self.assertEqual( sense.feat('synset') , 'some.synset.id')

    def test032_event(self):
        """Sanity Check - Events"""
        l= self.doc['sandbox']
        event = l.annotation(folia.Event)

        self.assertEqual( event.cls , 'applause')
        self.assertEqual( event.feat('actor') , 'audience')

    def test033_list(self):
        """Sanity Check - List"""
        l = self.doc['sandbox.list.1']
        self.assertTrue( isinstance( l[0], folia.ListItem) )
        self.assertEqual( l[0].n, '1' ) #testing common n attribute
        self.assertEqual( l[0].text(), 'Eerste testitem')
        self.assertTrue( isinstance( l[-1], folia.ListItem) )
        self.assertEqual( l[1].text(), 'Tweede testitem')
        self.assertEqual( l[1].n, '2' )

    def test034_figure(self):
        """Sanity Check - Figure"""
        fig = self.doc['sandbox.figure.1']
        self.assertEqual( fig.src, "http://upload.wikimedia.org/wikipedia/commons/8/8e/Family_tree.svg")
        self.assertEqual( fig.caption(), 'Een stamboom')

    def test035_event(self):
        """Sanity Check - Event"""
        e = self.doc['sandbox.event.1']
        self.assertEqual( e.feat('actor'), 'proycon')
        self.assertEqual( e.feat('begindatetime'), '2011-12-15T19:01')
        self.assertEqual( e.feat('enddatetime'), '2011-12-15T19:05')

    def test036_parsen(self):
        """Sanity Check - Paragraph and Sentence annotation"""
        p = self.doc['WR-P-E-J-0000000001.p.1']
        self.assertEqual( p.cls, 'firstparagraph' )
        s = self.doc['WR-P-E-J-0000000001.p.1.s.6']
        self.assertEqual( s.cls, 'sentence' )


    def test037a_feat(self):
        """Sanity Check - Feature test (including shortcut)"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
<metadata src="test.cmdi.xml" type="cmdi">
<annotations>
    <pos-annotation set="test"/>
</annotations>
</metadata>
<text xml:id="test.text">
    <div xml:id="div">
    <head xml:id="head">
        <s xml:id="head.1.s.1">
            <w xml:id="head.1.s.1.w.1">
                <t>blah</t>
                <pos class="NN(blah)" head="NN" />
            </w>
        </s>
    </head>
    <p xml:id="p.1">
        <s xml:id="p.1.s.1">
            <w xml:id="p.1.s.1.w.1">
                <t>blah</t>
                <pos class="NN(blah)">
                    <feat subset="head" class="NN" />
                </pos>
            </w>
        </s>
    </p>
    </div>
</text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc['head.1.s.1.w.1'].pos() , 'NN(blah)')
        self.assertEqual( doc['head.1.s.1.w.1'].annotation(folia.PosAnnotation).feat('head') , 'NN')
        self.assertEqual( doc['p.1.s.1.w.1'].pos() , 'NN(blah)')
        self.assertEqual( doc['p.1.s.1.w.1'].annotation(folia.PosAnnotation).feat('head') , 'NN')

    def test037b_multiclassfeat(self):
        """Sanity Check - Multiclass feature"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
<metadata src="test.cmdi.xml" type="cmdi">
<annotations>
    <pos-annotation set="test"/>
</annotations>
</metadata>
<text xml:id="test.text">
    <div xml:id="div">
    <p xml:id="p.1">
        <s xml:id="p.1.s.1">
            <w xml:id="p.1.s.1.w.1">
                <t>blah</t>
                <pos class="NN(a,b,c)">
                    <feat subset="x" class="a" />
                    <feat subset="x" class="b" />
                    <feat subset="x" class="c" />
                </pos>
            </w>
        </s>
    </p>
    </div>
</text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc['p.1.s.1.w.1'].pos() , 'NN(a,b,c)')
        self.assertEqual( doc['p.1.s.1.w.1'].annotation(folia.PosAnnotation).feat('x') , ['a','b','c'] )

    def test038a_morphemeboundary(self):
        """Sanity check - Obtaining annotation should not descend into morphology layer"""
        self.assertRaises( folia.NoSuchAnnotation,  self.doc['WR-P-E-J-0000000001.sandbox.2.s.1.w.2'].annotation , folia.PosAnnotation)

    def test038b_morphemeboundary(self):
        """Sanity check - Obtaining morphemes and token annotation under morphemes"""

        w = self.doc['WR-P-E-J-0000000001.sandbox.2.s.1.w.2']
        l = list(w.morphemes()) #get all morphemes
        self.assertEqual(len(l), 2)
        m = w.morpheme(1) #get second morpheme
        self.assertEqual(m.annotation(folia.PosAnnotation).cls, 'n')

    def test039_findspan(self):
        """Sanity Check - Find span on layer"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.7']
        semrolelayer = s.annotation(folia.SemanticRolesLayer)
        roles = list(semrolelayer.annotations(folia.SemanticRole))
        self.assertEqual(semrolelayer.findspan( self.doc['WR-P-E-J-0000000001.p.1.s.7.w.4'], self.doc['WR-P-E-J-0000000001.p.1.s.7.w.5']), roles[1] )

    def test040_spaniter(self):
        """Sanity Check - Iteration over spans"""
        t = []
        sentence = self.doc["WR-P-E-J-0000000001.p.1.s.1"]
        for layer in sentence.select(folia.EntitiesLayer):
            for entity in layer.select(folia.Entity):
                for word in entity.wrefs():
                    t.append(word.text())
        self.assertEqual(t, ['ander','woord'])

    def test041_findspans(self):
        """Sanity check - Find spans given words (no set)"""
        t = []
        word = self.doc["WR-P-E-J-0000000001.p.1.s.1.w.4"]
        for entity in word.findspans(folia.EntitiesLayer):
            for word in entity.wrefs():
                t.append(word.text())
        self.assertEqual(t, ['ander','woord'])

    def test041b_findspans(self):
        """Sanity check - Find spans given words (specific set)"""
        t = []
        word = self.doc["example.table.1.w.3"]
        for entity in word.findspans(folia.EntitiesLayer, "http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml"):
            for word in entity.wrefs():
                t.append(word.text())
        self.assertEqual(t, ['Maarten','van','Gompel'])

    def test041c_findspans(self):
        """Sanity check - Find spans given words (specific set, by SpanAnnotation class)"""
        t = []
        word = self.doc["example.table.1.w.3"]
        for entity in word.findspans(folia.Entity, "http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml"):
            for word in entity.wrefs():
                t.append(word.text())
        self.assertEqual(t, ['Maarten','van','Gompel'])

    def test042_table(self):
        """Sanity check - Table"""
        table = self.doc["example.table.1"]
        self.assertTrue( isinstance(table, folia.Table))
        self.assertTrue( isinstance(table[0], folia.TableHead))
        self.assertTrue( isinstance(table[0][0], folia.Row))
        self.assertEqual( len(table[0][0]), 2) #two cells
        self.assertTrue( isinstance(table[0][0][0], folia.Cell))
        self.assertEqual( table[0][0][0].text(), "Naam" )
        self.assertEqual( table[0][0].text(), "Naam | Universiteit" ) #text of whole row


    def test043_string(self):
        """Sanity check - String"""
        s = self.doc["sandbox.3.head"]
        self.assertTrue( s.hasannotation(folia.String) )
        st = next(s.select(folia.String))
        self.assertEqual( st.text(), "FoLiA developers")
        self.assertEqual( st.annotation(folia.LangAnnotation).cls, "eng")

    def test044_textmarkup(self):
        """Sanity check - Text Markup"""
        s = self.doc["sandbox.3.head"]
        t = s.textcontent()
        self.assertEqual( s.count(folia.TextMarkupString), 1)
        self.assertEqual( t.count(folia.TextMarkupString), 1)

        st = next(t.select(folia.TextMarkupString))
        self.assertEqual( st.text(), "FoLiA developers" ) #testing value (full text value)

        self.assertEqual( st.resolve(), self.doc['sandbox.3.str']) #testing resolving references


        self.assertTrue( isinstance( self.doc['WR-P-E-J-0000000001.p.1.s.6'].textcontent()[-1], folia.Linebreak) )  #did we get the linebreak properly?

        #testing nesting
        self.assertEqual( len(st), 2)
        self.assertEqual( st[0], self.doc['sandbox.3.str.bold'])

        #testing TextMarkup.text()
        self.assertEqual( st[0].text(), 'FoLiA' )

        #resolving returns self if it's not a reference
        self.assertEqual( self.doc['sandbox.3.str.bold'].resolve(), self.doc['sandbox.3.str.bold'])


    def test045_spancorrection(self):
        """Sanity Check - Corrections over span elements"""
        s = self.doc['example.last.cell']
        entities = list(s.select(folia.Entity,set="http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml"))
        self.assertEqual( len(entities),1 )
        self.assertEqual( entities[0].id , "example.tilburg.university.org" )


    def test046_entry(self):
        """Sanity Check - Checking entry, term, definition and example"""
        entry = self.doc['entry.1']
        terms = list(entry.select(folia.Term))
        self.assertEqual( len(terms),1 )
        self.assertEqual( terms[0].text() ,"Stemma" )
        definitions = list(entry.select(folia.Definition))
        self.assertEqual( len(definitions),2 )
        examples = list(entry.select(folia.Example))
        self.assertEqual( len(examples),1 )

    def test046a_text(self):
        """Sanity Check - Text serialisation test with linebreaks and whitespaces"""
        p = self.doc['WR-P-E-J-0000000001.p.1'] #this is a bit of a malformed paragraph due to the explicit whitespace and linebreaks in it, but makes for a nice test:
        self.assertEqual( p.text(), "Stemma is een ander woord voor stamboom . In de historische wetenschap wordt zo'n stamboom , onder de naam stemma codicum ( handschriftelijke genealogie ) , gebruikt om de verwantschap tussen handschriften weer te geven . \n\nWerkwijze\n\nHiervoor worden de handschriften genummerd en gedateerd zodat ze op de juiste plaats van hun afstammingsgeschiedenis geplaatst kunnen worden . De hoofdletter A wordt gebruikt voor het originele handschrift . De andere handschriften krijgen ook een letter die verband kan houden met hun plaats van oorsprong óf plaats van bewaring. Verdwenen handschriften waarvan men toch vermoedt dat ze ooit bestaan hebben worden ook in het stemma opgenomen en worden weergegeven door de laatste letters van het alfabet en worden tussen vierkante haken geplaatst .\nTenslotte gaat men de verwantschap tussen de handschriften aanduiden . Een volle lijn duidt op een verwantschap , terweil een stippelijn op een onzekere verwantschap duidt .")


    def test046b_text(self):
        """Sanity Check - Text serialisation on lists"""
        l = self.doc['sandbox.list.1'] #this is a bit of a malformed paragraph due to the explicit whitespace and linebreaks in it, but makes for a nice test:
        self.assertEqual( l.text(), "Eerste testitem\nTweede testitem")

    def test047_alignment(self):
        """Sanity check - Alignment"""
        word = self.doc['WR-P-E-J-0000000001.p.1.s.3.w.10']
        a = word.annotation(folia.Alignment)
        self.assertEqual( a.cls, "reference")
        aref = next(a.select(folia.AlignReference,ignore=False))
        self.assertEqual( aref.id,"WR-P-E-J-0000000001.p.1.s.3.w.5" )
        self.assertEqual( aref.type, 'w' )
        self.assertEqual( aref.t,"handschriften" )

    def test048_observations(self):
        """Sanity check - Observations"""
        word = self.doc['WR-P-E-J-0000000001.p.1.s.8.w.9']
        observation = list(word.findspans(folia.ObservationLayer))[0]
        self.assertEqual( observation.cls , "ei_ij_error")
        self.assertEqual( observation.description() , "Confusion between EI and IJ diphtongues")

    def test049_sentiment(self):
        """Sanity check - Sentiments"""
        sentence = self.doc['WR-P-E-J-0000000001.sandbox.2.s.3']
        sentiments = sentence.annotation(folia.SentimentLayer)
        sentiment = sentiments.annotation(folia.Sentiment)
        self.assertEqual( sentiment.cls , "disappointment")
        self.assertEqual( sentiment.feat('polarity') , "negative")
        self.assertEqual( sentiment.feat('strength') , "strong")
        self.assertEqual( sentiment.annotation(folia.Source).text(), "Hij")
        self.assertEqual( sentiment.annotation(folia.Headspan).text(), "erg teleurgesteld")

    def test050_statement(self):
        """Sanity check - Statements"""
        sentence = self.doc['WR-P-E-J-0000000001.sandbox.2.s.2']
        sentiments = sentence.annotation(folia.StatementLayer)
        sentiment = sentiments.annotation(folia.Statement)
        self.assertEqual( sentiment.cls , "promise")
        self.assertEqual( sentiment.annotation(folia.Source).text(), "Hij")
        self.assertEqual( sentiment.annotation(folia.Relation).text(), "had beloofd")
        self.assertEqual( sentiment.annotation(folia.Headspan).text(), "hij zou winnen")

    def test099_write(self):
        """Sanity Check - Writing to file"""
        self.doc.save(os.path.join(TMPDIR,'foliasavetest.xml'))

    def test099b_write(self):
        """Sanity Check - Writing to GZ file"""
        self.doc.save(os.path.join(TMPDIR,'foliasavetest.xml.gz'))

    def test099c_write(self):
        """Sanity Check - Writing to BZ2 file"""
        self.doc.save(os.path.join(TMPDIR,'foliasavetest.xml.bz2'))

    def test100a_sanity(self):
        """Sanity Check - A - Checking output file against input (should be equal)"""
        f = io.open(os.path.join(TMPDIR,'foliatest.xml'),'w',encoding='utf-8')
        f.write(FOLIAEXAMPLE)
        f.close()
        self.doc.save(os.path.join(TMPDIR,'foliatest100.xml'))
        self.assertEqual(  folia.Document(file=os.path.join(TMPDIR,'foliatest100.xml'),debug=False), self.doc )

    def test100b_sanity_xmldiff(self):
        """Sanity Check - B - Checking output file against input using xmldiff (should be equal)"""
        f = io.open(os.path.join(TMPDIR,'foliatest.xml'),'w',encoding='utf-8')
        f.write(FOLIAEXAMPLE)
        f.close()
        #use xmldiff to compare the two:
        self.doc.save(os.path.join(TMPDIR,'foliatest100.xml'))
        retcode = os.system('xmldiff -c ' + os.path.join(TMPDIR,'foliatest.xml') + ' ' + os.path.join(TMPDIR,'foliatest100.xml'))
        #retcode = 1 #disabled (memory hog)
        self.assertEqual( retcode, 0)

    def test101a_metadataextref(self):
        """Sanity Check - Metadata external reference (CMDI)"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
<metadata src="test.cmdi.xml" type="cmdi">
<annotations>
    <event-annotation set="test"/>
</annotations>
</metadata>
<text xml:id="test.text" />
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc.metadatatype, folia.MetaDataType.CMDI )
        self.assertEqual( doc.metadatafile, 'test.cmdi.xml' )

    def test101b_metadataextref2(self):
        """Sanity Check - Metadata external reference (IMDI)"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
<metadata src="test.imdi.xml" type="imdi">
<annotations>
    <event-annotation set="test"/>
</annotations>
</metadata>
<text xml:id="test.text" />
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc.metadatatype, folia.MetaDataType.IMDI )
        self.assertEqual( doc.metadatafile, 'test.imdi.xml' )

    def test101c_metadatainternal(self):
        """Sanity Check - Metadata internal (foreign data) (Dublin Core)"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
<metadata type="dc">
  <annotations>
  </annotations>
  <foreign-data xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier>mydoc</dc:identifier>
    <dc:format>text/xml</dc:format>
    <dc:type>Example</dc:type>
    <dc:contributor>proycon</dc:contributor>
    <dc:creator>proycon</dc:creator>
    <dc:language>en</dc:language>
    <dc:publisher>Radboud University</dc:publisher>
    <dc:rights>public Domain</dc:rights>
  </foreign-data>
</metadata>
<text xml:id="test.text" />
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc.metadatatype, "dc" )
        self.assertEqual( doc.metadata.node.xpath('//dc:creator', namespaces={'dc':'http://purl.org/dc/elements/1.1/'})[0].text , 'proycon' )
        xmlcheck(doc.xmlstring(), xml)

    def test101d_metadatainternal(self):
        """Sanity Check - Metadata internal (double)"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
<metadata type="dc">
  <annotations>
  </annotations>
  <foreign-data xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier>mydoc</dc:identifier>
    <dc:format>text/xml</dc:format>
    <dc:type>Example</dc:type>
    <dc:contributor>proycon</dc:contributor>
    <dc:creator>proycon</dc:creator>
    <dc:language>en</dc:language>
    <dc:publisher>Radboud University</dc:publisher>
  </foreign-data>
  <foreign-data xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:rights>public Domain</dc:rights>
  </foreign-data>
</metadata>
<text xml:id="test.text" />
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc.metadatatype, "dc" )
        self.assertEqual( doc.metadata.node.xpath('//dc:creator', namespaces={'dc':'http://purl.org/dc/elements/1.1/'})[0].text , 'proycon' )
        xmlcheck(doc.xmlstring(), xml)

    def test102a_declarations(self):
        """Sanity Check - Declarations - Default set"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
      <gap-annotation annotator="sloot" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( next(doc['example.text.1'].select(folia.Gap)).set, 'gap-set' )


    def test102a2_declarations(self):
        """Sanity Check - Declarations - Default set, no further defaults"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
      <gap-annotation set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" annotator="proycon" annotatortype="manual" />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( next(doc['example.text.1'].select(folia.Gap)).set, 'gap-set' )
        self.assertEqual( next(doc['example.text.1'].select(folia.Gap)).annotator, 'proycon' )
        self.assertEqual( next(doc['example.text.1'].select(folia.Gap)).annotatortype, folia.AnnotatorType.MANUAL)

    def test102b_declarations(self):
        """Sanity Check - Declarations - Set mismatching """
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
      <gap-annotation annotator="sloot" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" set="extended-gap-set" />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        self.assertRaises( ValueError,  folia.Document, string=xml)


    def test102c_declarations(self):
        """Sanity Check - Declarations - Multiple sets for the same annotation type"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
      <gap-annotation annotator="sloot" set="extended-gap-set"/>
      <gap-annotation annotator="sloot" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" set="gap-set"/>
    <gap class="Y" set="extended-gap-set"/>
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( next(doc['example.text.1'].select(folia.Gap)).set, 'gap-set' )
        self.assertEqual( list(doc['example.text.1'].select(folia.Gap))[1].set, 'extended-gap-set' )

    def test102d1_declarations(self):
        """Sanity Check - Declarations - Multiple sets for the same annotation type (testing failure)"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
      <gap-annotation annotator="sloot" set="extended-gap-set"/>
      <gap-annotation annotator="sloot" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" set="gap-set"/>
    <gap class="Y" />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        self.assertRaises(ValueError,  folia.Document, string=xml )





    def test102d2_declarations(self):
        """Sanity Check - Declarations - Multiple sets for the same annotation type (testing failure)"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
      <gap-annotation annotator="sloot" set="extended-gap-set"/>
      <gap-annotation annotator="sloot" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" set="gap-set"/>
    <gap class="Y" set="gip-set"/>
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        self.assertRaises(ValueError,  folia.Document, string=xml )

    def test102d3_declarations(self):
        """Sanity Check - Declarations - Ignore Duplicates"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
      <gap-annotation annotator="sloot" set="gap-set"/>
      <gap-annotation annotator="sloot" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" set="gap-set"/>
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)

        doc = folia.Document(string=xml)
        self.assertEqual( doc.defaultset(folia.AnnotationType.GAP), 'gap-set' )
        self.assertEqual( doc.defaultannotator(folia.AnnotationType.GAP), "sloot" )


    def test102e_declarations(self):
        """Sanity Check - Declarations - Missing declaration"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" set="extended-gap-set" />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        self.assertRaises( ValueError,  folia.Document, string=xml)

    def test102f_declarations(self):
        """Sanity Check - Declarations - Declaration not needed"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)


    def test102g_declarations(self):
        """Sanity Check - Declarations - 'Undefined' set in declaration"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
        <gap-annotation annotator="sloot" />
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X"  />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( next(doc['example.text.1'].select(folia.Gap)).set, 'undefined' )

    def test102h_declarations(self):
        """Sanity Check - Declarations - Double ambiguous declarations unset default"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
         <gap-annotation annotator="sloot" set="gap-set"/>
         <gap-annotation annotator="proycon" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertRaises(folia.NoDefaultError, doc.defaultannotator, folia.AnnotationType.GAP)


    def test102i_declarations(self):
        """Sanity Check - Declarations - miscellanious trouble"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
         <gap-annotation annotator="sloot" set="gap1-set"/>
         <gap-annotation annotator="sloot" set="gap2-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" set="gap1-set"/>
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc.defaultannotator(folia.AnnotationType.GAP,"gap1-set"), "sloot" )
        doc.declare(folia.AnnotationType.GAP, "gap1-set", annotator='proycon' ) #slightly different behaviour from libfolia: here this overrides the earlier default
        self.assertEqual( doc.defaultannotator(folia.AnnotationType.GAP,"gap1-set"), "proycon" )
        self.assertEqual( doc.defaultannotator(folia.AnnotationType.GAP,"gap2-set"), "sloot" )

        text = doc["example.text.1"]
        text.append( folia.Gap(doc, set='gap1-set', cls='Y', annotator='proycon') )
        text.append( folia.Gap(doc, set='gap1-set', cls='Z1' ) )
        text.append( folia.Gap(doc, set='gap2-set', cls='Z2' ) )
        text.append( folia.Gap(doc, set='gap2-set', cls='Y2', annotator='onbekend' ) )
        gaps = list(text.select(folia.Gap))
        self.assertTrue( xmlcheck(gaps[0].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" annotator="sloot" class="X" set="gap1-set"/>' ) )
        self.assertTrue( xmlcheck(gaps[1].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" class="Y" set="gap1-set"/>') )
        self.assertTrue( xmlcheck(gaps[2].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" class="Z1" set="gap1-set"/>') )
        self.assertTrue( xmlcheck(gaps[3].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" class="Z2" set="gap2-set"/>') )
        self.assertTrue( xmlcheck(gaps[4].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" annotator="onbekend" class="Y2" set="gap2-set"/>') )


    def test102j_declarations(self):
        """Sanity Check - Declarations - Adding a declaration in other set."""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
         <gap-annotation annotator="sloot" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        text = doc["example.text.1"]
        doc.declare(folia.AnnotationType.GAP, "other-set", annotator='proycon' )
        text.append( folia.Gap(doc, set='other-set', cls='Y', annotator='proycon') )
        text.append( folia.Gap(doc, set='other-set', cls='Z' ) )

        gaps = list(text.select(folia.Gap))
        self.assertEqual( gaps[0].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" class="X" set="gap-set"/>' )
        self.assertEqual( gaps[1].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" class="Y" set="other-set"/>' )
        self.assertEqual( gaps[2].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" class="Z" set="other-set"/>' )


    def test102k_declarations(self):
        """Sanity Check - Declarations - Several annotator types."""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
         <gap-annotation annotatortype="auto" set="gap-set"/>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc.defaultannotatortype(folia.AnnotationType.GAP, 'gap-set'),  folia.AnnotatorType.AUTO)
        text = doc["example.text.1"]
        gaps = list(text.select(folia.Gap))
        self.assertTrue( xmlcheck(gaps[0].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" class="X"/>' ) )

        doc.declare(folia.AnnotationType.GAP, "gap-set", annotatortype=folia.AnnotatorType.MANUAL )
        self.assertEqual( doc.defaultannotatortype(folia.AnnotationType.GAP), folia.AnnotatorType.MANUAL )
        self.assertRaises( ValueError, folia.Gap, doc, set='gap-set', cls='Y', annotatortype='unknown' )

        text.append( folia.Gap(doc, set='gap-set', cls='Y', annotatortype='manual' ) )
        text.append( folia.Gap(doc, set='gap-set', cls='Z', annotatortype='auto' ) )

        gaps = list(text.select(folia.Gap))
        self.assertTrue( xmlcheck(gaps[0].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" annotatortype="auto" class="X" />') )
        self.assertTrue( xmlcheck(gaps[1].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" class="Y" />') )
        self.assertTrue( xmlcheck(gaps[2].xmlstring(), '<gap xmlns="http://ilk.uvt.nl/folia" annotatortype="auto" class="Z" />') )



    def test102l_declarations(self):
        """Sanity Check - Declarations - Datetime default."""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
         <gap-annotation set="gap-set" datetime="2011-12-15T19:00" />
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <gap class="X" />
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertEqual( doc.defaultdatetime(folia.AnnotationType.GAP, 'gap-set'),  folia.parse_datetime('2011-12-15T19:00') )

        self.assertEqual( next(doc["example.text.1"].select(folia.Gap)).datetime ,  folia.parse_datetime('2011-12-15T19:00') )





    def test103_namespaces(self):
        """Sanity Check - Alien namespaces - Checking whether properly ignored"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://ilk.uvt.nl/folia" xmlns:alien="http://somewhere.else" xml:id="example" generator="{generator}" version="{version}">
  <metadata type="native">
    <annotations>
    </annotations>
  </metadata>
  <text xml:id="example.text.1">
    <s xml:id="example.text.1.s.1">
        <alien:blah>
            <w xml:id="example.text.1.s.1.alienword">
                <t>blah</t>
            </w>
        </alien:blah>
        <w xml:id="example.text.1.s.1.w.1">
            <t>word</t>
            <alien:invasion number="99999" />
        </w>
    </s>
  </text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertTrue( len(list(doc['example.text.1.s.1'].words())) == 1 ) #second word is in alien namespace, not read
        self.assertRaises( KeyError,  doc.__getitem__, 'example.text.1.s.1.alienword') #doesn't exist


    def test104_speech(self):
        """Sanity Check - Speech data (without attributes)"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
        <utterance-annotation set="utterances" />
    </annotations>
  </metadata>
  <speech xml:id="example.speech">
    <utt xml:id="example.speech.utt.1">
        <ph>həlˈəʊ wˈɜːld</ph>
    </utt>
    <utt xml:id="example.speech.utt.2">
        <w xml:id="example.speech.utt.2.w.1">
          <ph>həlˈəʊ</ph>
        </w>
        <w xml:id="example.speech.utt.2.w.2">
           <ph>wˈɜːld</ph>
        </w>
    </utt>
  </speech>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertTrue( isinstance(doc.data[0], folia.Speech) )
        self.assertTrue( isinstance(doc['example.speech.utt.1'], folia.Utterance) )
        self.assertEqual( doc['example.speech.utt.1'].phon(), "həlˈəʊ wˈɜːld" )
        self.assertRaises( folia.NoSuchText,  doc['example.speech.utt.1'].text) #doesn't exist
        self.assertEqual( doc['example.speech.utt.2'].phon(), "həlˈəʊ wˈɜːld" )


    def test104b_speech(self):
        """Sanity Check - Speech data with speech attributes"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
  <metadata type="native">
    <annotations>
        <utterance-annotation set="utterances" />
    </annotations>
  </metadata>
  <speech xml:id="example.speech" src="helloworld.ogg" speaker="proycon">
    <utt xml:id="example.speech.utt.1" begintime="00:00:00" endtime="00:00:02.012">
        <ph>həlˈəʊ wˈɜːld</ph>
    </utt>
    <utt xml:id="example.speech.utt.2">
        <w xml:id="example.speech.utt.2.w.1" begintime="00:00:00" endtime="00:00:01">
          <ph>həlˈəʊ</ph>
        </w>
        <w xml:id="example.speech.utt.2.w.2" begintime="00:00:01.267" endtime="00:00:02.012">
           <ph>wˈɜːld</ph>
        </w>
    </utt>
  </speech>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertTrue( isinstance(doc.data[0], folia.Speech) )
        self.assertTrue( isinstance(doc['example.speech.utt.1'], folia.Utterance) )
        self.assertEqual( doc['example.speech.utt.1'].phon(), "həlˈəʊ wˈɜːld" )
        self.assertRaises( folia.NoSuchText,  doc['example.speech.utt.1'].text) #doesn't exist
        self.assertEqual( doc['example.speech.utt.2'].phon(), "həlˈəʊ wˈɜːld" )
        self.assertEqual( doc['example.speech'].speech_speaker(), "proycon" )
        self.assertEqual( doc['example.speech'].speech_src(), "helloworld.ogg" )
        self.assertEqual( doc['example.speech.utt.1'].begintime, (0,0,0,0) )
        self.assertEqual( doc['example.speech.utt.1'].endtime, (0,0,2,12) )
        #testing inheritance
        self.assertEqual( doc['example.speech.utt.2.w.2'].speech_speaker(), "proycon" )
        self.assertEqual( doc['example.speech.utt.2.w.2'].speech_src(), "helloworld.ogg" )
        self.assertEqual( doc['example.speech.utt.2.w.2'].begintime, (0,0,1,267) )
        self.assertEqual( doc['example.speech.utt.2.w.2'].endtime, (0,0,2,12) )


    def test104c_speech(self):
        """Sanity Check - Testing serialisation of speech data with speech attributes"""
        speechxml = """<speech xmlns="http://ilk.uvt.nl/folia" xml:id="example.speech" src="helloworld.ogg" speaker="proycon">
        <utt xml:id="example.speech.utt.1" begintime="00:00:00.000" endtime="00:00:02.012">
        <ph>həlˈəʊ wˈɜːld</ph>
    </utt>
    <utt xml:id="example.speech.utt.2">
        <w xml:id="example.speech.utt.2.w.1" begintime="00:00:00.000" endtime="00:00:01.000">
          <ph>həlˈəʊ</ph>
        </w>
        <w xml:id="example.speech.utt.2.w.2" begintime="00:00:01.267" endtime="00:00:02.012">
           <ph>wˈɜːld</ph>
        </w>
    </utt>
  </speech>"""
        xml = """<?xml version="1.0"?>\n
<FoLiA xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://ilk.uvt.nl/folia" xml:id="example" generator="manual" version="0.12">
  <metadata type="native">
    <annotations>
        <utterance-annotation set="utterances" />
    </annotations>
  </metadata>
  %s
</FoLiA>""" % speechxml
        doc = folia.Document(string=xml)
        self.assertTrue( xmlcheck( doc['example.speech'].xmlstring(), u(speechxml)) )

    def test105_complexalignment(self):
        """Sanity Check - Complex alignment"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xlink="http://www.w3.org/1999/xlink" xml:id="test" version="{version}" generator="{generator}">
<metadata type="native">
 <annotations>
    <complexalignment-annotation />
    <alignment-annotation set="blah" />
 </annotations>
</metadata>
<text xml:id="test.text">
    <p xml:id="p.1">
	<s xml:id="p.1.s.1"><t>Dit is een test.</t></s>
	<s xml:id="p.1.s.2"><t>Ik wil kijken of het werkt.</t></s>
	<complexalignments>
	    <complexalignment>
		<alignment>
		    <aref id="p.1.s.1" type="s" />
		    <aref id="p.1.s.2" type="s" />
		</alignment>
		<alignment class="translation" xlink:href="en.folia.xml" xlink:type="simple">
		    <aref id="p.1.s.1" type="s" />
		</alignment>
	    </complexalignment>
	</complexalignments>
    </p>
</text>
</FoLiA>""".format(version=folia.FOLIAVERSION, generator='pynlpl.formats.folia-v' + folia.LIBVERSION)
        doc = folia.Document(string=xml)
        self.assertTrue(doc.xml() is not None) #serialisation check

        l = doc.paragraphs(0).annotation(folia.ComplexAlignmentLayer)
        ca = list(l.annotations(folia.ComplexAlignment))
        self.assertEqual(len(ca),1)
        alignments = list(ca[0].select(folia.Alignment))
        self.assertEqual(len(alignments),2)



class Test4Edit(unittest.TestCase):

    def setUp(self):
        global FOLIAEXAMPLE
        self.doc = folia.Document(string=FOLIAEXAMPLE)

    def test001_addsentence(self):
        """Edit Check - Adding a sentence to first paragraph (verbose)"""

        #grab last paragraph
        p = self.doc.paragraphs(0)

        #how many sentences?
        tmp = len(list(p.sentences()))

        #make a sentence
        s = folia.Sentence(self.doc, generate_id_in=p)
        #add words to the sentence
        s.append( folia.Word(self.doc, text='Dit',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        s.append( folia.Word(self.doc, text='is',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        s.append( folia.Word(self.doc, text='een',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        s.append( folia.Word(self.doc, text='nieuwe',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        s.append( folia.Word(self.doc, text='zin',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO, space=False ) )
        s.append( folia.Word(self.doc, text='.',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )

        #add the sentence
        p.append(s)

        #ID check
        self.assertEqual( s[0].id, s.id + '.w.1' )
        self.assertEqual( s[1].id, s.id + '.w.2' )
        self.assertEqual( s[2].id, s.id + '.w.3' )
        self.assertEqual( s[3].id, s.id + '.w.4' )
        self.assertEqual( s[4].id, s.id + '.w.5' )
        self.assertEqual( s[5].id, s.id + '.w.6' )

        #index check
        self.assertEqual( self.doc[s.id], s )
        self.assertEqual( self.doc[s.id + '.w.3'], s[2] )

        #attribute check
        self.assertEqual( s[0].annotator, 'testscript' )
        self.assertEqual( s[0].annotatortype, folia.AnnotatorType.AUTO )

        #addition to paragraph correct?
        self.assertEqual( len(list(p.sentences())) , tmp + 1)
        self.assertEqual( p[-1] , s)

        # text() ok?
        self.assertEqual( s.text(), "Dit is een nieuwe zin." )

        # xml() ok?
        self.assertTrue( xmlcheck( s.xmlstring(), '<s xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.9"><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.1" annotator="testscript"><t>Dit</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.2" annotator="testscript"><t>is</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.3" annotator="testscript"><t>een</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.4" annotator="testscript"><t>nieuwe</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.5" annotator="testscript" space="no"><t>zin</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.6" annotator="testscript"><t>.</t></w></s>') )

    def test001b_addsentence(self):
        """Edit Check - Adding a sentence to first paragraph (shortcut)"""

        #grab last paragraph
        p = self.doc.paragraphs(0)

        #how many sentences?
        tmp = len(list(p.sentences()))

        s = p.append(folia.Sentence)
        s.append(folia.Word,'Dit')
        s.append(folia.Word,'is')
        s.append(folia.Word,'een')
        s.append(folia.Word,'nieuwe')
        w = s.append(folia.Word,'zin')
        w2 = s.append(folia.Word,'.',cls='PUNCTUATION')

        self.assertEqual( s.id, 'WR-P-E-J-0000000001.p.1.s.9')
        self.assertEqual( len(list(s.words())), 6 ) #number of words in sentence
        self.assertEqual( w.text(), 'zin' ) #text check
        self.assertEqual( self.doc[w.id], w ) #index check

        #addition to paragraph correct?
        self.assertEqual( len(list(p.sentences())) , tmp + 1)
        self.assertEqual( p[-1] , s)

        self.assertTrue( xmlcheck(s.xmlstring(), '<s xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.9"><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.1"><t>Dit</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.2"><t>is</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.3"><t>een</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.4"><t>nieuwe</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.5"><t>zin</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.6" class="PUNCTUATION"><t>.</t></w></s>'))


    def test001c_addsentence(self):
        """Edit Check - Adding a sentence to first paragraph (using add instead of append)"""

        #grab last paragraph
        p = self.doc.paragraphs(0)

        #how many sentences?
        tmp = len(list(p.sentences()))

        s = p.add(folia.Sentence)
        s.add(folia.Word,'Dit')
        s.add(folia.Word,'is')
        s.add(folia.Word,'een')
        s.add(folia.Word,'nieuwe')
        w = s.add(folia.Word,'zin')
        w2 = s.add(folia.Word,'.',cls='PUNCTUATION')

        self.assertEqual( len(list(s.words())), 6 ) #number of words in sentence
        self.assertEqual( w.text(), 'zin' ) #text check
        self.assertEqual( self.doc[w.id], w ) #index check

        #addition to paragraph correct?
        self.assertEqual( len(list(p.sentences())) , tmp + 1)
        self.assertEqual( p[-1] , s)

        self.assertTrue( xmlcheck(s.xmlstring(), '<s xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.9"><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.1"><t>Dit</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.2"><t>is</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.3"><t>een</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.4"><t>nieuwe</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.5"><t>zin</t></w><w xml:id="WR-P-E-J-0000000001.p.1.s.9.w.6" class="PUNCTUATION"><t>.</t></w></s>'))

    def test002_addannotation(self):
        """Edit Check - Adding a token annotation (pos, lemma) (pre-generated instances)"""

        #grab a word (naam)
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.11']

        self.doc.declare(folia.PosAnnotation, 'adhocpos')
        self.doc.declare(folia.LemmaAnnotation, 'adhoclemma')

        #add a pos annotation (in a different set than the one already present, to prevent conflict)
        w.append( folia.PosAnnotation(self.doc, set='adhocpos', cls='NOUN', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        w.append( folia.LemmaAnnotation(self.doc, set='adhoclemma', cls='NAAM', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO, datetime=datetime(1982, 12, 15, 19, 0, 1) ) )

        #retrieve and check
        p = w.annotation(folia.PosAnnotation, 'adhocpos')
        self.assertTrue( isinstance(p, folia.PosAnnotation) )
        self.assertEqual( p.cls, 'NOUN' )

        l = w.annotation(folia.LemmaAnnotation, 'adhoclemma')
        self.assertTrue( isinstance(l, folia.LemmaAnnotation) )
        self.assertEqual( l.cls, 'NAAM' )

        self.assertTrue( xmlcheck(w.xmlstring(), '<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.2.w.11"><t>naam</t><pos class="N(soort,ev,basis,zijd,stan)" set="cgn-combinedtags"/><lemma class="naam" set="lemmas-nl"/><pos class="NOUN" set="adhocpos" annotatortype="auto" annotator="testscript"/><lemma set="adhoclemma" class="NAAM" datetime="1982-12-15T19:00:01" annotatortype="auto" annotator="testscript"/></w>') )

    def test002b_addannotation(self):
        """Edit Check - Adding a token annotation (pos, lemma) (instances generated on the fly)"""

        #grab a word (naam)
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.11']

        self.doc.declare(folia.PosAnnotation, 'adhocpos')
        self.doc.declare(folia.LemmaAnnotation, 'adhoclemma')

        #add a pos annotation (in a different set than the one already present, to prevent conflict)
        w.append( folia.PosAnnotation, set='adhocpos', cls='NOUN', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO)
        w.append( folia.LemmaAnnotation, set='adhoclemma', cls='NAAM', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO )

        #retrieve and check
        p = w.annotation(folia.PosAnnotation, 'adhocpos')
        self.assertTrue( isinstance(p, folia.PosAnnotation) )
        self.assertEqual( p.cls, 'NOUN' )

        l = w.annotation(folia.LemmaAnnotation, 'adhoclemma')
        self.assertTrue( isinstance(l, folia.LemmaAnnotation) )
        self.assertEqual( l.cls, 'NAAM' )

        self.assertTrue( xmlcheck(w.xmlstring(), '<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.2.w.11"><t>naam</t><pos class="N(soort,ev,basis,zijd,stan)" set="cgn-combinedtags"/><lemma class="naam" set="lemmas-nl"/><pos class="NOUN" set="adhocpos" annotatortype="auto" annotator="testscript"/><lemma class="NAAM" set="adhoclemma" annotatortype="auto" annotator="testscript"/></w>'))

    def test002c_addannotation(self):
        """Edit Check - Adding a token annotation (pos, lemma) (using add instead of append)"""

        #grab a word (naam)
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.11']

        self.doc.declare(folia.PosAnnotation, 'adhocpos')
        self.doc.declare(folia.LemmaAnnotation, 'adhoclemma')

        #add a pos annotation (in a different set than the one already present, to prevent conflict)
        w.add( folia.PosAnnotation(self.doc, set='adhocpos', cls='NOUN', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        w.add( folia.LemmaAnnotation(self.doc, set='adhoclemma', cls='NAAM', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO, datetime=datetime(1982, 12, 15, 19, 0, 1) ) )

        #retrieve and check
        p = w.annotation(folia.PosAnnotation, 'adhocpos')
        self.assertTrue( isinstance(p, folia.PosAnnotation) )
        self.assertEqual( p.cls, 'NOUN' )

        l = w.annotation(folia.LemmaAnnotation, 'adhoclemma')
        self.assertTrue( isinstance(l, folia.LemmaAnnotation) )
        self.assertEqual( l.cls, 'NAAM' )

        self.assertTrue( xmlcheck(w.xmlstring(), '<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.2.w.11"><t>naam</t><pos class="N(soort,ev,basis,zijd,stan)" set="cgn-combinedtags"/><lemma class="naam" set="lemmas-nl"/><pos class="NOUN" set="adhocpos" annotatortype="auto" annotator="testscript"/><lemma set="adhoclemma" class="NAAM" datetime="1982-12-15T19:00:01" annotatortype="auto" annotator="testscript"/></w>') )

    def test004_addinvalidannotation(self):
        """Edit Check - Adding a token default-set annotation that clashes with the existing one"""
        #grab a word (naam)
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.11']

        #add a pos annotation without specifying a set (should take default set), but this will clash with existing tag!

        self.assertRaises( folia.DuplicateAnnotationError, w.append, folia.PosAnnotation(self.doc,  cls='N', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        self.assertRaises( folia.DuplicateAnnotationError, w.append, folia.LemmaAnnotation(self.doc, cls='naam', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO ) )

    def test005_addalternative(self):
        """Edit Check - Adding an alternative token annotation"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.11']
        w.append( folia.Alternative(self.doc, generate_id_in=w, contents=folia.PosAnnotation(self.doc, cls='V')))

        #reobtaining it:
        alt = list(w.alternatives()) #all alternatives

        set = self.doc.defaultset(folia.AnnotationType.POS)

        alt2 = list(w.alternatives(folia.PosAnnotation, set))

        self.assertEqual( alt[0],alt2[0] )
        self.assertEqual( len(alt),1 )
        self.assertEqual( len(alt2),1 )
        self.assertTrue( isinstance(alt[0].annotation(folia.PosAnnotation, set), folia.PosAnnotation) )

        self.assertTrue( xmlcheck(w.xmlstring(), '<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.2.w.11"><t>naam</t><pos class="N(soort,ev,basis,zijd,stan)"/><lemma class="naam"/><alt xml:id="WR-P-E-J-0000000001.p.1.s.2.w.11.alt.1" auth="no"><pos class="V"/></alt></w>'))


    def test006_addcorrection(self):
        """Edit Check - Correcting Text"""
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn

        w.correct(new='stippellijn', set='corrections',cls='spelling',annotator='testscript', annotatortype=folia.AnnotatorType.AUTO)
        self.assertEqual( w.annotation(folia.Correction).original(0).text() ,'stippelijn' )
        self.assertEqual( w.annotation(folia.Correction).new(0).text() ,'stippellijn' )
        self.assertEqual( w.text(), 'stippellijn')

        self.assertTrue( xmlcheck(w.xmlstring(),'<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11"><pos class="FOUTN(soort,ev,basis,zijd,stan)"/><lemma class="stippelijn"/><correction xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11.correction.1" class="spelling" annotatortype="auto" annotator="testscript"><new><t>stippellijn</t></new><original auth="no"><t>stippelijn</t></original></correction></w>'))

    def test006b_addcorrection(self):
        """Edit Check - Correcting Text (2)"""
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn

        w.correct(new=folia.TextContent(self.doc,value='stippellijn',set='undefined',cls='current'), set='corrections',cls='spelling',annotator='testscript', annotatortype=folia.AnnotatorType.AUTO)
        self.assertEqual( w.annotation(folia.Correction).original(0).text() ,'stippelijn' )
        self.assertEqual( w.annotation(folia.Correction).new(0).text() ,'stippellijn' )
        self.assertEqual( w.text(), 'stippellijn')

        self.assertTrue( xmlcheck(w.xmlstring(),'<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11"><pos class="FOUTN(soort,ev,basis,zijd,stan)"/><lemma class="stippelijn"/><correction xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11.correction.1" class="spelling" annotatortype="auto" annotator="testscript"><new><t>stippellijn</t></new><original auth="no"><t>stippelijn</t></original></correction></w>'))

    def test007_addcorrection2(self):
        """Edit Check - Correcting a Token Annotation element"""
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn
        oldpos = w.annotation(folia.PosAnnotation)
        newpos = folia.PosAnnotation(self.doc, cls='N(soort,ev,basis,zijd,stan)')
        w.correct(original=oldpos,new=newpos, set='corrections',cls='spelling',annotator='testscript', annotatortype=folia.AnnotatorType.AUTO)

        self.assertEqual( w.annotation(folia.Correction).original(0) ,oldpos )
        self.assertEqual( w.annotation(folia.Correction).new(0),newpos )

        self.assertTrue( xmlcheck(w.xmlstring(),'<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11"><t>stippelijn</t><correction xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11.correction.1" class="spelling" annotatortype="auto" annotator="testscript"><new><pos class="N(soort,ev,basis,zijd,stan)"/></new><original auth="no"><pos class="FOUTN(soort,ev,basis,zijd,stan)"/></original></correction><lemma class="stippelijn"/></w>'))

    def test008_addsuggestion(self):
        """Edit Check - Suggesting a text correction"""
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn
        w.correct(suggestion='stippellijn', set='corrections',cls='spelling',annotator='testscript', annotatortype=folia.AnnotatorType.AUTO)

        self.assertTrue( isinstance(w.annotation(folia.Correction), folia.Correction) )
        self.assertEqual( w.annotation(folia.Correction).suggestions(0).text() , 'stippellijn' )
        self.assertEqual( w.text(), 'stippelijn')

        self.assertTrue( xmlcheck(w.xmlstring(),'<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11"><t>stippelijn</t><pos class="FOUTN(soort,ev,basis,zijd,stan)"/><lemma class="stippelijn"/><correction xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11.correction.1" class="spelling" annotatortype="auto" annotator="testscript"><suggestion auth="no"><t>stippellijn</t></suggestion></correction></w>'))

    def test009a_idclash(self):
        """Edit Check - Checking for exception on adding a duplicate ID"""
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11']

        self.assertRaises( folia.DuplicateIDError,  w.sentence().append, folia.Word, id='WR-P-E-J-0000000001.p.1.s.8.w.11', text='stippellijn')


    #def test009b_textcorrectionlevel(self):
    #    """Edit Check - Checking for exception on an adding TextContent of wrong level"""
    #    w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11']
    #
    #    self.assertRaises(  ValueError, w.append, folia.TextContent, value='blah', corrected=folia.TextCorrectionLevel.ORIGINAL )
    #

    #def test009c_duptextcontent(self):
    #    """Edit Check - Checking for exception on an adding duplicate textcontent"""
    #    w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11']
    #
    #    self.assertRaises(  folia.DuplicateAnnotationError, w.append, folia.TextContent, value='blah', corrected=folia.TextCorrectionLevel.PROCESSED )

    def test010_documentlesselement(self):
        """Edit Check - Creating an initially document-less tokenannotation element and adding it to a word"""

        #not associated with any document yet (first argument is None instead of Document instance)
        pos = folia.PosAnnotation(None, set='fakecgn', cls='N')

        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11']
        w.append(pos)

        self.assertEqual( w.annotation(folia.PosAnnotation,'fakecgn'), pos)
        self.assertEqual( pos.parent, w)
        self.assertEqual( pos.doc, w.doc)

        self.assertTrue( xmlcheck(w.xmlstring(), '<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11"><t>stippelijn</t><pos class="FOUTN(soort,ev,basis,zijd,stan)"/><lemma class="stippelijn"/><pos class="N" set="fakecgn"/></w>'))

    def test011_subtokenannot(self):
        """Edit Check - Adding morphemes"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.5.w.3']
        l = w.append( folia.MorphologyLayer )
        l.append( folia.Morpheme(self.doc, folia.TextContent(self.doc, value='handschrift', offset=0), folia.LemmaAnnotation(self.doc, cls='handschrift'), cls='stem',function='lexical'  ))
        l.append( folia.Morpheme(self.doc, folia.TextContent(self.doc, value='en', offset=11), cls='suffix',function='inflexional' ))


        self.assertEqual( len(l), 2) #two morphemes
        self.assertTrue( isinstance(l[0], folia.Morpheme ) )
        self.assertEqual( l[0].text(), 'handschrift' )
        self.assertEqual( l[0].cls , 'stem' )
        self.assertEqual( l[0].feat('function'), 'lexical' )
        self.assertEqual( l[1].text(), 'en' )
        self.assertEqual( l[1].cls, 'suffix' )
        self.assertEqual( l[1].feat('function'), 'inflexional' )



        self.assertTrue( xmlcheck(w.xmlstring(),'<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.5.w.3"><t>handschriften</t><pos class="N(soort,mv,basis)"/><lemma class="handschrift"/><morphology><morpheme function="lexical" class="stem"><t offset="0">handschrift</t><lemma class="handschrift"/></morpheme><morpheme function="inflexional" class="suffix"><t offset="11">en</t></morpheme></morphology></w>'))

    def test012_alignment(self):
        """Edit Check - Adding Alignment"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.6.w.8']

        a = w.append( folia.Alignment, cls="coreference")
        a.append( folia.AlignReference, id='WR-P-E-J-0000000001.p.1.s.6.w.1', type=folia.Word)
        a.append( folia.AlignReference, id='WR-P-E-J-0000000001.p.1.s.6.w.2', type=folia.Word)

        self.assertEqual( next(a.resolve()), self.doc['WR-P-E-J-0000000001.p.1.s.6.w.1'] )
        self.assertEqual( list(a.resolve())[1], self.doc['WR-P-E-J-0000000001.p.1.s.6.w.2'] )

        self.assertTrue( xmlcheck(w.xmlstring(),'<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.6.w.8"><t>ze</t><pos class="VNW(pers,pron,stan,red,3,mv)"/><lemma class="ze"/><alignment class="coreference"><aref type="w" id="WR-P-E-J-0000000001.p.1.s.6.w.1"/><aref type="w" id="WR-P-E-J-0000000001.p.1.s.6.w.2"/></alignment></w>'))



    def test013_spanannot(self):
        """Edit Check - Adding nested Span Annotatation (syntax)"""

        s = self.doc['WR-P-E-J-0000000001.p.1.s.4']
        #sentence: 'De hoofdletter A wordt gebruikt voor het originele handschrift .'
        layer = s.append(folia.SyntaxLayer)
        layer.append(
            folia.SyntacticUnit(self.doc,cls='s',contents=[
                folia.SyntacticUnit(self.doc,cls='np', contents=[
                    folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.1'] ,cls='det'),
                    folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.2'], cls='n'),
                    folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.3'], cls='n'),
                ]),
                folia.SyntacticUnit(self.doc,cls='vp',contents=[
                    folia.SyntacticUnit(self.doc,cls='vp',contents=[
                        folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.4'], cls='v'),
                        folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.5'], cls='participle'),
                    ]),
                    folia.SyntacticUnit(self.doc, cls='pp',contents=[
                        folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.6'], cls='prep'),
                        folia.SyntacticUnit(self.doc, cls='np',contents=[
                            folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.7'], cls='det'),
                            folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.8'], cls='adj'),
                            folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.9'], cls='n'),
                        ])
                    ])
                ])
            ])
        )

        self.assertTrue( xmlcheck(layer.xmlstring(),'<syntax xmlns="http://ilk.uvt.nl/folia"><su class="s"><su class="np"><su class="det"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.1" t="De"/></su><su class="n"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.2" t="hoofdletter"/></su><su class="n"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.3" t="A"/></su></su><su class="vp"><su class="vp"><su class="v"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.4" t="wordt"/></su><su class="participle"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.5" t="gebruikt"/></su></su><su class="pp"><su class="prep"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.6" t="voor"/></su><su class="np"><su class="det"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.7" t="het"/></su><su class="adj"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.8" t="originele"/></su><su class="n"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.9" t="handschrift"/></su></su></su></su></su></syntax>'))

    def test013a_spanannot(self):
        """Edit Check - Adding Span Annotation (entity, from word using add)"""
        word = self.doc["WR-P-E-J-0000000001.p.1.s.4.w.2"] #hoofdletter
        word2 = self.doc["WR-P-E-J-0000000001.p.1.s.4.w.3"] #A
        entity = word.add(folia.Entity, word, word2, cls="misc",set="http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml")

        self.assertIsInstance(entity, folia.Entity)
        self.assertTrue(xmlcheck(entity.parent.parent.xmlstring(),'<part xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.4.part.1"><w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.1"><t offset="0">De</t><t class="original" offset="0">De</t><pos class="LID(bep,stan,rest)"/><lemma class="de"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.2"><t offset="3">hoofdletter</t><pos class="N(soort,ev,basis,zijd,stan)"/><lemma class="hoofdletter"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.3"><t>A</t><pos class="SPEC(symb)"/><lemma class="_"/></w><entities><entity class="misc" set="http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.2" t="hoofdletter"/><wref id="WR-P-E-J-0000000001.p.1.s.4.w.3" t="A"/></entity></entities></part>'))

    def test013b_spanannot(self):
        """Edit Check - Adding nested Span Annotatation (add as append)"""

        s = self.doc['WR-P-E-J-0000000001.p.1.s.4']
        #sentence: 'De hoofdletter A wordt gebruikt voor het originele handschrift .'
        layer = s.add(folia.SyntaxLayer)
        layer.add(
            folia.SyntacticUnit(self.doc,cls='s',contents=[
                folia.SyntacticUnit(self.doc,cls='np', contents=[
                    folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.1'] ,cls='det'),
                    folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.2'], cls='n'),
                    folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.3'], cls='n'),
                ]),
                folia.SyntacticUnit(self.doc,cls='vp',contents=[
                    folia.SyntacticUnit(self.doc,cls='vp',contents=[
                        folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.4'], cls='v'),
                        folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.5'], cls='participle'),
                    ]),
                    folia.SyntacticUnit(self.doc, cls='pp',contents=[
                        folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.6'], cls='prep'),
                        folia.SyntacticUnit(self.doc, cls='np',contents=[
                            folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.7'], cls='det'),
                            folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.8'], cls='adj'),
                            folia.SyntacticUnit(self.doc, self.doc['WR-P-E-J-0000000001.p.1.s.4.w.9'], cls='n'),
                        ])
                    ])
                ])
            ])
        )

        self.assertTrue( xmlcheck(layer.xmlstring(),'<syntax xmlns="http://ilk.uvt.nl/folia"><su class="s"><su class="np"><su class="det"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.1" t="De"/></su><su class="n"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.2" t="hoofdletter"/></su><su class="n"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.3" t="A"/></su></su><su class="vp"><su class="vp"><su class="v"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.4" t="wordt"/></su><su class="participle"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.5" t="gebruikt"/></su></su><su class="pp"><su class="prep"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.6" t="voor"/></su><su class="np"><su class="det"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.7" t="het"/></su><su class="adj"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.8" t="originele"/></su><su class="n"><wref id="WR-P-E-J-0000000001.p.1.s.4.w.9" t="handschrift"/></su></su></su></su></su></syntax>'))

    def test013c_spanannotcorrection(self):
        """Edit Check - Correcting Span Annotation"""
        s = self.doc['example.cell']
        l = s.annotation(folia.EntitiesLayer)
        l.correct(original=self.doc['example.radboud.university.nijmegen.org'], new=folia.Entity(self.doc, *self.doc['example.radboud.university.nijmegen.org'].wrefs(), cls="loc",set="http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml") ,set='corrections',cls='wrongclass')

        self.assertTrue( xmlcheck(l.xmlstring(), '<entities xmlns="http://ilk.uvt.nl/folia"><correction xml:id="example.cell.correction.1" class="wrongclass"><new><entity class="loc" set="http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml"><wref t="Radboud" id="example.table.1.w.6"/><wref t="University" id="example.table.1.w.7"/><wref t="Nijmegen" id="example.table.1.w.8"/></entity></new><original auth="no"><entity xml:id="example.radboud.university.nijmegen.org" class="org" set="http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml"><wref t="Radboud" id="example.table.1.w.6"/><wref t="University" id="example.table.1.w.7"/><wref t="Nijmegen" id="example.table.1.w.8"/><comment annotator="proycon">This is our university!</comment></entity></original></correction></entities>'))

    def test014_replace(self):
        """Edit Check - Replacing an annotation"""
        word = self.doc['WR-P-E-J-0000000001.p.1.s.3.w.14']
        word.replace(folia.PosAnnotation(self.doc, cls='BOGUS') )

        self.assertEqual( len(list(word.annotations(folia.PosAnnotation))), 1)
        self.assertEqual( word.annotation(folia.PosAnnotation).cls, 'BOGUS')

        self.assertTrue( xmlcheck(word.xmlstring(), '<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.3.w.14"><t>plaats</t><lemma class="plaats"/><pos class="BOGUS"/></w>'))

    def test015_remove(self):
        """Edit Check - Removing an annotation"""
        word = self.doc['WR-P-E-J-0000000001.p.1.s.3.w.14']
        word.remove( word.annotation(folia.PosAnnotation) )

        self.assertRaises( folia.NoSuchAnnotation, word.annotation, folia.PosAnnotation )

        self.assertTrue( xmlcheck(word.xmlstring(), '<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.3.w.14"><t>plaats</t><lemma class="plaats"/></w>'))

    def test016_datetime(self):
        """Edit Check - Time stamp"""
        w = self.doc['WR-P-E-J-0000000001.p.1.s.8.w.16']
        pos = w.annotation(folia.PosAnnotation)
        pos.datetime = datetime(1982, 12, 15, 19, 0, 1) #(the datetime of my joyful birth)

        self.assertTrue( xmlcheck(pos.xmlstring(), '<pos xmlns="http://ilk.uvt.nl/folia" class="WW(pv,tgw,met-t)" datetime="1982-12-15T19:00:01"/>'))

    def test017_wordtext(self):
        """Edit Check - Altering word text"""

        #Important note: directly altering text is usually bad practise, you'll want to use proper corrections instead.
        w = self.doc['WR-P-E-J-0000000001.p.1.s.8.w.9']
        self.assertEqual(w.text(), 'terweil')

        w.settext('terwijl')
        self.assertEqual(w.text(), 'terwijl')

    def test017b_wordtext(self):
        """Edit Check - Altering word text with reserved symbols"""

        #Important note: directly altering text is usually bad practise, you'll want to use proper corrections instead.
        w = self.doc['WR-P-E-J-0000000001.p.1.s.8.w.9']

        w.settext('1 & 1 > 0')
        self.assertEqual(w.text(), '1 & 1 > 0')
        self.assertEqual(w.textcontent().xmlstring(), '<t xmlns="http://ilk.uvt.nl/folia">1 &amp; 1 &gt; 0</t>')

    def test018a_sentencetext(self):
        """Edit Check - Altering sentence text (untokenised by definition)"""
        s = self.doc['WR-P-E-J-0000000001.p.1.s.1']

        self.assertEqual(s.text(), 'Stemma is een ander woord voor stamboom .') #text is obtained from children, since there is no direct text associated

        self.assertFalse(s.hastext()) #no text DIRECTLY associated with the sentence

        #associating text directly with the sentence: de-tokenised by definition!
        s.settext('Stemma is een ander woord voor stamboom.')
        self.assertTrue(s.hastext())
        self.assertEqual(s.text(), 'Stemma is een ander woord voor stamboom .') #text still obtained from children rather than directly associated text!!
        self.assertEqual(s.stricttext(), 'Stemma is een ander woord voor stamboom.')

    def test018b_sentencetext(self):
        """Edit Check - Altering sentence text (untokenised by definition)"""

        s = self.doc['WR-P-E-J-0000000001.p.1.s.8']

        self.assertEqual( s.text(), 'Een volle lijn duidt op een verwantschap , terweil een stippelijn op een onzekere verwantschap duidt .' ) #dynamic from children


        s.settext('Een volle lijn duidt op een verwantschap, terwijl een stippellijn op een onzekere verwantschap duidt.' ) #setting the correct text here will cause a mismatch with the text on deeper levels, but is permitted (deep validation should detect it)

        s.settext('Een volle lijn duidt op een verwantschap, terweil een stippelijn op een onzekere verwantschap duidt.', 'original' )

        self.assertEqual( s.text(), 'Een volle lijn duidt op een verwantschap , terweil een stippelijn op een onzekere verwantschap duidt .' ) #from children by default (child has erroneous stippelijn and terweil)
        self.assertTrue( s.hastext('original') )
        self.assertEqual( s.stricttext('original'), 'Een volle lijn duidt op een verwantschap, terweil een stippelijn op een onzekere verwantschap duidt.' )

        self.assertTrue( xmlcheck(s.xmlstring(), '<s xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.8"><t>Een volle lijn duidt op een verwantschap, terwijl een stippellijn op een onzekere verwantschap duidt.</t><t class="original">Een volle lijn duidt op een verwantschap, terweil een stippelijn op een onzekere verwantschap duidt.</t><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.1"><t>Een</t><pos class="LID(onbep,stan,agr)"/><lemma class="een"/></w><quote xml:id="WR-P-E-J-0000000001.p.1.s.8.q.1"><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.2"><t>volle</t><pos class="ADJ(prenom,basis,met-e,stan)"/><lemma class="vol"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.3"><t>lijn</t><pos class="N(soort,ev,basis,zijd,stan)"/><lemma class="lijn"/></w></quote><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.4"><t>duidt</t><pos class="WW(pv,tgw,met-t)"/><lemma class="duiden"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.5"><t>op</t><pos class="VZ(init)"/><lemma class="op"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.6"><t>een</t><pos class="LID(onbep,stan,agr)"/><lemma class="een"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.7"><t>verwantschap</t><pos class="N(soort,ev,basis,zijd,stan)"/><lemma class="verwantschap"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.8"><t>,</t><pos class="LET()"/><lemma class=","/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.9"><t>terweil</t><errordetection class="spelling"/><pos class="VG(onder)"/><lemma class="terweil"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.10"><t>een</t><pos class="LID(onbep,stan,agr)"/><lemma class="een"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11"><t>stippelijn</t><pos class="FOUTN(soort,ev,basis,zijd,stan)"/><lemma class="stippelijn"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.12"><t>op</t><pos class="VZ(init)"/><lemma class="op"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.13"><t>een</t><pos class="LID(onbep,stan,agr)"/><lemma class="een"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.14"><t>onzekere</t><pos class="ADJ(prenom,basis,met-e,stan)"/><lemma class="onzeker"/><correction xml:id="WR-P-E-J-0000000001.p.1.s.8.w.14.c.1" class="spelling"><suggestion  auth="no" n="1/2"><t>twijfelachtige</t></suggestion><suggestion  auth="no" n="2/2"><t>ongewisse</t></suggestion></correction></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.15"><t>verwantschap</t><pos class="N(soort,ev,basis,zijd,stan)" datetime="2011-07-20T19:00:01"/><lemma class="verwantschap"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.16"><t>duidt</t><pos class="WW(pv,tgw,met-t)"/><lemma class="duiden"/></w><w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.17"><t>.</t><pos class="LET()"/><lemma class="."/></w><observations><observation class="ei_ij_error"><wref id="WR-P-E-J-0000000001.p.1.s.8.w.9" t="terweil"/><desc>Confusion between EI and IJ diphtongues</desc></observation></observations></s>'))

    def test019_adderrordetection(self):
        """Edit Check - Error Detection"""
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn

        w.append( folia.ErrorDetection(self.doc, cls="spelling", annotator="testscript", annotatortype=folia.AnnotatorType.AUTO) )
        self.assertEqual( w.annotation(folia.ErrorDetection).cls ,'spelling' )

        #self.assertTrue( xmlcheck(w.xmlstring(),'<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11"><pos class="FOUTN(soort,ev,basis,zijd,stan)"/><lemma class="stippelijn"/><correction xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11.correction.1" class="spelling" annotatortype="auto" annotator="testscript"><new><t>stippellijn</t></new><original auth="no"><t>stippelijn</t></original></correction></w>'))

    #def test008_addaltcorrection(self):
    #    """Edit Check - Adding alternative corrections"""
    #    w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn
    #    w.correcttext('stippellijn', set='corrections',cls='spelling',annotator='testscript', annotatortype='auto', alternative=True)
    #
    #    alt = w.alternatives(folia.AnnotationType.CORRECTION)
    #    self.assertEqual( alt[0].annotation(folia.Correction).original[0] ,'stippelijn' )
    #    self.assertEqual( alt[0].annotation(folia.Correction).new[0] ,'stippellijn' )

    #def test009_addaltcorrection2(self):
    #    """Edit Check - Adding an alternative and a selected correction"""
    #    w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn
    #    w.correcttext('stippel-lijn', set='corrections',cls='spelling',annotator='testscript', annotatortype='auto', alternative=True)

    #    w.correcttext('stippellijn', set='corrections',cls='spelling',annotator='testscript', annotatortype='auto')

    #    alt = w.alternatives(folia.AnnotationType.CORRECTION)
    #    self.assertEqual( alt[0].annotation(folia.Correction).id ,'WR-P-E-J-0000000001.p.1.s.8.w.11.correction.1' )
    #    self.assertEqual( alt[0].annotation(folia.Correction).original[0] ,'stippelijn' )
    #    self.assertEqual( alt[0].annotation(folia.Correction).new[0] ,'stippel-lijn' )

    #    self.assertEqual( w.annotation(folia.Correction).id ,'WR-P-E-J-0000000001.p.1.s.8.w.11.correction.2' )
    #    self.assertEqual( w.annotation(folia.Correction).original[0] ,'stippelijn' )
    #    self.assertEqual( w.annotation(folia.Correction).new[0] ,'stippellijn' )
    #    self.assertEqual( w.text(), 'stippellijn')

class Test4Create(unittest.TestCase):
        def test001_create(self):
            """Creating a FoLiA Document from scratch"""
            self.doc = folia.Document(id='example')
            self.doc.declare(folia.AnnotationType.TOKEN, 'adhocset',annotator='proycon')

            self.assertEqual(self.doc.defaultset(folia.AnnotationType.TOKEN), 'adhocset')
            self.assertEqual(self.doc.defaultannotator(folia.AnnotationType.TOKEN, 'adhocset'), 'proycon')

            text = folia.Text(self.doc, id=self.doc.id + '.text.1')
            self.doc.append( text )

            text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.1', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.1', text="De"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.2', text="site"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.3', text="staat"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.4', text="online"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.5', text=".")
                ]
                )
            )

            self.assertEqual( len(self.doc.index[self.doc.id + '.s.1']), 5)

class Test5Correction(unittest.TestCase):
        def setUp(self):
            self.doc = folia.Document(id='example')
            self.doc.declare(folia.AnnotationType.TOKEN, set='adhocset',annotator='proycon')
            self.text = folia.Text(self.doc, id=self.doc.id + '.text.1')
            self.doc.append( self.text )


        def test001_splitcorrection(self):
            """Correction - Split correction"""

            self.text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.1', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.1', text="De"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.2', text="site"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.3', text="staat"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.4', text="online"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.5', text=".")
                ]
                )
            )


            w = self.doc.index[self.doc.id + '.s.1.w.4']

            w.split( folia.Word(self.doc, id=self.doc.id + '.s.1.w.4a', text="on"), folia.Word(self.doc, id=self.doc.id + '.s.1.w.4b', text="line") )

            s = self.doc.index[self.doc.id + '.s.1']
            self.assertEqual( s.words(-3).text(), 'on' )
            self.assertEqual( s.words(-2).text(), 'line' )
            self.assertEqual( s.text(), 'De site staat on line .' )
            self.assertEqual( len(list(s.words())), 6 )
            self.assertTrue( xmlcheck(s.xmlstring(),  '<s xmlns="http://ilk.uvt.nl/folia" xml:id="example.s.1"><w xml:id="example.s.1.w.1"><t>De</t></w><w xml:id="example.s.1.w.2"><t>site</t></w><w xml:id="example.s.1.w.3"><t>staat</t></w><correction xml:id="example.s.1.correction.1"><new><w xml:id="example.s.1.w.4a"><t>on</t></w><w xml:id="example.s.1.w.4b"><t>line</t></w></new><original auth="no"><w xml:id="example.s.1.w.4"><t>online</t></w></original></correction><w xml:id="example.s.1.w.5"><t>.</t></w></s>'))


        def test001_splitcorrection2(self):
            """Correction - Split suggestion"""

            self.text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.1', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.1', text="De"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.2', text="site"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.3', text="staat"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.4', text="online"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.5', text=".")
                ]
                )
            )


            w = self.doc.index[self.doc.id + '.s.1.w.4']

            s = self.doc.index[self.doc.id + '.s.1']
            w.split( folia.Word(self.doc, generate_id_in=s, text="on"), folia.Word(self.doc, generate_id_in=s, text="line"), suggest=True )

            self.assertEqual( len(list(s.words())), 5 )
            self.assertEqual( s.words(-2).text(), 'online' )
            self.assertEqual( s.text(), 'De site staat online .' )

            self.assertTrue( xmlcheck(s.xmlstring(), '<s xmlns="http://ilk.uvt.nl/folia" xml:id="example.s.1"><w xml:id="example.s.1.w.1"><t>De</t></w><w xml:id="example.s.1.w.2"><t>site</t></w><w xml:id="example.s.1.w.3"><t>staat</t></w><correction xml:id="example.s.1.correction.1"><current><w xml:id="example.s.1.w.4"><t>online</t></w></current><suggestion auth="no"><w xml:id="example.s.1.w.6"><t>on</t></w><w xml:id="example.s.1.w.7"><t>line</t></w></suggestion></correction><w xml:id="example.s.1.w.5"><t>.</t></w></s>'))


        def test002_mergecorrection(self):
            """Correction - Merge corrections"""
            self.text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.1', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.1', text="De"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.2', text="site"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.3', text="staat"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.4', text="on"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.5', text="line"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.6', text=".")
                ]
                )
            )

            s = self.doc.index[self.doc.id + '.s.1']


            s.mergewords( folia.Word(self.doc, 'online', id=self.doc.id + '.s.1.w.4-5') , self.doc.index[self.doc.id + '.s.1.w.4'], self.doc.index[self.doc.id + '.s.1.w.5'] )

            self.assertEqual( len(list(s.words())), 5 )
            self.assertEqual( s.text(), 'De site staat online .')

            #incorrection() test, check if newly added word correctly reports being part of a correction
            w = self.doc.index[self.doc.id + '.s.1.w.4-5']
            self.assertTrue( isinstance(w.incorrection(), folia.Correction) ) #incorrection return the correction the word is part of, or None if not part of a correction,


            self.assertTrue( xmlcheck(s.xmlstring(),  '<s xmlns="http://ilk.uvt.nl/folia" xml:id="example.s.1"><w xml:id="example.s.1.w.1"><t>De</t></w><w xml:id="example.s.1.w.2"><t>site</t></w><w xml:id="example.s.1.w.3"><t>staat</t></w><correction xml:id="example.s.1.correction.1"><new><w xml:id="example.s.1.w.4-5"><t>online</t></w></new><original auth="no"><w xml:id="example.s.1.w.4"><t>on</t></w><w xml:id="example.s.1.w.5"><t>line</t></w></original></correction><w xml:id="example.s.1.w.6"><t>.</t></w></s>'))


        def test003_deletecorrection(self):
            """Correction - Deletion"""

            self.text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.1', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.1', text="Ik"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.2', text="zie"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.3', text="een"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.4', text="groot"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.5', text="huis"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.6', text=".")
                ]
                )
            )
            s = self.doc.index[self.doc.id + '.s.1']
            s.deleteword(self.doc.index[self.doc.id + '.s.1.w.4'])
            self.assertEqual( len(list(s.words())), 5 )
            self.assertEqual( s.text(), 'Ik zie een huis .')

            self.assertTrue( xmlcheck(s.xmlstring(), '<s xmlns="http://ilk.uvt.nl/folia" xml:id="example.s.1"><w xml:id="example.s.1.w.1"><t>Ik</t></w><w xml:id="example.s.1.w.2"><t>zie</t></w><w xml:id="example.s.1.w.3"><t>een</t></w><correction xml:id="example.s.1.correction.1"><new/><original auth="no"><w xml:id="example.s.1.w.4"><t>groot</t></w></original></correction><w xml:id="example.s.1.w.5"><t>huis</t></w><w xml:id="example.s.1.w.6"><t>.</t></w></s>') )

        def test004_insertcorrection(self):
            """Correction - Insert"""
            self.text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.1', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.1', text="Ik"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.2', text="zie"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.3', text="een"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.4', text="huis"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.5', text=".")
                ]
                )
            )
            s = self.doc.index[self.doc.id + '.s.1']
            s.insertword( folia.Word(self.doc, id=self.doc.id+'.s.1.w.3b',text='groot'),  self.doc.index[self.doc.id + '.s.1.w.3'])
            self.assertEqual( len(list(s.words())), 6 )

            self.assertEqual( s.text(), 'Ik zie een groot huis .')
            self.assertTrue( xmlcheck( s.xmlstring(), '<s xmlns="http://ilk.uvt.nl/folia" xml:id="example.s.1"><w xml:id="example.s.1.w.1"><t>Ik</t></w><w xml:id="example.s.1.w.2"><t>zie</t></w><w xml:id="example.s.1.w.3"><t>een</t></w><correction xml:id="example.s.1.correction.1"><new><w xml:id="example.s.1.w.3b"><t>groot</t></w></new></correction><w xml:id="example.s.1.w.4"><t>huis</t></w><w xml:id="example.s.1.w.5"><t>.</t></w></s>'))

        def test005_reusecorrection(self):
            """Correction - Re-using a correction with only suggestions"""
            global FOLIAEXAMPLE
            self.doc = folia.Document(string=FOLIAEXAMPLE)

            w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn
            w.correct(suggestion='stippellijn', set='corrections',cls='spelling',annotator='testscript', annotatortype=folia.AnnotatorType.AUTO)
            c = w.annotation(folia.Correction)

            self.assertTrue( isinstance(w.annotation(folia.Correction), folia.Correction) )
            self.assertEqual( w.annotation(folia.Correction).suggestions(0).text() , 'stippellijn' )
            self.assertEqual( w.text(), 'stippelijn')

            w.correct(new='stippellijn',set='corrections',cls='spelling',annotator='John Doe', annotatortype=folia.AnnotatorType.MANUAL,reuse=c.id)

            self.assertEqual( w.text(), 'stippellijn')
            self.assertEqual( len(list(w.annotations(folia.Correction))), 1 )
            self.assertEqual( w.annotation(folia.Correction).suggestions(0).text() , 'stippellijn' )
            self.assertEqual( w.annotation(folia.Correction).suggestions(0).annotator , 'testscript' )
            self.assertEqual( w.annotation(folia.Correction).suggestions(0).annotatortype , folia.AnnotatorType.AUTO)
            self.assertEqual( w.annotation(folia.Correction).new(0).text() , 'stippellijn' )
            self.assertEqual( w.annotation(folia.Correction).annotator , 'John Doe' )
            self.assertEqual( w.annotation(folia.Correction).annotatortype , folia.AnnotatorType.MANUAL)

            self.assertTrue( xmlcheck(w.xmlstring(), '<w xmlns="http://ilk.uvt.nl/folia" xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11"><pos class="FOUTN(soort,ev,basis,zijd,stan)"/><lemma class="stippelijn"/><correction xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11.correction.1" class="spelling" annotator="John Doe"><suggestion annotator="testscript" auth="no" annotatortype="auto"><t>stippellijn</t></suggestion><new><t>stippellijn</t></new><original auth="no"><t>stippelijn</t></original></correction></w>'))

        def test006_deletionsuggestion(self):
            """Correction - Suggestion for deletion with parent merge suggestion"""
            self.text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.1', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.1', text="De"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.2', text="site"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.3', text="staat"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.4', text="on"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.5', text="line"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.6', text=".")
                ]),
            )
            self.text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.2', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.2.w.1', text="sinds"),
                    folia.Word(self.doc,id=self.doc.id + '.s.2.w.2', text="vorige"),
                    folia.Word(self.doc,id=self.doc.id + '.s.2.w.3', text="week"),
                    folia.Word(self.doc,id=self.doc.id + '.s.2.w.4', text="zondag"),
                    folia.Word(self.doc,id=self.doc.id + '.s.2.w.6', text=".")
                ])
            )

            s = self.doc.index[self.doc.id + '.s.1']
            s2 = self.doc.index[self.doc.id + '.s.2']
            w = self.doc.index[self.doc.id + '.s.1.w.6']
            s.remove(w)
            s.append( folia.Correction(self.doc, folia.Current(self.doc, w), folia.Suggestion(self.doc, merge=s2.id)) )

            self.assertTrue( xmlcheck(s.xmlstring(),  '<s xmlns="http://ilk.uvt.nl/folia" xml:id="example.s.1"><w xml:id="example.s.1.w.1"><t>De</t></w><w xml:id="example.s.1.w.2"><t>site</t></w><w xml:id="example.s.1.w.3"><t>staat</t></w><w xml:id="example.s.1.w.4"><t>on</t></w><w xml:id="example.s.1.w.5"><t>line</t></w><correction><current><w xml:id="example.s.1.w.6"><t>.</t></w></current><suggestion merge="example.s.2" auth="no"/></correction></s>'))



class Test6Query(unittest.TestCase):
    def setUp(self):
        global FOLIAEXAMPLE
        self.doc = folia.Document(string=FOLIAEXAMPLE)

    def test001_findwords_simple(self):
        """Querying - Find words (simple)"""
        matches = list(self.doc.findwords( folia.Pattern('van','het','alfabet') ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 3 )
        self.assertEqual( matches[0][0].text(), 'van' )
        self.assertEqual( matches[0][1].text(), 'het' )
        self.assertEqual( matches[0][2].text(), 'alfabet' )


    def test002_findwords_wildcard(self):
        """Querying - Find words (with wildcard)"""
        matches = list(self.doc.findwords( folia.Pattern('van','het',True) ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 3 )

        self.assertEqual( matches[0][0].text(), 'van' )
        self.assertEqual( matches[0][1].text(), 'het' )
        self.assertEqual( matches[0][2].text(), 'alfabet' )

    def test003_findwords_annotation(self):
        """Querying - Find words by annotation"""
        matches = list(self.doc.findwords( folia.Pattern('de','historisch','wetenschap','worden', matchannotation=folia.LemmaAnnotation) ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 4 )
        self.assertEqual( matches[0][0].text(), 'de' )
        self.assertEqual( matches[0][1].text(), 'historische' )
        self.assertEqual( matches[0][2].text(), 'wetenschap' )
        self.assertEqual( matches[0][3].text(), 'wordt' )



    def test004_findwords_multi(self):
        """Querying - Find words using a conjunction of multiple patterns """
        matches = list(self.doc.findwords( folia.Pattern('de','historische',True, 'wordt'), folia.Pattern('de','historisch','wetenschap','worden', matchannotation=folia.LemmaAnnotation) ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 4 )
        self.assertEqual( matches[0][0].text(), 'de' )
        self.assertEqual( matches[0][1].text(), 'historische' )
        self.assertEqual( matches[0][2].text(), 'wetenschap' )
        self.assertEqual( matches[0][3].text(), 'wordt' )

    def test005_findwords_none(self):
        """Querying - Find words that don't exist"""
        matches = list(self.doc.findwords( folia.Pattern('bli','bla','blu')))
        self.assertEqual( len(matches), 0)

    def test006_findwords_overlap(self):
        """Querying - Find words with overlap"""
        doc = folia.Document(id='test')
        text = folia.Text(doc, id='test.text')

        text.append(
            folia.Sentence(doc,id=doc.id + '.s.1', contents=[
                folia.Word(doc,id=doc.id + '.s.1.w.1', text="a"),
                folia.Word(doc,id=doc.id + '.s.1.w.2', text="a"),
                folia.Word(doc,id=doc.id + '.s.1.w.3', text="a"),
                folia.Word(doc,id=doc.id + '.s.1.w.4', text="A"),
                folia.Word(doc,id=doc.id + '.s.1.w.5', text="b"),
                folia.Word(doc,id=doc.id + '.s.1.w.6', text="a"),
                folia.Word(doc,id=doc.id + '.s.1.w.7', text="a"),
            ]
            )
        )
        doc.append(text)

        matches = list(doc.findwords( folia.Pattern('a','a')))
        self.assertEqual( len(matches), 4)
        matches = list(doc.findwords( folia.Pattern('a','a',casesensitive=True)))
        self.assertEqual( len(matches), 3)

    def test007_findwords_context(self):
        """Querying - Find words with context"""
        matches = list(self.doc.findwords( folia.Pattern('van','het','alfabet'), leftcontext=3, rightcontext=3 ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 9 )
        self.assertEqual( matches[0][0].text(), 'de' )
        self.assertEqual( matches[0][1].text(), 'laatste' )
        self.assertEqual( matches[0][2].text(), 'letters' )
        self.assertEqual( matches[0][3].text(), 'van' )
        self.assertEqual( matches[0][4].text(), 'het' )
        self.assertEqual( matches[0][5].text(), 'alfabet' )
        self.assertEqual( matches[0][6].text(), 'en' )
        self.assertEqual( matches[0][7].text(), 'worden' )
        self.assertEqual( matches[0][8].text(), 'tussen' )

    def test008_findwords_disjunction(self):
        """Querying - Find words with disjunctions"""
        matches = list(self.doc.findwords( folia.Pattern('de',('historische','hedendaagse'),'wetenschap','wordt') ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 4 )
        self.assertEqual( matches[0][0].text(), 'de' )
        self.assertEqual( matches[0][1].text(), 'historische' )
        self.assertEqual( matches[0][2].text(), 'wetenschap' )
        self.assertEqual( matches[0][3].text(), 'wordt' )

    def test009_findwords_regexp(self):
        """Querying - Find words with regular expressions"""
        matches = list(self.doc.findwords( folia.Pattern('de',folia.RegExp('hist.*'),folia.RegExp('.*schap'),folia.RegExp('w[oae]rdt')) ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 4 )
        self.assertEqual( matches[0][0].text(), 'de' )
        self.assertEqual( matches[0][1].text(), 'historische' )
        self.assertEqual( matches[0][2].text(), 'wetenschap' )
        self.assertEqual( matches[0][3].text(), 'wordt' )


    def test010a_findwords_variablewildcard(self):
        """Querying - Find words with variable wildcard"""
        matches = list(self.doc.findwords( folia.Pattern('de','laatste','*','alfabet') ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 6 )
        self.assertEqual( matches[0][0].text(), 'de' )
        self.assertEqual( matches[0][1].text(), 'laatste' )
        self.assertEqual( matches[0][2].text(), 'letters' )
        self.assertEqual( matches[0][3].text(), 'van' )
        self.assertEqual( matches[0][4].text(), 'het' )
        self.assertEqual( matches[0][5].text(), 'alfabet' )

    def test010b_findwords_varwildoverlap(self):
        """Querying - Find words with variable wildcard and overlap"""
        doc = folia.Document(id='test')
        text = folia.Text(doc, id='test.text')

        text.append(
            folia.Sentence(doc,id=doc.id + '.s.1', contents=[
                folia.Word(doc,id=doc.id + '.s.1.w.1', text="a"),
                folia.Word(doc,id=doc.id + '.s.1.w.2', text="b"),
                folia.Word(doc,id=doc.id + '.s.1.w.3', text="c"),
                folia.Word(doc,id=doc.id + '.s.1.w.4', text="d"),
                folia.Word(doc,id=doc.id + '.s.1.w.5', text="a"),
                folia.Word(doc,id=doc.id + '.s.1.w.6', text="b"),
                folia.Word(doc,id=doc.id + '.s.1.w.7', text="c"),
            ]
            )
        )
        doc.append(text)

        matches = list(doc.findwords( folia.Pattern('a','*', 'c')))
        self.assertEqual( len(matches), 3)


    def test011_findwords_annotation_na(self):
        """Querying - Find words by non existing annotation"""
        matches = list(self.doc.findwords( folia.Pattern('bli','bla','blu', matchannotation=folia.SenseAnnotation) ))
        self.assertEqual( len(matches), 0 )



class Test9Reader(unittest.TestCase):
    def setUp(self):
        self.reader = folia.Reader(os.path.join(TMPDIR,"foliatest.xml"), folia.Word)

    def test000_worditer(self):
        """Stream reader - Iterating over words"""
        count = 0
        for word in self.reader:
            count += 1
        self.assertEqual(count, 192)

    def test001_findwords_simple(self):
        """Querying using stream reader - Find words (simple)"""
        matches = list(self.reader.findwords( folia.Pattern('van','het','alfabet') ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 3 )
        self.assertEqual( matches[0][0].text(), 'van' )
        self.assertEqual( matches[0][1].text(), 'het' )
        self.assertEqual( matches[0][2].text(), 'alfabet' )


    def test002_findwords_wildcard(self):
        """Querying using stream reader - Find words (with wildcard)"""
        matches = list(self.reader.findwords( folia.Pattern('van','het',True) ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 3 )

        self.assertEqual( matches[0][0].text(), 'van' )
        self.assertEqual( matches[0][1].text(), 'het' )
        self.assertEqual( matches[0][2].text(), 'alfabet' )

    def test003_findwords_annotation(self):
        """Querying using stream reader - Find words by annotation"""
        matches = list(self.reader.findwords( folia.Pattern('de','historisch','wetenschap','worden', matchannotation=folia.LemmaAnnotation) ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 4 )
        self.assertEqual( matches[0][0].text(), 'de' )
        self.assertEqual( matches[0][1].text(), 'historische' )
        self.assertEqual( matches[0][2].text(), 'wetenschap' )
        self.assertEqual( matches[0][3].text(), 'wordt' )



    def test004_findwords_multi(self):
        """Querying using stream reader - Find words using a conjunction of multiple patterns """
        matches = list(self.reader.findwords( folia.Pattern('de','historische',True, 'wordt'), folia.Pattern('de','historisch','wetenschap','worden', matchannotation=folia.LemmaAnnotation) ))
        self.assertEqual( len(matches), 1 )
        self.assertEqual( len(matches[0]), 4 )
        self.assertEqual( matches[0][0].text(), 'de' )
        self.assertEqual( matches[0][1].text(), 'historische' )
        self.assertEqual( matches[0][2].text(), 'wetenschap' )
        self.assertEqual( matches[0][3].text(), 'wordt' )

    def test005_findwords_none(self):
        """Querying using stream reader - Find words that don't exist"""
        matches = list(self.reader.findwords( folia.Pattern('bli','bla','blu')))
        self.assertEqual( len(matches), 0)


    def test011_findwords_annotation_na(self):
        """Querying using stream reader - Find words by non existing annotation"""
        matches = list(self.reader.findwords( folia.Pattern('bli','bla','blu', matchannotation=folia.SenseAnnotation) ))
        self.assertEqual( len(matches), 0 )

class Test7XpathQuery(unittest.TestCase):
    def test050_findwords_xpath(self):
        """Xpath Querying - Collect all words (including non-authoritative)"""
        count = 0
        for word in folia.Query(os.path.join(TMPDIR,'foliatest.xml'),'//f:w'):
            count += 1
            self.assertTrue( isinstance(word, folia.Word) )
        self.assertEqual(count, 192)

    def test051_findwords_xpath(self):
        """Xpath Querying - Collect all words (authoritative only)"""
        count = 0
        for word in folia.Query(os.path.join(TMPDIR,'foliatest.xml'),'//f:w[not(ancestor-or-self::*/@auth)]'):
            count += 1
            self.assertTrue( isinstance(word, folia.Word) )
        self.assertEqual(count, 190)


class Test8Validation(unittest.TestCase):
      def test000_relaxng(self):
        """Validation - RelaxNG schema generation"""
        folia.relaxng()

      def test001_shallowvalidation(self):
        """Validation - Shallow validation against automatically generated RelaxNG schema"""
        folia.validate(os.path.join(TMPDIR,'foliasavetest.xml'))

      def test002_loadsetdefinitions(self):
        """Validation - Loading of set definitions"""
        doc = folia.Document(file=os.path.join(TMPDIR,'foliatest.xml'), loadsetdefinitions=True)
        assert isinstance( doc.setdefinitions["http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml"], folia.SetDefinition)

      def test003_deepvalidation(self):
        """Validation - Deep Validation"""
        try:
            doc = folia.Document(file=os.path.join(TMPDIR,'foliatest.xml'), deepvalidation=True, allowadhocsets=True)
            assert isinstance( doc.setdefinitions["http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml"], folia.SetDefinition)
        except NotImplementedError:
            print("Deep validation not implemented yet! (not failing over this)",file=sys.stderr)
            return


f = io.open(FOLIAPATH + '/test/example.xml', 'r',encoding='utf-8')
FOLIAEXAMPLE = f.read()
f.close()

#We cheat, by setting the generator and version attributes to match the library, so xmldiff doesn't complain when we compare against this reference
FOLIAEXAMPLE = re.sub(r' version="[^"]*" generator="[^"]*"', ' version="' + folia.FOLIAVERSION + '" generator="pynlpl.formats.folia-v' + folia.LIBVERSION + '"', FOLIAEXAMPLE, re.MULTILINE)

#Another cheat, alien namespace attributes are ignored by the folia library, strip them so xmldiff doesn't complain
FOLIAEXAMPLE = re.sub(r' xmlns:alien="[^"]*" alien:attrib="[^"]*"', '', FOLIAEXAMPLE, re.MULTILINE)


DCOIEXAMPLE="""<?xml version="1.0" encoding="iso-8859-15"?>
<DCOI xmlns:imdi="http://www.mpi.nl/IMDI/Schema/IMDI" xmlns="http://lands.let.ru.nl/projects/d-coi/ns/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:d-coi="http://lands.let.ru.nl/projects/d-coi/ns/1.0" xsi:schemaLocation="http://lands.let.ru.nl/projects/d-coi/ns/1.0 dcoi.xsd" xml:id="WR-P-E-J-0000125009">
  <imdi:METATRANSCRIPT xmlns:imdi="http://www.mpi.nl/IMDI/Schema/IMDI" Date="2009-01-27" Type="SESSION" Version="1">
    <imdi:Session>
      <imdi:Name>WR-P-E-J-0000125009</imdi:Name>
      <imdi:Title>Aspirine 3D model van Aspirine</imdi:Title>
      <imdi:Date>2009-01-27</imdi:Date>
      <imdi:Description/>
      <imdi:MDGroup>
        <imdi:Location>
          <imdi:Continent>Europe</imdi:Continent>
          <imdi:Country>NL/B</imdi:Country>
        </imdi:Location>
        <imdi:Keys/>
        <imdi:Project>
          <imdi:Name>D-Coi</imdi:Name>
          <imdi:Title/>
          <imdi:Id/>
          <imdi:Contact/>
          <imdi:Description/>
        </imdi:Project>
        <imdi:Collector>
          <imdi:Name/>
          <imdi:Contact/>
          <imdi:Description/>
        </imdi:Collector>
        <imdi:Content>
          <imdi:Task/>
          <imdi:Modalities/>
          <imdi:CommunicationContext>
            <imdi:Interactivity/>
            <imdi:PlanningType/>
            <imdi:Involvement/>
          </imdi:CommunicationContext>
          <imdi:Genre>
            <imdi:Interactional/>
            <imdi:Discursive/>
            <imdi:Performance/>
          </imdi:Genre>
          <imdi:Languages>
            <imdi:Language>
              <imdi:Id/>
              <imdi:Name>Dutch</imdi:Name>
              <imdi:Description/>
            </imdi:Language>
          </imdi:Languages>
          <imdi:Keys/>
        </imdi:Content>
        <imdi:Participants/>
      </imdi:MDGroup>
      <imdi:Resources>
        <imdi:MediaFile>
          <imdi:ResourceLink/>
          <imdi:Size>162304</imdi:Size>
          <imdi:Type/>
          <imdi:Format/>
          <imdi:Quality>Unknown</imdi:Quality>
          <imdi:RecordingConditions/>
          <imdi:TimePosition Start="Unknown"/>
          <imdi:Access>
            <imdi:Availability/>
            <imdi:Date/>
            <imdi:Owner/>
            <imdi:Publisher/>
            <imdi:Contact/>
            <imdi:Description/>
          </imdi:Access>
          <imdi:Description/>
        </imdi:MediaFile>
        <imdi:AnnotationUnit>
          <imdi:ResourceLink/>
          <imdi:MediaResourceLink/>
          <imdi:Annotator/>
          <imdi:Date/>
          <imdi:Type/>
          <imdi:Format/>
          <imdi:ContentEncoding/>
          <imdi:CharacterEncoding/>
          <imdi:Access>
            <imdi:Availability/>
            <imdi:Date/>
            <imdi:Owner/>
            <imdi:Publisher/>
            <imdi:Contact/>
            <imdi:Description/>
          </imdi:Access>
          <imdi:LanguageId/>
          <imdi:Anonymous>false</imdi:Anonymous>
          <imdi:Description/>
        </imdi:AnnotationUnit>
        <imdi:Source>
          <imdi:Id/>
          <imdi:Format/>
          <imdi:Quality>Unknown</imdi:Quality>
          <imdi:TimePosition Start="Unknown"/>
          <imdi:Access>
            <imdi:Availability>GNU Free Documentation License</imdi:Availability>
            <imdi:Date/>
            <imdi:Owner/>
            <imdi:Publisher>Wikimedia Foundation (NL/B)</imdi:Publisher>
            <imdi:Contact/>
            <imdi:Description/>
          </imdi:Access>
          <imdi:Description/>
        </imdi:Source>
      </imdi:Resources>
    </imdi:Session>
  </imdi:METATRANSCRIPT>
  <text xml:id="WR-P-E-J-0000125009.text">
    <body>
      <div xml:id="WR-P-E-J-0000125009.div.1">
        <head xml:id="WR-P-E-J-0000125009.head.1">
          <s xml:id="WR-P-E-J-0000125009.head.1.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.1.s.1.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.head.1.s.2">
            <w xml:id="WR-P-E-J-0000125009.head.1.s.2.w.1" pos="TW(hoofd,prenom,stan)" lemma="3D">3D</w>
            <w xml:id="WR-P-E-J-0000125009.head.1.s.2.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="model">model</w>
            <w xml:id="WR-P-E-J-0000125009.head.1.s.2.w.3" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.head.1.s.2.w.4" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.1">
          <s xml:id="WR-P-E-J-0000125009.p.1.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.2" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.3" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.4" pos="N(soort,ev,basis,zijd,stan)" lemma="merknaam">merknaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.5" pos="VZ(init)" lemma="voor">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.6" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.7" pos="N(soort,ev,basis,zijd,stan)" lemma="medicijn">medicijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.8" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.9" pos="N(eigen,ev,basis,zijd,stan)" lemma="Bayer">Bayer</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.10" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.1.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.2" pos="ADJ(prenom,basis,met-e,stan)" lemma="werkzaam">werkzame</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.3" pos="N(soort,ev,basis,zijd,stan)" lemma="stof">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.4" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.5" pos="N(soort,ev,basis,onz,stan)" lemma="acetylsalicylzuur">acetylsalicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.6" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.1.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.2" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.3" pos="BW()" lemma="ook">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.4" pos="ADJ(vrij,basis,zonder)" lemma="bekend">bekend</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.5" pos="VZ(init)" lemma="onder">onder</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.6" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.7" pos="N(soort,ev,basis,zijd,stan)" lemma="naam">naam</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="acetosal">acetosal</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.9" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.10" pos="N(soort,mv,basis)" lemma="aspro">aspro</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.11" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.12" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.13" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.14" pos="N(soort,ev,basis,zijd,stan)" lemma="merknaam">merknaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.15" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.16" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.17" pos="SPEC(deeleigen)" lemma="_">Nicholas</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.18" pos="SPEC(deeleigen)" lemma="_">Ltd.</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.19" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.20" pos="WW(pv,tgw,met-t)" lemma="werken">werkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.21" pos="ADJ(vrij,basis,zonder)" lemma="pijnstillend">pijnstillend</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.22" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.23" pos="ADJ(vrij,basis,zonder)" lemma="koortsverlagend">koortsverlagend</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.24" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.25" pos="ADJ(vrij,basis,zonder)" lemma="ontstekingsremmend">ontstekingsremmend</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.26" pos="LET()" lemma=".">.</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.2">
          <s xml:id="WR-P-E-J-0000125009.p.2.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.1" pos="ADJ(vrij,basis,zonder)" lemma="Oorspronkelijk">Oorspronkelijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.2" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.3" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.4" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.5" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.6" pos="N(soort,ev,basis,onz,stan)" lemma="salicylzuur">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.7" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="pijnstiller">pijnstiller</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.9" pos="WW(vd,vrij,zonder)" lemma="ontdekken">ontdekt</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.10" pos="VG(onder)" lemma="doordat">doordat</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.11" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.12" pos="WW(pv,verl,ev)" lemma="worden">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.13" pos="WW(vd,vrij,zonder)" lemma="identificeren">geïdentificeerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.14" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.15" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.16" pos="ADJ(prenom,basis,met-e,stan)" lemma="werkzaam">werkzame</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.17" pos="N(soort,ev,basis,zijd,stan)" lemma="stof">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.18" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.19" pos="N(soort,ev,basis,zijd,stan)" lemma="wilgenbast">wilgenbast</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.20" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.2.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.1" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="zuur">zuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.3" pos="BW()" lemma="zelf">zelf</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.4" pos="WW(pv,verl,ev)" lemma="worden">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.5" pos="BW()" lemma="echter">echter</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.6" pos="ADJ(prenom,basis,zonder)" lemma="bijzonder">bijzonder</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.7" pos="ADJ(vrij,basis,zonder)" lemma="slecht">slecht</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.8" pos="VZ(init)" lemma="door">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.9" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="maag">maag</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.11" pos="WW(vd,vrij,zonder)" lemma="tolereren">getolereerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.12" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.2.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="acetyl-ester">acetyl-ester</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.3" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.4" pos="BW()" lemma="daarin">daarin</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.5" pos="VNW(onbep,grad,stan,vrij,zonder,basis)" lemma="veel">veel</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.6" pos="ADJ(vrij,comp,zonder)" lemma="goed">beter</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.7" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.2.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.1" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">Deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="stof">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.3" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.4" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.5" pos="ADJ(prenom,basis,met-e,stan)" lemma="zuiver">zuivere</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="toestand">toestand</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.7" pos="VG(neven)" lemma="of">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.8" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.9" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.10" pos="VNW(onbep,pron,stan,vol,3o,ev)" lemma="iets">iets</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.11" pos="VNW(onbep,grad,stan,vrij,zonder,comp)" lemma="minder">minder</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.12" pos="ADJ(prenom,basis,met-e,stan)" lemma="maagprikkelende">maagprikkelende</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="calciumzout">calciumzout</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.14" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.15" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.16" pos="N(soort,ev,basis,zijd,stan)" lemma="markt">markt</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.17" pos="WW(vd,vrij,zonder)" lemma="brengen">gebracht</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.18" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.19" pos="N(soort,ev,basis,zijd,stan)" lemma="ascal">ascal</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.20" pos="LET()" lemma=")">)</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.3">
          <s xml:id="WR-P-E-J-0000125009.p.3.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.3" pos="BW()" lemma="zelf">zelf</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.4" pos="WW(pv,tgw,ev)" lemma="berusten">berust</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.5" pos="BW()" lemma="erop">erop</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.6" pos="VG(onder)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.7" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.8" pos="ADJ(vrij,basis,zonder)" lemma="irreversibel">irreversibel</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.9" pos="WW(pv,tgw,met-t)" lemma="binden">bindt</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.10" pos="VZ(init)" lemma="aan">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.11" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.12" pos="N(soort,ev,basis,onz,stan)" lemma="enzym">enzym</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="cyclo-oxygenase">cyclo-oxygenase</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.14" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.15" pos="N(soort,ev,basis,zijd,stan)" lemma="cox">COX</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.16" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.17" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.18" pos="BW()" lemma="waardoor">waardoor</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.19" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.20" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.21" pos="VNW(onbep,grad,stan,vrij,zonder,comp)" lemma="veel">meer</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.22" pos="WW(pv,tgw,ev)" lemma="kunnen">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.23" pos="WW(inf,vrij,zonder)" lemma="helpen">helpen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.24" pos="N(soort,ev,basis,zijd,stan)" lemma="arachidonzuur">arachidonzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.25" pos="VZ(init)" lemma="om">om</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.26" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.27" pos="WW(inf,vrij,zonder)" lemma="zetten">zetten</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.28" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.29" pos="N(soort,mv,basis)" lemma="prostaglandine">prostaglandines</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.30" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.31" pos="N(soort,mv,basis)" lemma="stof">stoffen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.32" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.33" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.34" pos="N(soort,mv,basis)" lemma="zenuwuiteinde">zenuwuiteinden</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.35" pos="ADJ(vrij,basis,zonder)" lemma="gevoelig">gevoelig</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.36" pos="WW(pv,tgw,mv)" lemma="maken">maken</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.37" pos="VZ(init)" lemma="voor">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.38" pos="N(soort,mv,basis)" lemma="prikkel">prikkels</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.39" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.3.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.2" pos="WW(vd,prenom,met-e)" lemma="vermelden">vermelde</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.3" pos="N(soort,mv,basis)" lemma="maagprobleem">maagproblemen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.4" pos="WW(pv,tgw,mv)" lemma="ontstaan">ontstaan</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.5" pos="VZ(init)" lemma="door">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.6" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.7" pos="ADJ(prenom,basis,met-e,stan)" lemma="irreversibel">irreversibele</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="binding">binding</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.9" pos="VZ(init)" lemma="aan">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.10" pos="N(eigen,ev,basis,zijd,stan)" lemma="Cox-1">COX-1</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.11" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.12" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="variant">variant</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.14" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.15" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.16" pos="N(soort,ev,basis,onz,stan)" lemma="enzym">enzym</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.17" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.18" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.19" pos="N(soort,ev,basis,zijd,stan)" lemma="rolspeelt">rolspeelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.20" pos="VZ(init)" lemma="bij">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.21" pos="N(soort,ev,basis,zijd,stan)" lemma="bescherming">bescherming</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.22" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.23" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.24" pos="N(soort,ev,basis,zijd,stan)" lemma="maag">maag</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.25" pos="VZ(init)" lemma="tegen">tegen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.26" pos="VNW(bez,det,stan,vol,3,ev,prenom,zonder,agr)" lemma="zijn">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.27" pos="ADJ(prenom,basis,zonder)" lemma="eigen">eigen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.28" pos="ADJ(prenom,basis,met-e,stan)" lemma="zuur">zure</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.29" pos="N(soort,ev,basis,zijd,stan)" lemma="inhoud">inhoud</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.30" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.3.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.1" pos="BW()" lemma="ook">Ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.2" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.3" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.4" pos="N(eigen,ev,basis,zijd,stan)" lemma="Cox-1">COX-1</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.5" pos="ADJ(vrij,basis,zonder)" lemma="aanwezig">aanwezig</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.6" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.7" pos="N(soort,mv,basis)" lemma="bloedplaatjes">bloedplaatjes</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.8" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.9" pos="BW()" lemma="vandaar">vandaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.10" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.11" pos="ADJ(prenom,basis,met-e,stan)" lemma="trombocytenaggregatieremmende">trombocytenaggregatieremmende</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.13" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.3.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.1" pos="BW()" lemma="vandaar">Vandaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.2" pos="VG(onder)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.3" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.4" pos="ADJ(prenom,basis,met-e,stan)" lemma="farmaceutisch">farmaceutische</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="industrie">industrie</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.6" pos="VNW(refl,pron,obl,red,3,getal)" lemma="zich">zich</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.7" pos="WW(pv,tgw,ev)" lemma="richten">richt</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.8" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.9" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="ontwikkeling">ontwikkeling</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.11" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.12" pos="N(eigen,ev,basis,zijd,stan)" lemma="Cox-2">COX-2</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.13" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.14" pos="N(soort,ev,basis,zijd,stan)" lemma="induceerbaar">induceerbaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.15" pos="N(soort,ev,basis,zijd,stan)" lemma="cox">COX</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.16" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.17" pos="ADJ(prenom,basis,met-e,stan)" lemma="specifiek">specifieke</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.18" pos="N(soort,mv,basis)" lemma="pijnstiller">pijnstillers</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.19" pos="LET()" lemma=".">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.2">
        <head xml:id="WR-P-E-J-0000125009.head.2">
          <s xml:id="WR-P-E-J-0000125009.head.2.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.2.s.1.w.1" pos="N(soort,ev,basis,zijd,stan)" lemma="geschiedenis">Geschiedenis</w>
            <w xml:id="WR-P-E-J-0000125009.head.2.s.1.w.2" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.head.2.s.1.w.3" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.4">
          <s xml:id="WR-P-E-J-0000125009.p.4.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="ontdekking">ontdekking</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.3" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.4" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.5" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.6" pos="ADJ(prenom,basis,zonder)" lemma="algemeen">algemeen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.7" pos="WW(vd,vrij,zonder)" lemma="toeschrijven">toegeschreven</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.8" pos="VZ(init)" lemma="aan">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.9" pos="SPEC(deeleigen)" lemma="_">Felix</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.10" pos="SPEC(deeleigen)" lemma="_">Hoffmann</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.11" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.12" pos="ADJ(vrij,basis,zonder)" lemma="werkzaam">werkzaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.13" pos="VZ(init)" lemma="bij">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.14" pos="N(eigen,ev,basis,zijd,stan)" lemma="Bayer">Bayer</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.15" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.16" pos="N(soort,ev,basis,onz,stan)" lemma="elberfeld">Elberfeld</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.17" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.1" pos="VZ(init)" lemma="uit">Uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="onderzoek">onderzoek</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.3" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.4" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.5" pos="N(soort,mv,basis)" lemma="labjournaal">labjournaals</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.6" pos="VZ(init)" lemma="bij">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.7" pos="N(eigen,ev,basis,zijd,stan)" lemma="Bayer">Bayer</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.8" pos="WW(pv,tgw,met-t)" lemma="blijken">blijkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.9" pos="BW()" lemma="echter">echter</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.10" pos="VG(onder)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.11" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.12" pos="ADJ(prenom,basis,met-e,stan)" lemma="werkelijk">werkelijke</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="ontdekker">ontdekker</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.14" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.15" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.16" pos="SPEC(deeleigen)" lemma="_">Arthur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.17" pos="SPEC(deeleigen)" lemma="_">Eichengrün</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.18" pos="WW(pv,verl,ev)" lemma="zijn">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.19" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.20" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.21" pos="N(soort,ev,basis,onz,stan)" lemma="onderzoek">onderzoek</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.22" pos="WW(pv,verl,ev)" lemma="doen">deed</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.23" pos="VZ(init)" lemma="naar">naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.24" pos="ADJ(prenom,comp,met-e,stan)" lemma="goed">betere</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.25" pos="N(soort,mv,basis)" lemma="pijnstiller">pijnstillers</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.26" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.1" pos="SPEC(deeleigen)" lemma="_">Felix</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.2" pos="SPEC(deeleigen)" lemma="_">Hoffmann</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.3" pos="WW(pv,verl,ev)" lemma="werken">werkte</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.4" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="laboratorium-assistent">laboratorium-assistent</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.6" pos="VZ(init)" lemma="onder">onder</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.7" pos="WW(pv,tgw,mv)" lemma="zijn">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="leiding">leiding</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.9" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.1" pos="VZ(init)" lemma="door">Door</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.2" pos="VNW(bez,det,stan,vol,3,ev,prenom,zonder,agr)" lemma="zijn">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.3" pos="ADJ(prenom,basis,met-e,stan)" lemma="joods">joodse</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.4" pos="N(soort,ev,basis,zijd,stan)" lemma="achtergrond">achtergrond</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.5" pos="WW(pv,verl,ev)" lemma="worden">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.6" pos="N(soort,mv,basis)" lemma="eichengrün">Eichengrün</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.7" pos="VZ(init)" lemma="door">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.8" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.9" pos="N(soort,ev,basis,zijd,stan)" lemma="nazis">Nazis</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.10" pos="VZ(init)" lemma="uit">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.11" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.12" pos="N(soort,mv,basis)" lemma="annalen">annalen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.13" pos="WW(vd,vrij,zonder)" lemma="schrappen">geschrapt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.14" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.15" pos="WW(pv,verl,ev)" lemma="worden">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.16" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.17" pos="N(soort,ev,basis,onz,stan)" lemma="verhaal">verhaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.18" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.19" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.20" pos="ADJ(prenom,basis,zonder)" lemma="rheumatisch">rheumatisch</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.21" pos="N(soort,ev,basis,zijd,stan)" lemma="vader">vader</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.22" pos="WW(vd,vrij,zonder)" lemma="bedenken">bedacht</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.23" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.1" pos="VZ(init)" lemma="in">In</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.2" pos="TW(hoofd,vrij)" lemma="1949">1949</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.3" pos="WW(pv,verl,ev)" lemma="publiceren">publiceerde</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.4" pos="N(soort,mv,basis)" lemma="eigengrün">Eigengrün</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.5" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.6" pos="N(soort,ev,basis,onz,stan)" lemma="artikel">artikel</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.7" pos="BW()" lemma="waarin">waarin</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.8" pos="VNW(pers,pron,nomin,vol,3,ev,masc)" lemma="hij">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.9" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="uitvinding">uitvinding</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.11" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="claimde">claimde</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.14" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.6">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.1" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">Deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="claim">claim</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.3" pos="WW(pv,verl,ev)" lemma="worden">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.4" pos="WW(vd,vrij,zonder)" lemma="bevestigen">bevestigd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.5" pos="VZ(init)" lemma="na">na</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.6" pos="N(soort,ev,basis,onz,stan)" lemma="onderzoek">onderzoek</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.7" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.8" pos="SPEC(deeleigen)" lemma="_">Walter</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.9" pos="SPEC(deeleigen)" lemma="_">Sneader</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.10" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.11" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="universiteit">universiteit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.13" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.14" pos="N(eigen,ev,basis,zijd,stan)" lemma="Glasgow">Glasgow</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.15" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.16" pos="TW(hoofd,vrij)" lemma="1999">1999</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.17" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.7">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.1" pos="N(soort,mv,basis)" lemma="salicylzuur">Salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.2" pos="WW(pv,verl,ev)" lemma="worden">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.3" pos="BW()" lemma="al">al</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.4" pos="WW(vd,vrij,zonder)" lemma="gebruiken">gebruikt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.5" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.6" pos="BW()" lemma="zelfs">zelfs</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.7" pos="N(eigen,ev,basis,zijd,stan)" lemma="Hippocrates">Hippocrates</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.8" pos="WW(pv,verl,ev)" lemma="kennen">kende</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.9" pos="VNW(aanw,adv-pron,stan,red,3,getal)" lemma="er">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.10" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.11" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.12" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.13" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.14" pos="VG(neven)" lemma="maar">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.15" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.16" pos="WW(pv,verl,ev)" lemma="zijn">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.17" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.18" pos="ADJ(prenom,basis,zonder)" lemma="walgelijk">walgelijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.19" pos="N(soort,ev,dim,onz,stan)" lemma="goed">goedje</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.20" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.21" pos="ADJ(vrij,basis,zonder)" lemma="erg">erg</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.22" pos="ADJ(vrij,basis,zonder)" lemma="slecht">slecht</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.23" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.24" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.25" pos="N(soort,ev,basis,zijd,stan)" lemma="maag">maag</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.26" pos="WW(pv,verl,ev)" lemma="liggen">lag</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.27" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.8">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.1" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">Dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="zuur">zuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.3" pos="WW(pv,verl,ev)" lemma="worden">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.4" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.5" pos="TW(rang,prenom,stan)" lemma="eerste">eerste</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="instantie">instantie</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.7" pos="ADJ(vrij,basis,zonder)" lemma="geëxtraheerd">geëxtraheerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.8" pos="VZ(init)" lemma="uit">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.9" pos="N(soort,ev,basis,zijd,stan)" lemma="bast">bast</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.10" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.11" pos="N(soort,mv,basis)" lemma="lid">leden</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.12" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.13" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.14" pos="N(soort,ev,basis,zijd,stan)" lemma="plantenfamilie">plantenfamilie</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.15" pos="LID(bep,gen,rest3)" lemma="de">der</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.16" pos="N(soort,mv,basis)" lemma="wilg">wilgen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.17" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.18" pos="ADJ(prenom,basis,met-e,stan)" lemma="Latijns">Latijnse</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.19" pos="N(soort,ev,basis,zijd,stan)" lemma="gelachtsnaam">gelachtsnaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.20" pos="N(soort,ev,basis,onz,stan)" lemma="salix">Salix</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.21" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.22" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.23" pos="BW()" lemma="vandaar">vandaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.24" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.25" pos="N(soort,ev,basis,zijd,stan)" lemma="naam">naam</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.26" pos="N(soort,ev,basis,onz,stan)" lemma="salicylzuur">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.27" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.9">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.1" pos="ADJ(vrij,basis,zonder)" lemma="Hetzelfde">Hetzelfde</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="zuur">zuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.3" pos="WW(pv,verl,ev)" lemma="zijn">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.4" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.5" pos="WW(inf,vrij,zonder)" lemma="vinden">vinden</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.6" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.7" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="moerasspirea">Moerasspirea</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.9" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.10" pos="BW()" lemma="vandaar">vandaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.11" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.12" pos="LET()" lemma="'">'</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="spir">spir</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.14" pos="LET()" lemma="'">'</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.15" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.16" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.17" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.10">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Hoffmann">Hoffmann</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.2" pos="WW(pv,verl,ev)" lemma="gaan">ging</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.3" pos="ADJ(vrij,basis,zonder)" lemma="systematisch">systematisch</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.4" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.5" pos="N(soort,ev,basis,onz,stan)" lemma="werk">werk</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.6" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.7" pos="WW(pv,verl,ev)" lemma="zoeken">zocht</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.8" pos="ADJ(vrij,basis,zonder)" lemma="hardnekkig">hardnekkig</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.9" pos="VZ(init)" lemma="naar">naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.10" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.11" pos="ADJ(prenom,basis,met-e,stan)" lemma="nieuw">nieuwe</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="verbinding">verbinding</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.13" pos="VZ(init)" lemma="om">om</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.14" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.15" pos="N(soort,ev,basis,onz,stan)" lemma="middel">middel</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.16" pos="ADJ(vrij,comp,zonder)" lemma="goed">beter</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.17" pos="ADJ(vrij,basis,zonder)" lemma="verteerbaar">verteerbaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.18" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.19" pos="WW(inf,vrij,zonder)" lemma="maken">maken</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.20" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.11">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.1" pos="VZ(init)" lemma="volgens">Volgens</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.2" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.3" pos="N(soort,ev,basis,onz,stan)" lemma="principe">principe</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.4" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.5" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="veredeling">veredeling</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.7" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.8" pos="WW(od,prenom,met-e)" lemma="bestaan">bestaande</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.9" pos="N(soort,mv,basis)" lemma="geneesmiddel">geneesmiddelen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.10" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.11" pos="BW()" lemma="waarmee">waarmee</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.12" pos="VNW(pers,pron,nomin,vol,3,ev,masc)" lemma="hij">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.13" pos="BW()" lemma="al">al</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.14" pos="BW()" lemma="eerder">eerder</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.15" pos="N(soort,ev,basis,onz,stan)" lemma="succes">succes</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.16" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.17" pos="WW(vd,vrij,zonder)" lemma="boeken">geboekt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.18" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.19" pos="WW(pv,tgw,met-t)" lemma="ontdekken">ontdekt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.20" pos="VNW(pers,pron,nomin,vol,3,ev,masc)" lemma="hij">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.21" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.22" pos="TW(hoofd,vrij)" lemma="1897">1897</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.23" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.24" pos="N(soort,ev,basis,zijd,stan)" lemma="oplossing">oplossing</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.25" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.26" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.27" pos="N(soort,ev,basis,onz,stan)" lemma="probleem">probleem</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.28" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.29" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.30" pos="N(soort,ev,basis,zijd,stan)" lemma="acetylering">acetylering</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.31" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.32" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.33" pos="N(soort,ev,basis,onz,stan)" lemma="salicylzuur">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.34" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.12">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.1" pos="VZ(init)" lemma="op">Op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.2" pos="TW(hoofd,vrij)" lemma="10">10</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.3" pos="N(eigen,ev,basis,zijd,stan)" lemma="augustus">augustus</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.4" pos="WW(pv,tgw,met-t)" lemma="beschrijven">beschrijft</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.5" pos="VNW(pers,pron,nomin,vol,3,ev,masc)" lemma="hij">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.6" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.7" pos="WW(pv,tgw,mv)" lemma="zijn">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="laboratoriumdagboek">laboratoriumdagboek</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.9" pos="BW()" lemma="hoe">hoe</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.10" pos="VNW(pers,pron,nomin,vol,3,ev,masc)" lemma="hij">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.11" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.12" pos="N(soort,ev,basis,onz,stan)" lemma="acetylsalicylzuur">acetylsalicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.13" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.14" pos="ADJ(vrij,basis,zonder)" lemma="chemisch">chemisch</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.15" pos="ADJ(prenom,basis,met-e,stan)" lemma="zuiver">zuivere</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.16" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.17" pos="ADJ(prenom,basis,met-e,stan)" lemma="bewaarbaar">bewaarbare</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.18" pos="N(soort,ev,basis,zijd,stan)" lemma="vorm">vorm</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.19" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.20" pos="WW(vd,vrij,zonder)" lemma="samengesteld">samengesteld</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.21" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.13">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.1" pos="VG(onder)" lemma="nadat">Nadat</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.2" pos="VNW(pers,pron,nomin,vol,3,ev,masc)" lemma="hij">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.3" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.4" pos="ADJ(prenom,basis,met-e,stan)" lemma="nieuw">nieuwe</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="stof">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.6" pos="BW()" lemma="samen">samen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.7" pos="VZ(init)" lemma="met">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="dokter">dokter</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.9" pos="SPEC(deeleigen)" lemma="_">Heinrich</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.10" pos="SPEC(deeleigen)" lemma="_">Dreser</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.11" pos="ADJ(vrij,basis,zonder)" lemma="uitbreiden">uitgebreid</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.12" pos="WW(vd,vrij,zonder)" lemma="testen">getest</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.13" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.14" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.15" pos="N(soort,mv,basis)" lemma="dier">dieren</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.16" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.17" pos="WW(pv,tgw,met-t)" lemma="komen">komt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.18" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.19" pos="N(soort,ev,basis,zijd,stan)" lemma="stof">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.20" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.21" pos="TW(hoofd,vrij)" lemma="1899">1899</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.22" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.23" pos="N(soort,ev,basis,zijd,stan)" lemma="poedervorm">poedervorm</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.24" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.25" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.26" pos="N(soort,ev,basis,zijd,stan)" lemma="markt">markt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.27" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.14">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.1" pos="LID(onbep,stan,agr)" lemma="een">Een</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="jaar">jaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.3" pos="ADJ(vrij,comp,zonder)" lemma="laat">later</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.4" pos="WW(pv,tgw,mv)" lemma="zijn">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.5" pos="VNW(aanw,adv-pron,stan,red,3,getal)" lemma="er">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.6" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.7" pos="ADJ(prenom,basis,met-e,stan)" lemma="gedoseerde">gedoseerde</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.8" pos="N(soort,mv,basis)" lemma="tablet">tabletten</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.9" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.15">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.1" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="wereldverbruik">wereldverbruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.3" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.4" pos="BW()" lemma="vandaag">vandaag</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.5" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.6" pos="N(soort,mv,basis)" lemma="dag">dag</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.7" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.8" pos="ADJ(vrij,basis,zonder)" lemma="vijftigduizend">vijftigduizend</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.9" pos="N(soort,ev,basis,zijd,stan)" lemma="ton">ton</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.10" pos="VG(neven)" lemma="of">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.11" pos="BW()" lemma="ongeveer">ongeveer</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.12" pos="TW(hoofd,prenom,stan)" lemma="honderd">honderd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.13" pos="N(soort,ev,basis,onz,stan)" lemma="miljard">miljard</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.14" pos="N(soort,mv,basis)" lemma="tablet">tabletten</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.15" pos="VZ(init)" lemma="per">per</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.16" pos="N(soort,ev,basis,onz,stan)" lemma="jaar">jaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.17" pos="WW(vd,vrij,zonder)" lemma="schatten">geschat</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.18" pos="LET()" lemma=".">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.3">
        <head xml:id="WR-P-E-J-0000125009.head.3">
          <s xml:id="WR-P-E-J-0000125009.head.3.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.3.s.1.w.1" pos="N(soort,ev,basis,zijd,stan)" lemma="geschiedenis">Geschiedenis</w>
            <w xml:id="WR-P-E-J-0000125009.head.3.s.1.w.2" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.head.3.s.1.w.3" pos="N(soort,ev,basis,zijd,stan)" lemma="aspro">Aspro</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.5">
          <s xml:id="WR-P-E-J-0000125009.p.5.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.1" pos="VZ(init)" lemma="tijdens">Tijdens</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.2" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.3" pos="ADJ(prenom,basis,met-e,stan)" lemma="1ste">1ste</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.4" pos="N(soort,ev,basis,zijd,stan)" lemma="wereldoorlog">Wereldoorlog</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.5" pos="WW(pv,verl,ev)" lemma="loven">loofde</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.6" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.7" pos="ADJ(prenom,basis,met-e,stan)" lemma="Brits">Britse</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="regering">regering</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.9" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="prijs">prijs</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.11" pos="VZ(fin)" lemma="uit">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.12" pos="VZ(init)" lemma="voor">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="eenieder">eenieder</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.14" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.15" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.16" pos="ADJ(prenom,basis,met-e,stan)" lemma="nieuw">nieuwe</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.17" pos="N(soort,ev,basis,zijd,stan)" lemma="formule">formule</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.18" pos="WW(pv,verl,ev)" lemma="kunnen">kon</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.19" pos="WW(inf,vrij,zonder)" lemma="vinden">vinden</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.20" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.21" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.22" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.23" pos="VZ(init)" lemma="gezien">gezien</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.24" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.25" pos="N(soort,ev,basis,onz,stan)" lemma="feit">feit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.26" pos="VG(onder)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.27" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.28" pos="N(soort,ev,basis,zijd,stan)" lemma="invoer">invoer</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.29" pos="VZ(init)" lemma="uit">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.30" pos="N(eigen,ev,basis,onz,stan)" lemma="Duitsland">Duitsland</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.31" pos="ADJ(vrij,basis,zonder)" lemma="stil">stil</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.32" pos="WW(pv,verl,ev)" lemma="liggen">lag</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.33" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.5.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.1" pos="LID(onbep,stan,agr)" lemma="een">Een</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="chemicus">chemicus</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.3" pos="VZ(init)" lemma="uit">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.4" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.5" pos="ADJ(prenom,basis,met-e,stan)" lemma="Australisch">Australische</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="melbourne">Melbourne</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.7" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.8" pos="SPEC(deeleigen)" lemma="_">George</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.9" pos="SPEC(deeleigen)" lemma="_">Nicholas</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.10" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.11" pos="WW(pv,verl,ev)" lemma="ontdekken">ontdekte</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.12" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.13" pos="TW(hoofd,vrij)" lemma="1915">1915</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.14" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.15" pos="ADJ(prenom,basis,met-e,stan)" lemma="synthetisch">synthetische</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.16" pos="N(soort,ev,basis,zijd,stan)" lemma="oplossing">oplossing</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.17" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.18" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.19" pos="BW()" lemma="zelfs">zelfs</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.20" pos="ADJ(vrij,comp,zonder)" lemma="zuiver">zuiverder</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.21" pos="WW(pv,verl,ev)" lemma="zijn">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.22" pos="BW()" lemma="dan">dan</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.23" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.24" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.25" pos="ADJ(prenom,basis,zonder)" lemma="oplosbaar">oplosbaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.26" pos="WW(pv,verl,ev)" lemma="zijn">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.27" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.5.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.1" pos="VNW(pers,pron,nomin,vol,3,ev,masc)" lemma="hij">Hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.2" pos="WW(pv,verl,ev)" lemma="noemen">noemde</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.3" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.4" pos="SPEC(deeleigen)" lemma="_">Aspro</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.5" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.6" pos="VNW(vb,pron,stan,vol,3o,ev)" lemma="wat">wat</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.7" pos="ADJ(vrij,comp,zonder)" lemma="laat">later</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.8" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.9" pos="ADJ(prenom,basis,met-e,stan)" lemma="geheel">gehele</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="wereld">wereld</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.11" pos="WW(pv,verl,ev)" lemma="veroveren">veroverde</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.12" pos="LET()" lemma=".">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.4">
        <head xml:id="WR-P-E-J-0000125009.head.4">
          <s xml:id="WR-P-E-J-0000125009.head.4.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.4.s.1.w.1" pos="ADJ(prenom,basis,met-e,stan)" lemma="Pijnstillende">Pijnstillende</w>
            <w xml:id="WR-P-E-J-0000125009.head.4.s.1.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.head.4.s.2">
            <w xml:id="WR-P-E-J-0000125009.head.4.s.2.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.6">
          <s xml:id="WR-P-E-J-0000125009.p.6.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.1" pos="N(soort,ev,basis,zijd,stan)" lemma="pijn">Pijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.2" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.3" pos="WW(pv,tgw,met-t)" lemma="veroorzaken">veroorzaakt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.4" pos="VZ(init)" lemma="door">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.5" pos="ADJ(prenom,basis,met-e,stan)" lemma="verschillend">verschillende</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.6" pos="N(soort,mv,basis)" lemma="stof">stoffen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.7" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.8" pos="N(soort,mv,basis)" lemma="vrijkomen">vrijkomen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.9" pos="VZ(init)" lemma="bij">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.10" pos="N(soort,mv,basis)" lemma="beschadiging">beschadigingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.11" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.1" pos="ADJ(prenom,basis,met-e,stan)" lemma="Werkende">Werkende</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.2" pos="N(soort,mv,basis)" lemma="cel">cellen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.3" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.4" pos="WW(vd,prenom,zonder)" lemma="beschadigen">beschadigd</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.5" pos="N(soort,ev,basis,onz,stan)" lemma="weefsel">weefsel</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.6" pos="WW(pv,tgw,mv)" lemma="geven">geven</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.7" pos="VNW(aanw,det,stan,prenom,zonder,rest)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.8" pos="N(soort,mv,basis)" lemma="stof">stoffen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.9" pos="VZ(fin)" lemma="af">af</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.10" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.11" pos="VZ(init)" lemma="onder">onder</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="invloed">invloed</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.13" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.14" pos="BW()" lemma="o.a.">o.a.</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.15" pos="N(soort,mv,basis)" lemma="cytokine">cytokinen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.16" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.17" pos="N(soort,mv,basis)" lemma="mitogeen">mitogenen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.18" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.1" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">Deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.2" pos="N(soort,mv,basis)" lemma="stof">stoffen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.3" pos="WW(pv,tgw,mv)" lemma="werken">werken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.4" pos="BW()" lemma="dan">dan</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.5" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.6" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.7" pos="N(soort,mv,basis)" lemma="zenuwuiteinde">zenuwuiteinden</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.8" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.9" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.10" pos="N(soort,ev,basis,onz,stan)" lemma="pijnsignaal">pijnsignaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.11" pos="VZ(init)" lemma="naar">naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.12" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.13" pos="N(soort,mv,basis)" lemma="hersenen">hersenen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.14" pos="WW(inf,vrij,zonder)" lemma="doorsturen">doorsturen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.15" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.1" pos="LID(onbep,stan,agr)" lemma="een">Een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="hormoon">hormoon</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.3" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.4" pos="VG(onder)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.5" pos="BW()" lemma="daarin">daarin</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.6" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.7" pos="ADJ(prenom,basis,met-e,stan)" lemma="belangrijk">belangrijke</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="rol">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.9" pos="WW(pv,tgw,met-t)" lemma="spelen">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.10" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.11" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.12" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.1" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">Prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.2" pos="WW(pv,tgw,met-t)" lemma="geven">geeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.3" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.4" pos="BW()" lemma="alleen">alleen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.5" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="pijnsignaal">pijnsignaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.7" pos="VZ(fin)" lemma="af">af</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.8" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.9" pos="VG(neven)" lemma="maar">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.10" pos="WW(pv,tgw,met-t)" lemma="spelen">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.11" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.12" pos="ADJ(prenom,basis,met-e,stan)" lemma="belangrijk">belangrijke</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="rol">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.14" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.15" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.16" pos="ADJ(prenom,basis,met-e,stan)" lemma="heel">hele</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.17" pos="N(soort,ev,basis,onz,stan)" lemma="lichaam">lichaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.18" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.6">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.1" pos="BW()" lemma="daarom">Daarom</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.2" pos="BW()" lemma="eerst">eerst</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.3" pos="VNW(onbep,pron,stan,vol,3o,ev)" lemma="wat">wat</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.4" pos="VNW(onbep,grad,stan,vrij,zonder,comp)" lemma="veel">meer</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.5" pos="VZ(init)" lemma="over">over</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">Prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.7" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.7">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.1" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">Prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.2" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.3" pos="WW(vd,vrij,zonder)" lemma="produceren">geproduceerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.4" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.5" pos="N(soort,mv,basis)" lemma="cel">cellen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.6" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.7" pos="WW(pv,tgw,met-t)" lemma="werken">werkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.8" pos="BW()" lemma="alleen">alleen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.9" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.10" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.11" pos="N(soort,ev,basis,zijd,stan)" lemma="buurt">buurt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.12" pos="VNW(vb,adv-pron,obl,vol,3o,getal)" lemma="waar">waar</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.13" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.14" pos="WW(vd,vrij,zonder)" lemma="produceren">geproduceerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.15" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.16" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.17" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.18" pos="BW()" lemma="dan">dan</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.19" pos="WW(vd,vrij,zonder)" lemma="afbreken">afgebroken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.20" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.8">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.1" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.2" pos="WW(pv,tgw,met-t)" lemma="stimuleren">stimuleert</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.3" pos="VZ(init)" lemma="naast">naast</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.4" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="pijnreactie">pijnreactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.6" pos="BW()" lemma="ook">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.7" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="ontstekingsreactie">ontstekingsreactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.9" pos="VG(onder)" lemma="wanneer">wanneer</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.10" pos="VNW(aanw,adv-pron,stan,red,3,getal)" lemma="er">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.11" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="infectie">infectie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.13" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.14" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.15" pos="WW(pv,tgw,met-t)" lemma="zorgen">zorgt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.16" pos="VZ(init)" lemma="voor">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.17" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.18" pos="N(soort,ev,basis,zijd,stan)" lemma="verhoging">verhoging</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.19" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.20" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.21" pos="N(soort,ev,basis,zijd,stan)" lemma="lichaamstemperatuur">lichaamstemperatuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.22" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.9">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.1" pos="VZ(init)" lemma="in">In</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.2" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.3" pos="N(soort,mv,basis)" lemma="cel">cellen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.4" pos="WW(pv,tgw,met-t)" lemma="spelen">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.5" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="cyclooxygenase">cyclooxygenase</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.7" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="cox">COX</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.9" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="enzym">enzym</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.11" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.12" pos="ADJ(prenom,basis,met-e,stan)" lemma="onmisbaar">onmisbare</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="rol">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.14" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.15" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.16" pos="WW(inf,nom,zonder,zonder-n)" lemma="maken">maken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.17" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.18" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.19" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.10">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.1" pos="N(soort,ev,basis,zijd,stan)" lemma="cyclooxygenase">Cyclooxygenase</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.2" pos="WW(pv,tgw,met-t)" lemma="katalyseren">katalyseert</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.3" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.4" pos="N(soort,ev,basis,zijd,stan)" lemma="omzetting">omzetting</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.5" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="arachidonzuur">arachidonzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.7" pos="VZ(init)" lemma="naar">naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.9" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.10" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.11" pos="N(soort,ev,basis,zijd,stan)" lemma="reactie">reactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.12" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.13" pos="BW()" lemma="ander">anders</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.14" pos="BW()" lemma="vrijwel">vrijwel</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.15" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.16" pos="WW(pv,tgw,met-t)" lemma="verlopen">verloopt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.17" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.11">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.3" pos="WW(pv,tgw,met-t)" lemma="voorkomen">voorkomt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.4" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.6" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.7" pos="N(eigen,ev,basis,onz,stan)" lemma="Cyclooxygenase">Cyclooxygenase</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.8" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.9" pos="WW(pv,tgw,met-t)" lemma="voorkomen">voorkomt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.10" pos="BW()" lemma="daarmee">daarmee</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.11" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="vorming">vorming</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.13" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.14" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.15" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.16" pos="BW()" lemma="waardoor">waardoor</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.17" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.18" pos="ADJ(prenom,basis,zonder)" lemma="groot">groot</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.19" pos="N(soort,ev,basis,onz,stan)" lemma="gedeelte">gedeelte</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.20" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.21" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.22" pos="N(soort,ev,basis,zijd,stan)" lemma="pijn">pijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.23" pos="WW(pv,tgw,met-t)" lemma="verdwijnen">verdwijnt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.24" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.25" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.26" pos="BW()" lemma="ook">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.27" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.28" pos="N(soort,ev,basis,zijd,stan)" lemma="koorts">koorts</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.29" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.30" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.31" pos="N(soort,ev,basis,zijd,stan)" lemma="ontsteking">ontsteking</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.32" pos="WW(vd,vrij,zonder)" lemma="remmen">geremd</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.33" pos="WW(pv,tgw,mv)" lemma="worden">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.34" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.35" pos="VG(onder)" lemma="omdat">omdat</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.36" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.37" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.38" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.39" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.40" pos="N(soort,mv,basis)" lemma="reactie">reacties</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.41" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.42" pos="VNW(onbep,grad,stan,vrij,zonder,comp)" lemma="veel">meer</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.43" pos="WW(pv,tgw,ev)" lemma="kunnen">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.44" pos="WW(inf,vrij,zonder)" lemma="veroorzaken">veroorzaken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.45" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.12">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.2" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.3" pos="BW()" lemma="dus">dus</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.4" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="inhibitor">inhibitor</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.6" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.7" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="stof">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.9" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.10" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.11" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.12" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.13" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.14" pos="N(soort,ev,basis,onz,stan)" lemma="eiwit">eiwit</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.15" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.16" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.17" pos="VNW(aanw,det,stan,prenom,zonder,evon)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.18" pos="N(soort,ev,basis,onz,stan)" lemma="geval">geval</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.19" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.20" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.21" pos="N(soort,ev,basis,zijd,stan)" lemma="cox">COX</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.22" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.23" pos="WW(pv,tgw,met-t)" lemma="remmen">remt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.24" pos="VG(neven)" lemma="of">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.25" pos="WW(pv,tgw,met-t)" lemma="stoppen">stopt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.26" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.13">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.1" pos="BW()" lemma="daarnaast">Daarnaast</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.2" pos="WW(pv,tgw,met-t)" lemma="spelen">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.3" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.4" pos="BW()" lemma="ook">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.5" pos="BW()" lemma="nog">nog</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.6" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.7" pos="N(soort,ev,basis,zijd,stan)" lemma="rol">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.8" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.9" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.10" pos="ADJ(prenom,basis,zonder)" lemma="normaal">normaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.11" pos="WW(inf,vrij,zonder)" lemma="functioneren">functioneren</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.12" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.14">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.3" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.4" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.5" pos="WW(vd,vrij,zonder)" lemma="maken">gemaakt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.6" pos="VZ(init)" lemma="door">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.7" pos="N(eigen,ev,basis,zijd,stan)" lemma="Cox-1">COX-1</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.8" pos="WW(pv,tgw,met-t)" lemma="werken">werkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.9" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.10" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.11" pos="ADJ(prenom,basis,met-e,stan)" lemma="normaal">normale</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.12" pos="N(soort,mv,basis)" lemma="proces">processen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.13" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.14" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.15" pos="N(soort,ev,basis,zijd,stan)" lemma="boodschapper">boodschapper</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.16" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.15">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="prostaglandine">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.3" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.4" pos="WW(pv,tgw,met-t)" lemma="werken">werkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.5" pos="VZ(init)" lemma="bij">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="beschadiging">beschadiging</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.7" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.8" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.9" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="rol">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.11" pos="WW(pv,tgw,met-t)" lemma="spelen">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.12" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.13" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.14" pos="N(soort,ev,basis,onz,stan)" lemma="pijnsignaal">pijnsignaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.15" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.16" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.17" pos="WW(vd,vrij,zonder)" lemma="maken">gemaakt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.18" pos="VZ(init)" lemma="door">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.19" pos="N(eigen,ev,basis,zijd,stan)" lemma="Cox-2">COX-2</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.20" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.16">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Cox-1">COX-1</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.2" pos="WW(pv,tgw,ev)" lemma="kunnen">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.3" pos="VG(onder)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.4" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.5" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.6" pos="WW(pv,tgw,met-t)" lemma="functioneren">functioneert</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.7" pos="N(soort,mv,basis)" lemma="maagbloeding">maagbloedingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.8" pos="SPEC(afk)" lemma="_">e.d.</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.9" pos="WW(inf,vrij,zonder)" lemma="veroorzaken">veroorzaken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.10" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.17">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.1" pos="VNW(aanw,adv-pron,stan,red,3,getal)" lemma="er">Er</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.2" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.3" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.4" pos="VZ(init)" lemma="sinds">sinds</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.5" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.6" pos="N(soort,ev,basis,onz,stan)" lemma="aantal">aantal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.7" pos="N(soort,mv,basis)" lemma="jaar">jaren</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.8" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.9" pos="N(soort,ev,basis,onz,stan)" lemma="aantal">aantal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.10" pos="ADJ(prenom,basis,met-e,stan)" lemma="ander">andere</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.11" pos="N(soort,mv,basis)" lemma="geneesmiddel">geneesmiddelen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.12" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.13" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.14" pos="N(soort,ev,basis,zijd,stan)" lemma="markt">markt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.15" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.16" pos="ADJ(vrij,basis,zonder)" lemma="selectief">selectief</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.17" pos="N(eigen,ev,basis,zijd,stan)" lemma="Cox-2">COX-2</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.18" pos="WW(inf,vrij,zonder)" lemma="remmen">remmen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.19" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.18">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.18.w.1" pos="WW(pv,tgw,ev)" lemma="zien">Zie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.18.w.2" pos="N(eigen,ev,basis,zijd,stan)" lemma="Cox-2">COX-2</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.18.w.3" pos="N(soort,mv,basis)" lemma="remmer">remmers</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.18.w.4" pos="LET()" lemma=".">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.5">
        <head xml:id="WR-P-E-J-0000125009.head.5">
          <s xml:id="WR-P-E-J-0000125009.head.5.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.5.s.1.w.1" pos="ADJ(prenom,basis,met-e,stan)" lemma="ander">Andere</w>
            <w xml:id="WR-P-E-J-0000125009.head.5.s.1.w.2" pos="N(soort,mv,basis)" lemma="werking">werkingen</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.head.5.s.2">
            <w xml:id="WR-P-E-J-0000125009.head.5.s.2.w.1" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">Werking</w>
            <w xml:id="WR-P-E-J-0000125009.head.5.s.2.w.2" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.head.5.s.2.w.3" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.head.5.s.2.w.4" pos="N(soort,mv,dim)" lemma="bloedplaatje">bloedplaatjes</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.7">
          <s xml:id="WR-P-E-J-0000125009.p.7.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.2" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.3" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.4" pos="BW()" lemma="alleen">alleen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.5" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.6" pos="N(soort,ev,basis,onz,stan)" lemma="analgeticum">analgeticum</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.7" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.8" pos="ADJ(prenom,basis,zonder)" lemma="pijnstillend">pijnstillend</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.9" pos="N(soort,ev,basis,onz,stan)" lemma="middel">middel</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.10" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.11" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.12" pos="VG(neven)" lemma="maar">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.13" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.14" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.15" pos="BW()" lemma="ook">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.16" pos="BW()" lemma="nog">nog</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.17" pos="ADJ(prenom,basis,met-e,stan)" lemma="ander">andere</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.18" pos="N(soort,mv,basis)" lemma="effect">effecten</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.19" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.20" pos="VNW(pr,pron,obl,vol,1,mv)" lemma="ons">ons</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.21" pos="N(soort,ev,basis,onz,stan)" lemma="lichaam">lichaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.22" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.2" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.3" pos="TW(hoofd,vrij)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.4" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.5" pos="ADJ(prenom,basis,zonder)" lemma="onomkeerbaar">onomkeerbaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.6" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.7" pos="N(soort,ev,basis,onz,stan)" lemma="effect">effect</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.8" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.9" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.10" pos="N(soort,mv,dim)" lemma="bloedplaatje">bloedplaatjes</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.11" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.12" pos="WW(pv,tgw,met-t)" lemma="belemmeren">belemmert</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.13" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.14" pos="VZ(init)" lemma="om">om</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.15" pos="BW()" lemma="samen">samen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.16" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.17" pos="WW(inf,vrij,zonder)" lemma="klonteren">klonteren</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.18" pos="LET()" lemma=":">:</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.19" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.20" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.21" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.22" pos="N(soort,ev,basis,zijd,stan)" lemma="trombocytenaggregatieremmer">trombocytenaggregatieremmer</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.23" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.1" pos="BW()" lemma="hierdoor">Hierdoor</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.2" pos="WW(pv,tgw,met-t)" lemma="verminderen">vermindert</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.3" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.4" pos="ADJ(prenom,basis,zonder)" lemma="stelpend">stelpend</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.5" pos="N(soort,ev,basis,onz,stan)" lemma="vermogen">vermogen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.6" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.7" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.8" pos="N(soort,ev,basis,onz,stan)" lemma="bloed">bloed</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.9" pos="VZ(init)" lemma="bij">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="bloedvatbeschadiging">bloedvatbeschadiging</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.11" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.2" pos="BW()" lemma="vaak">vaak</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.3" pos="WW(vd,prenom,met-e)" lemma="gebruiken">gebruikte</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.4" pos="N(soort,ev,basis,zijd,stan)" lemma="benaming">benaming</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.5" pos="LET()" lemma="'">'</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="bloedverdunner">bloedverdunner</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.7" pos="LET()" lemma="'">'</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.8" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.9" pos="ADJ(vrij,basis,zonder)" lemma="onjuist">onjuist</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.10" pos="LET()" lemma="-">-</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.11" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.12" pos="N(soort,ev,basis,onz,stan)" lemma="bloed">bloed</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.13" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.14" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.15" pos="ADJ(vrij,comp,zonder)" lemma="dun">dunner</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.16" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.1" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">Dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="effect">effect</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.3" pos="WW(pv,tgw,met-t)" lemma="treden">treedt</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.4" pos="BW()" lemma="al">al</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.5" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.6" pos="VZ(init)" lemma="na">na</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.7" pos="TW(hoofd,prenom,stan)" lemma="1/4">1/4</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.8" pos="N(soort,ev,basis,onz,stan)" lemma="aspirinetablet">aspirinetablet</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.9" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.10" pos="WW(pv,tgw,met-t)" lemma="houden">houdt</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.11" pos="VZ(init)" lemma="aan">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.12" pos="VZ(init)" lemma="tot">tot</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.13" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.14" pos="ADJ(prenom,basis,met-e,stan)" lemma="uitgeschakelde">uitgeschakelde</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.15" pos="N(soort,mv,dim)" lemma="bloedplaatje">bloedplaatjes</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.16" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.17" pos="VZ(init)" lemma="na">na</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.18" pos="BW()" lemma="ongeveer">ongeveer</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.19" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.20" pos="N(soort,ev,basis,zijd,stan)" lemma="week">week</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.21" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.22" pos="BW()" lemma="allemaal">allemaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.23" pos="WW(pv,tgw,mv)" lemma="zijn">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.24" pos="WW(vd,vrij,zonder)" lemma="vervangen">vervangen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.25" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.6">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.1" pos="VZ(init)" lemma="voor">Voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.2" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.3" pos="ADJ(prenom,sup,met-e,stan)" lemma="laat">laatste</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.4" pos="N(soort,ev,basis,onz,stan)" lemma="effect">effect</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.5" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.6" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.7" pos="N(soort,ev,basis,onz,stan)" lemma="middel">middel</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.8" pos="ADJ(vrij,basis,zonder)" lemma="tegenwoordig">tegenwoordig</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.9" pos="BW()" lemma="zeer">zeer</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.10" pos="VNW(onbep,grad,stan,vrij,zonder,basis)" lemma="veel">veel</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.11" pos="WW(vd,vrij,zonder)" lemma="voorschrijven">voorgeschreven</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.12" pos="VZ(init)" lemma="aan">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.13" pos="N(soort,mv,basis)" lemma="mens">mensen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.14" pos="VNW(betr,pron,stan,vol,persoon,getal)" lemma="die">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.15" pos="BW()" lemma="eerder">eerder</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.16" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.17" pos="N(soort,ev,basis,zijd,stan)" lemma="beroerte">beroerte</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.18" pos="VG(neven)" lemma="of">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.19" pos="N(soort,ev,basis,zijd,stan)" lemma="hartaanval">hartaanval</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.20" pos="WW(pv,tgw,mv)" lemma="hebben">hebben</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.21" pos="WW(vd,vrij,zonder)" lemma="hebben">gehad</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.22" pos="LET()" lemma=";">;</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.23" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.24" pos="WW(pv,tgw,met-t)" lemma="verminderen">vermindert</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.25" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.26" pos="N(soort,mv,basis)" lemma="kan">kans</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.27" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.28" pos="N(soort,ev,basis,zijd,stan)" lemma="herhaling">herhaling</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.29" pos="VZ(init)" lemma="met">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.30" pos="BW()" lemma="ca">ca</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.31" pos="TW(hoofd,prenom,stan)" lemma="40">40</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.32" pos="N(soort,ev,basis,onz,stan)" lemma="%">%</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.33" pos="LET()" lemma=".">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.6">
        <head xml:id="WR-P-E-J-0000125009.head.6">
          <s xml:id="WR-P-E-J-0000125009.head.6.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.6.s.1.w.1" pos="ADJ(prenom,basis,met-e,stan)" lemma="ander">Andere</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.8">
          <s xml:id="WR-P-E-J-0000125009.p.8.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.1" pos="BW()" lemma="ook">Ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.2" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.3" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.4" pos="N(soort,ev,basis,onz,stan)" lemma="gebied">gebied</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.5" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.6" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.7" pos="N(soort,ev,basis,zijd,stan)" lemma="kanker-preventie">kanker-preventie</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.8" pos="WW(pv,tgw,mv)" lemma="liggen">liggen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.9" pos="VNW(aanw,adv-pron,stan,red,3,getal)" lemma="er">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.10" pos="ADJ(vrij,basis,zonder)" lemma="mogelijk">mogelijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.11" pos="N(soort,mv,basis)" lemma="toepassing">toepassingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.12" pos="VZ(init)" lemma="voor">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.14" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.15" pos="VG(onder)" lemma="aangezien">aangezien</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.16" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.17" pos="N(soort,ev,basis,zijd,stan)" lemma="tumorvorming">tumorvorming</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.18" pos="N(soort,ev,basis,zijd,stan)" lemma="tegengaat">tegengaat</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.19" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.8.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.1" pos="LID(bep,stan,evon)" lemma="het">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.2" pos="ADJ(prenom,basis,zonder)" lemma="dagelijks">dagelijks</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.3" pos="N(soort,ev,basis,onz,stan)" lemma="slikken">slikken</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.4" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.5" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.6" pos="ADJ(prenom,basis,met-e,stan)" lemma="klein">kleine</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.7" pos="N(soort,ev,basis,zijd,stan)" lemma="dosis">dosis</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.9" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.10" pos="VZ(init)" lemma="gedurende">gedurende</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.11" pos="TW(hoofd,vrij)" lemma="5">5</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.12" pos="N(soort,ev,basis,onz,stan)" lemma="jaar">jaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.13" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.14" pos="WW(pv,verl,ev)" lemma="zullen">zou</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.15" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.16" pos="N(soort,mv,basis)" lemma="kan">kans</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.17" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.18" pos="N(soort,mv,basis)" lemma="tumor">tumoren</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.19" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.20" pos="N(soort,ev,basis,zijd,stan)" lemma="slokdarm">slokdarm</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.21" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.22" pos="N(soort,ev,basis,onz,stan)" lemma="darmstelsel">darmstelsel</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.23" pos="VZ(init)" lemma="met">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.24" pos="TW(hoofd,prenom,stan)" lemma="twee">twee</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.25" pos="TW(rang,prenom,stan)" lemma="derde">derde</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.26" pos="WW(pv,tgw,mv)" lemma="doen">doen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.27" pos="WW(inf,vrij,zonder)" lemma="afnemen">afnemen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.28" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.8.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.1" pos="VZ(init)" lemma="naar">Naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.2" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.3" pos="WW(pv,tgw,met-t)" lemma="schijnen">schijnt</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.4" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.6" pos="BW()" lemma="ook">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.7" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.8" pos="ADJ(prenom,basis,met-e,stan)" lemma="positief">positieve</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.9" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.10" pos="VZ(init)" lemma="tegen">tegen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.11" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="ziekte">ziekte</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.13" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.14" pos="N(soort,ev,basis,onz,stan)" lemma="alzheimer">Alzheimer</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.15" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.16" pos="SPEC(afgebr)" lemma="_">zwangerschaps-</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.17" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.18" pos="SPEC(afgebr)" lemma="_">darm-</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.19" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.20" pos="SPEC(afgebr)" lemma="_">hart-</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.21" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.22" pos="N(soort,mv,basis)" lemma="vaatziekte">vaatziekten</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.23" pos="LET()" lemma=".">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.7">
        <head xml:id="WR-P-E-J-0000125009.head.7">
          <s xml:id="WR-P-E-J-0000125009.head.7.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.7.s.1.w.1" pos="N(soort,mv,basis)" lemma="bijwerking">Bijwerkingen</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.9">
          <s xml:id="WR-P-E-J-0000125009.p.9.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.2" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.3" pos="BW()" lemma="vrij">vrij</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.4" pos="ADJ(vrij,basis,zonder)" lemma="sterk">sterk</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.5" pos="ADJ(vrij,basis,zonder)" lemma="maagprikkelend">maagprikkelend</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.6" pos="LET()" lemma=":">:</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.7" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.8" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.9" pos="BW()" lemma="nu">nu</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.10" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.11" pos="ADJ(prenom,basis,zonder)" lemma="nieuw">nieuw</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.12" pos="N(soort,ev,basis,onz,stan)" lemma="geneesmiddel">geneesmiddel</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.13" pos="WW(pv,verl,ev)" lemma="zullen">zou</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.14" pos="WW(pv,tgw,mv)" lemma="moeten">moeten</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.15" pos="WW(inf,vrij,zonder)" lemma="worden">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.16" pos="WW(inf,vrij,zonder)" lemma="geregistreerd">geregistreerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.17" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.18" pos="N(soort,ev,basis,zijd,stan)" lemma="pijnstiller">pijnstiller</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.19" pos="WW(pv,verl,ev)" lemma="zullen">zou</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.20" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.21" pos="ADJ(vrij,basis,zonder)" lemma="waarschijnlijk">waarschijnlijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.22" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.23" pos="WW(inf,vrij,zonder)" lemma="lukken">lukken</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.24" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.9.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.1" pos="VZ(init)" lemma="bij">Bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="gebruik">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.3" pos="WW(pv,tgw,mv)" lemma="kunnen">kunnen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.4" pos="N(soort,mv,basis)" lemma="maag-klacht">maag-klachten</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.5" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.6" pos="BW()" lemma="zelfs">zelfs</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.7" pos="N(soort,mv,basis)" lemma="maagbloeding">maagbloedingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.8" pos="WW(pv,tgw,mv)" lemma="ontstaan">ontstaan</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.9" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.9.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.1" pos="N(eigen,ev,basis,zijd,stan)" lemma="Aspirine">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.2" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.3" pos="BW()" lemma="vooral">vooral</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.4" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.5" pos="ADJ(prenom,basis,met-e,stan)" lemma="hoog">hoge</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.6" pos="N(soort,mv,basis)" lemma="dosering">doseringen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.7" pos="ADJ(prenom,basis,met-e,stan)" lemma="ernstig">ernstige</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.8" pos="N(soort,mv,basis)" lemma="bijwerking">bijwerkingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.9" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.10" pos="VZ(init)" lemma="met">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.11" pos="N(soort,ev,basis,dat)" lemma="naam">name</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.12" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.13" pos="BW()" lemma="al">al</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.14" pos="WW(vd,prenom,met-e)" lemma="noemen">genoemde</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.15" pos="N(soort,mv,basis)" lemma="maagbloeding">maagbloedingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.16" pos="VG(neven)" lemma="maar">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.17" pos="BW()" lemma="ook">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.18" pos="N(soort,mv,basis)" lemma="oorsuizen">oorsuizen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.19" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.20" pos="N(soort,ev,basis,zijd,stan)" lemma="doofheid">doofheid</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.21" pos="WW(pv,tgw,mv)" lemma="kunnen">kunnen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.22" pos="WW(inf,vrij,zonder)" lemma="optreden">optreden</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.23" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.9.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.1" pos="BW()" lemma="ook">Ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.2" pos="WW(pv,tgw,ev)" lemma="weten">weet</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.3" pos="VNW(pers,pron,nomin,red,3p,ev,masc)" lemma="men">men</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.4" pos="VG(onder)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.5" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.6" pos="N(soort,ev,basis,onz,stan)" lemma="gebruik">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.7" pos="BW()" lemma="ervan">ervan</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.8" pos="ADJ(vrij,basis,zonder)" lemma="tijdelijk">tijdelijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.9" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="aanmaak">aanmaak</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.11" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.12" pos="N(soort,ev,basis,onz,stan)" lemma="testosteron">testosteron</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.13" pos="WW(pv,tgw,met-t)" lemma="verminderen">vermindert</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.14" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.15" pos="VG(neven)" lemma="maar">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.16" pos="VNW(aanw,det,stan,prenom,zonder,evon)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.17" pos="N(soort,ev,basis,onz,stan)" lemma="neveneffect">neveneffect</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.18" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.19" pos="VNW(onbep,det,stan,prenom,zonder,agr)" lemma="geen">geen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.20" pos="WW(od,prenom,met-e)" lemma="blijven">blijvende</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.21" pos="VG(neven)" lemma="of">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.22" pos="ADJ(vrij,basis,zonder)" lemma="erg">erg</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.23" pos="ADJ(prenom,basis,met-e,stan)" lemma="schadelijk">schadelijke</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.24" pos="N(soort,ev,basis,zijd,stan)" lemma="werking">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.25" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.9.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.1" pos="VZ(init)" lemma="naast">Naast</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="gebruik">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.3" pos="VZ(init)" lemma="bij">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.4" pos="N(soort,ev,basis,zijd,stan)" lemma="zwangerschap">zwangerschap</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.5" pos="VG(neven)" lemma="of">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="toediening">toediening</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.7" pos="VZ(init)" lemma="aan">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.8" pos="N(soort,mv,basis)" lemma="baby">baby's</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.9" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.10" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.11" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.12" pos="BW()" lemma="lief">liefst</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.13" pos="BW()" lemma="ook">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.14" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.15" pos="VZ(init)" lemma="met">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.16" pos="N(soort,ev,basis,zijd,stan)" lemma="alcohol">alcohol</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.17" pos="WW(pv,tgw,met-t)" lemma="gebruiken">gebruikt</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.18" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.19" pos="VG(onder)" lemma="omdat">omdat</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.20" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.21" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.22" pos="N(soort,mv,basis)" lemma="kan">kans</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.23" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.24" pos="N(soort,mv,basis)" lemma="maagklacht">maagklachten</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.25" pos="WW(pv,tgw,ev)" lemma="kunnen">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.26" pos="WW(inf,vrij,zonder)" lemma="verhogen">verhogen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.27" pos="LET()" lemma=".">.</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.10">
          <s xml:id="WR-P-E-J-0000125009.p.10.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.1" pos="N(soort,ev,basis,onz,stan)" lemma="advies">Advies</w>
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.2" pos="VZ(init)" lemma="voor">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.3" pos="N(soort,ev,basis,onz,stan)" lemma="gebruik">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.4" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="pijnstiller">pijnstiller</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.11">
          <s xml:id="WR-P-E-J-0000125009.p.11.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.1" pos="VZ(init)" lemma="voor">Voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.2" pos="N(soort,ev,basis,onz,stan)" lemma="gebruik">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.3" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.4" pos="ADJ(prenom,basis,met-e,stan)" lemma="eenvoudig">eenvoudige</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="pijnstiller">pijnstiller</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.6" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.7" pos="ADJ(prenom,basis,zonder)" lemma="medisch">medisch</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.8" pos="WW(vd,prenom,zonder)" lemma="zien">gezien</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.9" pos="ADJ(nom,basis,zonder,zonder-n)" lemma="algemeen">algemeen</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.10" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.11" pos="N(soort,ev,basis,zijd,stan)" lemma="voorkeur">voorkeur</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.12" pos="WW(vd,vrij,zonder)" lemma="geven">gegeven</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.13" pos="VZ(init)" lemma="aan">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.14" pos="N(soort,ev,basis,zijd,stan)" lemma="paracetamol">paracetamol</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.15" pos="LET()" lemma=".">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.8">
        <head xml:id="WR-P-E-J-0000125009.head.8">
          <s xml:id="WR-P-E-J-0000125009.head.8.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.8.s.1.w.1" pos="N(soort,ev,basis,zijd,stan)" lemma="synthese">Synthese</w>
            <w xml:id="WR-P-E-J-0000125009.head.8.s.1.w.2" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.head.8.s.1.w.3" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.12">
          <s xml:id="WR-P-E-J-0000125009.p.12.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.1" pos="VZ(init)" lemma="bij">Bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.2" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.3" pos="WW(inf,nom,zonder,zonder-n)" lemma="maken">maken</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.4" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.5" pos="N(soort,ev,basis,onz,stan)" lemma="acetylsalicylzuur">acetylsalicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.6" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.7" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.8" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.9" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.10" pos="N(soort,ev,basis,onz,stan)" lemma="laboratorium">laboratorium</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.11" pos="N(soort,ev,basis,zijd,stan)" lemma="schaal">schaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.12" pos="WW(pv,tgw,met-t)" lemma="gaan">gaat</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.13" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.14" pos="VZ(init)" lemma="om">om</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.15" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.16" pos="N(soort,ev,basis,zijd,stan)" lemma="opbrengst">opbrengst</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.17" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.18" pos="VNW(onbep,det,stan,prenom,met-e,rest)" lemma="enkel">enkele</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.19" pos="N(soort,mv,basis)" lemma="gram">grammen</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.20" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.12.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.1" pos="VZ(init)" lemma="bij">Bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.2" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.3" pos="N(soort,ev,basis,zijd,stan)" lemma="bereiding">bereiding</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.4" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.6" pos="WW(pv,tgw,ev)" lemma="kunnen">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.7" pos="WW(inf,vrij,zonder)" lemma="worden">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.8" pos="WW(vd,vrij,zonder)" lemma="uitgaan">uitgegaan</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.9" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.10" pos="ADJ(prenom,basis,met-e,stan)" lemma="verschillend">verschillende</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.11" pos="N(soort,ev,basis,onz,stan)" lemma="begin">begin</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.12" pos="N(soort,mv,basis)" lemma="product">producten</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.13" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.14" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.15" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.16" pos="N(soort,ev,basis,zijd,stan)" lemma="beschrijving">beschrijving</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.17" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.18" pos="WW(vd,vrij,zonder)" lemma="uitgaan">uitgegaan</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.19" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.20" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.21" pos="N(soort,ev,basis,zijd,stan)" lemma="beginstof">beginstof</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.22" pos="N(soort,ev,basis,onz,stan)" lemma="salicylzuur">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.23" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.12.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.1" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">Dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.2" pos="WW(pv,tgw,met-t)" lemma="hebben">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.3" pos="VZ(init)" lemma="als">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.4" pos="N(soort,ev,basis,onz,stan)" lemma="voordeel">voordeel</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.5" pos="VG(onder)" lemma="dat">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.6" pos="VNW(aanw,adv-pron,stan,red,3,getal)" lemma="er">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.7" pos="BW()" lemma="maar">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.8" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.9" pos="N(soort,ev,basis,zijd,stan)" lemma="synthese">synthese</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="stap">stap</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.11" pos="WW(vd,vrij,zonder)" lemma="uitvoeren">uitgevoerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.12" pos="WW(pv,tgw,met-t)" lemma="hoeven">hoeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.13" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.14" pos="WW(inf,vrij,zonder)" lemma="worden">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.15" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.12.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.1" pos="VZ(init)" lemma="uitgaande">Uitgaande</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.2" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.3" pos="N(soort,ev,basis,onz,stan)" lemma="salicylzuur">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.4" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.5" pos="N(soort,ev,basis,zijd,stan)" lemma="azijnzuuranhydride">azijnzuuranhydride</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.6" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.7" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.8" pos="N(soort,ev,basis,onz,stan)" lemma="salicylzuur">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.9" pos="ADJ(vrij,basis,zonder)" lemma="veresterd">veresterd</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.10" pos="VZ(init)" lemma="volgens">volgens</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.11" pos="ADJ(prenom,basis,met-e,stan)" lemma="nevenstaand">nevenstaande</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="reactie">reactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.13" pos="LET()" lemma=":">:</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.13">
          <s xml:id="WR-P-E-J-0000125009.p.13.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.1" pos="VG(onder)" lemma="zoals">Zoals</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.2" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.3" pos="WW(inf,vrij,zonder)" lemma="zien">zien</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.4" pos="VZ(init)" lemma="boven">boven</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.5" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="reactiepijl">reactiepijl</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.7" pos="WW(pv,tgw,met-t)" lemma="vinden">vindt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.8" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.9" pos="N(soort,ev,basis,zijd,stan)" lemma="synthese">synthese</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.10" pos="N(soort,ev,basis,zijd,stan)" lemma="plaats">plaats</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.11" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.12" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="zuur">zuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.14" pos="N(soort,ev,basis,onz,stan)" lemma="milieu">milieu</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.15" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.1" pos="VZ(init)" lemma="in">In</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.2" pos="VNW(aanw,det,stan,prenom,zonder,evon)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.3" pos="N(soort,ev,basis,onz,stan)" lemma="geval">geval</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.4" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.5" pos="WW(vd,vrij,zonder)" lemma="kiezen">gekozen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.6" pos="VZ(init)" lemma="voor">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.7" pos="WW(vd,prenom,zonder)" lemma="concentreren">geconcentreerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.8" pos="N(soort,ev,basis,onz,stan)" lemma="fosforzuur">fosforzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.9" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.1" pos="VZ(init)" lemma="na">Na</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.2" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.3" pos="N(soort,ev,basis,zijd,stan)" lemma="reactie">reactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.4" pos="WW(pv,tgw,ev)" lemma="moeten">moet</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.5" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="hoofdproduct">hoofdproduct</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.7" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.8" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.9" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.10" pos="WW(vd,vrij,zonder)" lemma="scheiden">gescheiden</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.11" pos="WW(inf,vrij,zonder)" lemma="worden">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.12" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.13" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.14" pos="N(soort,mv,basis)" lemma="bijproduct">bijproducten</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.15" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.16" pos="N(soort,ev,basis,zijd,stan)" lemma="azijnzuur">azijnzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.17" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.18" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.19" pos="ADJ(prenom,basis,met-e,stan)" lemma="gereageerde">gereageerde</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.20" pos="N(soort,mv,basis)" lemma="reactant">reactanten</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.21" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.22" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.23" pos="VNW(aanw,pron,stan,vol,3o,ev)" lemma="dit">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.24" pos="WW(pv,tgw,met-t)" lemma="gebeuren">gebeurt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.25" pos="VZ(init)" lemma="door">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.26" pos="N(soort,ev,basis,onz,stan)" lemma="middel">middel</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.27" pos="VZ(init)" lemma="van">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.28" pos="N(soort,ev,basis,zijd,stan)" lemma="herkristallisatie">herkristallisatie</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.29" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.2" pos="N(soort,ev,basis,zijd,stan)" lemma="herkristallisatie">herkristallisatie</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.3" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.4" pos="WW(vd,vrij,zonder)" lemma="uitvoeren">uitgevoerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.5" pos="VZ(init)" lemma="door">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.6" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.7" pos="ADJ(prenom,basis,met-e,stan)" lemma="ruw">ruwe</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.8" pos="N(soort,ev,basis,onz,stan)" lemma="product">product</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.9" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.10" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.11" pos="WW(inf,vrij,zonder)" lemma="lossen">lossen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.12" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.13" pos="N(soort,ev,basis,zijd,stan)" lemma="methanol">methanol</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.14" pos="LET()" lemma="(">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.15" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.16" pos="LID(onbep,stan,agr)" lemma="een">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.17" pos="N(soort,ev,basis,zijd,stan)" lemma="reflux">reflux</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.18" pos="N(soort,ev,basis,zijd,stan)" lemma="opstelling">opstelling</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.19" pos="LET()" lemma=")">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.20" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.21" pos="BW()" lemma="dan">dan</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.22" pos="BW()" lemma="net">net</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.23" pos="BW()" lemma="genoeg">genoeg</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.24" pos="N(soort,ev,basis,onz,stan)" lemma="water">water</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.25" pos="VZ(init)" lemma="toe">toe</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.26" pos="VZ(init)" lemma="te">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.27" pos="WW(inf,vrij,zonder)" lemma="voegen">voegen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.28" pos="VG(onder)" lemma="zodat">zodat</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.29" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.30" pos="N(soort,mv,basis)" lemma="verontreiniging">verontreinigingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.31" pos="WW(inf,vrij,zonder)" lemma="uitkristalliseren">uitkristalliseren</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.32" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.33" pos="VG(neven)" lemma="maar">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.34" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.35" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.36" pos="BW()" lemma="niet">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.37" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.1" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.2" pos="ADJ(prenom,basis,met-e,stan)" lemma="heet">hete</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.3" pos="N(soort,ev,basis,onz,stan)" lemma="mengsel">mengsel</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.4" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.5" pos="BW()" lemma="nu">nu</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.6" pos="WW(vd,vrij,zonder)" lemma="filtreren">gefiltreerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.7" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.8" pos="BW()" lemma="waardoor">waardoor</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.9" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.10" pos="N(soort,mv,basis)" lemma="verontreiniging">verontreinigingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.11" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.12" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.13" pos="N(soort,ev,basis,onz,stan)" lemma="filter">filter</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.14" pos="WW(pv,tgw,mv)" lemma="achterblijven">achterblijven</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.15" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.16" pos="BW()" lemma="alleen">alleen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.17" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.18" pos="ADJ(prenom,basis,met-e,stan)" lemma="zuiver">zuivere</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.19" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.20" pos="VZ(init)" lemma="in">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.21" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.22" pos="N(soort,ev,basis,onz,stan)" lemma="filtraat">filtraat</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.23" pos="WW(pv,tgw,met-t)" lemma="komen">komt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.24" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.6">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.1" pos="VZ(init)" lemma="na">Na</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.2" pos="VNW(aanw,det,stan,prenom,met-e,rest)" lemma="deze">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.3" pos="N(soort,ev,basis,zijd,stan)" lemma="filtratie">filtratie</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.4" pos="WW(pv,tgw,met-t)" lemma="worden">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.5" pos="VNW(pers,pron,stan,red,3,ev,onz)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.6" pos="N(soort,ev,basis,zijd,stan)" lemma="filtraat">filtraat</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.7" pos="ADJ(vrij,basis,zonder)" lemma="gekoeld">gekoeld</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.8" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.9" pos="BW()" lemma="opnieuw">opnieuw</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.10" pos="WW(vd,vrij,zonder)" lemma="filtreren">gefiltreerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.11" pos="LET()" lemma=",">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.12" pos="LID(bep,stan,rest)" lemma="de">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.13" pos="ADJ(prenom,basis,met-e,stan)" lemma="gezuiverde">gezuiverde</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.14" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.15" pos="WW(pv,tgw,met-t)" lemma="blijven">blijft</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.16" pos="BW()" lemma="nu">nu</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.17" pos="VZ(init)" lemma="achter">achter</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.18" pos="VZ(init)" lemma="op">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.19" pos="LID(bep,stan,evon)" lemma="het">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.20" pos="N(soort,ev,basis,onz,stan)" lemma="filter">filter</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.21" pos="LET()" lemma=".">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.7">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.1" pos="LID(bep,stan,rest)" lemma="de">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.2" pos="WW(vd,prenom,zonder)" lemma="verkrijgen">verkregen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.3" pos="N(soort,ev,basis,zijd,stan)" lemma="aspirine">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.4" pos="WW(pv,tgw,ev)" lemma="kunnen">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.5" pos="BW()" lemma="nu">nu</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.6" pos="WW(pv,tgw,mv)" lemma="worden">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.7" pos="WW(vd,vrij,zonder)" lemma="drogen">gedroogd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.8" pos="VG(neven)" lemma="en">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.9" pos="WW(pv,tgw,ev)" lemma="zijn">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.10" pos="ADJ(vrij,basis,zonder)" lemma="klaar">klaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.11" pos="VZ(init)" lemma="voor">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.12" pos="N(soort,ev,basis,zijd,stan)" lemma="verpakking">verpakking</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.13" pos="VG(neven)" lemma="of">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.14" pos="N(soort,ev,basis,onz,stan)" lemma="gebruik">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.15" pos="LET()" lemma=".">.</w>
          </s>
        </p>
      </div>
    </body>
    <gap reason="backmatter" hand="proycon">
       <desc>Backmatter</desc>
       <content>
bli bli bla, bla bla bli
       </content>
    </gap>
  </text>
</DCOI>"""


if __name__ == '__main__':
    unittest.main()
