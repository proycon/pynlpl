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
from pynlpl.formats import fql

Q1 = 'SELECT pos WHERE class = "n" FOR w WHERE text = "house" AND class != "punct" RETURN actor'
Q2 = 'ADD w WITH text "house" (ADD pos WITH class "n") FOR ID sentence'

Qstamboom_actor = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN target"
Qstamboom_target = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN target"

class Test1UnparsedQuery(unittest.TestCase):

    def test1_basic(self):
        """Basic query with some literals"""
        qs = Q1
        qu = fql.UnparsedQuery(qs)

        self.assertEqual( qu.q, ['SELECT','pos','WHERE','class','=','n','FOR','w','WHERE','text','=','house','AND','class','!=','punct','RETURN','actor'])
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
        q = fql.Query(Q1)

    def test2_parse(self):
        q = fql.Query(Q2)

    def test3_parse(self):
        q = fql.Query(Qstamboom_target)

class test3Evaluation(unittest.TestCase):
    pass


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
