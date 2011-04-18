
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
        self.assertEqual( w.text , "Stemma" ) 
        self.assertEqual( str(w) , "Stemma" ) 
        self.assertEqual( unicode(w) , u"Stemma" ) 
        
        
    def test005_last_word(self):                                    
        """Sanity check - Last word"""            
        #grab first word
        w = self.doc.words(-1) # shortcut for doc.words()[0]         
        self.assertTrue( isinstance(w, folia.Word) )
        self.assertEqual( w.id , 'WR-P-E-J-0000000001.p.1.s.8.w.17' ) 
        self.assertEqual( w.text , "." )             
        self.assertEqual( str(w) , "." )             
        
    def test006_first_sentence(self):                                    
        """Sanity check - Sentence"""                                
        #grab last sentence
        s = self.doc.sentences(1)
        self.assertTrue( isinstance(s, folia.Sentence) )
        self.assertEqual( s.id, 'WR-P-E-J-0000000001.p.1.s.1' )
        self.assertEqual( s.text, None ) #no text DIRECTLY associated with the sentence
        self.assertEqual( str(s), "Stemma is een ander woord voor stamboom . " ) 
        
    def test007_index(self):                                    
        """Sanity check - Index"""            
        #grab something using the index
        w = self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7'] 
        self.assertTrue( isinstance(w, folia.Word) )
        self.assertEqual( self.doc['WR-P-E-J-0000000001.p.1.s.2.w.7'] , self.doc.index['WR-P-E-J-0000000001.p.1.s.2.w.7'] )         
        self.assertEqual( w.id , 'WR-P-E-J-0000000001.p.1.s.2.w.7' )         
        self.assertEqual( w.text , "stamboom" ) 
        
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
        self.assertEqual( w.text, 'stippellijn')    
        
        
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
            <w xml:id="WR-P-E-J-0000125009.head.1.s.1.w.1">Aspirine</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.head.1.s.2">
            <w xml:id="WR-P-E-J-0000125009.head.1.s.2.w.1">3D</w>
            <w xml:id="WR-P-E-J-0000125009.head.1.s.2.w.2">model</w>
            <w xml:id="WR-P-E-J-0000125009.head.1.s.2.w.3">van</w>
            <w xml:id="WR-P-E-J-0000125009.head.1.s.2.w.4">Aspirine</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.1">
          <s xml:id="WR-P-E-J-0000125009.p.1.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.1">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.2">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.3">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.4">merknaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.5">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.6">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.7">medicijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.8">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.9">Bayer</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.1.w.10">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.1.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.2">werkzame</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.3">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.4">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.5">acetylsalicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.2.w.6">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.1.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.1">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.2">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.3">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.4">bekend</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.5">onder</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.6">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.7">naam</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.8">acetosal</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.9">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.10">aspro</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.11">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.12">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.13">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.14">merknaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.15">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.16">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.17">Nicholas</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.18">Ltd.</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.19">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.20">werkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.21">pijnstillend</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.22">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.23">koortsverlagend</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.24">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.25">ontstekingsremmend</w>
            <w xml:id="WR-P-E-J-0000125009.p.1.s.3.w.26">.</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.2">
          <s xml:id="WR-P-E-J-0000125009.p.2.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.1">Oorspronkelijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.2">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.3">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.4">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.5">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.6">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.7">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.8">pijnstiller</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.9">ontdekt</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.10">doordat</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.11">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.12">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.13">geïdentificeerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.14">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.15">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.16">werkzame</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.17">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.18">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.19">wilgenbast</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.1.w.20">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.2.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.1">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.2">zuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.3">zelf</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.4">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.5">echter</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.6">bijzonder</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.7">slecht</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.8">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.9">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.10">maag</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.11">getolereerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.2.w.12">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.2.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.2">acetyl-ester</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.3">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.4">daarin</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.5">veel</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.6">beter</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.3.w.7">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.2.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.1">Deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.2">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.3">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.4">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.5">zuivere</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.6">toestand</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.7">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.8">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.9">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.10">iets</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.11">minder</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.12">maagprikkelende</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.13">calciumzout</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.14">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.15">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.16">markt</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.17">gebracht</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.18">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.19">ascal</w>
            <w xml:id="WR-P-E-J-0000125009.p.2.s.4.w.20">)</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.3">
          <s xml:id="WR-P-E-J-0000125009.p.3.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.2">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.3">zelf</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.4">berust</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.5">erop</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.6">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.7">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.8">irreversibel</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.9">bindt</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.10">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.11">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.12">enzym</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.13">cyclo-oxygenase</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.14">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.15">COX</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.16">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.17">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.18">waardoor</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.19">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.20">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.21">meer</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.22">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.23">helpen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.24">arachidonzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.25">om</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.26">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.27">zetten</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.28">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.29">prostaglandines</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.30">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.31">stoffen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.32">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.33">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.34">zenuwuiteinden</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.35">gevoelig</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.36">maken</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.37">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.38">prikkels</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.1.w.39">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.3.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.2">vermelde</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.3">maagproblemen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.4">ontstaan</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.5">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.6">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.7">irreversibele</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.8">binding</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.9">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.10">COX-1</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.11">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.12">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.13">variant</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.14">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.15">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.16">enzym</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.17">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.18">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.19">rolspeelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.20">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.21">bescherming</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.22">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.23">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.24">maag</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.25">tegen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.26">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.27">eigen</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.28">zure</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.29">inhoud</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.2.w.30">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.3.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.1">Ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.2">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.3">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.4">COX-1</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.5">aanwezig</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.6">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.7">bloedplaatjes</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.8">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.9">vandaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.10">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.11">trombocytenaggregatieremmende</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.12">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.3.w.13">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.3.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.1">Vandaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.2">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.3">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.4">farmaceutische</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.5">industrie</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.6">zich</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.7">richt</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.8">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.9">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.10">ontwikkeling</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.11">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.12">COX-2</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.13">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.14">induceerbaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.15">COX</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.16">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.17">specifieke</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.18">pijnstillers</w>
            <w xml:id="WR-P-E-J-0000125009.p.3.s.4.w.19">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.2">
        <head xml:id="WR-P-E-J-0000125009.head.2">
          <s xml:id="WR-P-E-J-0000125009.head.2.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.2.s.1.w.1">Geschiedenis</w>
            <w xml:id="WR-P-E-J-0000125009.head.2.s.1.w.2">van</w>
            <w xml:id="WR-P-E-J-0000125009.head.2.s.1.w.3">Aspirine</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.4">
          <s xml:id="WR-P-E-J-0000125009.p.4.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.2">ontdekking</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.3">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.4">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.5">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.6">algemeen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.7">toegeschreven</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.8">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.9">Felix</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.10">Hoffmann</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.11">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.12">werkzaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.13">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.14">Bayer</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.15">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.16">Elberfeld</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.1.w.17">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.1">Uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.2">onderzoek</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.3">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.4">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.5">labjournaals</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.6">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.7">Bayer</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.8">blijkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.9">echter</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.10">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.11">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.12">werkelijke</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.13">ontdekker</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.14">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.15">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.16">Arthur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.17">Eichengrün</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.18">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.19">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.20">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.21">onderzoek</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.22">deed</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.23">naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.24">betere</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.25">pijnstillers</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.2.w.26">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.1">Felix</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.2">Hoffmann</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.3">werkte</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.4">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.5">laboratorium-assistent</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.6">onder</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.7">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.8">leiding</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.3.w.9">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.1">Door</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.2">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.3">joodse</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.4">achtergrond</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.5">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.6">Eichengrün</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.7">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.8">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.9">Nazis</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.10">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.11">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.12">annalen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.13">geschrapt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.14">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.15">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.16">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.17">verhaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.18">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.19">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.20">rheumatisch</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.21">vader</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.22">bedacht</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.4.w.23">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.1">In</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.2">1949</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.3">publiceerde</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.4">Eigengrün</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.5">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.6">artikel</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.7">waarin</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.8">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.9">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.10">uitvinding</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.11">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.12">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.13">claimde</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.5.w.14">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.6">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.1">Deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.2">claim</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.3">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.4">bevestigd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.5">na</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.6">onderzoek</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.7">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.8">Walter</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.9">Sneader</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.10">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.11">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.12">universiteit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.13">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.14">Glasgow</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.15">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.16">1999</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.6.w.17">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.7">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.1">Salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.2">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.3">al</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.4">gebruikt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.5">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.6">zelfs</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.7">Hippocrates</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.8">kende</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.9">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.10">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.11">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.12">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.13">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.14">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.15">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.16">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.17">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.18">walgelijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.19">goedje</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.20">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.21">erg</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.22">slecht</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.23">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.24">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.25">maag</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.26">lag</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.7.w.27">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.8">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.1">Dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.2">zuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.3">werd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.4">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.5">eerste</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.6">instantie</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.7">geëxtraheerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.8">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.9">bast</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.10">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.11">leden</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.12">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.13">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.14">plantenfamilie</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.15">der</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.16">wilgen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.17">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.18">Latijnse</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.19">gelachtsnaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.20">Salix</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.21">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.22">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.23">vandaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.24">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.25">naam</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.26">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.8.w.27">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.9">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.1">Hetzelfde</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.2">zuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.3">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.4">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.5">vinden</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.6">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.7">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.8">Moerasspirea</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.9">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.10">vandaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.11">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.12">'</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.13">spir</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.14">'</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.15">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.16">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.9.w.17">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.10">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.1">Hoffmann</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.2">ging</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.3">systematisch</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.4">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.5">werk</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.6">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.7">zocht</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.8">hardnekkig</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.9">naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.10">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.11">nieuwe</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.12">verbinding</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.13">om</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.14">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.15">middel</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.16">beter</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.17">verteerbaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.18">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.19">maken</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.10.w.20">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.11">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.1">Volgens</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.2">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.3">principe</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.4">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.5">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.6">veredeling</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.7">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.8">bestaande</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.9">geneesmiddelen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.10">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.11">waarmee</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.12">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.13">al</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.14">eerder</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.15">succes</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.16">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.17">geboekt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.18">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.19">ontdekt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.20">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.21">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.22">1897</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.23">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.24">oplossing</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.25">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.26">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.27">probleem</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.28">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.29">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.30">acetylering</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.31">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.32">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.33">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.11.w.34">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.12">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.1">Op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.2">10</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.3">augustus</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.4">beschrijft</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.5">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.6">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.7">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.8">laboratoriumdagboek</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.9">hoe</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.10">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.11">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.12">acetylsalicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.13">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.14">chemisch</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.15">zuivere</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.16">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.17">bewaarbare</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.18">vorm</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.19">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.20">samengesteld</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.12.w.21">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.13">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.1">Nadat</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.2">hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.3">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.4">nieuwe</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.5">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.6">samen</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.7">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.8">dokter</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.9">Heinrich</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.10">Dreser</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.11">uitgebreid</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.12">getest</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.13">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.14">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.15">dieren</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.16">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.17">komt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.18">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.19">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.20">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.21">1899</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.22">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.23">poedervorm</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.24">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.25">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.26">markt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.13.w.27">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.14">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.1">Een</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.2">jaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.3">later</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.4">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.5">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.6">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.7">gedoseerde</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.8">tabletten</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.14.w.9">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.4.s.15">
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.1">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.2">wereldverbruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.3">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.4">vandaag</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.5">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.6">dag</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.7">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.8">vijftigduizend</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.9">ton</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.10">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.11">ongeveer</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.12">honderd</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.13">miljard</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.14">tabletten</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.15">per</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.16">jaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.17">geschat</w>
            <w xml:id="WR-P-E-J-0000125009.p.4.s.15.w.18">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.3">
        <head xml:id="WR-P-E-J-0000125009.head.3">
          <s xml:id="WR-P-E-J-0000125009.head.3.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.3.s.1.w.1">Geschiedenis</w>
            <w xml:id="WR-P-E-J-0000125009.head.3.s.1.w.2">van</w>
            <w xml:id="WR-P-E-J-0000125009.head.3.s.1.w.3">Aspro</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.5">
          <s xml:id="WR-P-E-J-0000125009.p.5.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.1">Tijdens</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.2">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.3">1ste</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.4">Wereldoorlog</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.5">loofde</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.6">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.7">Britse</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.8">regering</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.9">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.10">prijs</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.11">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.12">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.13">eenieder</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.14">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.15">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.16">nieuwe</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.17">formule</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.18">kon</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.19">vinden</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.20">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.21">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.22">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.23">gezien</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.24">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.25">feit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.26">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.27">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.28">invoer</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.29">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.30">Duitsland</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.31">stil</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.32">lag</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.1.w.33">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.5.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.1">Een</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.2">chemicus</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.3">uit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.4">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.5">Australische</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.6">Melbourne</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.7">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.8">George</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.9">Nicholas</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.10">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.11">ontdekte</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.12">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.13">1915</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.14">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.15">synthetische</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.16">oplossing</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.17">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.18">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.19">zelfs</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.20">zuiverder</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.21">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.22">dan</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.23">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.24">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.25">oplosbaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.26">was</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.2.w.27">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.5.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.1">Hij</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.2">noemde</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.3">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.4">Aspro</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.5">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.6">wat</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.7">later</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.8">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.9">gehele</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.10">wereld</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.11">veroverde</w>
            <w xml:id="WR-P-E-J-0000125009.p.5.s.3.w.12">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.4">
        <head xml:id="WR-P-E-J-0000125009.head.4">
          <s xml:id="WR-P-E-J-0000125009.head.4.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.4.s.1.w.1">Pijnstillende</w>
            <w xml:id="WR-P-E-J-0000125009.head.4.s.1.w.2">werking</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.head.4.s.2">
            <w xml:id="WR-P-E-J-0000125009.head.4.s.2.w.1">Aspirine</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.6">
          <s xml:id="WR-P-E-J-0000125009.p.6.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.1">Pijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.2">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.3">veroorzaakt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.4">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.5">verschillende</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.6">stoffen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.7">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.8">vrijkomen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.9">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.10">beschadigingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.1.w.11">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.1">Werkende</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.2">cellen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.3">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.4">beschadigd</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.5">weefsel</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.6">geven</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.7">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.8">stoffen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.9">af</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.10">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.11">onder</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.12">invloed</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.13">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.14">o.a.</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.15">cytokinen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.16">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.17">mitogenen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.2.w.18">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.1">Deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.2">stoffen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.3">werken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.4">dan</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.5">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.6">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.7">zenuwuiteinden</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.8">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.9">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.10">pijnsignaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.11">naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.12">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.13">hersenen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.14">doorsturen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.3.w.15">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.1">Een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.2">hormoon</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.3">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.4">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.5">daarin</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.6">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.7">belangrijke</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.8">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.9">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.10">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.11">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.4.w.12">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.1">Prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.2">geeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.3">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.4">alleen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.5">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.6">pijnsignaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.7">af</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.8">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.9">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.10">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.11">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.12">belangrijke</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.13">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.14">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.15">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.16">hele</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.17">lichaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.5.w.18">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.6">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.1">Daarom</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.2">eerst</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.3">wat</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.4">meer</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.5">over</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.6">Prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.6.w.7">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.7">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.1">Prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.2">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.3">geproduceerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.4">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.5">cellen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.6">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.7">werkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.8">alleen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.9">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.10">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.11">buurt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.12">waar</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.13">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.14">geproduceerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.15">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.16">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.17">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.18">dan</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.19">afgebroken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.7.w.20">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.8">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.1">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.2">stimuleert</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.3">naast</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.4">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.5">pijnreactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.6">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.7">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.8">ontstekingsreactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.9">wanneer</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.10">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.11">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.12">infectie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.13">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.14">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.15">zorgt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.16">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.17">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.18">verhoging</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.19">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.20">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.21">lichaamstemperatuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.8.w.22">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.9">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.1">In</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.2">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.3">cellen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.4">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.5">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.6">cyclooxygenase</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.7">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.8">COX</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.9">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.10">enzym</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.11">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.12">onmisbare</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.13">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.14">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.15">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.16">maken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.17">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.18">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.9.w.19">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.10">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.1">Cyclooxygenase</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.2">katalyseert</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.3">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.4">omzetting</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.5">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.6">arachidonzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.7">naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.8">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.9">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.10">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.11">reactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.12">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.13">anders</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.14">vrijwel</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.15">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.16">verloopt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.10.w.17">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.11">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.2">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.3">voorkomt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.4">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.5">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.6">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.7">Cyclooxygenase</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.8">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.9">voorkomt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.10">daarmee</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.11">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.12">vorming</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.13">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.14">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.15">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.16">waardoor</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.17">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.18">groot</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.19">gedeelte</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.20">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.21">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.22">pijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.23">verdwijnt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.24">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.25">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.26">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.27">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.28">koorts</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.29">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.30">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.31">ontsteking</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.32">geremd</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.33">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.34">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.35">omdat</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.36">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.37">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.38">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.39">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.40">reacties</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.41">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.42">meer</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.43">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.44">veroorzaken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.11.w.45">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.12">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.1">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.2">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.3">dus</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.4">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.5">inhibitor</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.6">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.7">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.8">stof</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.9">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.10">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.11">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.12">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.13">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.14">eiwit</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.15">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.16">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.17">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.18">geval</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.19">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.20">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.21">COX</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.22">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.23">remt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.24">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.25">stopt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.12.w.26">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.13">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.1">Daarnaast</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.2">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.3">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.4">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.5">nog</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.6">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.7">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.8">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.9">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.10">normaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.11">functioneren</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.13.w.12">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.14">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.2">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.3">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.4">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.5">gemaakt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.6">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.7">COX-1</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.8">werkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.9">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.10">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.11">normale</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.12">processen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.13">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.14">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.15">boodschapper</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.14.w.16">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.15">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.2">prostaglandine</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.3">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.4">werkt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.5">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.6">beschadiging</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.7">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.8">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.9">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.10">rol</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.11">speelt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.12">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.13">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.14">pijnsignaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.15">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.16">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.17">gemaakt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.18">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.19">COX-2</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.15.w.20">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.16">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.1">COX-1</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.2">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.3">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.4">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.5">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.6">functioneert</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.7">maagbloedingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.8">e.d.</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.9">veroorzaken</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.16.w.10">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.17">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.1">Er</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.2">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.3">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.4">sinds</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.5">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.6">aantal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.7">jaren</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.8">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.9">aantal</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.10">andere</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.11">geneesmiddelen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.12">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.13">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.14">markt</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.15">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.16">selectief</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.17">COX-2</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.18">remmen</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.17.w.19">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.6.s.18">
            <w xml:id="WR-P-E-J-0000125009.p.6.s.18.w.1">Zie</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.18.w.2">COX-2</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.18.w.3">remmers</w>
            <w xml:id="WR-P-E-J-0000125009.p.6.s.18.w.4">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.5">
        <head xml:id="WR-P-E-J-0000125009.head.5">
          <s xml:id="WR-P-E-J-0000125009.head.5.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.5.s.1.w.1">Andere</w>
            <w xml:id="WR-P-E-J-0000125009.head.5.s.1.w.2">werkingen</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.head.5.s.2">
            <w xml:id="WR-P-E-J-0000125009.head.5.s.2.w.1">Werking</w>
            <w xml:id="WR-P-E-J-0000125009.head.5.s.2.w.2">op</w>
            <w xml:id="WR-P-E-J-0000125009.head.5.s.2.w.3">de</w>
            <w xml:id="WR-P-E-J-0000125009.head.5.s.2.w.4">bloedplaatjes</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.7">
          <s xml:id="WR-P-E-J-0000125009.p.7.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.1">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.2">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.3">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.4">alleen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.5">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.6">analgeticum</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.7">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.8">pijnstillend</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.9">middel</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.10">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.11">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.12">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.13">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.14">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.15">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.16">nog</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.17">andere</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.18">effecten</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.19">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.20">ons</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.21">lichaam</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.1.w.22">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.1">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.2">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.3">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.4">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.5">onomkeerbaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.6">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.7">effect</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.8">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.9">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.10">bloedplaatjes</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.11">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.12">belemmert</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.13">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.14">om</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.15">samen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.16">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.17">klonteren</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.18">:</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.19">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.20">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.21">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.22">trombocytenaggregatieremmer</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.2.w.23">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.1">Hierdoor</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.2">vermindert</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.3">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.4">stelpend</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.5">vermogen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.6">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.7">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.8">bloed</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.9">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.10">bloedvatbeschadiging</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.3.w.11">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.2">vaak</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.3">gebruikte</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.4">benaming</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.5">'</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.6">bloedverdunner</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.7">'</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.8">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.9">onjuist</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.10">-</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.11">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.12">bloed</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.13">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.14">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.15">dunner</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.4.w.16">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.1">Dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.2">effect</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.3">treedt</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.4">al</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.5">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.6">na</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.7">1/4</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.8">aspirinetablet</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.9">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.10">houdt</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.11">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.12">tot</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.13">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.14">uitgeschakelde</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.15">bloedplaatjes</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.16">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.17">na</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.18">ongeveer</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.19">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.20">week</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.21">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.22">allemaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.23">zijn</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.24">vervangen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.5.w.25">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.7.s.6">
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.1">Voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.2">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.3">laatste</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.4">effect</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.5">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.6">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.7">middel</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.8">tegenwoordig</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.9">zeer</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.10">veel</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.11">voorgeschreven</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.12">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.13">mensen</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.14">die</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.15">eerder</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.16">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.17">beroerte</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.18">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.19">hartaanval</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.20">hebben</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.21">gehad</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.22">;</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.23">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.24">vermindert</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.25">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.26">kans</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.27">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.28">herhaling</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.29">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.30">ca</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.31">40</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.32">%</w>
            <w xml:id="WR-P-E-J-0000125009.p.7.s.6.w.33">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.6">
        <head xml:id="WR-P-E-J-0000125009.head.6">
          <s xml:id="WR-P-E-J-0000125009.head.6.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.6.s.1.w.1">Andere</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.8">
          <s xml:id="WR-P-E-J-0000125009.p.8.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.1">Ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.2">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.3">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.4">gebied</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.5">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.6">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.7">kanker-preventie</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.8">liggen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.9">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.10">mogelijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.11">toepassingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.12">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.13">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.14">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.15">aangezien</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.16">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.17">tumorvorming</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.18">tegengaat</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.1.w.19">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.8.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.1">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.2">dagelijks</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.3">slikken</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.4">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.5">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.6">kleine</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.7">dosis</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.8">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.9">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.10">gedurende</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.11">5</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.12">jaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.13">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.14">zou</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.15">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.16">kans</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.17">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.18">tumoren</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.19">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.20">slokdarm</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.21">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.22">darmstelsel</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.23">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.24">twee</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.25">derde</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.26">doen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.27">afnemen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.2.w.28">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.8.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.1">Naar</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.2">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.3">schijnt</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.4">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.5">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.6">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.7">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.8">positieve</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.9">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.10">tegen</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.11">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.12">ziekte</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.13">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.14">Alzheimer</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.15">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.16">zwangerschaps-</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.17">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.18">darm-</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.19">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.20">hart-</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.21">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.22">vaatziekten</w>
            <w xml:id="WR-P-E-J-0000125009.p.8.s.3.w.23">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.7">
        <head xml:id="WR-P-E-J-0000125009.head.7">
          <s xml:id="WR-P-E-J-0000125009.head.7.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.7.s.1.w.1">Bijwerkingen</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.9">
          <s xml:id="WR-P-E-J-0000125009.p.9.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.1">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.2">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.3">vrij</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.4">sterk</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.5">maagprikkelend</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.6">:</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.7">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.8">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.9">nu</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.10">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.11">nieuw</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.12">geneesmiddel</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.13">zou</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.14">moeten</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.15">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.16">geregistreerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.17">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.18">pijnstiller</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.19">zou</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.20">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.21">waarschijnlijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.22">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.23">lukken</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.1.w.24">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.9.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.1">Bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.2">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.3">kunnen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.4">maag-klachten</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.5">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.6">zelfs</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.7">maagbloedingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.8">ontstaan</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.2.w.9">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.9.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.1">Aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.2">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.3">vooral</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.4">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.5">hoge</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.6">doseringen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.7">ernstige</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.8">bijwerkingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.9">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.10">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.11">name</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.12">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.13">al</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.14">genoemde</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.15">maagbloedingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.16">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.17">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.18">oorsuizen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.19">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.20">doofheid</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.21">kunnen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.22">optreden</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.3.w.23">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.9.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.1">Ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.2">weet</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.3">men</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.4">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.5">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.6">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.7">ervan</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.8">tijdelijk</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.9">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.10">aanmaak</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.11">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.12">testosteron</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.13">vermindert</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.14">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.15">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.16">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.17">neveneffect</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.18">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.19">geen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.20">blijvende</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.21">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.22">erg</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.23">schadelijke</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.24">werking</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.4.w.25">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.9.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.1">Naast</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.2">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.3">bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.4">zwangerschap</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.5">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.6">toediening</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.7">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.8">baby's</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.9">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.10">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.11">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.12">liefst</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.13">ook</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.14">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.15">met</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.16">alcohol</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.17">gebruikt</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.18">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.19">omdat</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.20">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.21">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.22">kans</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.23">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.24">maagklachten</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.25">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.26">verhogen</w>
            <w xml:id="WR-P-E-J-0000125009.p.9.s.5.w.27">.</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.10">
          <s xml:id="WR-P-E-J-0000125009.p.10.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.1">Advies</w>
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.2">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.3">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.4">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.10.s.1.w.5">pijnstiller</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.11">
          <s xml:id="WR-P-E-J-0000125009.p.11.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.1">Voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.2">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.3">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.4">eenvoudige</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.5">pijnstiller</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.6">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.7">medisch</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.8">gezien</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.9">algemeen</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.10">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.11">voorkeur</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.12">gegeven</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.13">aan</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.14">paracetamol</w>
            <w xml:id="WR-P-E-J-0000125009.p.11.s.1.w.15">.</w>
          </s>
        </p>
      </div>
      <div xml:id="WR-P-E-J-0000125009.div.8">
        <head xml:id="WR-P-E-J-0000125009.head.8">
          <s xml:id="WR-P-E-J-0000125009.head.8.s.1">
            <w xml:id="WR-P-E-J-0000125009.head.8.s.1.w.1">Synthese</w>
            <w xml:id="WR-P-E-J-0000125009.head.8.s.1.w.2">van</w>
            <w xml:id="WR-P-E-J-0000125009.head.8.s.1.w.3">aspirine</w>
          </s>
        </head>
        <p xml:id="WR-P-E-J-0000125009.p.12">
          <s xml:id="WR-P-E-J-0000125009.p.12.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.1">Bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.2">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.3">maken</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.4">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.5">acetylsalicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.6">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.7">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.8">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.9">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.10">laboratorium</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.11">schaal</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.12">gaat</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.13">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.14">om</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.15">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.16">opbrengst</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.17">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.18">enkele</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.19">grammen</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.1.w.20">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.12.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.1">Bij</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.2">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.3">bereiding</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.4">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.5">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.6">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.7">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.8">uitgegaan</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.9">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.10">verschillende</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.11">begin</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.12">producten</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.13">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.14">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.15">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.16">beschrijving</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.17">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.18">uitgegaan</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.19">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.20">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.21">beginstof</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.22">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.2.w.23">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.12.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.1">Dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.2">heeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.3">als</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.4">voordeel</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.5">dat</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.6">er</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.7">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.8">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.9">synthese</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.10">stap</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.11">uitgevoerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.12">hoeft</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.13">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.14">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.3.w.15">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.12.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.1">Uitgaande</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.2">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.3">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.4">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.5">azijnzuuranhydride</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.6">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.7">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.8">salicylzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.9">veresterd</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.10">volgens</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.11">nevenstaande</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.12">reactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.12.s.4.w.13">:</w>
          </s>
        </p>
        <p xml:id="WR-P-E-J-0000125009.p.13">
          <s xml:id="WR-P-E-J-0000125009.p.13.s.1">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.1">Zoals</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.2">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.3">zien</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.4">boven</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.5">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.6">reactiepijl</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.7">vindt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.8">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.9">synthese</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.10">plaats</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.11">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.12">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.13">zuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.14">milieu</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.1.w.15">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.2">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.1">In</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.2">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.3">geval</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.4">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.5">gekozen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.6">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.7">geconcentreerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.8">fosforzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.2.w.9">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.3">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.1">Na</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.2">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.3">reactie</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.4">moet</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.5">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.6">hoofdproduct</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.7">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.8">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.9">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.10">gescheiden</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.11">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.12">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.13">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.14">bijproducten</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.15">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.16">azijnzuur</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.17">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.18">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.19">gereageerde</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.20">reactanten</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.21">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.22">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.23">dit</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.24">gebeurt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.25">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.26">middel</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.27">van</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.28">herkristallisatie</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.3.w.29">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.4">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.2">herkristallisatie</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.3">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.4">uitgevoerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.5">door</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.6">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.7">ruwe</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.8">product</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.9">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.10">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.11">lossen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.12">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.13">methanol</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.14">(</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.15">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.16">een</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.17">reflux</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.18">opstelling</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.19">)</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.20">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.21">dan</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.22">net</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.23">genoeg</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.24">water</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.25">toe</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.26">te</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.27">voegen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.28">zodat</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.29">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.30">verontreinigingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.31">uitkristalliseren</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.32">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.33">maar</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.34">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.35">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.36">niet</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.4.w.37">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.5">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.1">Het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.2">hete</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.3">mengsel</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.4">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.5">nu</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.6">gefiltreerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.7">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.8">waardoor</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.9">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.10">verontreinigingen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.11">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.12">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.13">filter</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.14">achterblijven</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.15">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.16">alleen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.17">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.18">zuivere</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.19">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.20">in</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.21">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.22">filtraat</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.23">komt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.5.w.24">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.6">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.1">Na</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.2">deze</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.3">filtratie</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.4">wordt</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.5">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.6">filtraat</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.7">gekoeld</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.8">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.9">opnieuw</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.10">gefiltreerd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.11">,</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.12">de</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.13">gezuiverde</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.14">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.15">blijft</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.16">nu</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.17">achter</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.18">op</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.19">het</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.20">filter</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.6.w.21">.</w>
          </s>
          <s xml:id="WR-P-E-J-0000125009.p.13.s.7">
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.1">De</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.2">verkregen</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.3">aspirine</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.4">kan</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.5">nu</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.6">worden</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.7">gedroogd</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.8">en</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.9">is</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.10">klaar</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.11">voor</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.12">verpakking</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.13">of</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.14">gebruik</w>
            <w xml:id="WR-P-E-J-0000125009.p.13.s.7.w.15">.</w>
          </s>
        </p>
      </div>
    </body>
    <gap reason="backmatter" hand=""/>
  </text>
</DCOI>"""
