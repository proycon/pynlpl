
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

import pynlpl.formats.folia as folia


class FoliaRead(unittest.TestCase):
                        
    def test1_readfromfile(self):        
        """Reading from file"""
        global FOLIAEXAMPLE
        #write example to file
        f = codecs.open('/tmp/foliatest.xml','w','utf-8')
        f.write(FOLIAEXAMPLE)    
        f.close()
        
        doc = folia.Document(file='/tmp/foliatest.xml')
        self.assertTrue(isinstance(doc,folia.Document))

class FoliaSanity(unittest.TestCase):
    
    def setUp(self):
        self.doc = folia.Document(file='/tmp/foliatest.xml')
        
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
        self.assertEqual( w.id , 'WR-P-E-J-0000000001.head.1.s.1.w.1' ) 
        self.assertEqual( w.text , "Stemma" ) 
        self.assertEqual( str(w) , "Stemma" ) 
        self.assertEqual( unicode(w) , u"Stemma" ) 
        
        
    def test005_last_word(self):                                    
        """Sanity check - Last word"""            
        #grab first word
        w = self.doc.words(-1) # shortcut for doc.words()[0]         
        self.assertEqual( w.id , 'WR-P-E-J-0000000001.p.1.s.8.w.17' ) 
        self.assertEqual( w.text , "." )             
        self.assertEqual( str(w) , "." )             
        
    def test006_first_sentence(self):                                    
        """Sanity check - Sentence"""                                
        #grab last sentence
        s = self.doc.sentences(1)
        self.assertEqual( s.id, 'WR-P-E-J-0000000001.p.1.s.1' )
        self.assertEqual( str(s), "Stemma is een ander woord voor stamboom . " ) 
        
        
        
        
            
        



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
              <t>stippellijn</t>
              <pos class="N(soort,ev,basis,zijd,stan)"/>
              <lemma class="stippellijn"/>
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
