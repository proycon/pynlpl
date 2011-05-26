#---------------------------------------------------------------
# PyNLPl - FoLiA Format Module
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Module for reading and writing FoLiA XML
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------



from lxml import etree as ElementTree
from lxml.builder import E, ElementMaker
from sys import stderr
from StringIO import StringIO
from pynlpl.formats.imdi import RELAXNG_IMDI
import inspect
import glob
import os

NSFOLIA = "http://ilk.uvt.nl/folia"
NSDCOI = "http://lands.let.ru.nl/projects/d-coi/ns/1.0"

class AnnotatorType:
    UNSET = 0
    AUTO = 1
    MANUAL = 2
    

class Attrib:
    ID, CLASS, ANNOTATOR, CONFIDENCE, N = (0,1,2,3,4)

class AnnotationType:
    TOKEN, DIVISION, POS, LEMMA, DOMAIN, SENSE, SYNTAX, CHUNKING, ENTITY, CORRECTION, SUGGESTION, ERRORDETECTION, ALTERNATIVE, PHON = range(14)
    
    #Alternative is a special one, not declared and not used except for ID generation
                  
          
class MetaDataType:
    NATIVE, CMDI, IMDI = range(3)     
    
class NoSuchAnnotation(Exception):
    pass

class NoSuchText(Exception):
    pass

class DuplicateAnnotationError(Exception):
    pass
    
class NoDefaultError(Exception):
    pass    
    
def parsecommonarguments(object, doc, annotationtype, required, allowed, **kwargs):
    object.doc = doc #The FoLiA root document
    supported = required + allowed
    
    if 'generate_id_in' in kwargs:
        kwargs['id'] = kwargs['generate_id_in'].generate_id(object.__class__)
        del kwargs['generate_id_in']
            
    if 'id' in kwargs:
        if not Attrib.ID in supported:
            raise ValueError("ID is not supported")
        object.id = kwargs['id']
        del kwargs['id']
    elif Attrib.ID in required:
        raise ValueError("ID is required for " + object.__class__.__name__)
    else:
        object.id = None

    if 'set' in kwargs:
        if not Attrib.CLASS in supported:
            raise ValueError("Set is not supported")
        object.set = kwargs['set']
        del kwargs['set']
    elif annotationtype in doc.annotationdefaults and 'set' in doc.annotationdefaults[annotationtype]:
        object.set = doc.annotationdefaults[annotationtype]['set']
    elif Attrib.CLASS in required:
        raise ValueError("Set is required for " + object.__class__.__name__)
    else:
        object.set = None        
            
            
    if 'class' in kwargs:
        if not Attrib.CLASS in supported:
            raise ValueError("Class is not supported for " + object.__class__.__name__)
        object.cls = kwargs['class']
        del kwargs['class']  
    elif 'cls' in kwargs:
        if not Attrib.CLASS in supported:
            raise ValueError("Class is not supported on " + object.__class__.__name__)
        object.cls = kwargs['cls']
        del kwargs['cls']
    elif Attrib.CLASS in required:
        raise ValueError("Class is required for " + object.__class__.__name__)
    else:
        object.cls = None
    
    
    
      
    
            
    if 'annotator' in kwargs:
        if not Attrib.ANNOTATOR in supported:
            raise ValueError("Annotator is not supported for " + object.__class__.__name__)
        object.annotator = kwargs['annotator']
        del kwargs['annotator']
    elif annotationtype in doc.annotationdefaults and 'annotator' in doc.annotationdefaults[annotationtype]:
        object.annotator = doc.annotationdefaults[annotationtype]['annotator']
    elif Attrib.ANNOTATOR in required:
        raise ValueError("Annotator is required for " + object.__class__.__name__)
    else:
        object.annotator = None        
    
        
    if 'annotatortype' in kwargs:
        if not Attrib.ANNOTATOR in supported:
            raise ValueError("Annotatortype is not supported for " + object.__class__.__name__)
        if kwargs['annotatortype'] == 'auto' or kwargs['annotatortype'] == AnnotatorType.AUTO:
            object.annotatortype = AnnotatorType.AUTO
        elif kwargs['annotatortype'] == 'manual' or kwargs['annotatortype']  == AnnotatorType.MANUAL:
            object.annotatortype = AnnotatorType.MANUAL
        else:
            raise ValueError("annotatortype must be 'auto' or 'manual'")                
        del kwargs['annotatortype']
    elif annotationtype in doc.annotationdefaults and 'annotatortype' in doc.annotationdefaults[annotationtype]:
        object.annotatortype = doc.annotationdefaults[annotationtype]['annotatortype']            
    elif Attrib.ANNOTATOR in required:
        raise ValueError("Annotatortype is required for " + object.__class__.__name__)        
    else:
        object.annotatortype = None        
    
        
        
    if 'confidence' in kwargs:
        if not Attrib.CONFIDENCE in supported:
            raise ValueError("Confidence is not supported")
        try:
            object.confidence = float(kwargs['confidence'])
            assert (object.confidence >= 0.0 and object.confidence <= 1.0)
        except:
            raise ValueError("Confidence must be a floating point number between 0 and 1")
        del kwargs['confidence']    
    elif Attrib.CONFIDENCE in required:
        raise ValueError("Confidence is required for " + object.__class__.__name__)
    else:
        object.confidence = None
        
        

    if 'n' in kwargs:
        if not Attrib.N in supported:
            raise ValueError("N is not supported")
            object.n = kwargs['n']
        del kwargs['n']                
    elif Attrib.N in required:
        raise ValueError("N is required")
    else:
        object.n = None    
    
    
    
    
            
        
        
    if object.ALLOWTEXT:
        if isinstance(object, Word):
            if 'text' in kwargs:
                if kwargs['text']:
                    object.settext(kwargs['text'], True) #default text is corrected text
                del kwargs['text']
        else:
            if 'text' in kwargs:
                if kwargs['text']:
                    object.settext(kwargs['text'], False) #default text is pre-corrected text
                del kwargs['text']
            if 'correctedtext' in kwargs:
                if kwargs['correctedtext']:
                    object.settext(kwargs['correctedtext'], True)
                del kwargs['correctedtext']
    elif 'text' in kwargs or 'correctedtext' in kwargs:
        raise ValueError("Text specified for an element that does not allow it is required for " + object.__class__.__name__)

    if doc.debug >= 2:
        print >>stderr, "   @id           = ", repr(object.id)
        print >>stderr, "   @set          = ", repr(object.set)
        print >>stderr, "   @class        = ", repr(object.cls)
        print >>stderr, "   @annotator    = ", repr(object.annotator)
        print >>stderr, "   @annotatortype= ", repr(object.annotatortype)
        print >>stderr, "   @confidence   = ", repr(object.confidence)
        print >>stderr, "   @n            = ", repr(object.n)
        
                
    #set index
    if object.id:
        if object.id in doc.index:
            if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Duplicate ID not permitted:" + object.id
            raise Exception("Duplicate ID not permitted: " + object.id)
        else:
            if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Adding to index: " + object.id
            doc.index[object.id] = object

    
    return kwargs
    
        




        
class AbstractElement(object):
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = ()
    ACCEPTED_DATA = ()
    ANNOTATIONTYPE = None
    XMLTAG = None
    ALLOWTEXT = False
    
    
    
    def __init__(self, doc, *args, **kwargs):
        if not isinstance(doc, Document):
            raise Exception("Expected first parameter to be instance of Document, got " + str(type(doc)))
        self.doc = doc
        self.parent = None
        self.data = []
        if self.ALLOWTEXT:
            self.textdata = []
        
            
        kwargs = parsecommonarguments(self, doc, self.ANNOTATIONTYPE, self.REQUIRED_ATTRIBS, self.OPTIONAL_ATTRIBS,**kwargs)
        for child in args:
            self.append(child)
        if 'contents' in kwargs:
            if isinstance(kwargs['contents'], list):
                for child in kwargs['contents']:
                    self.append(child)
            else:
                self.append(kwargs['contents'])
            del kwargs['contents']
                    
        for key in kwargs:
            raise ValueError("Parameter '" + key + "' not supported by " + self.__class__.__name__)        
        

    def text(self):
        """If there is a corrected text, it will be selected, otherwise uncorrected text, and if text exists and error will be raised. Note that text() only covers explicitly provided text! Use unicode() or str() otherwise"""
        if not self.ALLOWTEXT:
            raise NotImplementedError("No text allowed for " + self.__class__.__name__) #on purpose        
        if len(self.textdata) == 0:
            raise NoSuchText
        return self.textdata[-1].value #newest by default
    
    def uncorrectedtext(self):
        if not self.ALLOWTEXT or isinstance(self,Word):
            raise NotImplementedError #on purpose            
        for t in self.textdata:
            if not t.corrected:
                return t.corrected
        raise NoSuchText
        
    def correctedtext(self):
        if not self.ALLOWTEXT:
            raise NotImplementedError #on purpose            
        for i in range(1,len(self.textdata) + 1):
            if self.textdata[-i].corrected:
                return self.textdata[-i].value
        raise NoSuchText

    def __len__(self):
        return len(self.data)
        
    def __nonzero__(self):
        return True
        
    def __iter__(self):
        """Iterate over children"""
        return iter(self.data)

    def __contains__(self, child):
        return child in self.data
            
    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise

    def __unicode__(self):
        #get the most actual text:
        # - first see if there is a text element (with corrected attribute)
        # - if not, descend into children to grab dynamically
        # - if that yields no results, try to get the uncorrected text (this may raise an exception if it too fails)
        try:
            return self.correctedtext()
        except:        
            #descend into children
            s = ""
            for e in self:
                try:                    
                    s += unicode(e) + " " #space separated by default, override for other behaviour
                except:
                    continue
            if s.strip():
                return s.strip()
            else:                
                return self.uncorrectedtext()
    
    def __str__(self):
        return unicode(self).encode('utf-8')
        
    def settext(self, text, corrected=False):
        """Set text: may take TextContent element, unicode, or string (utf-8). Only in the latter two cases, the corrected parameter will be consulted. Existing texts will be *REPLACED*"""
        if not self.ALLOWTEXT:
            raise NotImplementedError #on purpose
        if isinstance(text, TextContent):
            replace = None
            prepend = False
            for i, t in enumerate(self.textdata):
                if t.corrected == text.corrected:
                    replace = i
                elif not text.corrected:
                    prepend = True                
            if not replace is None:
                self.textdata[replace] = text
            elif prepend:
                self.textdata.insert(0,text)
            else:
                self.textdata.append(text)  
            text.parent = self
            if not text.ref and self.parent:
                text.ref = self.parent 
        elif isinstance(text, unicode):
            assert corrected in [False,'inline',True]
            self.settext(TextContent(self.doc, value=text, corrected=corrected))
        elif isinstance(text, str):
            assert corrected in [False,'inline',True]
            self.settext(TextContent(self.doc, value=unicode(text,'utf-8'), corrected=corrected))
        
            
    def append(self, child):
        if child.__class__ in self.ACCEPTED_DATA or child.__class__.__base__ in self.ACCEPTED_DATA:
            self.data.append(child)
            child.parent = self
        elif child and child.ALLOWTEXT:
            self.settext(child)
        else:
            raise ValueError("Unable to append object of type " + child.__class__.__name__ + " to " + self.__class__.__name__ )
            
            

    def xml(self, attribs = None,elements = None, skipchildren = False):  
        global NSFOLIA
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
        
        if not attribs: attribs = {}
        if not elements: elements = []
        
        if self.id:
            attribs['{http://www.w3.org/XML/1998/namespace}id'] = self.id
            
        #Some attributes only need to be added if they are not the same as what's already set in the declaration    
        try:
            if self.set and (not self.ANNOTATIONTYPE in self.doc.annotationdefaults or not 'set' in self.doc.annotationdefaults[self.ANNOTATIONTYPE] or self.set != self.doc.annotationdefaults[self.ANNOTATIONTYPE]['set']):
                attribs['{' + NSFOLIA + '}set'] = self.set        
        except AttributeError:
            pass
        
        try:
            if self.cls:
                attribs['{' + NSFOLIA + '}class'] = self.cls
        except AttributeError:
            pass            
        try:            
            if self.annotator and (not self.ANNOTATIONTYPE in self.doc.annotationdefaults or not 'annotator' in self.doc.annotationdefaults[self.ANNOTATIONTYPE] or self.annotator != self.doc.annotationdefaults[self.ANNOTATIONTYPE]['annotator']):
                attribs['{' + NSFOLIA + '}annotator'] = self.annotator
            if self.annotatortype and (not self.ANNOTATIONTYPE in self.doc.annotationdefaults or not 'annotatortype' in self.doc.annotationdefaults[self.ANNOTATIONTYPE] or self.annotatortype != self.doc.annotationdefaults[self.ANNOTATIONTYPE]['annotatortype']):
                if self.annotatortype == AnnotatorType.AUTO:
                    attribs['{' + NSFOLIA + '}annotatortype'] = 'auto'
                elif self.annotatortype == AnnotatorType.MANUAL:
                    attribs['{' + NSFOLIA + '}annotatortype'] = 'manual'
        except AttributeError:
            pass       
        try:
            if self.confidence:
                attribs['{' + NSFOLIA + '}confidence'] = str(self.confidence)
        except AttributeError:
            pass
        try:
            if self.n:
                attribs['{' + NSFOLIA + '}n'] = str(self.n)
        except AttributeError:
            pass
            
        e  = E._makeelement('{' + NSFOLIA + '}' + self.XMLTAG, **attribs)        
        
        if self.ALLOWTEXT:
            for t in self.textdata:
                e.append(t.xml()) 
            
        #append children:
        if not skipchildren and self.data:
            for child in self:
                e.append(child.xml())
        if elements:
            for e2 in elements:
                e.append(e2)
        return e

    def xmlstring(self):
        return ElementTree.tostring(self.xml(), xml_declaration=False, pretty_print=True, encoding='utf-8')        
        
        
    def select(self, cls, set=None, recursive=True,  ignorelist=[], node=None):
        l = []
        if not node:
            node = self        
        for e in self.data:
            ignore = False                            
            for c in ignorelist:
                if c == e.__class__ or issubclass(e.__class__,c):
                    ignore = True
                    break
            if ignore: 
                continue
        
            if isinstance(e, cls):                
                if not set is None:
                    try:
                        if e.set != set:
                            continue
                    except:
                        continue
                l.append(e)
            if recursive:
                for e2 in e.select(cls, set, recursive, ignorelist, e):
                    if not set is None:
                        try:
                            if e2.set != set:
                                continue
                        except:
                            continue
                    l.append(e2)
        return l
        

    def xselect(self, cls, recursive=True, node=None):
        if not node:
            node = self
        for e in self:
            if isinstance(e, cls):
                if not set is None:
                    try:
                        if e.set != set:
                            continue
                    except:
                        continue 
                yield e
            elif recursive:
                for e2 in e.select(cls, recursive, e):
                    if not set is None:
                        try:
                            if e2.set != set:
                                continue
                        except:
                            continue
                    yield e2
        
    
    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
            global NSFOLIA
            E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})

            attribs = []
            if Attrib.ID in cls.REQUIRED_ATTRIBS:
                attribs.append( E.attribute(name='id', ns="http://www.w3.org/XML/1998/namespace") )
            elif Attrib.ID in cls.OPTIONAL_ATTRIBS:
                attribs.append( E.optional( E.attribute(name='id', ns="http://www.w3.org/XML/1998/namespace") ) )                    
            if Attrib.CLASS in cls.REQUIRED_ATTRIBS:
                #Set is a tough one, we can't require it as it may be defined in the declaration: we make it optional and need schematron to resolve this later
                attribs.append( E.attribute(name='class') )
                attribs.append( E.optional( E.attribute( name='set' ) ) )  
            elif Attrib.CLASS in cls.OPTIONAL_ATTRIBS:
                attribs.append( E.optional( E.attribute(name='class') ) )
                attribs.append( E.optional( E.attribute( name='set' ) ) )                                          
            if Attrib.ANNOTATOR in cls.REQUIRED_ATTRIBS or Attrib.ANNOTATOR in cls.OPTIONAL_ATTRIBS:
               #Similarly tough
               attribs.append( E.optional( E.attribute(name='annotator') ) ) 
               attribs.append( E.optional( E.attribute(name='annotatortype') ) ) 
            if Attrib.CONFIDENCE in cls.REQUIRED_ATTRIBS:
               attribs.append(  E.attribute(E.data(type='double',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'), name='confidence',ns=NSFOLIA) )
            elif Attrib.CONFIDENCE in cls.OPTIONAL_ATTRIBS:
               attribs.append(  E.optional( E.attribute(E.data(type='double',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'), name='confidence',ns=NSFOLIA) ) )
            if Attrib.N in cls.REQUIRED_ATTRIBS:
               attribs.append( E.attribute( name='n') )
            elif Attrib.N in cls.OPTIONAL_ATTRIBS:
               attribs.append( E.optional( E.attribute( name='n') ) )
            
            if cls.ALLOWTEXT:
                attribs.append( E.optional( E.ref(name='t') ) ) #yes, not actually an attrib, I know, but should go here
                        
            if extraattribs:
                    for e in extraattribs:
                        attribs.append(e) #s
            
            
            elements = [] #(including attributes)
            
            if includechildren:
                for c in cls.ACCEPTED_DATA:
                    try:
                        if c.XMLTAG:
                            elements.append( E.zeroOrMore( E.ref(name=c.XMLTAG) ) )
                    except AttributeError:
                        continue
                        
            if extraelements:
                    for e in extraelements:
                        elements.append( e )                                                            
                        
            if elements:
                if len(elements) > 1:
                    attribs.append( E.interleave(*elements) )
                else:
                    attribs.append( *elements )
            return E.define( E.element(*attribs, **{name: cls.XMLTAG}), name=cls.XMLTAG, ns=NSFOLIA)
    
    @classmethod
    def parsexml(Class, node, doc):
        assert issubclass(Class, AbstractElement)
        global NSFOLIA, NSDCOI
        nslen = len(NSFOLIA) + 2
        nslendcoi = len(NSDCOI) + 2
        dcoi = (node.tag[:nslendcoi] == '{' + NSDCOI + '}')
        args = []
        kwargs = {}
        text = None
        for subnode in node:
            if subnode.tag == '{' + NSFOLIA + '}t' and Class.ALLOWTEXT:
                text = subnode.text
            elif subnode.tag[:nslen] == '{' + NSFOLIA + '}':
                if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Processing subnode " + subnode.tag[nslen:]
                args.append(doc.parsexml(subnode) )                
            elif subnode.tag[:nslendcoi] == '{' + NSDCOI + '}':
                #Dcoi support
                if Class is Text and subnode.tag[nslendcoi:] == 'body':
                    for subsubnode in subnode:            
                        if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Processing DCOI subnode " + subnode.tag[nslendcoi:]
                        args.append(doc.parsexml(subsubnode) ) 
                else:
                    if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Processing DCOI subnode " + subnode.tag[nslendcoi:]
                    args.append(doc.parsexml(subnode) ) 
            elif doc.debug >= 1:
                print >>stderr, "[PyNLPl FoLiA DEBUG] Ignoring subnode outside of FoLiA namespace: " + subnode.tag
                    

        
        id = dcoipos = dcoilemma = dcoicorrection = dcoicorrectionoriginal = None
        for key, value in node.attrib.items():
            if key == '{http://www.w3.org/XML/1998/namespace}id':
                id = value
                key = 'id'
            elif key[:nslen] == '{' + NSFOLIA + '}':
                key = key[nslen:]
            elif key[:nslendcoi] == '{' + NSDCOI + '}':                
                key = key[nslendcoi:]
                

            #D-Coi support:
            if Class is Word and key == 'pos':
                dcoipos = value
                continue
            elif Class is Word and  key == 'lemma':
                dcoilemma = value
                continue
            elif Class is Word and  key == 'correction':
                dcoicorrection = value #class
                continue
            elif Class is Word and  key == 'original':
                dcoicorrectionoriginal = value                
                continue
            elif Class is Gap and  key == 'reason':
                key = 'class'
            elif Class is Gap and  key == 'hand':
                key = 'annotator'    
            
            kwargs[key] = value
                                
        #D-Coi support:
        if dcoi and Class.ALLOWTEXT:
            text = node.text.strip()
                    
                                
                                    
        #if node.text and node.text.strip():
        #   kwargs['value'] = node.text
        if text:
            kwargs['text'] = text
            if not AnnotationType.TOKEN in doc.annotationdefaults:                    
                doc.declare(AnnotationType.TOKEN, set='http://ilk.uvt.nl/folia/sets/ilktok.foliaset')
                                                            
        if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found " + node.tag[nslen:]
        instance = Class(doc, *args, **kwargs)
        #if id:
        #    if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Adding to index: " + id
        #    doc.index[id] = instance
        if dcoipos:
            if not AnnotationType.POS in doc.annotationdefaults:
                doc.declare(AnnotationType.POS, set='http://ilk.uvt.nl/folia/sets/cgn-legacy.foliaset')
            instance.append( PosAnnotation(doc, cls=dcoipos) )
        if dcoilemma:
            if not AnnotationType.LEMMA in doc.annotationdefaults:
                doc.declare(AnnotationType.LEMMA, set='http://ilk.uvt.nl/folia/sets/mblem-nl.foliaset')
            instance.append( LemmaAnnotation(doc, cls=dcoilemma) )            
        if dcoicorrection and dcoicorrectionoriginal and text:
            if not AnnotationType.CORRECTION in doc.annotationdefaults:
                doc.declare(AnnotationType.CORRECTION, set='http://ilk.uvt.nl/folia/sets/dcoi-corrections.foliaset')
            instance.append( Correction(doc, generate_id_in=instance, cls=dcoicorrection, original=dcoicorrectionoriginal, new=text) )                        
        return instance        
            
    def resolveword(self, id):
        return None
        
    def remove(self, child):
        child.parent = None
        self.data.remove(child)

class AllowTokenAnnotation(object):
    """Elements that allow token annotation (including extended annotation) must inherit from this class"""
    
    def annotations(self, annotationtype=None):
        """Generator yielding all annotations of a certain type. Raises a Raises a NoSuchAnnotation exception if none was found."""
        found = False 
        if inspect.isclass(annotationtype): annotationtype = annotationtype.ANNOTATIONTYPE
        for e in self:
            try:
                if annotationtype is None or e.ANNOTATIONTYPE == annotationtype:
                    found = True
                    yield e
            except AttributeError:
                continue
        if not found:
            raise NoSuchAnnotation()
    
    def hasannotation(self,type,set=None):
        """Returns an integer indicating whether such as annotation exists, and if so, how many"""
        l = self.select(type,set,False) #non-recursive
        return len(l)

    def annotation(self, type, set=None):
        """Will return a SINGLE annotation (even if there are multiple). Raises a NoSuchAnnotation exception if none was found"""
        l = self.select(type,set,False) #non-recursive
        if len(l) >= 1:
            return l[0]
        else:
            raise NoSuchAnnotation()            

    def alternatives(self, annotationtype=None, set=None):
        """Return a list of alternatives, either all or only of a specific type, and possibly restrained also by set"""
        l = []
        if inspect.isclass(annotationtype): annotationtype = annotationtype.ANNOTATIONTYPE
        for e in self.select(Alternative):
            if annotationtype is None:
                l.append(e)
            elif len(e) >= 1: #child elements?
                for e2 in e:
                    try:
                        if e2.ANNOTATIONTYPE == annotationtype:
                            try:
                                if set is None or e2.set == set:
                                    found = True
                                    l.append(e) #not e2
                                    break #yield an alternative only once (in case there are multiple matches)
                            except AttributeError:
                                continue
                    except AttributeError:
                        continue
        return l

class AllowGenerateID(object):
    def _getmaxid(self, xmltag):        
        maxid = 0
        try:
            if xmltag in self.maxid:
                maxid = self.maxid[xmltag]
        except:
            pass
            
        #if self.data: #NOT RECURSIVE ON PURPOSE!
        #    for c in self.data:
        #        try:
        #            tmp = c._getmaxid(xmltag)
        #            if tmp > maxid:
        #                maxid = tmp
        #        except AttributeError:
        #            continue
        #print repr(self), self.maxid, "\n"
        return maxid
            
        
    def _setmaxid(self, child):
        try:
            self.maxid
        except AttributeError:
            self.maxid = {}            
        try:
            if child.id and child.XMLTAG:
                fields = child.id.split(self.doc.IDSEPARATOR)
                if len(fields) > 1 and fields[-1].isdigit():
                    if not child.XMLTAG in self.maxid:
                        self.maxid[child.XMLTAG] = int(fields[-1])
                        #print "set maxid on " + repr(self) + ", " + child.XMLTAG + " to " + fields[-1]
                    else:
                        if self.maxid[child.XMLTAG] < int(fields[-1]):
                           self.maxid[child.XMLTAG] = int(fields[-1]) 
                           #print "set maxid on " + repr(self) + ", " + child.XMLTAG + " to " + fields[-1] 
        except AttributeError:
            pass        
                
        

    def generate_id(self, cls):
        if isinstance(cls,str):
            xmltag = cls
        else:
            try:
                xmltag = cls.XMLTAG
            except:
                raise Exception("Expected a class such as Alternative, Correction, etc...")
                
        maxid = self._getmaxid(xmltag) 
        i = 0
        while True:
            i += 1
            id = self.id + '.' + xmltag + '.' + str(self._getmaxid(xmltag) + i)
            if not id in self.doc.index:
                return id    
                 
                 
class AbstractStructureElement(AbstractElement, AllowTokenAnnotation, AllowGenerateID):
    def __init__(self, doc, *args, **kwargs):            
        super(AbstractStructureElement,self).__init__(doc, *args, **kwargs)

    def __unicode__(self):
        try:
            return self.correctedtext()
        except:        
            #descend into children
            s = ""
            for e in self:
                try:               
                    es = unicode(e)
                    if es:                    
                        s += es + "\n\n" #bigger gap between structure elements
                except:
                    continue
            if s.strip():
                return s.strip()
            else:                
                return self.uncorrectedtext()    
    
    def resolveword(self, id): 
        for child in self:
            r =  child.resolveword(id)            
            if r:
                return r
        return None          
        
    def append(self, child):
        super(AbstractStructureElement,self).append(child)
        self._setmaxid(child)     
                

    def words(self, index = None):        
        if index is None:         
            return self.select(Word,None,True,[AbstractSpanAnnotation])
        else:
            return sum(self.select(Word,None,True,[AbstractSpanAnnotation]),[])[index]
                   
    def paragraphs(self, index = None):
        if index is None:
            return sum([ t.select(Paragraph) for t in self.data ],[])
        else:
            return sum([ t.select(Paragraph) for t in self.data ],[])[index]
    
    def sentences(self, index = None):
        if index is None:
            return sum([ t.select(Sentence,None,True,[Quote]) for t in self.data ],[])
        else:
            return sum([ t.select(Sentence,None,True,[Quote]) for t in self.data ],[])[index]

class TextContent(AbstractElement):
    XMLTAG = 't'
    
    def __init__(self, doc, *args, **kwargs):
        if not 'value' in kwargs:
            raise Exception("TextContent expects value= parameter")
        
        if isinstance(kwargs['value'], unicode):
            self.value = kwargs['value']   
            del kwargs['value'] 
        elif isinstance(kwargs['value'], str):
            self.value = unicode(kwargs['value'],'utf-8')        
            del kwargs['value']
        else:
            raise Exception("Invalid value: " + repr(kwargs['value']))

        #Correct can be True, False or 'inline'
        if 'corrected' in kwargs:
            self.corrected = kwargs['corrected']
            del kwargs['corrected']
        else:
            self.corrected = False

        
        if 'offset' in kwargs: #offset
            self.offset = int(kwargs['offset'])
            del kwargs['offset']
        else:
            self.offset = None            

        if 'newoffset' in kwargs: #new offset
            self.newoffset = int(kwargs['newoffset'])
            del kwargs['offset']
        else:
            self.newoffset = None            

            
        if 'ref' in kwargs: #reference to offset
            if isinstance(self.ref, AbstractElement):
                self.ref = kwargs['ref']
            else:
                self.ref = doc.index[kwargs['ref']]
            del kwargs['ref']
        else:
            self.ref = None #will be set upon parent.append()
            
        if 'length' in kwargs:
            self.length = int(kwargs['length'])
        else:
            self.length = len(self.value)
            
        super(TextContent,self).__init__(doc, *args, **kwargs)
    
    def __unicode__(self):
        return self.value
        
    def __str__(self):
        return self.value.encode('utf-8')
        
    def append(self, child):
        raise NotImplementedError #on purpose
    
    def __iter__(self):
        return iter(self.value)
    
    def __len__(self):    
        return len(self.value)
        
    @classmethod
    def parsexml(Class, node, doc):
        global NSFOLIA
        nslen = len(NSFOLIA) + 2
        args = []
        kwargs = {}
        kwargs['corrected'] = False
        if 'corrected' in node.attrib:
            if node.attrib['corrected'] == 'yes':
                kwargs['corrected'] = True
            elif node.attrib['corrected'] == 'inline':
                kwargs['corrected'] = 'inline'
            elif node.attrib['corrected'] == 'no':
                kwargs['corrected'] = False
            else:
                raise Exception("Invalid value for corrected: ", node.attrib['corrected'])
        
        if 'offset' in node.attrib:
            kwargs['offset'] = int(node.attrib['offset'])
        elif 'newoffset' in node.attrib:
            kwargs['newoffset'] = int(node.attrib['newoffset'])
        elif 'length' in node.attrib:
            kwargs['length'] = int(node.attrib['length'])
        elif 'ref' in node.attrib:
            kwargs['ref'] = node.attrib['ref']

        kwargs['value'] = node.text
        return TextContent(doc, **kwargs)
    
    
    def xml(self, attribs = None,elements = None, skipchildren = False):   
        global NSFOLIA
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})

        attribs = {}  
        if not self.offset is None:
            attribs['{' + NSFOLIA + '}offset'] = str(self.offset)
        if not self.newoffset is None:
            attribs['{' + NSFOLIA + '}newoffset'] = str(self.newoffset)
        if self.length != len(self.value):
            attribs['{' + NSFOLIA + '}length'] = str(self.length)
        if self.parent and self.ref and self.ref != self.parent.parent:
            attribs['{' + NSFOLIA + '}ref'] = self.ref.id
        if self.corrected == 'inline':
            attribs['{' + NSFOLIA + '}corrected'] = 'inline'
        elif self.corrected and not isinstance(self.parent, Word):
            attribs['{' + NSFOLIA + '}corrected'] = 'yes'
            
        return E.t(self.value, **attribs)
        
class Word(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    XMLTAG = 'w'
    ANNOTATIONTYPE = AnnotationType.TOKEN
    ALLOWTEXT = True
    
    def __init__(self, doc, *args, **kwargs):
        self.space = True
                      
        if 'space' in kwargs:            
            self.space = kwargs['space']
            del kwargs['space']
        super(Word,self).__init__(doc, *args, **kwargs)
                
        
    
    def append(self, child):
        if isinstance(child, AbstractTokenAnnotation) or isinstance(child, Alternative) or isinstance(child, Correction):
            if isinstance(child, Correction):
                #TODO: replace other child within the same set
                #TODO: make sure there are not other corrections on the same thing 
                
                conflicts = []                
                
                #Are there correction already?
                if self.hasannotation(Correction):
                    #are there conflicts with the correction that is about to be added?
                    corrections = self.annotations(Correction)
                    for correction in corrections:            
                        for element1 in child.new:
                            for element2 in correction.new:
                                if element1.__class__ == element2.__class__:
                                    if element1.set == element2.set:
                                        if not correction in conflicts:
                                            conflicts.append(correction)
                                            break                
                
                if conflicts:
                    if len(conflicts) >= 2:
                        raise Exception("Unable to add correction. Unresolvable conflict with existing corrections")                                
                    else:                        
                        conflict = conflicts[0]
                        if conflict.new == child.original:
                            #good, we can nest
                            #TODO: ID trouble?
                            self.data.remove(conflict)
                            child.original = [conflict]                                                        
                        else:
                            raise Exception("Unable to add correction. Unresolvable conflict with existing correction")                                
                
            elif isinstance(child, AbstractTokenAnnotation):
                #sanity check, there may be no other child within the same set
                try:
                    if not child.ALLOWDUPLICATES:
                        self.annotation(child.__class__, child.set)
                        raise DuplicateAnnotationError
                except NoSuchAnnotation:
                    #good, that's what we want
                    pass
            self.data.append(child)
            child.parent = self
            self._setmaxid(child)
        else:
            raise TypeError("Invalid type for Word:" + str(type(child)))


    def sentence(self):
        #return the sentence this word is a part of, otherwise return None
        e = self;
        while e.parent: 
            if isinstance(e, Sentence):
                return e
            e = e.parent
        return None
        
        
    def paragraph(self):
        #return the paragraph this sentence is a part of (None otherwise)
        e = self;
        while e.parent: 
            if isinstance(e, Paragraph):
                return e
            e = e.parent  
        return None        
        
    def division(self):
        #return the division this sentence is a part of (None otherwise)
        e = self;
        while e.parent: 
            if isinstance(e, Division):
                return e
            e = e.parent  
        return None
                
        

    def incorrection(self):
        #Is this word part of a correction? If so, return correction, otherwise return None
        e = self
        
        
        while not e.parent is None:            
                if isinstance(e, Correction):
                    return e
                if isinstance(e, Sentence):
                    break
                e = e.parent
            
        return None
        
        

    def pos(self,set=None):
        """Return the PoS annotation (will return only one if there are multiple!)"""
        return self.annotation(PosAnnotation,set)
            
    def lemma(self, set=None):
        return self.annotation(LemmaAnnotation,set)

    def sense(self,set=None):
        return self.annotation(SenseAnnotation,set)
        
    def domain(self,set=None):
        return self.annotation(DomainAnnotation,set)        


    def settext(self, text, corrected=True):
        if isinstance(text, TextContent) and not text.corrected:
            raise Exception("Can only add text content with corrected=yes")
        return super(Word,self).settext(text,True)
        
    def resolveword(self, id):
        if id == self.id:
            return self
        else:
            return None
    
    def getcorrection(self,set=None,cls=None):
        try:
            return self.getcorrections(set,cls)[0]
        except:
            raise NoSuchAnnotation
    
    def getcorrections(self, set=None,cls=None):
        try:
            l = []        
            for correction in self.annotations(Correction):
                if ((not set or correction.set == set) and (not cls or correction.cls == cls)):
                    l.append(correction)
            return l
        except NoSuchAnnotation:
            raise
    
    @classmethod
    def parsexml(Class, node, doc):
        assert Class is Word
        global NSFOLIA
        nslen = len(NSFOLIA) + 2
        instance = super(Word,Class).parsexml(node, doc)
        if 'space' in node.attrib:
            if node.attrib['space'] == 'no':
                instance.space = False
        return instance


    def xml(self, attribs = None,elements = None, skipchildren = False):   
        if not attribs: attribs = {}
        if not self.space:
            attribs['space'] = 'no'
        return super(Word,self).xml(attribs,elements, False)  

                
        
    
    def split(self, *newwords, **kwargs):
        self.sentence().splitword(self, *newwords, **kwargs)

    def correcttext(self, **kwargs):        
        if 'new' in kwargs:
            kwargs['original'] = self.text()              
        elif not 'suggestions' in kwargs and not 'suggestion' in kwargs:
            raise Exception("No new= or suggestions= specified")
                
        
        if 'suggestion' in kwargs:
            kwargs['suggestions'] = [kwargs['suggestion']]
            del kwargs['suggestion']
        
        if 'suggestions' in kwargs:    
            suggestions = []
            for s in kwargs['suggestions']:
                if isinstance(s,Suggestion):
                    suggestions.append(s)
                elif isinstance(s, AbstractTokenAnnotation) or isinstance(s, TextContent ):
                    suggestions.append( Suggestion(self.doc, s) )
                elif isinstance(s, unicode) or isinstance(s, str):
                    suggestions.append( Suggestion(self.doc, text=TextContent(self.doc, value=s, corrected=True)) )        
                else:
                    raise Exception("Unexpected type for suggestion")
            kwargs['suggestions'] = suggestions
            
        if not 'id' in kwargs:
            kwargs['id'] = self.generate_id(Correction)
        #if 'alternative' in kwargs:
        #    if kwargs['alternative']:
        #        del kwargs['alternative']
        #        c = Alternative(self.doc, Correction(self.doc, **kwargs), id=self.generate_id(Alternative))            
        #    else:
        #        del kwargs['alternative']
        #else:
        
        if 'reuse' in kwargs:
            #reuse an existing correction instead of making a new one
            if isinstance(kwargs['reuse'], Correction):
                c = kwargs['reuse']
            else: #assume it's an index
                c = self.doc.index[kwargs['reuse']]
            del kwargs['reuse']
            if 'new' in kwargs:
                c.setnew(kwargs['new'])
            if 'original' in kwargs:
                c.setoriginal(kwargs['original'])
            if 'current' in kwargs:
                c.setcurrent(kwargs['current'])
            if 'suggestions' in kwargs:
                for suggestion in kwargs['suggestions']:
                    c.addsuggestion(suggestion)
        else:
            c = Correction(self.doc, **kwargs)
            self.append( c )    
        if 'new' in kwargs:
            self.settext(kwargs['new'])
        
        return c 
        
        
        
            
    def correctannotation(self, original, new, **kwargs):
        if not original in self:
            kwargs['original'] = original
            raise Exception("Original not found!")
        kwargs['new'] = new
        if not 'id' in kwargs:
            kwargs['id'] = self.generate_id(Correction)
        self.remove(original)        
        if 'alternative' in kwargs and kwargs['alternative']:
            c = Alternative(  Correction(self.doc, **kwargs) , id=self.generate_id(Alternative))
            del kwargs['alternative']
        else:
            c = Correction(self.doc, **kwargs)
            self.append( new )
        self.append( c )
        return c 
        

    @classmethod        
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        global NSFOLIA
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        if not extraelements:
            extraelements = []
        done = {}
        for c in globals().values():
                if 'relaxng' in dir(c):
                    if c.relaxng and c.XMLTAG and not c.XMLTAG in done:
                        if issubclass(c, AbstractTokenAnnotation) or c is Correction:
                            extraelements.append( E.zeroOrMore( E.ref(name=c.XMLTAG) ) )
                            done[c.XMLTAG] = True
        
        return super(Word,cls).relaxng(includechildren, extraattribs , extraelements)




class Feature(AbstractElement):
    XMLTAG = 'feat'
    XMLATTRIB = None
    SUBSET = None
    
    def __init__(self,**kwargs):
        if self.SUBSET:
            self.subset = self.SUBSET
        elif 'subset' in kwargs: 
            self.subset = kwargs['subset']
        else:
            raise Exception("No subset specified!")
        if 'cls' in kwargs:
            self.cls = kwargs['cls']
        elif 'class' in kwargs:
            self.cls = kwargs['class']
        else:
            raise Exception("No class specified!")            
        
    def xml(self):
        global NSFOLIA
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
        attribs = {}
        if self.subset != self.SUBSET:
            attribs['{' + NSFOLIA + '}subset'] = self.subset 
        attribs['{' + NSFOLIA + '}class'] =  self.cls
        return E._makeelement('{' + NSFOLIA + '}' + self.XMLTAG, **attribs)        
    
    @classmethod
    def relaxns(cls, includechildren=True, extraattribs = None, extraelements=None):
        global NSFOLIA
        #TODO: add XMLATTRIB
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.Element(E.attribute(name='subset'), E.attribute(name='class'), E.empty(),name=cls.XMLTAG), name=cls.XMLTAG,ns=NSFOLIA)

class AbstractAnnotation(AbstractElement):
    def feat(self,subset):
        for f in self:
            if isinstance(f, Feature) and f.subset == subset:
                return f.cls

class AbstractTokenAnnotation(AbstractAnnotation, AllowGenerateID): 
    ALLOWDUPLICATES = False #Allow duplicates within the same set? 

    def append(self, child):
        super(AbstractTokenAnnotation,self).append(child)
        self._setmaxid(child)

class AbstractExtendedTokenAnnotation(AbstractTokenAnnotation): 
    pass
    
class AbstractSpanAnnotation(AbstractAnnotation, AllowGenerateID): 
    def xml(self, attribs = None,elements = None, skipchildren = False):  
        global NSFOLIA
        if not attribs: attribs = {}
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        e = super(AbstractSpanAnnotation,self).xml(attribs, elements, True)
        for child in self:
            if isinstance(child, Word):
                #Include REFERENCES to word items instead of word items themselves
                attribs['{' + NSFOLIA + '}id'] = child.id                    
                if child.text:
                    attribs['{' + NSFOLIA + '}t'] = child.text()
                e.append( E.wref(**attribs) )
            else:
                e.append( child.xml() )
        return e    


    def append(self, child):
        if isinstance(child, Word) and WordReference in self.ACCEPTED_DATA:
            #Accept Word instances instead of WordReference, references will be automagically used upon serialisation
            self.data.append(child)
            child.parent = self
            self._setmaxid(child)
        else:
            return super(AbstractSpanAnnotation,self).append(child)    
            

class AbstractAnnotationLayer(AbstractElement):
    OPTIONAL_ATTRIBS = (Attrib.CLASS,)
    def __init__(self, doc, *args, **kwargs):
        if 'set' in kwargs:
            self.set = kwargs['set']
            del kwargs['set']
        super(AbstractAnnotationLayer,self).__init__(doc, *args, **kwargs)

class ErrorDetection(AbstractExtendedTokenAnnotation):
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.ERRORDETECTION
    XMLTAG = 'errordetection'
    ALLOWDUPLICATES = True #Allow duplicates within the same set 
    
    def __init__(self,  doc, *args, **kwargs):
        if 'error' in kwargs:            
            if (kwargs['error'] is False or kwargs['error'].lower() == 'no' or kwargs['error'].lower() == 'false'):
                self.error = False
            else:
                self.error = True
            del kwargs['error']
        else:
            self.error = True        
        super(ErrorDetection,self).__init__(doc, *args, **kwargs)


    def xml(self, attribs = None,elements = None, skipchildren = False):   
        if not attribs: attribs = {}
        if self.error:
            attribs['error'] = 'yes'
        else:
            attribs['error'] = 'no'
        return super(ErrorDetection,self).xml(attribs,elements, False)  
    
            
                        
class Suggestion(AbstractElement):
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.SUGGESTION
    ACCEPTED_DATA = (AbstractTokenAnnotation, Word)
    ALLOWTEXT = True
    XMLTAG = 'suggestion'
    
    
    
    
            
class Correction(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.CORRECTION
    XMLTAG = 'correction'

    def __init__(self,  doc, *args, **kwargs):
        if not (('new' in kwargs and 'original' in kwargs) or (('suggestions' in kwargs or 'suggestion' in kwargs))):
             raise Exception("Excepted either new= and original= arguments, or suggestions= and current= arguments.")
                         
        self.suggestions = []        
        if 'suggestion' in kwargs:             
            kwargs['suggestions'] = [ kwargs['suggestion'] ]
            del kwargs['suggestion']
            
        if 'suggestions' in kwargs: 
            for suggestion in kwargs['suggestions']:
                self.addsuggestion(suggestion)          
            del kwargs['suggestions']            
                    
        if 'current' in kwargs:            
            self.setcurrent(kwargs['current'])
            del kwargs['current']
        else:
            self.current = []
        
        if 'new' in kwargs:
            self.setnew(kwargs['new'])
            del kwargs['new'] 
        else:
            self.new = []            
            
        if 'original' in kwargs:
            self.setoriginal(kwargs['original'])
            del kwargs['original'] 
        else:
            self.original = []
            
            
        if self.new and self.original and self.new[0].__class__ != self.original[0].__class__:
            raise Exception("New and Original are of different types!")             
        super(Correction,self).__init__(doc, *args, **kwargs)
        

    def setnew(self, e):
        if isinstance(e, AbstractElement) or isinstance(e, unicode):
            self.new = [ e ]
        elif isinstance(e, TextContent):
            self.new = [ e.value ]                
        elif isinstance(e, str):
            self.new = [ unicode(e,'utf-8') ]
        elif isinstance(e, list) or isinstance(e, tuple):                
            self.new =e
        else:
            raise Exception("Invalid type for new: " + repr(e))
        for x in self.new:
            if isinstance(x, AbstractElement):
                x.parent = self              

    def setcurrent(self, e):
        if isinstance(e, AbstractElement) or isinstance(e, unicode):
            self.current = [ e ]
        elif isinstance(e, TextContent):
            self.current = [ e.value ]                
        elif isinstance(e, str):
            self.current = [ unicode(e,'utf-8') ]
        elif isinstance(e, list) or isinstance(e, tuple):                
            self.current = e
        else:
            raise Exception("Invalid type for current: " + repr(e))
        for x in self.current:
            if isinstance(x, AbstractElement):
                x.parent = self  


    def setoriginal(self, e):            
        if isinstance(e, AbstractElement) or isinstance(e, unicode):
            self.original = [ e ]
        elif isinstance(e, TextContent):
            self.original = [ e.value ]                
        elif isinstance(e, str):
            self.original = [ unicode(e,'utf-8') ]
        elif isinstance(e, list) or isinstance(e, tuple):                
            self.original = e
        else:
            raise Exception("Invalid type for original: " + repr(e))
        for x in self.original:
            if isinstance(x, AbstractElement):
                x.parent = self            
        
    def addsuggestion(self, suggestion, **kwargs):
        if isinstance(suggestion, TextContent) or isinstance(suggestion, AbstractTokenAnnotation):    
            child = suggestion
            suggestion = Suggestion(child, **kwargs)
            child.parent = suggestion
        elif isinstance(suggestion, str) or isinstance(suggestion, unicode):    
            suggestion = Suggestion(TextContent(self.doc, value=suggestion, corrected=True, **kwargs))
        elif not isinstance(suggestion, Suggestion):
            raise Exception("Suggestion has to be of type Suggestion, got " + str(type(suggestion)))                
        self.suggestions.append(suggestion)
        suggestion.parent = self      
        #print "DEBUG: ",  suggestion, type(suggestion), len(suggestion)
        for x in suggestion:
            #print 'DEBUG:    ', x, type(x), len(x), type(x.parent)            
            x.parent = suggestion
            
    def __unicode__(self):
        s = ""
        if self.current:
            for e in self.current:
                try:
                    if isinstance(e, Word):
                        s += unicode(e)
                        if e.space:
                            s += ' '
                    else:
                        s += unicode(e)
                except:
                    continue
        elif self.new:
            for s in self.new:
                try:
                    if isinstance(e, Word):
                        s += unicode(e)
                        if e.space:
                            s += ' '
                    else:
                        s += unicode(e)
                except:
                    continue
        return s
        
    
        

    def xml(self, attribs = None, elements = None, skipchildren = False):
        if not attribs: attribs = {}
        if not elements: elements = []
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})            
        if self.new or self.original:
            elements.append( E.new( *[ x.xml() if isinstance(x, AbstractElement) else E.t(x) for x in self.new ] ) ) 
            elements.append( E.original( *[ x.xml() if isinstance(x, AbstractElement) else E.t(x) for x in self.original ] ) )    
        if self.suggestions:
            for suggestion in self.suggestions:
                elements.append( suggestion.xml() )
        if self.current:
            elements.append( E.current( *[ x.xml() for x in self.current ] ) ) 
        return super(Correction,self).xml(attribs,elements, True)  

    def select(self, cls, set=None, recursive=True,  ignorelist=[], node=None):
        """Select on Correction only descends in either "NEW" or "CURRENT" branch"""
        l = []
        if not node:
            node = self  
        
        if self.new:
            source = self.new
        elif self.current:
            source = self.current
        else:
            return l #empty list
            
        for e in source:
            ignore = False                            
            for c in ignorelist:
                if c == e.__class__ or issubclass(e.__class__,c):
                    ignore = True
                    break
            if ignore: 
                continue
        
            if isinstance(e, cls):                
                if not set is None:
                    try:
                        if e.set != set:
                            continue
                    except:
                        continue
                l.append(e)
            if recursive and isinstance(e, AbstractElement):
                for e2 in e.select(cls, set, recursive, ignorelist, e):
                    if not set is None:
                        try:
                            if e2.set != set:
                                continue
                        except:
                            continue
                    l.append(e2)                    
        return l
        

    @classmethod
    def parsexml(Class, node, doc):
        assert issubclass(Class, AbstractElement)
        global NSFOLIA
        nslen = len(NSFOLIA) + 2
        args = []
        kwargs = {}
        kwargs['original'] = []
        kwargs['new'] = []
        kwargs['current'] = []
        kwargs['suggestions'] = []
        for subnode in node:
             if subnode.tag == '{' + NSFOLIA + '}original':                        
                if len(subnode) == 1:
                    if subnode[0].tag == '{' + NSFOLIA + '}t':
                        kwargs['original'] = [ subnode[0].text ]
                    else:
                        kwargs['original'] = [ doc.parsexml(subnode[0]) ]
                else:
                    kwargs['original'] = [ doc.parsexml(x) for x in subnode ] 
             elif subnode.tag == '{' + NSFOLIA + '}new':
                if len(subnode) == 1:
                    if subnode[0].tag == '{' + NSFOLIA + '}t':
                        kwargs['new'] = [ subnode[0].text ]
                    else:
                        kwargs['new'] = [ ( doc.parsexml(subnode[0]) ) ]
                else:
                    kwargs['new'] = [ doc.parsexml(x) for x in subnode ] 
             elif subnode.tag == '{' + NSFOLIA + '}suggestion':
                 if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Processing subnode suggestion"
                 kwargs['suggestions'].append( doc.parsexml(subnode) )
             elif subnode.tag == '{' + NSFOLIA + '}current':
                if len(subnode) == 1:
                    if subnode[0].tag == '{' + NSFOLIA + '}t':
                        kwargs['current'] = [ subnode[0].text ]
                    else:
                        kwargs['current'] = [ ( doc.parsexml(subnode[0]) ) ]
                else:
                    kwargs['current'] = [ doc.parsexml(x) for x in subnode ] 
             elif subnode.tag[:nslen] == '{' + NSFOLIA + '}':
                if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Processing subnode " + subnode.tag[nslen:]
                args.append( doc.parsexml(subnode) )
             elif doc.debug >= 1:
                print >>stderr, "[PyNLPl FoLiA DEBUG] Ignoring subnode outside of FoLiA namespace: " + subnode.tag
                    
        id = None
        for key, value in node.attrib.items():
            if key == '{http://www.w3.org/XML/1998/namespace}id':
                id = value
                key = 'id'
            elif key[:nslen] == '{' + NSFOLIA + '}':
                key = key[nslen:]
            kwargs[key] = value                                    
        
        if not kwargs['current']:
            del kwargs['current']
        if not kwargs['suggestions']:
            del kwargs['suggestions']
    
    
                                
        if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found " + node.tag[nslen:]
        instance = Class(doc, *args, **kwargs)
        if id:
            doc.index[value] = instance
        return instance   
            
class Alternative(AbstractElement, AllowTokenAnnotation, AllowGenerateID):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (AbstractTokenAnnotation, Correction)
    ANNOTATIONTYPE = AnnotationType.ALTERNATIVE
    XMLTAG = 'alt'

class AlternativeLayers(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (AbstractAnnotationLayer,)    
    XMLTAG = 'altlayers'
    

class WordReference(AbstractElement):
    """Only used when word reference can not be resolved, if they can, Word objects will be used"""
    REQUIRED_ATTRIBS = (Attrib.ID,)
    XMLTAG = 'wref'
    ANNOTATIONTYPE = AnnotationType.TOKEN
    
    @classmethod
    def parsexml(Class, node, doc):
        global NSFOLIA
        assert Class is WordReference or issubclass(Class, WordReference)
        #special handling for word references
        id = node.attrib['id']
        if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found word reference"
        try:
            return doc[id]
        except KeyError:
            if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] ...Unresolvable!"
            return WordReference(id=id)    
            
class AlignReference(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    XMLTAG = 'aref'    
    pass #TODO: IMPLEMENT
        

        
class SyntacticUnit(AbstractSpanAnnotation):
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.SYNTAX
    XMLTAG = 'su'
    
SyntacticUnit.ACCEPTED_DATA = (SyntacticUnit,WordReference)

class Chunk(AbstractSpanAnnotation):
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ACCEPTED_DATA = (WordReference,)
    ANNOTATIONTYPE = AnnotationType.CHUNKING
    XMLTAG = 'chunk'

class Entity(AbstractSpanAnnotation):
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ACCEPTED_DATA = (WordReference,)
    ANNOTATIONTYPE = AnnotationType.ENTITY
    XMLTAG = 'entity'
    
class SyntaxLayer(AbstractAnnotationLayer):
    ACCEPTED_DATA = (SyntacticUnit,)
    XMLTAG = 'syntax'

class ChunkingLayer(AbstractAnnotationLayer):
    ACCEPTED_DATA = (Chunk,)
    XMLTAG = 'chunking'

class EntitiesLayer(AbstractAnnotationLayer):
    ACCEPTED_DATA = (Entity,)
    XMLTAG = 'entities'

    
class PosAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.POS
    ACCEPTED_DATA = (Feature,)
    XMLTAG = 'pos'

class LemmaAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.LEMMA
    ACCEPTED_DATA = (Feature,)
    XMLTAG = 'lemma'
    
class PhonAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.PHON
    ACCEPTED_DATA = (Feature,)
    XMLTAG = 'phon'


class DomainAnnotation(AbstractExtendedTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.DOMAIN
    ACCEPTED_DATA = (Feature,)
    XMLTAG = 'domain'

class SynsetFeature(Feature):
    XMLATTRIB = 'synset' #allow feature as attribute
    XMLTAG = 'synset'
    ANNOTATIONTYPE = AnnotationType.SENSE
    SUBSET = 'synset' #associated subset
    

class SenseAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.SENSE
    ACCEPTED_DATA = (Feature,SynsetFeature)
    XMLTAG = 'sense'
    


class Quote(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = ()    
    XMLTAG = 'quote'
    ALLOWTEXT = True
    #ACCEPTED DATA defined later below
    
    def __init__(self,  doc, *args, **kwargs):
        super(Quote,self).__init__(doc, *args, **kwargs)

    def __unicode__(self):
        s = u""
        for e in self.data:
            if isinstance(e, Word):
                s += unicode(e)
                if e.space:
                    s += ' '
            elif isinstance(e, Sentence):
                s += unicode(e)
        if not s and self.text:
            return self.text            
        return s

    def resolveword(self, id):
        for child in self:
            r =  child.resolveword(id)            
            if r:
                return r
        return None        
        
        
class Sentence(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Word, Quote, AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Correction)
    ALLOWTEXT = True
    XMLTAG = 's'
    
    def __init__(self,  doc, *args, **kwargs):
        super(Sentence,self).__init__(doc, *args, **kwargs)
     
                
    def resolveword(self, id):
        for child in self:
            r =  child.resolveword(id)            
            if r:
                return r
        return None
        
    def __unicode__(self):
        if self.textdata:
            return self.text()
        else:
            o = ""
            for e in self.words():
                o += unicode(e)
                if e.space == ' ' or e.space is True:
                    o += ' '
                elif e.space:
                    o += e.space                    
            return o


    def paragraph(self):
        #return the sentence this sentence is a part of (None otherwise)
        e = self;
        while e.parent: 
            if isinstance(e, Paragraph):
                return e
            e = e.parent  
        return None
 
    def division(self):
        #return the division this sentence is a part of (None otherwise)
        e = self;
        while e.parent: 
            if isinstance(e, Division):
                return e
            e = e.parent  
        return None
        
        
        
    def splitword(self, originalword, *newwords, **kwargs):
        if isinstance(originalword, str) or isinstance(originalword, unicode):
            originalword = self.doc[originalword]            
        if not originalword in self or not isinstance(originalword, Word):
            raise Exception("Original not found or not instance of Word!")
        else:
            kwargs['original'] = originalword
            
        if not all( [ isinstance(w, Word) for w in newwords ] ):
            raise Exception("New words must be Word instances!")

        if not 'id' in kwargs and not 'generate_id_in' in kwargs:
            kwargs['generate_id_in'] = self

        
        if 'suggest' in kwargs and kwargs['suggest']:            
            kwargs['suggestion'] = Suggestion(self.doc, *newwords)
            kwargs['current'] = originalword
            del kwargs['suggest']
        else:            
            if not 'new' in kwargs:
                kwargs['new'] = newwords
        insertindex = self.data.index(originalword)        
        c = Correction(self.doc, **kwargs)
        originalword.parent = c
        self.data[insertindex] = c 
        c.parent = self
        return c 
        
        
    def mergewords(self, newword,  *originalwords,**kwargs):
        for w in originalwords:            
            if not isinstance(w, Word):
                raise Exception("Original word is not a Word instance: " + str(type(w)))    
                    
        
        if not isinstance(newword, Word):        
            raise Exception("New word must be a Word instance")

        if not 'id' in kwargs and not 'generate_id_in' in kwargs:
            kwargs['generate_id_in'] = self
        
        if 'suggest' in kwargs and kwargs['suggest']:            
            kwargs['suggestion'] = Suggestion(self.doc, newword)
            kwargs['current'] = originalwords
            del kwargs['suggest']
        else:            
            kwargs['original'] = originalwords                
            if not 'new' in kwargs:
                kwargs['new'] = newword    
        insertindex = self.data.index(originalwords[0])        
        c = Correction(self.doc, **kwargs)
        self.data.insert( insertindex, c )
        c.parent = self
        for w in originalwords:            
            self.remove(w)        
        return c 
        
        
    def deleteword(self, word, **kwargs):
        if isinstance(word, str) or isinstance(word, unicode):
            word = self.doc[word]            
        if not isinstance(word, Word):
            raise Exception("Original not instance of Word!")
        
            

        if 'suggest' in kwargs and kwargs['suggest']:            
            kwargs['current'] = word
            kwargs['suggestions'] = []
            del kwargs['suggest']
        else:            
            kwargs['original'] = word
            kwargs['new'] = []
            
        if not 'id' in kwargs and not 'generate_id_in' in kwargs:
            kwargs['generate_id_in'] = self
            
        insertindex = self.data.index(word)        
        c = Correction(self.doc, **kwargs)
        self.data[insertindex] = c
        word.parent = c
        c.parent = self
        return c 
        
    def insertword(self, newword, prevword, **kwargs):
        if isinstance(prevword, str) or isinstance(prevword, unicode):
            prevword = self.doc[prevword]            
        if not prevword in self or not isinstance(prevword, Word):
            raise Exception("Previous word not found or not instance of Word!")
        if not isinstance(newword, Word):
            raise Exception("New word no instance of Word!")
        
        insertindex = self.data.index(prevword)
    
        
        if 'suggest' in kwargs and kwargs['suggest']:            
            kwargs['suggestion'] = newword
            del kwargs['suggest']
        else:
            kwargs['original'] = []
            kwargs['new'] = newword
        
        if not 'id' in kwargs and not 'generate_id_in' in kwargs:
            kwargs['generate_id_in'] = self
        c = Correction(self.doc, **kwargs)
        self.data.insert( insertindex, c )
        c.parent = self
        return c 

        
    def words(self):
        return self.select(Word)           

Quote.ACCEPTED_DATA = (Word, Sentence, Quote)        

class Paragraph(AbstractStructureElement):    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Sentence, AbstractExtendedTokenAnnotation, Correction)
    XMLTAG = 'p'
    ALLOWTEXT = True
    
     
        
    def __unicode__(self):
        p = u" ".join( ( unicode(x) for x in self.data if isinstance(x, Sentence) ) )
        if not p and self.text:
            return self.text            
        return p

    def __str__(self):    
        return unicode(self).encode('utf-8')        
    
    def sentences(self):
        return self.select(Sentence)
        
    def words(self):
        return self.select(Word)    
                              
                
class Head(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Sentence,)
    XMLTAG = 'head'          
    
    def __init__(self, doc, *args, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']
            del kwargs['text']
        else:
            self.text = None 
        super(Head, self).__init__(doc, *args, **kwargs)    
        
    def __unicode__(self):
        p = u" ".join( ( unicode(x) for x in self.data if isinstance(x, Sentence) ) )
        if not p and self.text:
            return self.text            
        return p




class Query(object):
    """An XPath query on FoLiA"""
    def __init__(self, node, expression):
        self.node = node
        self.expression = expression
        
    def __iter__(self):
        raise NotImplementedError
        





class Document(object):
    
    IDSEPARATOR = '.'
    
    def __init__(self, *args, **kwargs):
        self.data = [] #will hold all texts (usually only one)
        
        self.annotationdefaults = {}
        self.annotations = [] #Ordered list of incorporated annotations ['token','pos', etc..]
        self.index = {} #all IDs go here
        
        self.metadata = [] #will point to XML Element holding IMDI or CMDI metadata
        self.metadatatype = MetaDataType.NATIVE
        self.metadatafile = None #reference to external metadata file
    
        #The metadata fields FoLiA is directly aware of:
        self._title = self._date = self._publisher = self._license = self._language = None
    
    
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            self.debug = False
    
        if 'load' in kwargs:
            self.loadall = kwargs['load'] #Load all in memory
        else:
            self.loadall = True
    
        if 'id' in kwargs:
            self.id = kwargs['id']
        elif 'file' in kwargs:
            self.filename = kwargs['file']
            self.load(self.filename)              
        elif 'string' in kwargs:
            s = kwargs['string']
            if isinstance(s, unicode):
                s = s.encode('utf-8')
            self.tree = ElementTree.parse(StringIO(s))
            self.parsexml(self.tree.getroot())    
        elif 'tree' in kwargs:
            self.parsexml(kwargs['tree'])
        else:
            raise Exception("No ID, filename or tree specified")
                            
            
    def load(self, filename):
        self.tree = ElementTree.parse(filename)
        self.parsexml(self.tree.getroot())
            
    def xpath(self, query):
        for result in self.tree.xpath(query,namespaces={'f': 'http://ilk.uvt.nl/folia','folia': 'http://ilk.uvt.nl/folia' }):
            yield self.parsexml(result)
        
    def save(self, filename=None):
        if not filename:
            filename = self.filename
        if not filename:
            raise Exception("No filename specified")
        f = open(filename,'w')
        f.write(self.xmlstring())
        f.close()

    def setcmdi(self,filename):
        self.metadatatype = MetaDataType.CMDI
        self.metadatafile = filename
        self.metadata = []
        #TODO: Parse CMDI
        
        
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        for text in self.data:
            yield text   
        
    def __getitem__(self, key):
        try:
            if isinstance(key, int):
                return self.data[key]
            else:
                return self.index[key]
        except KeyError:
            raise
            
    def append(self,text):
        assert isinstance(text, Text)
        self.data.append(text)


    def xmldeclarations(self):
        l = []
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        
        for annotationtype in self.annotations:
            label = None
            #Find the 'label' for the declarations dynamically (aka: AnnotationType --> String)
            for key, value in vars(AnnotationType).items():
                if value == annotationtype:
                    label = key
                    break
            #gather attribs
            attribs = {}
            for key, value in self.annotationdefaults[annotationtype].items():                
                if key == 'annotatortype':
                    if value == AnnotatorType.MANUAL:
                        attribs['{' + NSFOLIA + '}' + key] = 'manual'
                    elif value == AnnotatorType.AUTO:
                        attribs['{' + NSFOLIA + '}' + key] = 'auto'
                elif value:
                    attribs['{' + NSFOLIA + '}' + key] = value
            if label:
                l.append( E._makeelement('{' + NSFOLIA + '}' + label.lower() + '-annotation', **attribs) )
            else:
                raise Exception("Invalid annotation type")            
        return l
        
    def xml(self):    
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace", 'xlink':"http://www.w3.org/1999/xlink"})
        attribs = {}
        attribs['{http://www.w3.org/XML/1998/namespace}id'] = self.id
        
        metadataattribs = {}
        if self.metadatatype == MetaDataType.NATIVE:
            metadataattribs['{' + NSFOLIA + '}type'] = 'native'
        elif self.metadatatype == MetaDataType.IMDI:
            metadataattribs['{' + NSFOLIA + '}type'] = 'imdi'
            if self.metadatafile:
                metadataattribs['{' + NSFOLIA + '}src'] = self.metadatafile
        elif self.metadatatype == MetaDataType.CMDI:
            metadataattribs['{' + NSFOLIA + '}type'] = 'cmdi'
            metadataattribs['{' + NSFOLIA + '}src'] = self.metadatafile
            
        e = E.FoLiA(
            E.metadata(
                E.annotations(
                    *self.xmldeclarations()
                ),
                *self.xmlmetadata(),
                **metadataattribs
            )            
        , **attribs)
        for text in self.data:
            e.append(text.xml())
        return e
    
    def xmlmetadata(self):
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        if self.metadatatype == MetaDataType.NATIVE:
            e = []
            if self.title(): e.append(E.meta(self.title(),id='title') )
            if self.date(): e.append(E.meta(self.date(),id='date') )
            if self.language(): e.append(E.meta(self.language(),id='language') )
            if self.license(): e.append(E.meta(self.license(),id='license') )    
            if self.publisher(): e.append(E.meta(self.publisher(),id='publisher') )
            return e
        elif self.metadatatype == MetaDataType.IMDI:
            if self.metadatafile:
                return [] #external
            else:
                return [self.metadata] #inline
        elif self.metadatatype == MetaDataType.CMDI: #CMDI, by definition external
            return []

            
            
     
    def parsexmldeclarations(self, node):
        if self.debug >= 1: 
            print >>stderr, "[PyNLPl FoLiA DEBUG] Processing Annotation Declarations"
        for subnode in node:
            if subnode.tag[:25] == '{' + NSFOLIA + '}' and subnode.tag[-11:] == '-annotation':
                prefix = subnode.tag[25:][:-11]
                type = None
                if prefix.upper() in vars(AnnotationType):
                    type = vars(AnnotationType)[prefix.upper()]
                else:
                    raise Exception("Unknown declaration: " + subnode.tag)
                    
                self.annotations.append(type)
                
                defaults = {}
                if 'set' in subnode.attrib:
                    defaults['set'] = subnode.attrib['set']
                if 'annotator' in subnode.attrib:
                    defaults['annotator'] = subnode.attrib['annotator']
                if 'annotatortype' in subnode.attrib:
                    if subnode.attrib['annotatortype'] == 'auto':
                        defaults['annotatortype'] = AnnotatorType.AUTO
                    else:
                        defaults['annotatortype'] = AnnotatorType.MANUAL                        
                self.annotationdefaults[type] = defaults
                if self.debug >= 1: 
                    print >>stderr, "[PyNLPl FoLiA DEBUG] Found declared annotation " + subnode.tag + ". Defaults: " + repr(defaults)

    def setimdi(self, node):
        #TODO: node or filename
        ns = {'imdi': 'http://www.mpi.nl/IMDI/Schema/IMDI'}
        self.metadatatype = MetaDataType.IMDI
        self.metadata = node
        n = node.xpath('imdi:Session/imdi:Title', namespaces=ns)
        if n and n[0].text: self._title = n[0].text
        n = node.xpath('imdi:Session/imdi:Date', namespaces=ns)
        if n and n[0].text: self._date = n[0].text
        n = node.xpath('//imdi:Source/imdi:Access/imdi:Publisher', namespaces=ns)
        if n and n[0].text: self._publisher = n[0].text        
        n = node.xpath('//imdi:Source/imdi:Access/imdi:Availability', namespaces=ns)
        if n and n[0].text: self._license = n[0].text            
        n = node.xpath('//imdi:Languages/imdi:Language/imdi:ID', namespaces=ns)
        if n and n[0].text: self._language = n[0].text            
        
    def declare(self, annotationtype, **kwargs):
        if not annotationtype in self.annotations:
            self.annotations.append(annotationtype)
        self.annotationdefaults[annotationtype] = kwargs
    
    def declared(self, annotationtype):
        return annotationtype in self.annotations
        
        
    def defaultset(self, annotationtype):
        try:
            return self.annotationdefaults[annotationtype]['set']
        except KeyError:
            raise NoDefaultError
        
    
    def defaultannotator(self, annotationtype):
        try:
            return self.annotationdefaults[annotationtype]['annotator']        
        except KeyError:
            raise NoDefaultError
            
    def defaultannotatortype(self, annotationtype):
        try:
            return self.annotationdefaults[annotationtype]['annotatortype']        
        except KeyError:
            raise NoDefaultError
            

            
        
    def title(self, value=None):
        if not (value is None): self._title = value
        return self._title
        
    def date(self, value=None):
        if not (value is None): self._date = value
        return self._date        
       
    def publisher(self, value=None):
        if not (value is None): self._publisher = value
        return self._publisher

    def license(self, value=None):
        if not (value is None): self._license = value
        return self._license                       
        
    def language(self, value=None):
        if not (value is None): self._language = value
        return self._language        
           

    def parsexml(self, node):
        """Main XML parser, will invoke class-specific XML parsers"""
        global XML2CLASS, NSFOLIA, NSDCOI
        nslen = len(NSFOLIA) + 2
        nslendcoi = len(NSDCOI) + 2
        
        if isinstance(node,ElementTree._ElementTree):        
            node = node.getroot()
        elif not isinstance(node,ElementTree._Element):
            node = ElementTree.parse(StringIO(node)).getroot()         
        if node.tag == '{' + NSFOLIA + '}FoLiA':
            if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found FoLiA document"
            try:
                self.id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
            except KeyError:
                raise Exception("FoLiA Document has no ID!")
            for subnode in node:
                if subnode.tag == '{' + NSFOLIA + '}metadata':
                    if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found Metadata"
                    for subsubnode in subnode:
                        if subsubnode.tag == '{http://www.mpi.nl/IMDI/Schema/IMDI}METATRANSCRIPT':
                            self.metadatatype = MetaDataType.IMDI
                            self.setimdi(subsubnode)
                        if subsubnode.tag == '{' + NSFOLIA + '}annotations':
                            self.parsexmldeclarations(subsubnode)
                elif subnode.tag == '{' + NSFOLIA + '}text' and self.loadall:
                    if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found Text"
                    self.data.append( self.parsexml(subnode) )
        elif node.tag == '{' + NSDCOI + '}DCOI':
            if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found DCOI document"
            try:
                self.id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
            except KeyError:
                raise Exception("D-Coi Document has no ID!")
            for subnode in node:
                if subnode.tag == '{http://www.mpi.nl/IMDI/Schema/IMDI}METATRANSCRIPT':
                    self.metadatatype = MetaDataType.IMDI
                    self.setimdi(subnode)
                elif subnode.tag == '{' + NSDCOI + '}text':
                    if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found Text"
                    self.data.append( self.parsexml(subnode) )
        elif node.tag[:nslen] == '{' + NSFOLIA + '}' and node.tag[nslen:] in XML2CLASS:
            #generic handling (FoLiA)
            Class = XML2CLASS[node.tag[nslen:]]                
            return Class.parsexml(node,self)
        elif node.tag[:nslendcoi] == '{' + NSDCOI + '}':
            #generic handling (D-Coi)
            if node.tag[nslendcoi:] in XML2CLASS:
                Class = XML2CLASS[node.tag[nslendcoi:]]                
                return Class.parsexml(node,self)     
            elif node.tag[nslendcoi:][0:3] == 'div': #support for div0, div1, etc:
                Class = Division
                return Class.parsexml(node,self)     
            else:       
                raise Exception("Unknown DCOI XML tag: " + node.tag)
        else:
            raise Exception("Unknown FoLiA XML tag: " + node.tag)
        
        
    def paragraphs(self, index = None):
        if index is None:
            return sum([ t.select(Paragraph) for t in self.data ],[])
        else:
            return sum([ t.select(Paragraph) for t in self.data ],[])[index]
    
    def sentences(self, index = None):
        if index is None:
            return sum([ t.select(Sentence,None,True,[Quote]) for t in self.data ],[])
        else:
            return sum([ t.select(Sentence,None,True,[Quote]) for t in self.data ],[])[index]

        
    def words(self, index = None):
        if index is None:            
            return sum([ t.select(Word,None,True,[AbstractSpanAnnotation]) for t in self.data ],[])
        else:
            return sum([ t.select(Word,None,True,[AbstractSpanAnnotation]) for t in self.data ],[])[index]
            

    def text(self):
        s = ""
        for t in self.data:
            if s: s += "\n\n\n"
            s = t.text()            
                    
    def xmlstring(self):
        return ElementTree.tostring(self.xml(), xml_declaration=True, pretty_print=True, encoding='utf-8')

    def __unicode__(self):
        s = u""
        for c in self.data:
            if s: s += "\n\n"
            try:
                s += unicode(c)
            except:
                continue
        return s
        
    def __str__(self):    
        return unicode(self).encode('utf-8')
    
class Gap(AbstractElement):    
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.N,)
    XMLTAG = 'gap'
    
    def __init__(self, doc, *args, **kwargs):
        if 'head' in kwargs:
            if not isinstance(kwargs['head'], Head):
                raise ValueError("Head must be of type Head")        
            self.head = kwargs['head']
            del kwargs['head']
        else:
            self.head = None
        if 'content' in kwargs:        
            self.content = kwargs['content']
            del kwargs['content']
        elif 'description' in kwargs:        
            self.description = kwargs['description']
            del kwargs['description']
        super(Gap,self).__init__(doc, *args, **kwargs)
        
    def __iter__(self):
        pass
        
    def _len__(self):
        return 0

        
   


        


            

    
class ListItem(AbstractStructureElement):
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    #ACCEPTED_DATA = (List, Sentence) #Defined below
    XMLTAG = 'listitem'
    
    def __init__(self, doc, *args, **kwargs):
        self.daWta = []
        super( ListItem, self).__init__(doc, *args, **kwargs)
    
class List(AbstractStructureElement):    
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    ACCEPTED_DATA = (ListItem,)
    XMLTAG = 'list'
    
    def __init__(self, doc, *args, **kwargs):
        self.data = []
        super( List, self).__init__(doc, *args, **kwargs)
        

ListItem.ACCEPTED_DATA = (List, Sentence)


class Figure(AbstractStructureElement):    
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    ACCEPTED_DATA = (Sentence,)
    XMLTAG = 'figure'
    
    def __init__(self, doc, *args, **kwargs):
        if 'url' in kwargs:
            self.url = kwargs['url']
            del kwargs['url']
        else:
            self.url = None 
        super(Figure, self).__init__(doc, *args, **kwargs)
        

class Division(AbstractStructureElement):    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.N)
    XMLTAG = 'div'
    ANNOTATIONTYPE = AnnotationType.DIVISION

    def __init__(self, doc, *args, **kwargs):
        if 'head' in kwargs:
            if not isinstance(kwargs['head'], Head):
                raise ValueError("Head must be of type Head")        
            head = kwargs['head']
            del kwargs['head']
        else:
            head = None
        super(Division, self).__init__(doc, *args, **kwargs)
        if head:
            self.append(head)
        
    def append(self, element):        
        if isinstance(element, Head):
            if self.data and isinstance(self.data[0], Head): #There can be only one, replace:
                self.data[0] = element
            else:
                self.data.insert(0, element)
        
            element.parent = self
        else:
            super(Division,self).append(element)
            
    def head(self):
        if self.data and isinstance(self.data[0], Head):
            return self.data[0]
        else:
            raise NoSuchAnnotation()
            
    def paragraphs(self):            
        return self.select(Paragraph)
    
    def sentences(self):
        return self.select(Sentence)
        
    def words(self):
        return self.select(Word)     
        

    @classmethod        
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        global NSFOLIA
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        if not extraelements:
            extraelements = []
        extraelements.append(E.optional( E.ref(name='head') ))
        return super(Division,cls).relaxng(includechildren, extraattribs , extraelements)

Division.ACCEPTED_DATA = (Division, Paragraph, Sentence, List, Figure, AbstractExtendedTokenAnnotation)

class Text(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Gap, Division, Paragraph, Sentence, List, Figure, AbstractExtendedTokenAnnotation)
    XMLTAG = 'text' 
        
    def paragraphs(self):            
        return self.select(Paragraph)
    
    def sentences(self):
        return self.select(Sentence)
        
    def words(self):
        return self.select(Word)        

    def __unicode__(self):
        try:
            return self.correctedtext()
        except:        
            #descend into children
            s = ""
            for e in self:
                try:               
                    es = unicode(e)
                    if es:                    
                        s += es + "\n\n"
                except:
                    continue
            if s.strip():
                return s.strip()
            else:                
                return self.uncorrectedtext()
        

class Corpus:
    def __init__(self,corpusdir, extension = 'xml', restrict_to_collection = "", conditionf=lambda x: True, ignoreerrors=False):
        self.corpusdir = corpusdir
        self.extension = extension
        self.restrict_to_collection = restrict_to_collection
        self.conditionf = conditionf
        self.ignoreerrors = ignoreerrors

    def __iter__(self):
        if not self.restrict_to_collection:
            for f in glob.glob(self.corpusdir+"/*." + self.extension):
                if self.conditionf(f):
                    try:
                        yield Document(file=f)
                    except:
                        print >>sys.stderr, "Error, unable to parse " + f
                        if not self.ignoreerrors:
                            raise
        for d in glob.glob(self.corpusdir+"/*"):
            if (not self.restrict_to_collection or self.restrict_to_collection == os.path.basename(d)) and (os.path.isdir(d)):
                for f in glob.glob(d+ "/*." + self.extension):
                    if self.conditionf(f):
                        try:
                            yield Document(file=f)
                        except:
                            print >>sys.stderr, "Error, unable to parse " + f
                            if not self.ignoreerrors:
                                raise



def relaxng_declarations():
    global NSFOLIA
    E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
    for key, value in vars(AnnotationType).items():
        if key[0] != '_':
            yield E.element( E.optional( E.attribute(name='set')) , E.optional(E.attribute(name='annotator')) , E.optional( E.attribute(name='annotatortype') )  , name=key.lower() + '-annotation')

            
def relaxng(filename=None):
    global NSFOLIA
    E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
    grammar = E.grammar( E.start ( E.element( #FoLiA
                E.attribute(name='id',ns="http://www.w3.org/XML/1998/namespace"),
                E.element( #metadata
                    E.element( E.zeroOrMore( E.choice( *relaxng_declarations() ) ) ,name='annotations'),
                    E.zeroOrMore(
                        E.element(E.attribute(name='id'), E.text(), name='meta'),
                    ),
                    #E.optional(
                    #    E.ref(name='METATRANSCRIPT')
                    #),
                    name='metadata',
                    #ns=NSFOLIA,
                ),
                E.oneOrMore(
                    E.ref(name='text'),
                ),
                name='FoLiA',
                ns = NSFOLIA
            ) ),            
            E.define(E.element(
              E.text(),
              name="t",
              ns=NSFOLIA) #,ns=NSFOLIA)
            ,name="t"),
            )  
             
    done = {}
    for c in globals().values():
        if 'relaxng' in dir(c):
            if c.relaxng and c.XMLTAG and not c.XMLTAG in done:
                done[c.XMLTAG] = True
                grammar.append( c.relaxng() )
    
    #for e in relaxng_imdi():
    #    grammar.append(e)
    if filename:
        f = open(filename,'w')
        f.write( ElementTree.tostring(relaxng(),pretty_print=True))
        f.close()

    return grammar




def validate(filename):
    try:
        doc = ElementTree.parse(filename)
    except:
        raise Exception("Not well-formed XML!")
    
    #See if there's inline IMDI and strip it off prior to validation (validator doesn't do IMDI)
    m = doc.xpath('//folia:metadata', namespaces={'f': 'http://ilk.uvt.nl/folia','folia': 'http://ilk.uvt.nl/folia' })
    if m:
        metadata = m[0]
        m = metadata.find('{http://www.mpi.nl/IMDI/Schema/IMDI}METATRANSCRIPT')
        if m is not None:
            metadata.remove(m)
    
    grammar = ElementTree.RelaxNG(relaxng())
    grammar.assertValid(doc) #will raise exceptions


XML2CLASS = {}
for c in vars().values():
    try:
        if c.XMLTAG:
            XML2CLASS[c.XMLTAG] = c
    except: 
        continue


