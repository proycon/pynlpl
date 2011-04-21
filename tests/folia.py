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

import sys
import os
import unittest
import codecs
sys.path.append(sys.path[0] + '/../../')
os.environ['PYTHONPATH'] = sys.path[0] + '/../../'

from StringIO import StringIO
import lxml.etree
import pynlpl.formats.folia as folia


class Test1Read(unittest.TestCase):
                        
    def test1_readfromfile(self):        
        """Reading from file"""
        global FOLIAEXAMPLE
        #write example to file
        f = codecs.open('/tmp/foliatest.xml','w','utf-8')
        f.write(FOLIAEXAMPLE)    
        f.close()
        
        doc = folia.Document(file='/tmp/foliatest.xml')
        self.assertTrue(isinstance(doc,folia.Document))
        
    def test2_readfromstring(self):        
        """Reading from string"""        
        global FOLIAEXAMPLE
        doc = folia.Document(string=FOLIAEXAMPLE)
        self.assertTrue(isinstance(doc,folia.Document))
        
    def test3_readfromstring(self):        
        """Reading from pre-parsed XML tree (lxml)"""        
        global FOLIAEXAMPLE
        doc = folia.Document(tree=lxml.etree.parse(StringIO(FOLIAEXAMPLE.encode('utf-8'))))
        self.assertTrue(isinstance(doc,folia.Document))

    def test4_readdcoi(self):        
        """Reading D-Coi file"""
        global DCOIEXAMPLE
        doc = folia.Document(tree=lxml.etree.parse(StringIO(DCOIEXAMPLE.encode('iso-8859-15'))))
        self.assertTrue(isinstance(doc,folia.Document))
        
class Test2Sanity(unittest.TestCase):
    
    def setUp(self):
        self.doc = folia.Document(file='/tmp/foliatest.xml')

    def test000_count_paragraphs(self):                                    
        """Sanity check - One text """        
        self.assertEqual( len(self.doc), 1) 
        self.assertTrue( isinstance( self.doc[0], folia.Text )) 
        
    def test001_count_paragraphs(self):                                    
        """Sanity check - Paragraph count"""        
        self.assertEqual( len(self.doc.paragraphs()) , 1)
        
    def test002_count_sentences(self):                                    
        """Sanity check - Sentences count"""        
        self.assertEqual( len(self.doc.sentences()) , 9)        
    
    def test003_count_words(self):                                    
        """Sanity check - Word count"""        
        self.assertEqual( len(self.doc.words()) , 151)
    
    def test004_first_word(self):                                    
        """Sanity check - First word"""            
        #grab first word
        w = self.doc.words(0) # shortcut for doc.words()[0]         
        self.assertTrue( isinstance(w, folia.Word) )
        self.assertEqual( w.id , 'WR-P-E-J-0000000001.head.1.s.1.w.1' )         
        self.assertEqual( w.text() , "Stemma" ) 
        self.assertEqual( str(w) , "Stemma" ) 
        self.assertEqual( unicode(w) , u"Stemma" ) 
        
        
    def test005_last_word(self):                                    
        """Sanity check - Last word"""            
        #grab first word
        w = self.doc.words(-1) # shortcut for doc.words()[0]         
        self.assertTrue( isinstance(w, folia.Word) )
        self.assertEqual( w.id , 'WR-P-E-J-0000000001.p.1.s.8.w.17' ) 
        self.assertEqual( w.text() , "." )             
        self.assertEqual( str(w) , "." )             
        
    def test006_first_sentence(self):                                    
        """Sanity check - Sentence"""                                
        #grab last sentence
        s = self.doc.sentences(1)
        self.assertTrue( isinstance(s, folia.Sentence) )
        self.assertEqual( s.id, 'WR-P-E-J-0000000001.p.1.s.1' )
        self.assertRaises( folia.NoSuchText, s.text) #no text DIRECTLY associated with the sentence
        self.assertEqual( str(s), "Stemma is een ander woord voor stamboom . " ) 
        
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
        
        self.assertEqual( w.pos(), w.annotation(folia.PosAnnotation) ) #w.pos() is just a shortcut 
        self.assertEqual( w.annotation(folia.PosAnnotation), w.select(folia.PosAnnotation)[0] ) #w.annotation() selects the single first annotation of that type, select is the generic method to retrieve pretty much everything
        self.assertTrue( isinstance(w.pos(), folia.PosAnnotation) )
        self.assertTrue( issubclass(folia.PosAnnotation, folia.AbstractTokenAnnotation) )
                
        self.assertEqual( w.pos().cls, 'N(soort,ev,basis,onz,stan)' ) #cls is used everywhere instead of class, since class is a reserved keyword in python
        self.assertEqual( w.pos().set, 'cgn-combinedtags' ) 
        self.assertEqual( w.pos().annotator, 'tadpole' ) 
        self.assertEqual( w.pos().annotatortype, folia.AnnotatorType.AUTO )

    
    def test010_lemma(self):                                        
        """Sanity check - Token Annotation - Lemma""" 
        #grab first word
        w = self.doc.words(0)
        
        self.assertEqual( w.lemma(), w.annotation(folia.LemmaAnnotation) ) #w.lemma() is just a shortcut 
        self.assertEqual( w.annotation(folia.LemmaAnnotation), w.select(folia.LemmaAnnotation)[0] ) #w.annotation() selects the single first annotation of that type, select is the generic method to retrieve pretty much everything
        self.assertTrue( isinstance(w.lemma(), folia.LemmaAnnotation))
                
        self.assertEqual( w.lemma().cls, 'stemma' )
        self.assertEqual( w.lemma().set, 'lemmas-nl' ) 
        self.assertEqual( w.lemma().annotator, 'tadpole' ) 
        self.assertEqual( w.lemma().annotatortype, folia.AnnotatorType.AUTO )

    def test011_tokenannot_notexist(self):                                        
        """Sanity check - Token Annotation - Non-existing element""" 
        #grab first word
        w = self.doc.words(0)
        
        self.assertEqual( len(w.select(folia.SenseAnnotation)), 0)  #list
        self.assertRaises( folia.NoSuchAnnotation, w.annotation, folia.SenseAnnotation) #exception


    def test099_write(self):        
        """Sanity Check - Writing to file"""
        self.doc.save('/tmp/foliasavetest.xml')
    
    def test100_sanity(self):                       
        """Sanity Check - Checking output file against input (should be equal)"""
        #use diff to compare the two:
        retcode = os.system('diff -w -c /tmp/foliatest.xml /tmp/foliasavetest.xml')
        self.assertEqual( retcode, 0)
        
class Test3Edit(unittest.TestCase):
        
    def setUp(self):
        global FOLIAEXAMPLE
        self.doc = folia.Document(tree=lxml.etree.parse(StringIO(FOLIAEXAMPLE.encode('utf-8'))))

    
    def test001_addsentence(self):        
        """Edit Check - Adding a sentence to last paragraph"""
        
        #grab last paragraph
        p = self.doc.paragraphs(-1)
                    
        #how many sentences?
        tmp = len(p)
                    
        #make a sentence            
        s = folia.Sentence(self.doc, generate_id_in=p)
        #add words to the sentence
        s.append( folia.Word(self.doc, text='Dit',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        s.append( folia.Word(self.doc, text='is',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        s.append( folia.Word(self.doc, text='een',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        s.append( folia.Word(self.doc, text='nieuwe',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        s.append( folia.Word(self.doc, text='zin',generate_id_in=s, annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
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
        self.assertEqual( len(p) , tmp + 1)
        self.assertEqual( p[-1] , s)
        
    def test002_addannotation(self):        
        """Edit Check - Adding a token annotation (pos, lemma)"""
         
        #grab a word (naam)
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.11']
        
        #add a pos annotation (in a different set than the one already present, to prevent conflict)
        w.append( folia.PosAnnotation(self.doc, set='adhocpos', cls='NOUN', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO) )
        w.append( folia.LemmaAnnotation(self.doc, set='adhoclemma', cls='NAAM', annotator='testscript', annotatortype=folia.AnnotatorType.AUTO ) ) 
        
        #retrieve and check
        p = w.annotation(folia.PosAnnotation, 'adhocpos')
        self.assertTrue( isinstance(p, folia.PosAnnotation) )
        self.assertEqual( p.cls, 'NOUN' )
        
        l = w.annotation(folia.LemmaAnnotation, 'adhoclemma')
        self.assertTrue( isinstance(l, folia.LemmaAnnotation) )
        self.assertEqual( l.cls, 'NAAM' )

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
        
        alt2 = w.alternatives(folia.AnnotationType.POS, set)        
        
        self.assertEqual( alt[0],alt2[0] )        
        self.assertEqual( len(alt),1 )
        self.assertEqual( len(alt2),1 )        
        self.assertTrue( isinstance(alt[0].annotation(folia.PosAnnotation, set), folia.PosAnnotation) )

    def test006_addcorrection(self):        
        """Edit Check - Correcting Text"""
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn
        w.correcttext('stippellijn', set='corrections',cls='spelling',annotator='testscript', annotatortype='auto') 
                    
        self.assertEqual( w.annotation(folia.Correction).original[0] ,'stippelijn' ) 
        self.assertEqual( w.annotation(folia.Correction).new[0] ,'stippellijn' )     
        self.assertEqual( w.text(), 'stippellijn')    
        
        
    def test007_addcorrection2(self):        
        """Edit Check - Correcting a Token Annotation element"""        
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn
        oldpos = w.annotation(folia.PosAnnotation)
        newpos = folia.PosAnnotation(self.doc, cls='N(soort,ev,basis,zijd,stan)')
        w.correct(w.annotation(oldpos),newpos, set='corrections',cls='spelling',annotator='testscript', annotatortype='auto') 
                    
        self.assertEqual( w.annotation(folia.Correction).original[0] ,oldpos ) 
        self.assertEqual( w.annotation(folia.Correction).new[0] ,'newpos' )     
    
    
    def test008_addaltcorrection(self):            
        """Edit Check - Adding alternative corrections"""        
        w = self.doc.index['WR-P-E-J-0000000001.p.1.s.8.w.11'] #stippelijn
        w.correcttext('stippellijn', set='corrections',cls='spelling',annotator='testscript', annotatortype='auto', alternative=True) 
            
        alt = w.alternatives(folia.AnnotationType.CORRECTION)        
        self.assertEqual( alt[0].annotation(folia.Correction).original[0] ,'stippelijn' ) 
        self.assertEqual( alt[0].annotation(folia.Correction).new[0] ,'stippellijn' ) 
        
class Test4Create(unittest.TestCase):
        def test001_create(self):
            """Creating a FoLiA Document from scratch"""
            self.doc = folia.Document(id='example')
            self.doc.declare(folia.AnnotationType.TOKEN, set='adhocset',annotator='proycon')
        
            self.assertEqual(self.doc.defaultset(folia.AnnotationType.TOKEN), 'adhocset')
            self.assertEqual(self.doc.defaultannotator(folia.AnnotationType.TOKEN), 'proycon')
    
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
        def test001_splitcorrection(self):  
            """Correction - Split corrections"""
            self.doc = folia.Document(id='example')
            self.doc.declare(folia.AnnotationType.TOKEN, set='adhocset',annotator='proycon')        
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
        
            s = self.doc.index[self.doc.id + '.s.1']
            w = self.doc.index[self.doc.id + '.s.1.w.4']
            
            s.splitword( w, folia.Word(self.doc, id=self.doc.id + '.s.1.w.4a', text="on"), folia.Word(self.doc, id=self.doc.id + '.s.1.w.4b', text="line") )
                        
            self.assertEqual( len(s.words()), 6 )
            
            
            
        def test002_mergecorrection(self):         
            """Correction - Merge corrections"""
            self.doc = folia.Document(id='example')
            self.doc.declare(folia.AnnotationType.TOKEN, set='adhocset',annotator='proycon')        
            text = folia.Text(self.doc, id=self.doc.id + '.text.1')
            self.doc.append( text )
            
            text.append(
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
            
                               
            s.mergewords( folia.Word(self.doc, id=self.doc.id + '.s.1.w.4-5') , self.doc.index[self.doc.id + '.s.1.w.5'], self.doc.index[self.doc.id + '.s.1.w.6'] )
           
            self.assertEqual( len(s.words()), 5 )
            
            
        def test003_deletecorrection(self):         
            """Correction - Deletion"""
            self.doc = folia.Document(id='example')
            self.doc.declare(folia.AnnotationType.TOKEN, set='adhocset',annotator='proycon')        
            text = folia.Text(self.doc, id=self.doc.id + '.text.1')
            self.doc.append( text )
            
            text.append(
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
        
            s.deleteword(self.doc.index[self.doc.id + '.s.1.w.4'])
            self.assertEqual( len(s.words()), 5 )

        def test004_insertcorrection(self):         
            """Correction - Insert"""
            self.doc = folia.Document(id='example')
            self.doc.declare(folia.AnnotationType.TOKEN, set='adhocset',annotator='proycon')        
            text = folia.Text(self.doc, id=self.doc.id + '.text.1')
            self.doc.append( text )
            
            text.append(
                folia.Sentence(self.doc,id=self.doc.id + '.s.1', contents=[
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.1', text="Ik"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.2', text="zie"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.3', text="een"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.4', text="huis"),
                    folia.Word(self.doc,id=self.doc.id + '.s.1.w.5', text=".")
                ]
                )
            )
            
            s.inswertword( folia.Word(self.doc, id=self.doc.id+'.s.1.w.3b',text='groot'),  self.doc.index[self.doc.id + '.s.1.w.3'])
            self.assertEqual( len(s.words()), 6 )

            
    
FOLIAEXAMPLE = u"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="folia.xsl"?>
<FoLiA xmlns="http://ilk.uvt.nl/folia" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:imdi="http://www.mpi.nl/IMDI/Schema/IMDI" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dcoi="http://lands.let.ru.nl/projects/d-coi/ns/1.0" xml:id="WR-P-E-J-0000000001">
  <metadata>
    <annotations>
      <token-annotation annotator="ilktok" annotatortype="auto" />
      <pos-annotation set="cgn-combinedtags" annotator="tadpole" annotatortype="auto" />
      <lemma-annotation set="lemmas-nl" annotator="tadpole" annotatortype="auto" />
    </annotations>
    <imdi:METATRANSCRIPT xmlns="http://lands.let.ru.nl/projects/d-coi/ns/1.0" xmlns:d-coi="http://lands.let.ru.nl/projects/d-coi/ns/1.0" Date="2009-01-27" Type="SESSION" Version="1">
    <imdi:Session>
      <imdi:Name>WR-P-E-J-0000000001</imdi:Name>
      <imdi:Title>Stemma</imdi:Title>
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
          <imdi:Size>2865</imdi:Size>
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
  </metadata>
  <text xml:id="WR-P-E-J-0000000001.text">
      <div xml:id="WR-P-E-J-0000000001.div0.1">
        <head xml:id="WR-P-E-J-0000000001.head.1">
          <s xml:id="WR-P-E-J-0000000001.head.1.s.1">
            <w xml:id="WR-P-E-J-0000000001.head.1.s.1.w.1">
              <t>Stemma</t>
              <pos class="N(soort,ev,basis,onz,stan)"/>
              <lemma class="stemma"/>
            </w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000000001.p.1">
          <s xml:id="WR-P-E-J-0000000001.p.1.s.1">
            <w xml:id="WR-P-E-J-0000000001.p.1.s.1.w.1">
              <t>Stemma</t>
              <pos class="N(eigen,ev,basis,zijd,stan)" />
              <lemma class="Stemma" />
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.1.w.2">
              <t>is</t>
              <pos class="WW(pv,tgw,ev)"/>
              <lemma class="zijn"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.1.w.3">
              <t>een</t>
              <pos class="LID(onbep,stan,agr)"/>
              <lemma class="een"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.1.w.4">
              <t>ander</t>
              <pos class="ADJ(prenom,basis,zonder)"/>
              <lemma class="ander"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.1.w.5">
              <t>woord</t>
              <pos class="N(soort,ev,basis,onz,stan)"/>
              <lemma class="woord"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.1.w.6">
              <t>voor</t>
              <pos class="VZ(init)"/>
              <lemma class="voor"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.1.w.7">
              <t>stamboom</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="stamboom"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.1.w.8">
              <t>.</t>
              <pos class="LET()"/>
              <lemma class="."/>
            </w>
            <syntax>
                <su class="sentence">
                 <su class="subject"><wref id="WR-P-E-J-0000000001.p.1.s.1.w.1" t="Stemma" /></su>
                 <su class="verb"><wref id="WR-P-E-J-0000000001.p.1.s.1.w.2" t="is" /></su>
                 <su class="predicate">
                    <su class="np">
                        <wref id="WR-P-E-J-0000000001.p.1.s.1.w.3" t="een" />
                        <wref id="WR-P-E-J-0000000001.p.1.s.1.w.4" t="ander" />
                        <wref id="WR-P-E-J-0000000001.p.1.s.1.w.5" t="woord" />
                    </su>
                    <su class="pp">
                        <wref id="WR-P-E-J-0000000001.p.1.s.1.w.6" t="voor" />
                        <wref id="WR-P-E-J-0000000001.p.1.s.1.w.7" t="stamboom" />
                    </su>
                 </su>
                 <wref id="WR-P-E-J-0000000001.p.1.s.1.w.8" t="." />
                </su>
            </syntax>
          </s>
          <s xml:id="WR-P-E-J-0000000001.p.1.s.2">
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.1">
              <t>In</t>
              <pos class="VZ(init)"/>
              <lemma class="in"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.2">
              <t>de</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.3">
              <t>historische</t>
              <pos class="ADJ(prenom,basis,met-e,stan)"/>
              <lemma class="historisch"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.4">
              <t>wetenschap</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="wetenschap"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.5">
              <t>wordt</t>
              <pos class="WW(pv,tgw,met-t)"/>
              <lemma class="worden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.6">
              <t>zo'n</t>
              <pos class="VNW(aanw,det,stan,prenom,zonder,agr)"/>
              <lemma class="zo'n"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.7">
              <t>stamboom</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="stamboom"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.8">
              <t>,</t>
              <pos class="LET()"/>
              <lemma class=","/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.9">
              <t>onder</t>
              <pos class="VZ(init)"/>
              <lemma class="onder"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.10">
              <t>de</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.11">
              <t>naam</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="naam"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.12">
              <t>stemma</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="stemma"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.13">
              <t>codicum</t>
              <pos class="N(soort,ev,basis,onz,stan)"/>
              <lemma class="codicum"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.14">
              <t>(</t>
              <pos class="LET()"/>
              <lemma class="("/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.15">
              <t>handschriftelijke</t>
              <pos class="ADJ(prenom,basis,met-e,stan)"/>
              <lemma class="handschriftelijk"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.16">
              <t>genealogie</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="genealogie"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.17">
              <t>)</t>
              <pos class="LET()"/>
              <lemma class=")"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.18">
              <t>,</t>
              <pos class="LET()"/>
              <lemma class=","/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.19">
              <t>gebruikt</t>
              <pos class="WW(vd,vrij,zonder)"/>
              <lemma class="gebruiken"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.20">
              <t>om</t>
              <pos class="VZ(init)"/>
              <lemma class="om"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.21">
              <t>de</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.22">
              <t>verwantschap</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="verwantschap"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.23">
              <t>tussen</t>
              <pos class="VZ(init)"/>
              <lemma class="tussen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.24">
              <t>handschrift</t>
              <pos class="N(soort,ev,basis,onz,stan)"/>
              <lemma class="handschrift"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.25">
              <t>en</t>
              <pos class="VG(neven)"/>
              <lemma class="en"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.26">
              <t>weer</t>
              <pos class="BW()"/>
              <lemma class="weer"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.27">
              <t>te</t>
              <pos class="VZ(init)"/>
              <lemma class="te"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.28">
              <t>geven</t>
              <pos class="WW(inf,vrij,zonder)"/>
              <lemma class="geven"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.2.w.29">
              <t>.</t>
              <pos class="LET()"/>
              <lemma class="."/>
            </w>
          </s>
          <s xml:id="WR-P-E-J-0000000001.p.1.s.3">
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.1">
              <t>Werkwijze</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="werkwijz"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.2">
              <t>Hiervoor</t>
              <pos class="BW()"/>
              <lemma class="hiervoor"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.3">
              <t>worden</t>
              <pos class="WW(pv,tgw,mv)"/>
              <lemma class="worden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.4">
              <t>de</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.5">
              <t>handschriften</t>
              <pos class="N(soort,mv,basis)"/>
              <lemma class="handschrift"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.6">
              <t>genummerd</t>
              <pos class="WW(vd,vrij,zonder)"/>
              <lemma class="nummeren"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.7">
              <t>en</t>
              <pos class="VG(neven)"/>
              <lemma class="en"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.8">
              <t>gedateerd</t>
              <pos class="WW(vd,vrij,zonder)"/>
              <lemma class="dateren"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.9">
              <t>zodat</t>
              <pos class="VG(onder)"/>
              <lemma class="zodat"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.10">
              <t>ze</t>
              <pos class="VNW(pers,pron,stan,red,3,ev,fem)"/>
              <lemma class="ze"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.11">
              <t>op</t>
              <pos class="VZ(init)"/>
              <lemma class="op"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.12">
              <t>de</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.13">
              <t>juiste</t>
              <pos class="ADJ(prenom,basis,met-e,stan)"/>
              <lemma class="juist"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.14">
              <t>plaats</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="plaats"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.15">
              <t>van</t>
              <pos class="VZ(init)"/>
              <lemma class="van"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.16">
              <t>hun</t>
              <pos class="VNW(bez,det,stan,vol,3,mv,prenom,zonder,agr)"/>
              <lemma class="hun"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.17">
              <t>afstammingsgeschiedenis</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="afstammingsgeschiedenis"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.18">
              <t>geplaatst</t>
              <pos class="WW(vd,vrij,zonder)"/>
              <lemma class="plaatsen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.19">
              <t>kunnen</t>
              <pos class="WW(pv,tgw,mv)"/>
              <lemma class="kunnen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.20">
              <t>worden</t>
              <pos class="WW(inf,vrij,zonder)"/>
              <lemma class="worden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.3.w.21">
              <t>.</t>
              <pos class="LET()"/>
              <lemma class="."/>
            </w>
          </s>
          <s xml:id="WR-P-E-J-0000000001.p.1.s.4">
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.1">
              <t>De</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.2">
              <t>hoofdletter</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="hoofdletter"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.3">
              <t>A</t>
              <pos class="SPEC(symb)"/>
              <lemma class="_"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.4">
              <t>wordt</t>
              <pos class="WW(pv,tgw,met-t)"/>
              <lemma class="worden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.5">
              <t>gebruikt</t>
              <pos class="WW(vd,vrij,zonder)"/>
              <lemma class="gebruiken"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.6">
              <t>voor</t>
              <pos class="VZ(init)"/>
              <lemma class="voor"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.7">
              <t>het</t>
              <pos class="LID(bep,stan,evon)"/>
              <lemma class="het"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.8">
              <t>originele</t>
              <pos class="ADJ(prenom,basis,met-e,stan)"/>
              <lemma class="origineel"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.9">
              <t>handschrift</t>
              <pos class="N(soort,ev,basis,onz,stan)"/>
              <lemma class="handschrift"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.4.w.10">
              <t>.</t>
              <pos class="LET()"/>
              <lemma class="."/>
            </w>
          </s>
          <s xml:id="WR-P-E-J-0000000001.p.1.s.5">
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.1">
              <t>De</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.2">
              <t>andere</t>
              <pos class="ADJ(prenom,basis,met-e,stan)"/>
              <lemma class="ander"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.3">
              <t>handschriften</t>
              <pos class="N(soort,mv,basis)"/>
              <lemma class="handschrift"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.4">
              <t>krijgen</t>
              <pos class="WW(pv,tgw,mv)"/>
              <lemma class="krijgen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.5">
              <t>ook</t>
              <pos class="BW()"/>
              <lemma class="ook"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.6">
              <t>een</t>
              <pos class="LID(onbep,stan,agr)"/>
              <lemma class="een"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.7">
              <t>letter</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="letter"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.8">
              <t>die</t>
              <pos class="VNW(betr,pron,stan,vol,persoon,getal)"/>
              <lemma class="die"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.9">
              <t>verband</t>
              <pos class="N(soort,ev,basis,onz,stan)"/>
              <lemma class="verband"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.10">
              <t>kan</t>
              <pos class="WW(pv,tgw,ev)"/>
              <lemma class="kunnen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.11">
              <t>houden</t>
              <pos class="WW(inf,vrij,zonder)"/>
              <lemma class="houden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.12">
              <t>met</t>
              <pos class="VZ(init)"/>
              <lemma class="met"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.13">
              <t>hun</t>
              <pos class="VNW(bez,det,stan,vol,3,mv,prenom,zonder,agr)"/>
              <lemma class="hun"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.14">
              <t>plaats</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="plaats"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.15">
              <t>van</t>
              <pos class="VZ(init)"/>
              <lemma class="van"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.16">
              <t>oorsprong</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="oorsprong"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.17">
              <t>of</t>
              <pos class="VG(neven)"/>
              <lemma class="of"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.18">
              <t>plaats</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="plaats"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.19">
              <t>van</t>
              <pos class="VZ(init)"/>
              <lemma class="van"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.20">
              <t>bewaring</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="bewaring"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.5.w.21">
              <t>.</t>
              <pos class="LET()"/>
              <lemma class="."/>
            </w>
          </s>
          <s xml:id="WR-P-E-J-0000000001.p.1.s.6">
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.1">
              <t>Verdwenen</t>
              <pos class="WW(vd,prenom,zonder)"/>
              <lemma class="verdwijnen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.2">
              <t>handschriften</t>
              <pos class="N(soort,mv,basis)"/>
              <lemma class="handschrift"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.3">
              <t>waarvan</t>
              <pos class="BW()"/>
              <lemma class="waarvan"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.4">
              <t>men</t>
              <pos class="VNW(pers,pron,nomin,red,3p,ev,masc)"/>
              <lemma class="men"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.5">
              <t>toch</t>
              <pos class="BW()"/>
              <lemma class="toch"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.6">
              <t>vermoedt</t>
              <pos class="WW(pv,tgw,met-t)"/>
              <lemma class="vermoeden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.7">
              <t>dat</t>
              <pos class="VG(onder)"/>
              <lemma class="dat"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.8">
              <t>ze</t>
              <pos class="VNW(pers,pron,stan,red,3,mv)"/>
              <lemma class="ze"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.9">
              <t>ooit</t>
              <pos class="BW()"/>
              <lemma class="ooit"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.10">
              <t>bestaan</t>
              <pos class="WW(inf,vrij,zonder)"/>
              <lemma class="bestaan"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.11">
              <t>hebben</t>
              <pos class="WW(inf,vrij,zonder)"/>
              <lemma class="hebben"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.12">
              <t>worden</t>
              <pos class="WW(inf,vrij,zonder)"/>
              <lemma class="worden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.13">
              <t>ook</t>
              <pos class="BW()"/>
              <lemma class="ook"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.14">
              <t>in</t>
              <pos class="VZ(init)"/>
              <lemma class="in"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.15">
              <t>het</t>
              <pos class="LID(bep,stan,evon)"/>
              <lemma class="het"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.16">
              <t>stemma</t>
              <pos class="N(soort,ev,basis,onz,stan)"/>
              <lemma class="stemma"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.17">
              <t>opgenomen</t>
              <pos class="WW(vd,vrij,zonder)"/>
              <lemma class="opnemen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.18">
              <t>en</t>
              <pos class="VG(neven)"/>
              <lemma class="en"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.19">
              <t>worden</t>
              <pos class="WW(pv,tgw,mv)"/>
              <lemma class="worden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.20">
              <t>weergegeven</t>
              <pos class="WW(vd,vrij,zonder)"/>
              <lemma class="weergeven"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.21">
              <t>door</t>
              <pos class="VZ(init)"/>
              <lemma class="door"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.22">
              <t>de</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.23">
              <t>laatste</t>
              <pos class="ADJ(prenom,sup,met-e,stan)"/>
              <lemma class="laat"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.24">
              <t>letters</t>
              <pos class="N(soort,mv,basis)"/>
              <lemma class="letter"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.25">
              <t>van</t>
              <pos class="VZ(init)"/>
              <lemma class="van"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.26">
              <t>het</t>
              <pos class="LID(bep,stan,evon)"/>
              <lemma class="het"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.27">
              <t>alfabet</t>
              <pos class="N(soort,ev,basis,onz,stan)"/>
              <lemma class="alfabet"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.28">
              <t>en</t>
              <pos class="VG(neven)"/>
              <lemma class="en"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.29">
              <t>worden</t>
              <pos class="WW(pv,tgw,mv)"/>
              <lemma class="worden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.30">
              <t>tussen</t>
              <pos class="VZ(init)"/>
              <lemma class="tussen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.31">
              <t>vierkante</t>
              <pos class="ADJ(prenom,basis,met-e,stan)"/>
              <lemma class="vierkant"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.32">
              <t>haken</t>
              <pos class="N(soort,mv,basis)"/>
              <lemma class="haak"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.33">
              <t>geplaatst</t>
              <pos class="WW(vd,vrij,zonder)"/>
              <lemma class="plaatsen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.6.w.34">
              <t>.</t>
              <pos class="LET()"/>
              <lemma class="."/>
            </w>
          </s>
          <s xml:id="WR-P-E-J-0000000001.p.1.s.7">
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.1">
              <t>Tenslotte</t>
              <pos class="BW()"/>
              <lemma class="tenslotte"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.2">
              <t>gaat</t>
              <pos class="WW(pv,tgw,met-t)"/>
              <lemma class="gaan"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.3">
              <t>men</t>
              <pos class="VNW(pers,pron,nomin,red,3p,ev,masc)"/>
              <lemma class="men"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.4">
              <t>de</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.5">
              <t>verwantschap</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="verwantschap"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.6">
              <t>tussen</t>
              <pos class="VZ(init)"/>
              <lemma class="tussen"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.7">
              <t>de</t>
              <pos class="LID(bep,stan,rest)"/>
              <lemma class="de"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.8">
              <t>handschriften</t>
              <pos class="N(soort,mv,basis)"/>
              <lemma class="handschrift"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.9">
              <t>aanduiden</t>
              <pos class="WW(inf,vrij,zonder)"/>
              <lemma class="aanduiden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.7.w.10">
              <t>.</t>
              <pos class="LET()"/>
              <lemma class="."/>
            </w>
          </s>
          <s xml:id="WR-P-E-J-0000000001.p.1.s.8">
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.1">
              <t>Een</t>
              <pos class="LID(onbep,stan,agr)"/>
              <lemma class="een"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.2">
              <t>volle</t>
              <pos class="ADJ(prenom,basis,met-e,stan)"/>
              <lemma class="vol"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.3">
              <t>lijn</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="lijn"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.4">
              <t>duidt</t>
              <pos class="WW(pv,tgw,met-t)"/>
              <lemma class="duiden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.5">
              <t>op</t>
              <pos class="VZ(init)"/>
              <lemma class="op"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.6">
              <t>een</t>
              <pos class="LID(onbep,stan,agr)"/>
              <lemma class="een"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.7">
              <t>verwantschap</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="verwantschap"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.8">
              <t>,</t>
              <pos class="LET()"/>
              <lemma class=","/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.9">
              <t>terwijl</t>
              <pos class="VG(onder)"/>
              <lemma class="terwijl"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.10">
              <t>een</t>
              <pos class="LID(onbep,stan,agr)"/>
              <lemma class="een"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.11">
              <t>stippelijn</t>
              <pos class="FOUTN(soort,ev,basis,zijd,stan)"/>
              <lemma class="stippelijn"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.12">
              <t>op</t>
              <pos class="VZ(init)"/>
              <lemma class="op"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.13">
              <t>een</t>
              <pos class="LID(onbep,stan,agr)"/>
              <lemma class="een"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.14">
              <t>onzekere</t>
              <pos class="ADJ(prenom,basis,met-e,stan)"/>
              <lemma class="onzeker"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.15">
              <t>verwantschap</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="verwantschap"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.16">
              <t>duidt</t>
              <pos class="WW(pv,tgw,met-t)"/>
              <lemma class="duiden"/>
            </w>
            <w xml:id="WR-P-E-J-0000000001.p.1.s.8.w.17">
              <t>.</t>
              <pos class="LET()"/>
              <lemma class="."/>
            </w>
          </s>
        </p>
      </div>
  </text>
</FoLiA>"""


DCOIEXAMPLE=u"""<?xml version="1.0" encoding="iso-8859-15"?>
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
    <gap reason="backmatter" hand=""/>
  </text>
</DCOI>"""
