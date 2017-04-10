# -*- coding: utf-8 -*-
#----------------------------------------------------------------
# PyNLPl - FoLiA Set Definition Module
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#
#   https://proycon.github.io/folia
#   httsp://github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#   Module for reading, editing and writing FoLiA XML
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

#pylint: disable=redefined-builtin,trailing-whitespace,superfluous-parens,bad-classmethod-argument,wrong-import-order,wrong-import-position,ungrouped-imports

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import


import sys
import io
import rdflib
from lxml import etree as ElementTree
if sys.version < '3':
    from StringIO import StringIO #pylint: disable=import-error,wrong-import-order
    from urllib import urlopen #pylint: disable=no-name-in-module,wrong-import-order
    from urllib2 import HTTPError
else:
    from io import StringIO,  BytesIO #pylint: disable=wrong-import-order,ungrouped-imports
    from urllib.request import urlopen #pylint: disable=E0611,wrong-import-order,ungrouped-imports
    from urllib.error import HTTPError


#foliaspec:namespace:NSFOLIA
#The FoLiA XML namespace
NSFOLIA = "http://ilk.uvt.nl/folia"

#foliaspec:setdefinitionnamespace:NSFOLIASETDEFINITION
NSFOLIASETDEFINITION = "http://folia.science.ru.nl/setdefinition"
NSSKOS = "http://www.w3.org/2004/02/skos/core"

class DeepValidationError(Exception):
    pass

class SetDefinitionError(DeepValidationError):
    pass

class SetType: #legacy only
    CLOSED, OPEN, MIXED, EMPTY = range(4)

class LegacyClassDefinition(object):
    def __init__(self,id, label, subclasses=None):
        self.id = id
        self.label = label
        if subclasses:
            self.subclasses = subclasses
        else:
            self.subclasses = []

    @classmethod
    def parsexml(Class, node):
        if not node.tag == '{' + NSFOLIA + '}class':
            raise Exception("Expected class tag for this xml node, got" + node.tag)

        if 'label' in node.attrib:
            label = node.attrib['label']
        else:
            label = ""

        subclasses= []
        for subnode in node:
            if isinstance(subnode.tag, str) or (sys.version < '3' and isinstance(subnode.tag, unicode)): #pylint: disable=undefined-variable
                if subnode.tag == '{' + NSFOLIA + '}class':
                    subclasses.append( LegacyClassDefinition.parsexml(subnode) )
                elif subnode.tag[:len(NSFOLIA) +2] == '{' + NSFOLIA + '}':
                    raise Exception("Invalid tag in Class definition: " + subnode.tag)
        if '{http://www.w3.org/XML/1998/namespace}id' in node.attrib:
            idkey = '{http://www.w3.org/XML/1998/namespace}id'
        else:
            idkey = 'id'
        return LegacyClassDefinition(node.attrib[idkey],label, subclasses)


    def __iter__(self):
        for c in self.subclasses:
            yield c

    def json(self):
        jsonnode = {'id': self.id, 'label': self.label}
        jsonnode['subclasses'] = []
        for subclass in self.subclasses:
            jsonnode['subclasses'].append(subclass.json())
        return jsonnode

    def rdf(self,graph, basens,parentseturi, parentclass=None, seqnr=None):
        graph.add((rdflib.term.URIRef(basens + '#' + self.id), rdflib.RDF.type, rdflib.term.URIRef(NSSKOS + '#Concept')))
        graph.add((rdflib.term.URIRef(basens + '#' + self.id), rdflib.term.URIRef(NSSKOS + '#notation'), rdflib.term.Literal(self.id)))
        graph.add((rdflib.term.URIRef(basens + '#' + self.id), rdflib.term.URIRef(NSSKOS + '#prefLabel'), rdflib.term.Literal(self.label)))
        graph.add((parentseturi , rdflib.term.URIRef(NSSKOS + '#member'), rdflib.term.URIRef(basens + '#' + self.id)))
        if seqnr is not None:
            graph.add((rdflib.term.URIRef(basens + '#' + self.id), rdflib.term.URIRef(NSFOLIASETDEFINITION + '#sequenceNumber'), rdflib.term.Literal(seqnr) ))
        if parentclass:
            graph.add((rdflib.term.URIRef(basens + '#' + self.id), rdflib.term.URIRef(NSSKOS + '#broader'), rdflib.term.URIRef(basens + '#' + parentclass) ))

        for subclass in self.subclasses:
            subclass.rdf(graph,basens,parentseturi, self.id)

class LegacySetDefinition(object):
    def __init__(self, id, type, classes = None, subsets = None, label =None):
        self.id = id
        self.type = type
        self.label = label
        if classes:
            self.classes = classes
        else:
            self.classes = []
        if subsets:
            self.subsets = subsets
        else:
            self.subsets = []

    @classmethod
    def parsexml(Class, node):
        issubset = node.tag == '{' + NSFOLIA + '}subset'
        if not issubset:
            assert node.tag == '{' + NSFOLIA + '}set'
        classes = []
        subsets= []
        if 'type' in node.attrib:
            if node.attrib['type'] == 'open':
                type = SetType.OPEN
            elif node.attrib['type'] == 'closed':
                type = SetType.CLOSED
            elif node.attrib['type'] == 'mixed':
                type = SetType.MIXED
            elif node.attrib['type'] == 'empty':
                type = SetType.EMPTY
            else:
                raise Exception("Invalid set type: ", type)
        else:
            type = SetType.CLOSED

        if 'label' in node.attrib:
            label = node.attrib['label']
        else:
            label = None

        for subnode in node:
            if isinstance(subnode.tag, str) or (sys.version < '3' and isinstance(subnode.tag, unicode)): #pylint: disable=undefined-variable
                if subnode.tag == '{' + NSFOLIA + '}class':
                    classes.append( LegacyClassDefinition.parsexml(subnode) )
                elif not issubset and subnode.tag == '{' + NSFOLIA + '}subset':
                    subsets.append( LegacySetDefinition.parsexml(subnode) )
                elif subnode.tag == '{' + NSFOLIA + '}constraint':
                    pass
                elif subnode.tag[:len(NSFOLIA) +2] == '{' + NSFOLIA + '}':
                    raise SetDefinitionError("Invalid tag in Set definition: " + subnode.tag)

        return LegacySetDefinition(node.attrib['{http://www.w3.org/XML/1998/namespace}id'],type,classes, subsets, label)


    def json(self):
        jsonnode = {'id': self.id}
        if self.label:
            jsonnode['label'] = self.label
        if self.type == SetType.OPEN:
            jsonnode['type'] = 'open'
        elif self.type == SetType.CLOSED:
            jsonnode['type'] = 'closed'
        elif self.type == SetType.MIXED:
            jsonnode['type'] = 'mixed'
        elif self.type == SetType.EMPTY:
            jsonnode['type'] = 'empty'
        jsonnode['subsets'] = {}
        for subset in self.subsets:
            jsonnode['subsets'][subset.id] = subset.json()
        jsonnode['classes'] = {}
        jsonnode['classorder'] = []
        for c in sorted(self.classes, key=lambda x: x.label):
            jsonnode['classes'][c.id] = c.json()
            jsonnode['classorder'].append( c.id )
        return jsonnode

    def rdf(self,graph, basens="",parenturi=None):
        if not basens:
            basens = NSFOLIASETDEFINITION + "/" + self.id
        if not parenturi:
            graph.bind( self.id, basens + '#', override=True ) #set a prefix for our namespace (does not use @base because of issue RDFLib/rdflib#559 )
            seturi = rdflib.term.URIRef(basens + '#Set')
        else:
            seturi = rdflib.term.URIRef(basens + '#Subset.' + self.id)

        graph.add((seturi, rdflib.RDF.type, rdflib.term.URIRef(NSSKOS + '#Collection')))
        if self.id:
            graph.add((seturi, rdflib.term.URIRef(NSSKOS + '#notation'), rdflib.term.Literal(self.id)))
        if self.type == SetType.OPEN:
            graph.add((seturi, rdflib.term.URIRef(NSFOLIASETDEFINITION + '#open'), rdflib.term.Literal(True)))
        elif self.type == SetType.EMPTY:
            graph.add((seturi, rdflib.term.URIRef(NSFOLIASETDEFINITION + '#empty'), rdflib.term.Literal(True)))
        if self.label:
            graph.add((seturi, rdflib.term.URIRef(NSSKOS + '#prefLabel'), rdflib.term.Literal(self.label)))
        if parenturi:
            graph.add((parenturi, rdflib.term.URIRef(NSSKOS + '#member'), seturi))

        for i, c in enumerate(self.classes):
            c.rdf(graph, basens, seturi, None, i+1)

        for s in self.subsets:
            s.rdf(graph, basens, seturi)


def xmltreefromstring(s):
    """Internal function, deals with different Python versions, unicode strings versus bytes, and with the leak bug in lxml"""
    if sys.version < '3':
        #Python 2
        if isinstance(s,unicode): #pylint: disable=undefined-variable
            s = s.encode('utf-8')
        try:
            return ElementTree.parse(StringIO(s), ElementTree.XMLParser(collect_ids=False))
        except TypeError:
            return ElementTree.parse(StringIO(s), ElementTree.XMLParser()) #older lxml, may leak!!!!
    else:
        #Python 3
        if isinstance(s,str):
            s = s.encode('utf-8')
        try:
            return ElementTree.parse(BytesIO(s), ElementTree.XMLParser(collect_ids=False))
        except TypeError:
            return ElementTree.parse(BytesIO(s), ElementTree.XMLParser()) #older lxml, may leak!!!!

class SetDefinition(object):
    def __init__(self, url, format=None, basens="",verbose=False):
        self.graph = rdflib.Graph()
        self.basens = basens
        self.mainsetcache = {}
        self.subsetcache = {}
        self.set_id_uri_cache = {}
        self.verbose = verbose
        self.graph.bind( 'fsd', NSFOLIASETDEFINITION+'#', override=True)
        self.graph.bind( 'skos', NSSKOS+'#', override=True)
        if not format:
            #try to guess format from URL
            if url.endswith('.ttl'):
                format = 'text/turtle'
            elif url.endswith('.n3'):
                format = 'text/n3'
            elif url.endswith('.rdf.xml') or url.endswith('.rdf'):
                format = 'application/rdf+xml'
            elif url.endswith('.xml'): #other XML will be considered legacy
                format = 'application/foliaset+xml' #legacy

        if format in ('application/foliaset+xml','legacy',None):
            #legacy format, has some checks and fallbacks if the format turns out to be RDF anyway
            self.legacyset = None
            if url[0] == '/' or url[0] == '.':
                #local file
                f = io.open(url,'r',encoding='utf-8')
            else:
                #remote URL
                if not self.basens:
                    self.basens = url
                try:
                    f = urlopen(url)
                except:
                    raise DeepValidationError("Unable to download " + url)
            try:
                data = f.read()
            except IOError:
                raise DeepValidationError("Unable to download " + url)
            finally:
                f.close()
            if data[0] in ('@',b'@',64):
                #this is not gonna be valid XML, but looks like turtle/n3 RDF
                self.graph.parse(location=url, format='text/turtle')
                if self.verbose:
                    print("Loaded set " + url + " (" + str(len(self.graph)) + " triples)",file=sys.stderr)
                return
            tree = xmltreefromstring(data)
            root = tree.getroot()
            if root.tag != '{' + NSFOLIA + '}set':
                if root.tag.lower().find('rdf') != 1:
                    #well, this is RDF after all...
                    self.graph.parse(location=url, format='rdf')
                    return
                else:
                    raise SetDefinitionError("Not a FoLiA Set Definition! Unexpected root tag:"+ root.tag)
            legacyset = LegacySetDefinition.parsexml(root)
            legacyset.rdf(self.graph, self.basens)
            if self.verbose:
                print("Loaded legacy set " + url + " (" + str(len(self.graph)) + " triples)",file=sys.stderr)
        else:
            try:
                self.graph.parse(location=url, format=format)
            except HTTPError:
                raise DeepValidationError("Unable to download " + url)
            if self.verbose:
                print("Loaded set " + url + " (" + str(len(self.graph)) + " triples)",file=sys.stderr)

    def testclass(self,cls):
        """Test for the presence of the class, returns the full URI or raises an exception"""
        mainsetinfo = self.mainset()
        if mainsetinfo['open']:
            return cls #everything is okay
        elif mainsetinfo['empty']:
            if cls:
                raise DeepValidationError("Expected an empty class, got \"" + cls + "\"")
        else:
            if not cls:
                raise DeepValidationError("No class specified")
            #closed set
            set_uri = mainsetinfo['uri']
            for row in self.graph.query("SELECT ?c WHERE { ?c rdf:type skos:Concept ; skos:notation \"" + cls + "\". <" + str(set_uri) + "> skos:member ?c }"):
                return str(row.c)
            raise DeepValidationError("Not a valid class: " + cls)

    def testsubclass(self, cls, subset, subclass):
        """Test for the presence of a class in a subset (used with features), returns the full URI or raises an exception"""
        subsetinfo = self.subset(subset)
        if subsetinfo['open']:
            return subclass #everything is okay
        else:
            subset_uri = subsetinfo['uri']
            if not subset_uri:
                raise DeepValidationError("Not a valid subset: " + subset)

            query = "SELECT ?c WHERE { ?c rdf:type skos:Concept ; skos:notation \"" + subclass + "\" . <" + str(subset_uri) + "> skos:member ?c }"
            for row in self.graph.query(query):
                return str(row.c)
            raise DeepValidationError("Not a valid class in subset " + subset + ": " + subclass)

    def get_set_uri(self, set_id=None):
        if set_id in self.set_id_uri_cache:
            return self.set_id_uri_cache[set_id]
        if set_id:
            for row in self.graph.query("SELECT ?s WHERE { ?s rdf:type skos:Collection ; skos:notation \"" + set_id + "\" }"):
                self.set_id_uri_cache[set_id] = row.s
                return row.s
            raise DeepValidationError("No such set: " + str(set_id))
        else:
            for row in self.graph.query("SELECT ?s WHERE { ?s rdf:type skos:Collection . FILTER NOT EXISTS { ?y rdf:type skos:Collection . ?y skos:member ?s } }"):
                self.set_id_uri_cache[set_id] = row.s
                return row.s
            raise DeepValidationError("Main set not found")

    def mainset(self):
        """Returns information regarding the set"""
        if self.mainsetcache:
            return self.mainsetcache
        set_uri = self.get_set_uri()
        for row in self.graph.query("SELECT ?seturi ?setid ?setlabel ?setopen ?setempty WHERE { ?seturi rdf:type skos:Collection . OPTIONAL { ?seturi skos:notation ?setid } OPTIONAL { ?seturi skos:prefLabel ?setlabel } OPTIONAL { ?seturi fsd:open ?setopen } OPTIONAL { ?seturi fsd:empty ?setempty } FILTER NOT EXISTS { ?y skos:member ?seturi . ?y rdf:type skos:Collection } }"):
            self.mainsetcache = {'uri': str(row.seturi), 'id': str(row.setid), 'label': str(row.setlabel) if row.setlabel else "", 'open': bool(row.setopen), 'empty': bool(row.setempty) }
            return self.mainsetcache
        raise DeepValidationError("Unable to find main set (set_uri=" + str(set_uri)+"), this should not happen")

    def subset(self, subset_id):
        """Returns information regarding the set"""
        if subset_id in self.subsetcache:
            return self.subsetcache[subset_id]
        set_uri = self.get_set_uri(subset_id)
        for row in self.graph.query("SELECT ?seturi ?setid ?setlabel ?setopen WHERE { ?seturi rdf:type skos:Collection . OPTIONAL { ?seturi skos:notation ?setid } OPTIONAL { ?seturi skos:prefLabel ?setlabel } OPTIONAL { ?seturi fsd:open ?setopen } FILTER (?seturi = <" + str(set_uri)+">) }"):
            self.subsetcache[str(row.setid)] = {'uri': str(row.seturi), 'id': str(row.setid), 'label': str(row.setlabel) if row.setlabel else "", 'open': bool(row.setopen) }
            return self.subsetcache[str(row.setid)]
        raise DeepValidationError("Unable to find subset (set_uri=" + str(set_uri)+")")

    def orderedclasses(self, set_uri_or_id=None, nestedhierarchy=False):
        """Higher-order generator function that yields class information in the right order, combines calls to :meth:`SetDefinition.classes` and :meth:`SetDefinition.classorder`"""
        classes = self.classes(set_uri_or_id, nestedhierarchy)
        for classid in self.classorder(classes):
            yield classes[classid]

    def __iter__(self):
        """Alias for :meth:`SetDefinition.orderedclasses`"""
        return self.orderedclasses()

    def classes(self, set_uri_or_id=None, nestedhierarchy=False):
        """Returns a dictionary of classes for the specified (sub)set (if None, default, the main set is selected)"""
        if set_uri_or_id and set_uri_or_id.startswith(('http://','https://')):
            set_uri = set_uri_or_id
        else:
            set_uri = self.get_set_uri(set_uri_or_id)

        assert set_uri is not None

        classes= {}
        uri2idmap = {}
        for row in self.graph.query("SELECT ?classuri ?classid ?classlabel ?parentclass ?seqnr  WHERE { ?classuri rdf:type skos:Concept ; skos:notation ?classid. <" + str(set_uri) + "> skos:member ?classuri . OPTIONAL { ?classuri skos:prefLabel ?classlabel } OPTIONAL { ?classuri skos:broader ?parentclass } OPTIONAL { ?classuri fsd:sequenceNumber ?seqnr } }"):
            classinfo = {'uri': str(row.classuri), 'id': str(row.classid),'label': str(row.classlabel) if row.classlabel else "" }
            if nestedhierarchy:
                uri2idmap[str(row.classuri)] = str(row.classid)
            if row.parentclass:
                classinfo['parentclass'] =  str(row.parentclass) #uri
            if row.seqnr:
                classinfo['seqnr'] =  int(row.seqnr)
            classes[str(row.classid)] = classinfo

        if nestedhierarchy:
            #build hierarchy
            removekeys = []
            for classid, classinfo in classes.items():
                if 'parentclass' in classinfo:
                    removekeys.append(classid)
                    parentclassid = uri2idmap[classinfo['parentclass']]
                    if 'subclasses' not in classes[parentclassid]:
                        classes[parentclassid]['subclasses'] = {}
                    classes[parentclassid]['subclasses'][classid] = classinfo
            for key in removekeys:
                del classes[key]
        return classes

    def classorder(self,classes):
        """Return a list of class IDs in order for presentational purposes: order is determined first and foremost by explicit ordering, else alphabetically by label or as a last resort by class ID"""
        return [ classid for classid, classitem in sorted( ((classid, classitem) for classid, classitem in classes.items() if 'seqnr' in classitem) , key=lambda pair: pair[1]['seqnr'] )] + \
               [ classid for classid, classitem in sorted( ((classid, classitem) for classid, classitem in classes.items() if 'seqnr' not in classitem) , key=lambda pair: pair[1]['label'] if 'label' in pair[1] else pair[1]['id']) ]



    def subsets(self, set_uri_or_id=None):
        if set_uri_or_id and set_uri_or_id.startswith(('http://', 'https://')):
            set_uri = set_uri_or_id
        else:
            set_uri = self.get_set_uri(set_uri_or_id)

        assert set_uri is not None

        for row in self.graph.query("SELECT ?seturi ?setid ?setlabel ?setopen WHERE { ?seturi rdf:type skos:Collection . <" + str(set_uri) + "> skos:member ?seturi . OPTIONAL { ?seturi skos:notation ?setid } OPTIONAL { ?seturi skos:prefLabel ?setlabel } OPTIONAL { ?seturi fsd:open ?setopen } }"):
            yield {'uri': str(row.seturi), 'id': str(row.setid), 'label': str(row.setlabel) if row.setlabel else "", 'open': bool(row.setopen) }

    def json(self):
        data = {'subsets': {}}
        setinfo = self.mainset()
        #backward compatibility, set type:
        if setinfo['open']:
            setinfo['type'] = 'open'
        else:
            setinfo['type'] = 'closed'
        data.update(setinfo)
        classes = self.classes()
        data['classes'] = classes
        data['classorder'] = self.classorder(classes)
        for subsetinfo in self.subsets():
            #backward compatibility, set type:
            if subsetinfo['open']:
                subsetinfo['type'] = 'open'
            else:
                subsetinfo['type'] = 'closed'
            data['subsets'][subsetinfo['id']] = subsetinfo
            classes = self.classes(subsetinfo['uri'])
            data['subsets'][subsetinfo['id']]['classes'] = classes
            data['subsets'][subsetinfo['id']]['classorder'] = self.classorder(classes)
        return data
