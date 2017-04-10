#!/usr/bin/env python
#-*- coding:utf-8 -*-


#Frog Wrapper with XML input and FoLiA output support


from __future__ import print_function, unicode_literals, division, absolute_import

import getopt
import lxml.etree
import sys
import os
import codecs

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'


import pynlpl.formats.folia as folia
from pynlpl.clients.frogclient import FrogClient

def legacyout(i, word,lemma,morph,pos):
    if word:
        out = str(i + 1) + "\t" + word + "\t" + lemma + "\t" + morph + "\t" + pos
        print(out.encode('utf-8'))
    else:
        print()

def usage():
    print >>sys.stderr,"frogwrapper.py  [options]"
    print >>sys.stderr,"------------------------------------------------------"
    print >>sys.stderr,"Input file:"
    print >>sys.stderr,"\t--txt=[file]       Plaintext input"
    print >>sys.stderr,"\t--xml=[file]       XML Input"
    print >>sys.stderr,"\t--folia=[file]     FoLiA XML Input"
    print >>sys.stderr,"Frog settings:"
    print >>sys.stderr,"\t-p [port]          Port the Frog server is running on"
    print >>sys.stderr,"Output type:"
    print >>sys.stderr,"\t--id=[ID]          ID for outputted FoLiA XML Document"
    print >>sys.stderr,"\t--legacy           Use legacy columned output instead of FoLiA"
    print >>sys.stderr,"\t-o                 Write output to input file (only works for --folia)"
    print >>sys.stderr,"XML Input:"
    print >>sys.stderr,"\t--selectsen=[expr] Use xpath expression to select sentences"
    print >>sys.stderr,"\t--selectpar=[expr] Use xpath expression to select paragraphs"
    print >>sys.stderr,"\t--idattrib=[attrb] Copy ID from this attribute"
    print >>sys.stderr,"Text Input:"
    print >>sys.stderr,"\t-N                 No structure"
    print >>sys.stderr,"\t-S                 One sentence per line (strict)"
    print >>sys.stderr,"\t-P                 One paragraph per line"
    print >>sys.stderr,"\t-I                 Value in first column (tab seperated) is ID!"
    print >>sys.stderr,"\t-E [encoding]      Encoding of input file (default: utf-8)"

try:
    opts, files = getopt.getopt(sys.argv[1:], "hSPINEp:o", ["txt=","xml=", "folia=","id=",'legacy','tok','selectsen=','selectpar=','idattrib='])
except getopt.GetoptError as err:
    # print help information and exit:
    print(str(err))
    usage()
    sys.exit(1)


textfile = xmlfile = foliafile = None
foliaid = 'UNTITLED'
legacy = None
tok = False
idinfirstcolumn = False
encoding = 'utf-8'
mode='s'
xpathselect = ''
idattrib=''
port = None
save = False

for o, a in opts:
    if o == "-h":
        usage()
        sys.exit(0)
    elif o == "-I":
        idinfirstcolumn = True
    elif o == "-S":
        mode = 's'
    elif o == "-P":
        mode = 'p'
    elif o == "-p":
        port = int(a)
    elif o == "-N":
        mode = 'n'
    elif o == "-E":
        encoding = a
    elif o == "--selectsen":
        mode='s'
        xpathselect = a
    elif o == "--selectpar":
        mode='p'
        xpathselect = a
    elif o == "--idattrib":
        idattrib = a
    elif o == "--txt":
        textfile = a
    elif o == "--xml":
        xmlfile = a
    elif o == "--folia":
        foliafile = a
    elif o == "--id":
        foliaid = a #ID
    elif o == "-o":
        save = True
    elif o == "--legacy":
        legacy = True
    elif o == "--tok":
        tok = True
    else:
        print >>sys.stderr, "ERROR: Unknown option:",o
        sys.exit(1)

if not port:
    print >> sys.stderr,"ERROR: No port specified to connect to Frog server"
    sys.exit(2)
elif (not textfile and not xmlfile and not foliafile):
    print >> sys.stderr,"ERROR: Specify a file with either --txt, --xml or --folia"
    sys.exit(2)
elif xmlfile and not xpathselect:
    print >> sys.stderr,"ERROR: You need to specify --selectsen or --selectpar when using --xml"
    sys.exit(2)

frogclient = FrogClient('localhost',port)

idmap = []
data = []

if textfile:
    f = codecs.open(textfile, 'r', encoding)
    for line in f.readlines():
        if idinfirstcolumn:
            id, line = line.split('\t',1)
            idmap.append(id.strip())
        else:
            idmap.append(None)
        data.append(line.strip())
    f.close()

if xmlfile:
    xmldoc = lxml.etree.parse(xmlfile)
    for node in xmldoc.xpath(xpathselect):
        if idattrib:
            if idattrib in node.attrib:
                idmap.append(node.attrib[idattrib])
            else:
                print >>sys.stderr,"WARNING: Attribute " + idattrib + " not found on node!"
                idmap.append(None)
        else:
            idmap.append(None)
        data.append(node.text)

if foliafile:
    foliadoc = folia.Document(file=foliafile)
    if not foliadoc.declared(folia.AnnotationType.TOKEN):
        foliadoc.declare(folia.AnnotationType.TOKEN, set='http://ilk.uvt.nl/folia/sets/ucto-nl.foliaset', annotator='Frog',annotatortype=folia.AnnotatorType.AUTO)
    if not foliadoc.declared(folia.AnnotationType.POS):
        foliadoc.declare(folia.AnnotationType.POS, set='http://ilk.uvt.nl/folia/sets/cgn-legacy.foliaset', annotator='Frog',annotatortype=folia.AnnotatorType.AUTO)
    if not foliadoc.declared(folia.AnnotationType.LEMMA):
        foliadoc.declare(folia.AnnotationType.LEMMA, set='http://ilk.uvt.nl/folia/sets/mblem-nl.foliaset', annotator='Frog',annotatortype=folia.AnnotatorType.AUTO)
    foliadoc.language('nld')
    text = foliadoc.data[-1]

    for p in foliadoc.paragraphs():
        found_s = False
        for s in p.sentences():
            found_w = False
            for w in s.words():
                found_w = True
            found_s = True
            if found_w:
                #pass tokenised sentence
                words = s.words()
                response = frogclient.process(" ".join([unicode(w) for w in words]))
                for i, (word, lemma, morph, pos) in enumerate(response):
                    if legacy: legacyout(i,word,lemma,morph,pos)
                    if unicode(words[i]) == word:
                        if lemma:
                            words[i].append( folia.LemmaAnnotation(foliadoc, cls=lemma) )
                        if pos:
                            words[i].append( folia.PosAnnotation(foliadoc, cls=pos) )
                    else:
                        print >>sys.stderr,"WARNING: Out of sync after calling Frog! ", i, word

            else:
                #pass untokenised sentence
                try:
                    sentext = s.text()
                except folia.NoSuchText:
                    continue
                response = frogclient.process(sentext)
                for i, (word, lemma, morph, pos) in enumerate(response):
                    if legacy: legacyout(i,word,lemma,morph,pos)
                    if word:
                        w = folia.Word(foliadoc, text=word, generate_id_in=s)
                        if lemma:
                            w.append( folia.LemmaAnnotation(foliadoc, cls=lemma) )
                        if pos:
                            w.append( folia.PosAnnotation(foliadoc, cls=pos) )
                        s.append(w)

            if not found_s:
                #pass paragraph
                try:
                    partext = p.text()
                except folia.NoSuchText:
                    continue

                s = folia.Sentence(foliadoc, generate_id_in=p)
                response = frogclient.process(partext)
                for i, (word, lemma, morph, pos) in enumerate(response):
                    if (not word or i == len(response) - 1) and len(s) > 0:
                        #gap or end of response: terminate sentence
                        p.append(s)
                        s = folia.Sentence(foliadoc, generate_id_in=p)
                    elif word:
                        w = folia.Word(foliadoc, text=word, generate_id_in=s)
                        if lemma:
                            w.append( folia.LemmaAnnotation(foliadoc, cls=lemma) )
                        if pos:
                            w.append( folia.PosAnnotation(foliadoc, cls=pos) )
                        s.append(w)


else:
    foliadoc = folia.Document(id=foliaid)
    foliadoc.declare(folia.AnnotationType.TOKEN, set='http://ilk.uvt.nl/folia/sets/ucto-nl.foliaset', annotator='Frog',annotatortype=folia.AnnotatorType.AUTO)
    foliadoc.declare(folia.AnnotationType.POS, set='http://ilk.uvt.nl/folia/sets/cgn-legacy.foliaset', annotator='Frog',annotatortype=folia.AnnotatorType.AUTO)
    foliadoc.declare(folia.AnnotationType.LEMMA, set='http://ilk.uvt.nl/folia/sets/mblem-nl.foliaset', annotator='Frog',annotatortype=folia.AnnotatorType.AUTO)
    foliadoc.language('nld')
    text = folia.Text(foliadoc, id=foliadoc.id + '.text.1')
    foliadoc.append(text)


    curid = None
    for (fragment, id) in zip(data,idmap):
        if mode == 's' or mode == 'n':
            if id:
                s = folia.Sentence(foliadoc, id=id)
            else:
                s = folia.Sentence(foliadoc, generate_id_in=text)
        elif mode == 'p':
            if id:
                p = folia.Paragraph(foliadoc, id=id)
            else:
                p = folia.Paragraph(foliadoc, generate_id_in=text)
            s = folia.Sentence(foliadoc, generate_id_in=p)

        curid = s.id
        response = frogclient.process(fragment)
        for i, (word, lemma, morph, pos) in enumerate(response):
            if legacy:
                legacyout(i,word,lemma,morph,pos)
                continue

            if word:
                w = folia.Word(foliadoc, text=word, generate_id_in=s)
                if lemma:
                    w.append( folia.LemmaAnnotation(foliadoc, cls=lemma) )
                if pos:
                    w.append( folia.PosAnnotation(foliadoc, cls=pos) )
                s.append(w)
            if (not word or i == len(response) - 1) and len(s) > 0:
                #gap or end of response: terminate sentence
                if mode == 'p':
                    p.append(s)
                    if (i == len(response) - 1):
                        text.append(p)
                elif mode == 'n' or (mode == 's' and i == len(response) - 1):
                    text.append(s)
                elif mode == 's':
                    continue

                if i < len(response) - 1: #not done yet?
                    #create new sentence
                    if mode == 'p':
                        s = folia.Sentence(foliadoc, generate_id_in=p)
                    elif mode == 'n' and id:
                        #no id for this unforeseen sentence, make something up
                        s = folia.Sentence(foliadoc, id=curid+'.X')
                        print("WARNING: Sentence found that was not in original",file=sys.stderr)

if not legacy:
    print(foliadoc.xmlstring())
if save and foliafile:
    foliadoc.save()
