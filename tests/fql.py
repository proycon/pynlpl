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

Qstamboom_focus = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN focus"
Qstamboom_target = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN target"

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
        """Parsing """ + Qstamboom_target
        q = fql.Query(Qstamboom_target)

class Test3Evaluation(unittest.TestCase):
    def setUp(self):
        self.doc = folia.Document(string=FOLIAEXAMPLE)

    def test1_evaluate_select_focus(self):
        q = fql.Query(Qstamboom_focus)
        results = q(self.doc, False)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))
        self.assertTrue(len(results),1)

    def test2_evaluate_select_target(self):
        q = fql.Query(Qstamboom_target)
        results = q(self.doc, False)
        self.assertTrue(isinstance(results[0], folia.Word))
        self.assertTrue(len(results),1)


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
