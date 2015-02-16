#!/usr/bin/env python
#-*- coding:utf-8 -*-


#---------------------------------------------------------------
# PyNLPl - Test Units for FoLiA Query Language
#   by Maarten van Gompel, Radboud University Nijmegen
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
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
from pynlpl.formats import fql, folia

Q1 = 'SELECT pos WHERE class = "n" FOR w WHERE text = "house" AND class != "punct" RETURN focus'
Q2 = 'ADD w WITH text "house" (ADD pos WITH class "n") FOR ID sentence'

Qselect_focus = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN focus"
Qselect_target = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN target"
Qselect_singlefocus = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"hoofdletter\" FOR w RETURN focus FORMAT single-python"
Qselect_singletarget = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"hoofdletter\" FOR w RETURN target FORMAT single-python"

Qselect_nestedtargets = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w FOR s ID \"WR-P-E-J-0000000001.p.1.s.2\" RETURN target FORMAT single-python"

Qedit = "EDIT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" WITH class \"blah\" FOR w FOR s ID \"WR-P-E-J-0000000001.p.1.s.2\""

class Test1UnparsedQuery(unittest.TestCase):

    def test1_basic(self):
        """Basic query with some literals"""
        qs = Q1
        qu = fql.UnparsedQuery(qs)

        self.assertEqual( qu.q, ['SELECT','pos','WHERE','class','=','n','FOR','w','WHERE','text','=','house','AND','class','!=','punct','RETURN','focus'])
        self.assertEqual( qu.mask, [0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0] )

    def test2_paren(self):
        """Query with parentheses"""
        qs = Q2
        qu = fql.UnparsedQuery(qs)

        self.assertEqual( len(qu), 9 )
        self.assertTrue( isinstance(qu.q[5], fql.UnparsedQuery))
        self.assertEqual( qu.mask, [0,0,0,0,1,2,0,0,0] )


class Test2ParseQuery(unittest.TestCase):
    def test1_parse(self):
        """Parsing """ + Q1
        q = fql.Query(Q1)

    def test2_parse(self):
        """Parsing """ + Q2
        q = fql.Query(Q2)

    def test3_parse(self):
        """Parsing """ + Qselect_target
        q = fql.Query(Qselect_target)

class Test3Evaluation(unittest.TestCase):
    def setUp(self):
        self.doc = folia.Document(string=FOLIAEXAMPLE)

    def test1_evaluate_select_focus(self):
        q = fql.Query(Qselect_focus)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))
        self.assertEqual(len(results),2)
        self.assertTrue(isinstance(results[1], folia.LemmaAnnotation))

    def test2_evaluate_select_singlefocus(self):
        q = fql.Query(Qselect_singlefocus)
        result = q(self.doc)
        self.assertTrue(isinstance(result, folia.LemmaAnnotation))

    def test3_evaluate_select_target(self):
        q = fql.Query(Qselect_target)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.Word))
        self.assertEqual(len(results),2)
        self.assertTrue(isinstance(results[1], folia.Word))

    def test4_evaluate_select_singletarget(self):
        q = fql.Query(Qselect_singletarget)
        result = q(self.doc)
        self.assertTrue(isinstance(result, folia.Word))

    def test5_evaluate_select_nestedtargets(self):
        q = fql.Query(Qselect_nestedtargets)
        result = q(self.doc)
        self.assertTrue(isinstance(result, folia.Word))

    def test6_evaluate_edit(self):
        q = fql.Query(Qedit)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))

if os.path.exists('../../FoLiA'):
    FOLIAPATH = '../../FoLiA/'
elif os.path.exists('../FoLiA'):
    FOLIAPATH = '../FoLiA/'
else:
    FOLIAPATH = 'FoLiA'
    print("Downloading FoLiA",file=sys.stderr)
    os.system("git clone https://github.com/proycon/folia.git FoLiA")

f = io.open(FOLIAPATH + '/test/example.xml', 'r',encoding='utf-8')
FOLIAEXAMPLE = f.read()
f.close()


if __name__ == '__main__':
    unittest.main()
