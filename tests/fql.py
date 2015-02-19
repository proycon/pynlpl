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

Qselect_multitarget_focus = "SELECT lemma OF \"lemmas-nl\" FOR ID \"WR-P-E-J-0000000001.p.1.s.4.w.4\" , ID \"WR-P-E-J-0000000001.p.1.s.4.w.5\""
Qselect_multitarget = "SELECT lemma OF \"lemmas-nl\" FOR ID \"WR-P-E-J-0000000001.p.1.s.4.w.4\" , ID \"WR-P-E-J-0000000001.p.1.s.4.w.5\" RETURN target"
Qselect_nestedtargets = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w FOR s ID \"WR-P-E-J-0000000001.p.1.s.2\" RETURN target FORMAT single-python"

Qedit = "EDIT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" WITH class \"blah\" FOR w FOR s ID \"WR-P-E-J-0000000001.p.1.s.2\""
Qadd = "ADD lemma OF \"lemmas-nl\" WITH class \"hebben\" FOR w ID \"WR-P-E-J-0000000001.sandbox.2.s.1.w.3\""
Qeditadd = "EDIT lemma OF \"lemmas-nl\" WITH class \"hebben\" FOR w ID \"WR-P-E-J-0000000001.sandbox.2.s.1.w.3\""
Qdelete = "DELETE lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w"
Qdelete_target = "DELETE lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN target"

Qcomplexadd = "APPEND w (ADD t WITH text \"gisteren\" ADD lemma OF \"lemmas-nl\" WITH class \"gisteren\") FOR ID \"WR-P-E-J-0000000001.sandbox.2.s.1.w.3\""

Qedittext = "EDIT w WHERE text = \"terweil\" WITH text \"terwijl\""

Qhas = "SELECT w WHERE (pos HAS class = \"LET()\")"
Qhas_shortcut = "SELECT w WHERE :pos = \"LET()\""

Qboolean = "SELECT w WHERE (pos HAS class = \"LET()\") AND ((lemma HAS class = \".\") OR (lemma HAS class = \",\"))"

Qcontext = "SELECT w WHERE (PREVIOUS w WHERE text = \"de\")"

Qselect_span = "SELECT entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WHERE class = \"per\" FOR ID \"example.table.1.w.3\""
Qselect_span2 = "SELECT entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WHERE class = \"per\" FOR SPAN ID \"example.table.1.w.3\" & ID \"example.table.1.w.4\" & ID \"example.table.1.w.5\""
Qselect_span2_returntarget = "SELECT entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WHERE class = \"per\" FOR SPAN ID \"example.table.1.w.3\" & ID \"example.table.1.w.4\" & ID \"example.table.1.w.5\" RETURN target"

Qadd_span = "ADD entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WITH class \"misc\" FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.4.w.2\" & ID \"WR-P-E-J-0000000001.p.1.s.4.w.3\""
Qadd_span_returntarget = "ADD entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WITH class \"misc\" FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.4.w.2\" & ID \"WR-P-E-J-0000000001.p.1.s.4.w.3\" RETURN target"

Qalt = "EDIT lemma WHERE class = \"terweil\" WITH class \"terwijl\" (AS ALTERNATIVE WITH confidence 0.9)"

Qdeclare = "DECLARE correction OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH annotator \"me\" annotatortype \"manual\""

Qcorrect1 = "EDIT lemma WHERE class = \"terweil\" WITH class \"terwijl\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"nonworderror\" confidence 0.9)"
Qcorrect2 = "EDIT lemma WHERE class = \"terweil\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" class \"terwijl\" WITH class \"nonworderror\" confidence 0.9)"
Qsuggest1 = "EDIT lemma WHERE class = \"terweil\" (AS SUGGESTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"nonworderror\" confidence 0.9)"

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

    def test3_complex(self):
        """Query with parentheses"""
        qu = fql.UnparsedQuery(Qboolean)
        self.assertEqual( len(qu.q), 6)



class Test2ParseQuery(unittest.TestCase):
    def test01_parse(self):
        """Parsing """ + Q1
        q = fql.Query(Q1)

    def test02_parse(self):
        """Parsing """ + Q2
        q = fql.Query(Q2)

    def test03_parse(self):
        """Parsing """ + Qselect_target
        q = fql.Query(Qselect_target)

    def test04_parse(self):
        """Parsing """ + Qcomplexadd
        q = fql.Query(Qcomplexadd)
        self.assertEqual( len(q.action.subactions), 1) #test whether subaction is parsed
        self.assertTrue( isinstance(q.action.subactions[0].nextaction, fql.Action) ) #test whether subaction has proper chain of two actions

    def test05_parse(self):
        """Parsing """ + Qhas
        q = fql.Query(Qhas)

    def test06_parse(self):
        """Parsing """ + Qhas_shortcut
        q = fql.Query(Qhas_shortcut)

    def test07_parse(self):
        """Parsing """ + Qboolean
        q = fql.Query(Qboolean)

    def test08_parse(self):
        """Parsing """ + Qcontext
        q = fql.Query(Qcontext)

    def test09_parse(self):
        """Parsing """ + Qalt
        q = fql.Query(Qalt)

    def test10_parse(self):
        """Parsing """ + Qcorrect1
        q = fql.Query(Qcorrect1)

    def test11_parse(self):
        """Parsing """ + Qcorrect2
        q = fql.Query(Qcorrect2)

class Test3Evaluation(unittest.TestCase):
    def setUp(self):
        self.doc = folia.Document(string=FOLIAEXAMPLE)

    def test01_evaluate_select_focus(self):
        q = fql.Query(Qselect_focus)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))
        self.assertEqual(len(results),2)
        self.assertTrue(isinstance(results[1], folia.LemmaAnnotation))

    def test02_evaluate_select_singlefocus(self):
        q = fql.Query(Qselect_singlefocus)
        result = q(self.doc)
        self.assertTrue(isinstance(result, folia.LemmaAnnotation))

    def test03_evaluate_select_target(self):
        q = fql.Query(Qselect_target)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.Word))
        self.assertEqual(len(results),2)
        self.assertTrue(isinstance(results[1], folia.Word))

    def test04_evaluate_select_singletarget(self):
        q = fql.Query(Qselect_singletarget)
        result = q(self.doc)
        self.assertTrue(isinstance(result, folia.Word))

    def test05_evaluate_select_nestedtargets(self):
        q = fql.Query(Qselect_nestedtargets)
        result = q(self.doc)
        self.assertTrue(isinstance(result, folia.Word))

    def test05a_evaluate_select_multitarget_focus(self):
        q = fql.Query(Qselect_multitarget_focus)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))
        self.assertEqual(len(results),2)
        self.assertTrue(isinstance(results[1], folia.LemmaAnnotation))

    def test05b_evaluate_select_multitarget(self):
        q = fql.Query(Qselect_multitarget)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.Word))
        self.assertEqual(len(results),2)
        self.assertTrue(isinstance(results[1], folia.Word))

    def test06_evaluate_edit(self):
        q = fql.Query(Qedit)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))

    def test07_evaluate_add(self):
        q = fql.Query(Qadd)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))

    def test08_evaluate_editadd(self):
        q = fql.Query(Qeditadd)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))

    def test09_evaluate_delete(self):
        q = fql.Query(Qdelete)
        results = q(self.doc)
        self.assertEqual(len(results),0)

    def test10_evaluate_delete(self):
        q = fql.Query(Qdelete_target)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.Word))
        self.assertEqual(len(results),2)
        self.assertTrue(isinstance(results[1], folia.Word))

    def test11_complexadd(self):
        q = fql.Query(Qcomplexadd)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Word)
        self.assertIsInstance(results[0][0], folia.TextContent)
        self.assertIsInstance(results[0][1], folia.LemmaAnnotation)

    def test12_edittext(self):
        q = fql.Query(Qedittext)
        results = q(self.doc)
        self.assertEqual(results[0].text(), "terwijl")


    def test13_subfilter(self):
        q = fql.Query(Qhas)
        results = q(self.doc)
        for result in results:
            self.assertIn(result.text(), (".",",","(",")"))

    def test14_subfilter_shortcut(self):
        q = fql.Query(Qhas_shortcut)
        results = q(self.doc)
        self.assertTrue( len(results) > 0 )
        for result in results:
            self.assertIn(result.text(), (".",",","(",")"))

    def test15_boolean(self):
        q = fql.Query(Qboolean)
        results = q(self.doc)
        self.assertTrue( len(results) > 0 )
        for result in results:
            self.assertIn(result.text(), (".",","))

    def test16_context(self):
        """Obtaining all words following 'de'"""
        q = fql.Query(Qcontext)
        results = q(self.doc)
        self.assertTrue( len(results) > 0 )
        self.assertEqual(results[0].text(), "historische")
        self.assertEqual(results[1].text(), "naam")
        self.assertEqual(results[2].text(), "verwantschap")
        self.assertEqual(results[3].text(), "handschriften")
        self.assertEqual(results[4].text(), "juiste")
        self.assertEqual(results[5].text(), "laatste")
        self.assertEqual(results[6].text(), "verwantschap")
        self.assertEqual(results[7].text(), "handschriften")

    def test17_select_span(self):
        """Select span"""
        q = fql.Query(Qselect_span)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Entity)
        self.assertEqual(len(list(results[0].wrefs())), 3)

    def test18_select_span2(self):
        """Select span"""
        q = fql.Query(Qselect_span2)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Entity)
        results = list(results[0].wrefs())
        self.assertIsInstance(results[0], folia.Word)
        self.assertEqual(results[0].text(), "Maarten")
        self.assertIsInstance(results[1], folia.Word)
        self.assertEqual(results[1].text(), "van")
        self.assertIsInstance(results[2], folia.Word)
        self.assertEqual(results[2].text(), "Gompel")

    def test19_select_span2_returntarget(self):
        """Select span"""
        q = fql.Query(Qselect_span2_returntarget)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Word)
        self.assertEqual(results[0].text(), "Maarten")
        self.assertIsInstance(results[1], folia.Word)
        self.assertEqual(results[1].text(), "van")
        self.assertIsInstance(results[2], folia.Word)
        self.assertEqual(results[2].text(), "Gompel")

    def test20a_add_span(self):
        """Add span"""
        q = fql.Query(Qadd_span)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Entity)
        self.assertEqual(results[0].cls, 'misc')
        results = list(results[0].wrefs())
        self.assertIsInstance(results[0], folia.Word)
        self.assertEqual(results[0].text(), "hoofdletter")
        self.assertIsInstance(results[1], folia.Word)
        self.assertEqual(results[1].text(), "A")

    def test20b_add_span_returntarget(self):
        """Add span (return target)"""
        q = fql.Query(Qadd_span_returntarget)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Word)
        self.assertEqual(results[0].text(), "hoofdletter")
        self.assertIsInstance(results[1], folia.Word)
        self.assertEqual(results[1].text(), "A")

    def test21_edit_alt(self):
        """Add alternative token annotation"""
        q = fql.Query(Qalt)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Alternative)
        self.assertIsInstance(results[0][0], folia.LemmaAnnotation)
        self.assertEqual(results[0][0].cls, "terwijl")

    def test22_declare(self):
        """Explicit declaration"""
        q = fql.Query(Qdeclare)
        results = q(self.doc)

    def test23a_edit_correct(self):
        """Add correction on token annotation"""
        q = fql.Query(Qcorrect1)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "nonworderror")
        self.assertEqual(results[0].confidence, 0.9)
        self.assertIsInstance(results[0].new(0), folia.LemmaAnnotation)
        self.assertEqual(results[0].new(0).cls, "terwijl")

    def test23b_edit_correct(self):
        """Add correction on token annotation (2)"""
        q = fql.Query(Qcorrect2)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "nonworderror")
        self.assertEqual(results[0].confidence, 0.9)
        self.assertIsInstance(results[0].new(0), folia.LemmaAnnotation)
        self.assertEqual(results[0].new(0).cls, "terwijl")

    def test23c_edit_suggest(self):
        """Add correction on token annotation"""
        q = fql.Query(Qsuggest1)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "nonworderror")
        self.assertEqual(results[0].confidence, 0.9)
        self.assertIsInstance(results[0].suggestions(0), folia.LemmaAnnotation)
        self.assertEqual(results[0].suggestions(0).cls, "terwijl")

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
