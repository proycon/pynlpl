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
from pynlpl.formats import fql, folia, cql

Q1 = 'SELECT pos WHERE class = "n" FOR w WHERE text = "house" AND class != "punct" RETURN focus'
Q2 = 'ADD w WITH text "house" (ADD pos WITH class "n") FOR ID sentence'

Qselect_focus = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN focus"
Qselect_target = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN target"
Qselect_singlefocus = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"hoofdletter\" FOR w RETURN focus FORMAT single-python"
Qselect_singletarget = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"hoofdletter\" FOR w RETURN target FORMAT single-python"



Qselect_multitarget_focus = "SELECT lemma OF \"lemmas-nl\" FOR ID \"WR-P-E-J-0000000001.p.1.s.4.w.4\" , ID \"WR-P-E-J-0000000001.p.1.s.4.w.5\""
Qselect_multitarget = "SELECT lemma OF \"lemmas-nl\" FOR ID \"WR-P-E-J-0000000001.p.1.s.4.w.4\" , ID \"WR-P-E-J-0000000001.p.1.s.4.w.5\" RETURN target"
Qselect_nestedtargets = "SELECT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w FOR s ID \"WR-P-E-J-0000000001.p.1.s.2\" RETURN target FORMAT single-python"

Qselect_startend = "SELECT FOR w START ID \"WR-P-E-J-0000000001.p.1.s.2.w.2\" END ID \"WR-P-E-J-0000000001.p.1.s.2.w.4\"" #inclusive
Qselect_startend2 = "SELECT FOR w START ID \"WR-P-E-J-0000000001.p.1.s.2.w.2\" ENDBEFORE ID \"WR-P-E-J-0000000001.p.1.s.2.w.4\"" #exclusive


Qin = "SELECT ph IN w"
Qin2 = "SELECT ph IN term"
Qin2ref = "SELECT ph FOR term"

Qedit = "EDIT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" WITH class \"blah\" FOR w FOR s ID \"WR-P-E-J-0000000001.p.1.s.2\""
Qeditconfidence = "EDIT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" WITH class \"blah\" confidence 0.5 FOR w FOR s ID \"WR-P-E-J-0000000001.p.1.s.2\""
Qeditconfidence2 = "EDIT lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" WITH class \"blah\" confidence NONE FOR w FOR s ID \"WR-P-E-J-0000000001.p.1.s.2\""
Qadd = "ADD lemma OF \"lemmas-nl\" WITH class \"hebben\" FOR w ID \"WR-P-E-J-0000000001.sandbox.2.s.1.w.3\""
Qeditadd = "EDIT lemma OF \"lemmas-nl\" WITH class \"hebben\" FOR w ID \"WR-P-E-J-0000000001.sandbox.2.s.1.w.3\""
Qdelete = "DELETE lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w"
Qdelete_target = "DELETE lemma OF \"lemmas-nl\" WHERE class = \"stamboom\" FOR w RETURN target"

Qcomplexadd = "APPEND w (ADD t WITH text \"gisteren\" ADD lemma OF \"lemmas-nl\" WITH class \"gisteren\") FOR ID \"WR-P-E-J-0000000001.sandbox.2.s.1.w.3\""

Qedittext = "EDIT w WHERE text = \"terweil\" WITH text \"terwijl\""
Qedittext2 = "EDIT t WITH text \"terwijl\" FOR w WHERE text = \"terweil\" RETURN target"
Qedittext3 = "EDIT t WITH text \"de\" FOR w ID \"WR-P-E-J-0000000001.p.1.s.8.w.10\" RETURN target"
Qedittext4 = "EDIT t WITH text \"ter\nwijl\" FOR w WHERE text = \"terweil\" RETURN target"

Qhas = "SELECT w WHERE (pos HAS class = \"LET()\")"
Qhas_shortcut = "SELECT w WHERE :pos = \"LET()\""

Qboolean = "SELECT w WHERE (pos HAS class = \"LET()\") AND ((lemma HAS class = \".\") OR (lemma HAS class = \",\"))"

Qcontext = "SELECT w WHERE (PREVIOUS w WHERE text = \"de\")"
Qcontext2 = "SELECT FOR SPAN w WHERE (pos HAS class CONTAINS \"LID(\") & w WHERE (pos HAS class CONTAINS \"ADJ(\") & w WHERE (pos HAS class CONTAINS \"N(\")"

Qselect_span = "SELECT entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WHERE class = \"per\" FOR ID \"example.table.1.w.3\""
Qselect_span2 = "SELECT entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WHERE class = \"per\" FOR SPAN ID \"example.table.1.w.3\" & ID \"example.table.1.w.4\" & ID \"example.table.1.w.5\""
Qselect_span2_returntarget = "SELECT entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WHERE class = \"per\" FOR SPAN ID \"example.table.1.w.3\" & ID \"example.table.1.w.4\" & ID \"example.table.1.w.5\" RETURN target"

Qadd_span = "ADD entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WITH class \"misc\" FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.4.w.2\" & ID \"WR-P-E-J-0000000001.p.1.s.4.w.3\""
Qadd_span_returntarget = "ADD entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WITH class \"misc\" FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.4.w.2\" & ID \"WR-P-E-J-0000000001.p.1.s.4.w.3\" RETURN target"
Qadd_span_returnancestortarget = "ADD entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WITH class \"misc\" FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.4.w.2\" & ID \"WR-P-E-J-0000000001.p.1.s.4.w.3\" RETURN ancestor-target"

Qalt = "EDIT lemma WHERE class = \"terweil\" WITH class \"terwijl\" (AS ALTERNATIVE WITH confidence 0.9)"

Qdeclare = "DECLARE correction OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH annotator \"me\" annotatortype \"manual\""

#implicitly tests auto-declaration:
Qcorrect1 = "EDIT lemma WHERE class = \"terweil\" WITH class \"terwijl\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"nonworderror\" confidence 0.9)"
Qcorrect2 = "EDIT lemma WHERE class = \"terweil\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" class \"terwijl\" WITH class \"nonworderror\" confidence 0.9)"

Qsuggest1 = "EDIT lemma WHERE class = \"terweil\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"nonworderror\" SUGGESTION class \"terwijl\" WITH confidence 0.9 SUGGESTION class \"gedurende\" WITH confidence 0.1)"
Qcorrectsuggest = "EDIT lemma WHERE class = \"terweil\" WITH class \"terwijl\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"nonworderror\" confidence 0.9 SUGGESTION class \"gedurende\" WITH confidence 0.1)"

Qcorrect_text = "EDIT t WHERE text = \"terweil\" WITH text \"terwijl\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"nonworderror\" confidence 0.9)"
Qsuggest_text = "EDIT t WHERE text = \"terweil\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"nonworderror\" SUGGESTION text \"terwijl\" WITH confidence 0.9 SUGGESTION text \"gedurende\" WITH confidence 0.1)"

Qcorrect_span = "EDIT entity OF \"http://raw.github.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml\" WHERE class = \"per\" WITH class \"misc\" (AS CORRECTION OF \"https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/namedentitycorrection.foliaset.xml\" WITH class \"wrongclass\" confidence 0.2) FOR ID \"example.table.1.w.3\""

Qrespan = "EDIT semrole WHERE class = \"actor\" RESPAN ID \"WR-P-E-J-0000000001.p.1.s.7.w.2\" & ID \"WR-P-E-J-0000000001.p.1.s.7.w.3\" FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.7.w.3\""

Qmerge = "SUBSTITUTE w WITH text \"weertegeven\" FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.2.w.26\" & ID \"WR-P-E-J-0000000001.p.1.s.2.w.27\" & ID \"WR-P-E-J-0000000001.p.1.s.2.w.28\""

Qsplit = "SUBSTITUTE w WITH text \"weer\" SUBSTITUTE w WITH text \"gegeven\" FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.6.w.20\""

Qcorrect_merge = "SUBSTITUTE w WITH text \"weertegeven\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"spliterror\") FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.2.w.26\" & ID \"WR-P-E-J-0000000001.p.1.s.2.w.27\" & ID \"WR-P-E-J-0000000001.p.1.s.2.w.28\""

Qcorrect_split = "SUBSTITUTE w WITH text \"weer\" SUBSTITUTE w WITH text \"gegeven\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"runonerror\") FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.6.w.20\""

Qsuggest_split = "SUBSTITUTE (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"runonerror\" SUGGESTION (SUBSTITUTE w WITH text \"weer\" SUBSTITUTE w WITH text \"gegeven\")) FOR SPAN ID \"WR-P-E-J-0000000001.p.1.s.6.w.20\""

Qprepend = "PREPEND w WITH text \"heel\" FOR ID \"WR-P-E-J-0000000001.p.1.s.1.w.4\""
Qcorrect_prepend = "PREPEND w WITH text \"heel\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"insertion\") FOR ID \"WR-P-E-J-0000000001.p.1.s.1.w.4\""

Qcorrect_delete = "DELETE w ID \"WR-P-E-J-0000000001.p.1.s.8.w.6\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"redundantword\")"

Qcql_context = '"de" [ tag="ADJ\(.*" ] [ tag="N\(.*" & lemma!="blah" ]'
Qcql_context2 = '[ pos = "LID\(.*" ]? [ pos = "ADJ\(.*" ]* [ pos = "N\(.*" ]'
Qcql_context3 = '[ pos = "N\(.*" ]{2}'
Qcql_context4 = '[ pos = "WW\(.*" ]+ [] [ pos = "WW\(.*" ]+'
Qcql_context5 = '[ pos = "VG\(.*" ] [ pos = "WW\(.*" ]* []?'
Qcql_context6 = '[ pos = "VG\(.*|VZ\.*" ]'

#test 4: advanced corrections (higher order corrections):
Qsplit2 = "SUBSTITUTE w WITH text \"Ik\" SUBSTITUTE w WITH text \"hoor\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"runonerror\") FOR SPAN ID \"correctionexample.s.4.w.1\""

Qmerge2 = "SUBSTITUTE w WITH text \"onweer\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"spliterror\") FOR SPAN ID \"correctionexample.s.4.w.2\" & ID \"correctionexample.s.4.w.3\""


Qdeletion2 = "DELETE w ID \"correctionexample.s.8.w.3\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"redundantword\")"
#Qdeletion2b = "SUBSTITUTE w ID \"correctionexample.s.8.w.3\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"redundantword\") FOR SPAN ID \"correctionexample.s.8.correction.1\""

#insertions when there is an existing suggestion, SUBSTITUTE insead of APPEND/PREPEND:
Qinsertion2 = "SUBSTITUTE w WITH text \".\" (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"missingpunctuation\") FOR SPAN ID \"correctionexample.s.9.correction.1\""


Qsuggest_insertion = "PREPEND (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"insertion\" SUGGESTION (ADD w WITH text \"heel\")) FOR ID \"WR-P-E-J-0000000001.p.1.s.1.w.4\""
Qsuggest_insertion2 = "APPEND (AS CORRECTION OF \"http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml\" WITH class \"insertion\" SUGGESTION (ADD w WITH text \"heel\")) FOR ID \"WR-P-E-J-0000000001.p.1.s.1.w.3\""

Qcomment = "ADD comment WITH text \"This is our university!\" FOR entity ID \"example.radboud.university.nijmegen.org\""


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

    def test12_parse(self):
        """Parsing """ + Qsuggest_split
        q = fql.Query(Qsuggest_split)
        self.assertIsInstance(q.action.form, fql.Correction)
        self.assertEqual( len(q.action.form.suggestions),1)


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
        self.assertEqual(results[0].cls, "blah")

    def test06a_evaluate_editconfidence(self):
        q = fql.Query(Qeditconfidence)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))
        self.assertEqual(results[0].cls, "blah")
        self.assertEqual(results[0].confidence, 0.5)

    def test06b_evaluate_editconfidence2(self):
        q = fql.Query(Qeditconfidence2)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))
        self.assertEqual(results[0].cls, "blah")
        self.assertEqual(results[0].confidence, None)

    def test07_evaluate_add(self):
        q = fql.Query(Qadd)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))
        self.assertEqual(results[0].cls, "hebben")

    def test08_evaluate_editadd(self):
        q = fql.Query(Qeditadd)
        results = q(self.doc)
        self.assertTrue(isinstance(results[0], folia.LemmaAnnotation))
        self.assertEqual(results[0].cls, "hebben")

    def test09_evaluate_delete(self):
        q = fql.Query(Qdelete)
        results = q(self.doc)
        self.assertEqual(len(results),2) #returns that what was deleted

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

    def test12b_edittext(self):
        q = fql.Query(Qedittext2)
        results = q(self.doc)
        self.assertEqual(results[0].text(), "terwijl")

    def test12c_edittext(self):
        q = fql.Query(Qedittext3)
        results = q(self.doc)
        self.assertEqual(results[0].text(), "de")

    def test12d_edittext(self):
        q = fql.Query(Qedittext4)
        results = q(self.doc)
        self.assertEqual(results[0].text(), "ter\nwijl")

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

    def test16b_context(self):
        """Obtaining LID ADJ N sequences"""
        q = fql.Query(Qcontext2)
        results = q(self.doc)
        self.assertTrue( len(results) > 0 )
        for result in results:
            self.assertIsInstance(result, fql.SpanSet)
            #print("RESULT: ", [w.text() for w in result])
            self.assertEqual(len(result), 3)
            self.assertIsInstance(result[0], folia.Word)
            self.assertIsInstance(result[1], folia.Word)
            self.assertIsInstance(result[2], folia.Word)
            self.assertEqual(result[0].pos()[:4], "LID(")
            self.assertEqual(result[1].pos()[:4], "ADJ(")
            self.assertEqual(result[2].pos()[:2], "N(")

    def test17_select_span(self):
        """Select span"""
        q = fql.Query(Qselect_span)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Entity)
        self.assertEqual(results[0].cls, 'per')
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
        self.assertIsInstance(results[0], fql.SpanSet)
        results = results[0]
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
        self.assertIsInstance(results[0], fql.SpanSet )
        results = results[0]
        self.assertIsInstance(results[0], folia.Word)
        self.assertEqual(results[0].text(), "hoofdletter")
        self.assertIsInstance(results[1], folia.Word)
        self.assertEqual(results[1].text(), "A")

    def test20c_add_span_returnancestortarget(self):
        """Add span (return ancestor target)"""
        q = fql.Query(Qadd_span_returnancestortarget)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Part )

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

    def test24a_edit_suggest(self):
        """Add suggestions for correction on token annotation"""
        q = fql.Query(Qsuggest1)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "nonworderror")
        self.assertEqual(results[0].parent.lemma(),"terweil")
        self.assertIsInstance(results[0].suggestions(0), folia.Suggestion)
        self.assertEqual(results[0].suggestions(0).confidence, 0.9)
        self.assertIsInstance(results[0].suggestions(0)[0], folia.LemmaAnnotation)
        self.assertEqual(results[0].suggestions(0)[0].cls, "terwijl")
        self.assertIsInstance(results[0].suggestions(1), folia.Suggestion)
        self.assertEqual(results[0].suggestions(1).confidence, 0.1)
        self.assertIsInstance(results[0].suggestions(1)[0], folia.LemmaAnnotation)
        self.assertEqual(results[0].suggestions(1)[0].cls, "gedurende")

    def test24b_edit_correctsuggest(self):
        """Add correction as well as suggestions on token annotation"""
        q = fql.Query(Qcorrectsuggest)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "nonworderror")
        self.assertEqual(results[0].confidence, 0.9)
        self.assertIsInstance(results[0].new(0), folia.LemmaAnnotation)
        self.assertEqual(results[0].new(0).cls, "terwijl")
        self.assertIsInstance(results[0].suggestions(0), folia.Suggestion)
        self.assertEqual(results[0].suggestions(0).confidence, 0.1)
        self.assertIsInstance(results[0].suggestions(0)[0], folia.LemmaAnnotation)
        self.assertEqual(results[0].suggestions(0)[0].cls, "gedurende")

    def test25a_edit_correct_text(self):
        """Add correction on text"""
        q = fql.Query(Qcorrect_text)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "nonworderror")
        self.assertEqual(results[0].confidence, 0.9)
        self.assertIsInstance(results[0].new(0), folia.TextContent)
        self.assertEqual(results[0].new(0).text(), "terwijl")

    def test25b_edit_suggest_text(self):
        """Add suggestion for correction on text"""
        q = fql.Query(Qsuggest_text)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "nonworderror")
        self.assertEqual(results[0].parent.text(),"terweil") #original
        self.assertIsInstance(results[0].suggestions(0), folia.Suggestion)
        self.assertEqual(results[0].suggestions(0).confidence, 0.9)
        self.assertIsInstance(results[0].suggestions(0)[0], folia.TextContent)
        self.assertEqual(results[0].suggestions(0)[0].text(), "terwijl")
        self.assertIsInstance(results[0].suggestions(1), folia.Suggestion)
        self.assertEqual(results[0].suggestions(1).confidence, 0.1)
        self.assertIsInstance(results[0].suggestions(1)[0], folia.TextContent)
        self.assertEqual(results[0].suggestions(1)[0].text(), "gedurende")

    def test26_correct_span(self):
        """Correction of span annotation"""
        q = fql.Query(Qcorrect_span)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertIsInstance(results[0].new(0), folia.Entity)
        self.assertEqual(results[0].new(0).cls, 'misc')
        self.assertEqual(len(list(results[0].new(0).wrefs())), 3)

    def test27_edit_respan(self):
        """Re-spanning"""
        q = fql.Query(Qrespan)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.SemanticRole)
        self.assertEqual(results[0].cls, "actor")
        results = list(results[0].wrefs())
        self.assertIsInstance(results[0], folia.Word)
        self.assertEqual(results[0].text(), "gaat") #yes, this is not a proper semantic role for class 'actor', I know.. but I had to make up a test
        self.assertIsInstance(results[1], folia.Word)
        self.assertEqual(results[1].text(), "men")

    def test28a_merge(self):
        """Substitute - Merging"""
        q = fql.Query(Qmerge)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Word)
        self.assertEqual(results[0].text(), "weertegeven")

    def test28b_split(self):
        """Substitute - Split"""
        q = fql.Query(Qsplit)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Word)
        self.assertIsInstance(results[1], folia.Word)
        self.assertEqual(results[0].text(), "weer")
        self.assertEqual(results[1].text(), "gegeven")

    def test28a_correct_merge(self):
        """Merge Correction"""
        q = fql.Query(Qcorrect_merge)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "spliterror")
        self.assertEqual(results[0].new(0).text(), "weertegeven")

    def test28b_correct_split(self):
        """Split Correction"""
        q = fql.Query(Qcorrect_split)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "runonerror")
        self.assertIsInstance(results[0].new(0), folia.Word)
        self.assertIsInstance(results[0].new(1), folia.Word)
        self.assertEqual(results[0].new(0).text(), "weer")
        self.assertEqual(results[0].new(1).text(), "gegeven")
        self.assertEqual(results[0].original(0).text(), "weergegeven")

    def test28b_suggest_split(self):
        """Split Suggestion for Correction"""
        q = fql.Query(Qsuggest_split)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "runonerror")
        self.assertIsInstance(results[0].suggestions(0)[0], folia.Word)
        self.assertIsInstance(results[0].suggestions(0)[1], folia.Word)
        self.assertEqual(results[0].suggestions(0)[0].text(), "weer")
        self.assertEqual(results[0].suggestions(0)[1].text(), "gegeven")
        self.assertEqual(results[0].current(0).text(), "weergegeven")

    def test29a_prepend(self):
        """Insertion using prepend"""
        q = fql.Query(Qprepend)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Word)
        self.assertEqual(results[0].text(), "heel")
        self.assertEqual(results[0].next(folia.Word).text(), "ander")

    def test29b_correct_prepend(self):
        """Insertion as correction (prepend)"""
        q = fql.Query(Qcorrect_prepend)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "insertion")
        self.assertEqual(results[0].text(), "heel")
        self.assertEqual(results[0].next(folia.Word).text(), "ander")

    def test30_select_startend(self):
        q = fql.Query(Qselect_startend)
        results = q(self.doc)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].text(), "de")
        self.assertEqual(results[1].text(), "historische")
        self.assertEqual(results[2].text(), "wetenschap")

    def test30_select_startend2(self):
        q = fql.Query(Qselect_startend2)
        results = q(self.doc)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].text(), "de")
        self.assertEqual(results[1].text(), "historische")

    def test31_in(self):
        q = fql.Query(Qin)
        results = q(self.doc)
        self.assertEqual(len(results), 2)

    def test31b_in2(self):
        q = fql.Query(Qin2)
        results = q(self.doc)
        self.assertEqual(len(results), 0)

    def test31c_in2ref(self):
        q = fql.Query(Qin2ref)
        results = q(self.doc)
        self.assertEqual(len(results), 6) #includes ph under phoneme

    def test31d_tfor(self):
        q = fql.Query("SELECT t FOR w ID \"WR-P-E-J-0000000001.sandbox.2.s.1.w.2\"")
        results = q(self.doc)
        self.assertEqual(len(results), 3) #includes t under morpheme

    def test31e_tin(self):
        q = fql.Query("SELECT t IN w ID \"WR-P-E-J-0000000001.sandbox.2.s.1.w.2\"")
        results = q(self.doc)
        self.assertEqual(len(results), 1)

    def test32_correct_delete(self):
        """Deletion as correction"""
        q = fql.Query(Qcorrect_delete)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "redundantword")
        self.assertEqual(results[0].hastext(), False)
        self.assertEqual(results[0].text(correctionhandling=folia.CorrectionHandling.ORIGINAL), "een")

    def test33_suggest_insertion(self):
        """Insertion as suggestion (prepend)"""
        q = fql.Query(Qsuggest_insertion)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "insertion")
        self.assertEqual(results[0].suggestions(0).text(), "heel")
        self.assertEqual(results[0].next(folia.Word,None).text(), "ander")

    def test34_suggest_insertion2(self):
        """Insertion as suggestion (append)"""
        q = fql.Query(Qsuggest_insertion2)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].cls, "insertion")
        self.assertEqual(results[0].suggestions(0).text(), "heel")
        self.assertEqual(results[0].next(folia.Word,None).text(), "ander")

    def test35_comment(self):
        """Adding a comment"""
        q = fql.Query(Qcomment)
        results = q(self.doc)
        self.assertIsInstance(results[0], folia.Comment)
        self.assertEqual(results[0].value, "This is our university!")
        self.assertEqual(results[0].parent.id, "example.radboud.university.nijmegen.org")

class Test4CQL(unittest.TestCase):
    def setUp(self):
        self.doc = folia.Document(string=FOLIAEXAMPLE)

    def test01_context(self):
        q = fql.Query(cql.cql2fql(Qcql_context))
        results = q(self.doc)
        self.assertTrue( len(results) > 0 )
        for result in results:
            self.assertIsInstance(result, fql.SpanSet)
            #print("RESULT: ", [w.text() for w in result])
            self.assertEqual(len(result), 3)
            self.assertIsInstance(result[0], folia.Word)
            self.assertIsInstance(result[1], folia.Word)
            self.assertIsInstance(result[2], folia.Word)
            self.assertEqual(result[0].text(), "de")
            self.assertEqual(result[1].pos()[:4], "ADJ(")
            self.assertEqual(result[2].pos()[:2], "N(")

    def test02_context(self):
        q = fql.Query(cql.cql2fql(Qcql_context2))
        results = q(self.doc)
        self.assertTrue( len(results) > 0 )

        textresults = []
        for result in results:
            self.assertIsInstance(result, fql.SpanSet)
            textresults.append(  tuple([w.text() for w in result]) )

        self.assertTrue( ('het','alfabet') in textresults )
        self.assertTrue( ('vierkante','haken') in textresults )
        self.assertTrue( ('plaats',) in textresults )
        self.assertTrue( ('het','originele','handschrift') in textresults )
        self.assertTrue( ('Een','volle','lijn') in textresults )

    def test03_context(self):
        q = fql.Query(cql.cql2fql(Qcql_context3))
        results = q(self.doc)
        self.assertEqual( len(results), 2 )

        textresults = []
        for result in results:
            self.assertIsInstance(result, fql.SpanSet)
            self.assertEqual(len(result), 2)
            textresults.append(  tuple([w.text() for w in result]) )

        #print(textresults,file=sys.stderr)

        self.assertTrue( ('naam','stemma') in textresults )
        self.assertTrue( ('stemma','codicum') in textresults )

    def test04_context(self):
        q = fql.Query(cql.cql2fql(Qcql_context4))
        results = q(self.doc)
        self.assertEqual( len(results),2  )

        textresults = []
        for result in results:
            self.assertIsInstance(result, fql.SpanSet)
            textresults.append(  tuple([w.text() for w in result]) )

        #print(textresults,file=sys.stderr)

        self.assertTrue( ('genummerd','en','gedateerd') in textresults )
        self.assertTrue( ('opgenomen','en','worden','weergegeven') in textresults )

    def test05_context(self):
        q = fql.Query(cql.cql2fql(Qcql_context5))
        results = q(self.doc)
        self.assertTrue( len(results) > 0 )

        textresults = []
        for result in results:
            self.assertIsInstance(result, fql.SpanSet)
            textresults.append(  tuple([w.text() for w in result]) )

        #print(textresults,file=sys.stderr)

        self.assertTrue( ('en','gedateerd','zodat') in textresults )
        self.assertTrue( ('en','worden','weergegeven','door') in textresults )
        self.assertTrue( ('zodat','ze') in textresults )
        self.assertTrue( ('en','worden','tussen') in textresults )
        self.assertTrue( ('terweil','een') in textresults )

    def test06_context(self):
        q = fql.Query(cql.cql2fql(Qcql_context6))
        results = q(self.doc)
        self.assertTrue( len(results) > 0 )

        for result in results:
            self.assertIsInstance(result, fql.SpanSet)
            self.assertEqual(len(result), 1)
            self.assertTrue(result[0].pos()[:2] == "VZ" or result[0].pos()[:2] == "VG" )

class Test4Evaluation(unittest.TestCase):
    """Higher-order corrections  (corrections on corrections)"""
    def setUp(self):
        self.doc = folia.Document(string=FOLIACORRECTIONEXAMPLE)

    def test1_split2(self):
        """Substitute - Split (higher-order)"""
        q = fql.Query(Qsplit2)
        results = q(self.doc)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].text(), "Ik hoor")

    def test2_merge2(self):
        """Substitute - Merge (higher-order)"""
        q = fql.Query(Qmerge2)
        results = q(self.doc)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].text(), "onweer")

    def test3_deletion2(self):
        """Deletion (higher-order)"""
        q = fql.Query(Qdeletion2)
        results = q(self.doc)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].hastext(), False)
        self.assertEqual(results[0].original().text(), "een")
        self.assertEqual(results[0].previous(None).id, "correctionexample.s.8.w.2")
        self.assertEqual(results[0].next(None).id, "correctionexample.s.8.w.4")

    def test3_insertion2(self):
        """Substitute - Insertion (higher-order)"""
        q = fql.Query(Qinsertion2)
        results = q(self.doc)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], folia.Correction)
        self.assertEqual(results[0].text(), '.')
        self.assertIsInstance(results[0].original()[0], folia.Correction)

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

f = io.open(FOLIAPATH + '/test/correctionexample.xml', 'r',encoding='utf-8')
FOLIACORRECTIONEXAMPLE = f.read()
f.close()

if __name__ == '__main__':
    unittest.main()
