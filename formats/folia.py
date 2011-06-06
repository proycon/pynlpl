#---------------------------------------------------------------
# PyNLPl - FoLiA Format Module
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Module for reading, editing and writing FoLiA XML
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------



from lxml import etree as ElementTree
from lxml.builder import E, ElementMaker
from sys import stderr
from StringIO import StringIO
from copy import copy
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
                  
class TextCorrectionLevel:
    UNCORRECTED, INLINE, CORRECTED = range(3)                  
          
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

class NoDescription(Exception):
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
    
    
    
    if 'text' in kwargs:
        object.settext(kwargs['text'])
        del kwargs['text']
    if 'correctedtext' in kwargs:
        object.settext(kwargs['text'], TextCorrectionLevel.CORRECTED)
        del kwargs['correctedtext']
    if 'uncorrectedtext' in kwargs:
        object.settext(kwargs['text'], TextCorrectionLevel.UNCORRECTED)        
        del kwargs['uncorrectedtext']
        
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
            raise DuplicateAnnotationError("Duplicate ID not permitted: " + object.id)
        else:
            if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Adding to index: " + object.id
            doc.index[object.id] = object

    
    return kwargs
    
        




        
class AbstractElement(object):
    REQUIRED_ATTRIBS = () #List of required attributes (Members from the Attrib class)
    OPTIONAL_ATTRIBS = () #List of optional attributes (Members from the Attrib class)
    ACCEPTED_DATA = () #List of accepted data, classes inherited from AbstractElement
    ANNOTATIONTYPE = None #Annotation type (Member of AnnotationType class)
    XMLTAG = None #XML-tag associated with this element
    OCCURRENCES = 0 #Number of times this element may occur in its parent (0=unlimited, default=0)
    OCCURRENCESPERSET = 1 #Number of times this element may occur per set (0=unlimited, default=1)

    MINTEXTCORRECTIONLEVEL = TextCorrectionLevel.UNCORRECTED #Specifies the minimum text correction level allowed (only if allowed at all in ACCEPTED_DATA), this will be the default for any textcontent set
    TEXTDELIMITER = " " #Delimiter to use when dynamically gathering text from child elements
    PRINTABLE = True #Is this element printable (aka, can its text method be called?)
    
    
    def __init__(self, doc, *args, **kwargs):
        if not isinstance(doc, Document):
            raise Exception("Expected first parameter to be instance of Document, got " + str(type(doc)))
        self.doc = doc
        self.parent = None
        self.data = []        
            
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

    def description(self):
        for e in self:
            if isinstance(e, Description):
                return e.value
        raise NoDescription
        
    def text(self, corrected=None):
        """Get text associated with this element. If no desired correctionlevel is specified 
           the 'best' level will be selected automatically:
            - Will first grab the corrected textcontent explicitly associated with the element
            - If not found, it will descend into the children and build text dynamically
            - If that yields no text, it will resort to the original uncorrected text
            - If none is found, a NoSuchText exception is raised.
        """
        
        #TODO: Implement handling of INLINE corrected textcontent
        if not self.PRINTABLE:
            raise NoSuchText
            
        if not (corrected is None):
            if self.MINTEXTCORRECTIONLEVEL > corrected:
                raise NotImplementedError("No such text allowed for " + self.__class__.__name__) #on purpose        
            text = None
            for child in self:
                if isinstance(child, TextContent) and child.corrected == corrected:
                    text = child
            if text is None:
                raise NoSuchText
            else:
                return text.value  
        else:
            if self.hastext(TextCorrectionLevel.CORRECTED):
                return self.text(TextCorrectionLevel.CORRECTED)
            else:
                #try to get text dynamically from children
                s = ""
                for e in self:
                    try:                  
                        delimiter = e.overridetextdelimiter()
                        if delimiter is None:
                            delimiter = self.TEXTDELIMITER #default delimiter set by parent
                        s += unicode(e) + delimiter
                    except NoSuchText:
                        continue                
                        
                if s.strip():
                    return s.strip()
                elif self.MINTEXTCORRECTIONLEVEL <= TextCorrectionLevel.UNCORRECTED:
                    #Resort to original uncorrected text (if available)
                    return self.text(TextCorrectionLevel.UNCORRECTED)
                else:
                    #No text
                    raise NoSuchText
                      
    def originaltext(self):
        """Alias for uncorrectedtext"""
        return self.text(TextCorrectionLevel.UNCORRECTED)
        
    def overridetextdelimiter(self):
        """May return a customised text delimiter that overrides the default text delimiter set by the parent. Defaults to None (do not override)"""
        return None #do not override
        
    
    def __len__(self):
        return len(self.data)
        
    def __nonzero__(self):
        return True #any instance evaluates to True in boolean tests!! (important to distinguish from uninstantianted None values!)
        
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
        return self.text()
                                
    def __str__(self):        
        return unicode(self).encode('utf-8')

    def copy(self):
        """Make a deep copy"""
        kwargs = {}    
        if self.id:
            kwargs['id'] = id
        if self.set:
            kwargs['set'] = set
        raise NotImplementedError #TODO: IMPLEMENT
                            
        
    def hastext(self,corrected=None):
        """Does this element have text?"""
        if corrected is None:
            #regardless of correctionlevel:
            return (len(self.select(TextContent,None,False)) > 0)
        else:
            return (len([ x for x in self.select(TextContent,None,False) if x.corrected == corrected]) > 0)            
    
            
    def settext(self, text, corrected=None):
        if corrected is None:
            corrected = self.MINTEXTCORRECTIONLEVEL
        self.replace(TextContent, value=text, corrected=corrected) 

    @classmethod
    def addable(Class, parent, set=None, raiseexceptions=True):
        """Tests whether a new element of this class can be added to the parent. Returns a boolean or raises ValueError exceptions (unless set to ignore)!
        
         This will use OCCURRENCES, but may be overidden for more customised behaviour"""
        
        
        if not Class in parent.ACCEPTED_DATA:
            #Class is not in accepted data, but perhaps any of its ancestors is?
            found = False
            c = Class
            try:
                while c.__base__:
                    if c.__base__ in parent.ACCEPTED_DATA:
                        found = True
                        break
                    c = c.__base__
            except:
                pass 
            if not found:            
                if raiseexceptions: 
                    raise ValueError("Unable to add object of type " + Class.__name__ + " to " + parent.__class__.__name__ + ". Type not allowed as child.")
                else:
                    return False
   

                
        if Class.OCCURRENCES > 0:
            #check if the parent doesn't have too many already
            count = len(parent.select(Class,None,True,['Original','Suggestion','Alternative']))
            if count >= Class.OCCURRENCES:
                if raiseexceptions:
                    raise DuplicateAnnotationError("Unable to add another object of type " + child.__class__.__name__ + " to " + __name__ + ". There are already " + str(count) + " instances of this class, which is the maximum.")                
                else:
                    return False
            
        if Class.OCCURRENCESPERSET > 0 and set and Attrib.CLASS in Class.REQUIRED_ATTRIBS:
            count = len(parent.select(Class,set,True, ['Original','Suggestion','Alternative'])) 
            if count >= Class.OCCURRENCESPERSET:
                if raiseexceptions:
                    raise DuplicateAnnotationError("Unable to add another object of set " + set + " and type " + Class.__name__ + " to " + __name__ + ". There are already " + str(count) + " instances of this class, which is the maximum for the set.")                
                else:
                    return False
                
                    
        return True
        
    
    def postappend(self):
        """This method will be called after an element is added to another. It can do extra checks and if necessary raise exceptions to prevent addition. By default it does nothing."""
        pass
        
                
    def append(self, child, *args, **kwargs):
        """Append a child element. Returns the added element 
        
        If an *instance* is passed as first argument, it will be appended
        If a *class* derived from AbstractElement is passed as first argument, an instance will first be created and then appended.
                    
        Keyword arguments:
            alternative     - If set to True, the element will be made into an alternative. 
            corrected       - Used only when passing strings to be made into TextContent elements.
        """
        
        
        #obtain the set (if available, necessary for checking addability)
        if 'set' in kwargs:
            set = kwargs['set']
        else: 
            try:
                set = child.set
            except:
                set = None                

        #Check if a Class rather than an instance was passed
        Class = None #do not set to child.__class__
        if inspect.isclass(child):
            Class = child
            if Class.addable(self, set):
                if not 'id' in kwargs and not 'generate_id_in' in kwargs and (Attrib.ID in Class.REQUIRED_ATTRIBS or Attrib.ID in Class.OPTIONAL_ATTRIBS):
                    kwargs['generate_id_in'] = self
                if Class is TextContent:
                    if not 'corrected' in kwargs:
                        kwargs['corrected'] = self.MINTEXTCORRECTIONLEVEL                    
                child = Class(self.doc, *args, **kwargs)
        elif args:            
            raise Exception("Too many arguments specified. Only possible when first argument is a class and not an instance")
        
        #Do the actual appending        
        if not Class and (isinstance(child,str) or isinstance(child,unicode)) and TextContent in self.ACCEPTED_DATA:
            #you can pass strings directly (just for convenience), will be made into textcontent automatically.
            if 'corrected' in kwargs:
                child = TextContent(self.doc, child, corrected=kwargs['corrected'] ) #MAYBE TODO: corrected attribute?
            else: 
                child = TextContent(self.doc, child, corrected=self.MINTEXTCORRECTIONLEVEL )
            self.data.append(child)
            child.parent = self
        elif Class or (isinstance(child, AbstractElement) and child.__class__.addable(self, set)): #(prevents calling addable again if already done above)
            if 'alternative' in kwargs and kwargs['alternative']:
                child = Alternative(self.doc, child, generate_id_in=self)
            self.data.append(child)
            child.parent = self                
        else:
            raise ValueError("Unable to append object of type " + child.__class__.__name__ + " to " + self.__class__.__name__ + ". Type not allowed as child.")
                
        child.postappend()
        return child
            
    @classmethod
    def findreplacables(Class, parent, set=None,**kwargs):
        """Find replacable elements. Auxiliary function used by replace(). Can be overriden for more fine-grained control"""
        return parent.select(Class,set)       
        


    def replace(self, child, *args, **kwargs):
        """Appends a child element like append(), but replaces any existing child element of the same type and set. If no such child element exists, this will act the same as append()
        
        Keyword arguments:
            alternative     - If set to True, the *replaced* element will be made into an alternative. Simply use append() if you want the added element
            to be an alternative.        
        """

        if 'set' in kwargs:
            set = kwargs['set']
        else: 
            try:
                set = child.set
            except:
                set = None  

        if inspect.isclass(child):
            Class = child
            replace = Class.findreplacables(self,set,**kwargs)
        else:
            Class = child.__class__
            kwargs['instance'] = child
            replace = Class.findreplacables(self,set,**kwargs)
            del kwargs['instance']
        

        
        if len(replace) == 0:
            #nothing to replace, simply call append
            if 'alternative' in kwargs:
                del kwargs['alternative'] #has other meaning in append()
            return self.append(child, *args, **kwargs)
        elif len(replace) > 1:
            raise Exception("Unable to replace. Multiple candidates found, unable to choose.")
        elif len(replace) == 1:
            self.data.remove(replace)
            if 'alternative' in kwargs and kwargs['alternative']:
                alt = self.append(Alternative)
                alt.append(replace)
                del kwargs['alternative'] #has other meaning in append()
            return self.append(child, *args, **kwargs)
                

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
        
            
        if not skipchildren and self.data:
            #append children,
            # we want make sure that text elements are in the right order,
            # so we first put them in  a list
            textelements = []
            otherelements = []
            for child in self:
                if isinstance(child, TextContent):
                    if child.corrected == TextCorrectionLevel.UNCORRECTED:
                        textelements.insert(0, child)                
                    else:
                        textelements.append(child)                
                else:
                    otherelements.append(child)
            for child in textelements+otherelements:
                e.append(child.xml())
        
        if elements: #extra elements
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
            if ignorelist:
                ignore = False                            
                for c in ignorelist:
                    if not inspect.isclass(c):
                        c = globals()[c]
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
            
            #if cls.ALLOWTEXT:
            #    attribs.append( E.optional( E.ref(name='t') ) ) #yes, not actually an attrib, I know, but should go here
                        
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
            if subnode.tag[:nslen] == '{' + NSFOLIA + '}':
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
        if dcoi and TextContent in Class.ACCEPTED_DATA:
            text = node.text.strip()
                    

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

class Description(AbstractElement):
    XMLTAG = 'desc'
    OCCURRENCES = 1
    
    def __init__(self,doc, *args, **kwargs):
        if 'value' in kwargs:
            if isinstance(kwargs['value'], unicode):
                self.value = kwargs['value']
            elif isinstance(kwargs['value'], str):
                self.value = unicode(kwargs['value'],'utf-8')
            else:
                raise Exception("value= parameter must be unicode or str instance")
        else:
            raise Exception("Description expects value= parameter")
        super(AbstractElement,self).__init__(doc, *args, **kwargs)
    
    def __nonzero__(self):
        return bool(self.value)
        
    def __unicode__(self):
        return self.value
        
    def __str__(self):
        return self.value.encode('utf-8')  
    
    
    
    def xml(self, attribs = None,elements = None, skipchildren = False):   
        global NSFOLIA
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})

        if not attribs:
            attribs = {}  
                    
        return E.desc(self.value, **attribs)        
        
    @classmethod
    def parsexml(Class, node, doc):
        global NSFOLIA
        kwargs = {}
        kwargs['value'] = node.text
        return Description(doc, **kwargs)    
    
    
class AllowCorrections(object):
    def correct(self, **kwargs):
        if 'reuse' in kwargs:
            #reuse an existing correction instead of making a new one
            if isinstance(kwargs['reuse'], Correction):
                c = kwargs['reuse']
            else: #assume it's an index
                try:
                    c = self.doc.index[kwargs['reuse']]
                    assert isinstance(c, Correction)
                except:
                    raise ValueError("reuse= must point to an existing correction (id or instance)!")
            
            suggestionsonly = (not c.hasnew() and not c.hasoriginal() and c.hassuggestions())
        else:
            if not 'id' in kwargs and not 'generate_id_in' in kwargs:
                kwargs['generate_id_in'] = self                        
            kwargs2 = copy(kwargs)
            for x in ['new','original','suggestion', 'suggestions','current']:
                if x in kwargs2:
                    del kwargs2[x]
            c = Correction(self.doc, **kwargs2)                        

        addnew = False

        if 'current' in kwargs:
            if 'original' in kwargs or 'new' in kwargs: raise Exception("When setting current=, original= and new= can not be set!") 
            if not isinstance(kwargs['current'], list) and not isinstance(kwargs['current'], tuple): kwargs['current'] = [kwargs['current']] #support both lists (for multiple elements at once), as well as single element
            c.replace(Current(self.doc, *kwargs['current']))
            del kwargs['current']
        if 'new' in kwargs:
            if not isinstance(kwargs['new'], list) and not isinstance(kwargs['new'], tuple): kwargs['new'] = [kwargs['new']] #support both lists (for multiple elements at once), as well as single element                        
            addnew = New(self.doc, *kwargs['new'])
            c.replace(addnew)
            for current in c.select(Current): #delete current if present
                c.remove(current)            
            del kwargs['new']
        if 'original' in kwargs:
            if not isinstance(kwargs['original'], list) and not isinstance(kwargs['original'], tuple): kwargs['original'] = [kwargs['original']] #support both lists (for multiple elements at once), as well as single element
            c.replace(Original(self.doc, *kwargs['original']))
            for o in kwargs['original']: #delete original from current element
                if o in self:
                    self.remove(o)            
            for current in c.select(Current):  #delete current if present
                c.remove(current)
            del kwargs['original']        
        elif addnew:
            #original not specified, find automagically:
            original = []
            for new in addnew:
                kwargs2 = {}
                if isinstance(new, TextContent):
                    kwargs2['corrected'] = new.corrected
                try:
                    set = new.set
                except:
                    set = None                
                original += new.__class__.findreplacables(self, set, **kwargs2)
            if not original:
                raise Exception("No original= specified and unable to automatically infer")
            else:
                c.replace(Original(self.doc, *original))
                for current in c.select(Current):  #delete current if present
                    c.remove(current)       
            
        if addnew:
            for original in c.original():
                if original in self:
                    self.remove(original)            
            
        if 'suggestion' in kwargs:
            kwargs['suggestions'] = [kwargs['suggestion']]
            del kwargs['suggestion']
        if 'suggestions' in kwargs:
            for suggestion in kwargs['suggestions']:
                if isinstance(suggestion, Suggestion):
                    c.append(suggestion)
                else:
                    c.append(Suggestion(self.doc, suggestion))                        
            del kwargs['suggestions']
            
            
        

        if 'reuse' in kwargs:
            if addnew and suggestionsonly:        
                #What was previously only a suggestion, now becomes a real correction
                #If annotator, annotatortypes
                #are associated with the correction as a whole, move it to the suggestions
                #correction-wide annotator, annotatortypes might be overwritten
                for suggestion in c.suggestions:
                    if c.annotator and not suggestion.annotator:
                        suggestion.annotator = c.annotator
                    if c.annotatortype and not suggestion.annotatortype:
                        suggestion.annotatortype = c.annotatortype
                                                                
            if 'annotator' in kwargs:
                c.annotator = kwargs['annotator']
            if 'annotatortype' in kwargs:
                c.annotatortype = kwargs['annotatortype']
            if 'confidence' in kwargs:
                c.confidence = float(kwargs['confidence'])                        
            del kwargs['reuse']
        else:
            self.append(c)
        return c 
    

class AllowTokenAnnotation(AllowCorrections):
    """Elements that allow token annotation (including extended annotation) must inherit from this class"""
    
    
    
    def annotationsold(self, annotationtype=None): #obsolete
        """Generator yielding all annotations of a certain type. Raises a Raises a NoSuchAnnotation exception if none was found."""
        found = False 
        if inspect.isclass(annotationtype): annotationtype = annotationtype.ANNOTATIONTYPE        
        for e in self:
            try:
                if annotationtype is None or e.ANNOTATIONTYPE == annotationtype:
                    found = True
                    yield e
                if e.ANNOTATIONTYPE == AnnotationType.Correction:
                    for e2 in e.new():
                        yield e2
                    for e2 in e.current():
                        yield e2
                    
            except AttributeError:
                continue
        if not found:
            raise NoSuchAnnotation()
            
    def annotations(self,type,set=None):        
        l = self.select(type,set,True,['Original','Suggestion','Alternative'])
        if not l:
            raise NoSuchAnnotation()
        else:
            return l
    
    def hasannotation(self,type,set=None):
        """Returns an integer indicating whether such as annotation exists, and if so, how many"""
        l = self.select(type,set,True,['Original','Suggestion','Alternative'])
        return len(l)

    def annotation(self, type, set=None):
        """Will return a SINGLE annotation (even if there are multiple). Raises a NoSuchAnnotation exception if none was found"""
        l = self.select(type,set,True,['Original','Suggestion','Alternative'])
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
    
    TEXTDELIMITER = "\n\n" #bigger gap between structure elements
    
    def __init__(self, doc, *args, **kwargs):            
        super(AbstractStructureElement,self).__init__(doc, *args, **kwargs)

    def resolveword(self, id): 
        for child in self:
            r =  child.resolveword(id)            
            if r:
                return r
        return None          
        
    def append(self, child, *args, **kwargs):
        e = super(AbstractStructureElement,self).append(child, *args, **kwargs)
        self._setmaxid(child)     
        return e
                

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

class AbstractAnnotation(AbstractElement):
    def feat(self,subset):
        for f in self:
            if isinstance(f, Feature) and f.subset == subset:
                return f.cls

class AbstractTokenAnnotation(AbstractAnnotation, AllowGenerateID): 
    OCCURRENCESPERSET = 1 #Do not allow duplicates within the same set

    def append(self, child, *args, **kwargs):
        e = super(AbstractTokenAnnotation,self).append(child, *args, **kwargs)
        self._setmaxid(child)
        return e

class AbstractExtendedTokenAnnotation(AbstractTokenAnnotation): 
    pass

class TextContent(AbstractElement):
    XMLTAG = 't'
    
    def __init__(self, doc, *args, **kwargs):
        if not 'value' in kwargs:
            if args and (isinstance(args[0], unicode) or isinstance(args[0], str)):
                kwargs['value'] = args[0]
                args = args[1:]
            else:
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
            self.corrected = None

        
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
    
    def text(self, corrected = None):
        if corrected is None or corrected == self.corrected:
            return self.value
        else:
            raise NoSuchText
        
    def __unicode__(self):
        return self.value
        
    def __str__(self):
        return self.value.encode('utf-8')
        
    def __eq__(self, other):
        if isinstance(other, TextContent):
            return self.value == other.value
        elif isinstance(other, unicode):
            return self.value == other
        elif isinstance(other, str):
            return self.value == unicode(other,'utf-8')
        else:
            return False
        
    def append(self, child, *args, **kwargs):
        raise NotImplementedError #on purpose
        
    def postappend(self):
        try:
            if not self.ref and self.parent.parent and self.parent.parent.hastext():
                self.ref = self.parent.parent
        except:
            pass
            
    
        if self.corrected is None:
            self.corrected = self.parent.MINTEXTCORRECTIONLEVEL                    
            
        if self.corrected < self.parent.MINTEXTCORRECTIONLEVEL:
            raise ValueError("Text Content (" + str(self.corrected) + ") must be of higher CorrectionLevel (" + str(self.parent.MINTEXTCORRECTIONLEVEL) + ")")
            
        if self.corrected == TextCorrectionLevel.UNCORRECTED or self.corrected == TextCorrectionLevel.CORRECTED:
            #there can be only one of this type.
            for child in self.parent:
                if not child is self and isinstance(child, TextContent) and child.corrected == self.corrected:            
                    raise DuplicateAnnotationError("Text element with same corrected status (except for inline) may not occur multiple times!")
            
    
    def __iter__(self):
        return iter(self.value)
    
    def __len__(self):    
        return len(self.value)
    
    @classmethod
    def findreplacables(Class, parent, set, **kwargs):
        #some extra behaviour for text content elements, replace also based on the 'corrected' attribute:
        if not 'corrected' in kwargs:
            if 'instance' in kwargs:
                kwargs['corrected'] = instance.corrected
            if Class.MINTEXTCORRECTIONLEVEL == TextCorrectionLevel.UNCORRECTED:
                kwargs['corrected'] = TextCorrectionLevel.UNCORRECTED
            else:
                kwargs['corrected'] = TextCorrectionLevel.CORRECTED
        replace = super(TextContent, Class).findreplacables(parent, set, **kwargs)
        replace = [ x for x in replace if x.corrected == kwargs['corrected']]
        del kwargs['corrected'] #always delete what we processed
        return replace
        
        
    @classmethod
    def parsexml(Class, node, doc):
        global NSFOLIA
        nslen = len(NSFOLIA) + 2
        args = []
        kwargs = {}
        if 'corrected' in node.attrib:
            if node.attrib['corrected'] == 'yes':
                kwargs['corrected'] = TextCorrectionLevel.CORRECTED
            elif node.attrib['corrected'] == 'inline':
                kwargs['corrected'] = TextCorrectionLevel.INLINE
            elif node.attrib['corrected'] == 'no':
                kwargs['corrected'] = TextCorrectionLevel.UNCORRECTED
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
        if self.corrected == TextCorrectionLevel.INLINE:
            attribs['{' + NSFOLIA + '}corrected'] = 'inline'
        elif self.corrected == TextCorrectionLevel.CORRECTED and self.parent.MINTEXTCORRECTIONLEVEL < TextCorrectionLevel.CORRECTED:
            attribs['{' + NSFOLIA + '}corrected'] = 'yes'
            
        return E.t(self.value, **attribs)
        
class Word(AbstractStructureElement, AllowCorrections):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    XMLTAG = 'w'
    ANNOTATIONTYPE = AnnotationType.TOKEN
    #ACCEPTED_DATA DEFINED LATER (after Correction)
    
    MINTEXTCORRECTIONLEVEL = TextCorrectionLevel.CORRECTED
    
    def __init__(self, doc, *args, **kwargs):
        self.space = True
                      
        if 'space' in kwargs:            
            self.space = kwargs['space']
            del kwargs['space']
        super(Word,self).__init__(doc, *args, **kwargs)
                        

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

    def overridetextdelimiter(self):
        """May return a customised text delimiter that overrides the default text delimiter set by the parent. Defaults to None (do not override)"""
        if self.space:
            return ' '
        else:
            return ''

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


    
class AbstractSpanAnnotation(AbstractAnnotation, AllowGenerateID): 
    OCCURRENCESPERSET = 0 #Allow duplicates within the same set


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


    def append(self, child, *args, **kwargs):
        if isinstance(child, Word) and WordReference in self.ACCEPTED_DATA:
            #Accept Word instances instead of WordReference, references will be automagically used upon serialisation
            self.data.append(child)
            return child
        else:
            return super(AbstractSpanAnnotation,self).append(child)    
            

class AbstractAnnotationLayer(AbstractElement):
    OPTIONAL_ATTRIBS = (Attrib.CLASS,)
    PRINTABLE = False
    
    def __init__(self, doc, *args, **kwargs):
        if 'set' in kwargs:
            self.set = kwargs['set']
            del kwargs['set']
        super(AbstractAnnotationLayer,self).__init__(doc, *args, **kwargs)
        

class AbstractCorrectionChild(AbstractElement):
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ACCEPTED_DATA = (AbstractTokenAnnotation, Word, TextContent, Description)
    

class ErrorDetection(AbstractExtendedTokenAnnotation):
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.ERRORDETECTION
    XMLTAG = 'errordetection'
    OCCURRENCESPERSET = 0 #Allow duplicates within the same set (0= unlimited)
    
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
    
            
                        
class Suggestion(AbstractCorrectionChild):
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.SUGGESTION
    XMLTAG = 'suggestion'
    OCCURRENCES = 0 #unlimited
    OCCURRENCESPERSET = 0 #Allow duplicates within the same set (0= unlimited)
    
    MINTEXTCORRECTIONLEVEL = TextCorrectionLevel.CORRECTED

class New(AbstractCorrectionChild):
    REQUIRED_ATTRIBS = (),
    OPTIONAL_ATTRIBS = (),    
    OCCURRENCES = 1
    XMLTAG = 'new'
    
    MINTEXTCORRECTIONLEVEL = TextCorrectionLevel.CORRECTED
    
    @classmethod
    def addable(Class, parent, set=None, raiseexceptions=True):
        if not super(New,Class).addable(parent,set,raiseexceptions): return False
        if any( ( isinstance(c, Current) for c in parent ) ):
            if raiseexceptions:
                raise ValueError("Can't add New element to Correction if there is a Current item")
            else:
                return False
        return True
    
class Original(AbstractCorrectionChild):
    REQUIRED_ATTRIBS = (),
    OPTIONAL_ATTRIBS = (),    
    OCCURRENCES = 1
    XMLTAG = 'original'
    
    @classmethod
    def addable(Class, parent, set=None, raiseexceptions=True):
        if not super(Original,Class).addable(parent,set,raiseexceptions): return False        
        if any( ( isinstance(c, Current)  for c in parent ) ):
             if raiseexceptions:
                raise Exception("Can't add Original item to Correction if there is a Current item")
             else: 
                return False
        return True    
    
    
class Current(AbstractCorrectionChild):
    REQUIRED_ATTRIBS = (),
    OPTIONAL_ATTRIBS = (),    
    OCCURRENCES = 1
    XMLTAG = 'current'         
    
    @classmethod
    def addable(Class, parent, set=None, raiseexceptions=True):
        if not super(Current,Class).addable(parent,set,raiseexceptions): return False
        if any( ( isinstance(c, New) or isinstance(c, Original) for c in parent ) ):
            if raiseexceptions:
                raise Exception("Can't add Current element to Correction if there is a New or Original element")
            else: 
                return False
        return True    
            
class Correction(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ACCEPTED_DATA = (New,Original,Current, Suggestion, Description)
    ANNOTATIONTYPE = AnnotationType.CORRECTION
    XMLTAG = 'correction'
    OCCURRENCESPERSET = 0 #Allow duplicates within the same set (0= unlimited)
    
    
    def hasnew(self):
        return bool(self.select(New,None,False, False))
        
    def hasoriginal(self):
        return bool(self.select(Original,None,False, False))
        
    def hascurrent(self):
        return bool(self.select(Current,None,False, False))        
        
    def hassuggestions(self):
        return bool(self.select(Suggestion,None,False, False))                
    
    
    def new(self,index = None):
        if index is None:
            try:
                return self.select(New,None,False)[0]
            except IndexError:
                raise NoSuchAnnotation
        else:
            l = self.select(New,None,False)
            if len(l) == 0:
                raise NoSuchAnnotation
            else:                
                return l[0][index]
        
    def original(self,index=None):
        if index is None:
            try:
                return self.select(Original,None,False, False)[0]
            except IndexError:
                raise NoSuchAnnotation
        else:
            l = self.select(Original,None,False, False)
            if len(l) == 0:
                raise NoSuchAnnotation
            else:                
                return l[0][index]
        
    def current(self,index=None):        
        if index is None:
            try:
                return self.select(Current,None,False)[0]       
            except IndexError:
                raise NoSuchAnnotation
        else:
            l =  self.select(Current,None,False)
            if len(l) == 0:
                raise NoSuchAnnotation
            else:                
                return l[0][index]
    
    def suggestions(self,index=None):
        if index is None:
            return self.select(Suggestion,None,False, False)    
        else:
            return self.select(Suggestion,None,False, False)[index]
              
            
    def __unicode__(self):
        for e in self:
            if isinstance(e, New) or isinstance(e, Current):
                return unicode(e)
        
    
    def select(self, cls, set=None, recursive=True,  ignorelist=[], node=None):
        """Select on Correction only descends in either "NEW" or "CURRENT" branch"""
        if ignorelist is False:
            #to override and go into all branches, set ignorelist explictly to False
            return super(Correction,self).select(cls,set,recursive, ignorelist, node)
        else:
            ignorelist = copy(ignorelist) #we don't want to alter an passed ignorelist (by ref)
            ignorelist.append(Original)
            ignorelist.append(Suggestion)
            return super(Correction,self).select(cls,set,recursive, ignorelist, node)
        
Original.ACCEPTED_DATA = (AbstractTokenAnnotation, Word, TextContent, Correction, Description)

            
class Alternative(AbstractElement, AllowTokenAnnotation, AllowGenerateID):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (AbstractTokenAnnotation, Correction)
    ANNOTATIONTYPE = AnnotationType.ALTERNATIVE
    XMLTAG = 'alt'
    PRINTABLE = False    


Word.ACCEPTED_DATA = (AbstractTokenAnnotation, TextContent, Correction, Alternative, Description)


class AlternativeLayers(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (AbstractAnnotationLayer)    
    XMLTAG = 'altlayers'
    PRINTABLE = False    

class WordReference(AbstractElement):
    """Only used when word reference can not be resolved, if they can, Word objects will be used"""
    REQUIRED_ATTRIBS = (Attrib.ID,)
    XMLTAG = 'wref'
    ANNOTATIONTYPE = AnnotationType.TOKEN
    
    def __init__(self, doc, *args, **kwargs):
        #Special constructor, not calling super constructor
        if not 'id' in kwargs:
            raise Exception("ID required for WordReference")
        assert(isinstance(doc,Document))
        self.doc = doc
        self.id = kwargs['id']
        self.annotator = None
        self.annotatortype = None
        self.confidence = None
        self.n = None
    
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
    
SyntacticUnit.ACCEPTED_DATA = (SyntacticUnit,WordReference, Description)

class Chunk(AbstractSpanAnnotation):
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ACCEPTED_DATA = (WordReference, Description)
    ANNOTATIONTYPE = AnnotationType.CHUNKING
    XMLTAG = 'chunk'

class Entity(AbstractSpanAnnotation):
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ACCEPTED_DATA = (WordReference, Description)
    ANNOTATIONTYPE = AnnotationType.ENTITY
    XMLTAG = 'entity'
    
class SyntaxLayer(AbstractAnnotationLayer):
    ACCEPTED_DATA = (SyntacticUnit,Description)
    XMLTAG = 'syntax'

class ChunkingLayer(AbstractAnnotationLayer):
    ACCEPTED_DATA = (Chunk,Description)
    XMLTAG = 'chunking'

class EntitiesLayer(AbstractAnnotationLayer):
    ACCEPTED_DATA = (Entity,Description)
    XMLTAG = 'entities'

    
class PosAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.POS
    ACCEPTED_DATA = (Feature,Description)
    XMLTAG = 'pos'

class LemmaAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.LEMMA
    ACCEPTED_DATA = (Feature,Description)
    XMLTAG = 'lemma'
    
class PhonAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.PHON
    ACCEPTED_DATA = (Feature,Description)
    XMLTAG = 'phon'


class DomainAnnotation(AbstractExtendedTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.DOMAIN
    ACCEPTED_DATA = (Feature,Description)
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
    ACCEPTED_DATA = (Feature,SynsetFeature, Description)
    XMLTAG = 'sense'
    


class Quote(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = ()    
    XMLTAG = 'quote'

    #ACCEPTED DATA defined later below
    
    def __init__(self,  doc, *args, **kwargs):
        super(Quote,self).__init__(doc, *args, **kwargs)


    def resolveword(self, id):
        for child in self:
            r =  child.resolveword(id)            
            if r:
                return r
        return None        
        
        
class Sentence(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Word, Quote, AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Correction, TextContent, Description)
    XMLTAG = 's'
    
    def __init__(self,  doc, *args, **kwargs):
        super(Sentence,self).__init__(doc, *args, **kwargs)
     
                
    def resolveword(self, id):
        for child in self:
            r =  child.resolveword(id)            
            if r:
                return r
        return None

    def corrections(self):
        """Are there corrections in this sentence?"""
        return bool(self.select(Correction))

    def paragraph(self):
        """return the paragraph this sentence is a part of (None otherwise)"""
        e = self;
        while e.parent: 
            if isinstance(e, Paragraph):
                return e
            e = e.parent  
        return None
 
    def division(self):
        """return the division this sentence is a part of (None otherwise)"""
        e = self;
        while e.parent: 
            if isinstance(e, Division):
                return e
            e = e.parent  
        return None
        

    def correctwords(self, originalwords, newwords, **kwargs):
        """Generic correction method for words. You most likely want to use the helper functions
           splitword() , mergewords(), deleteword(), insertword() instead"""
        for w in originalwords:            
            if not isinstance(w, Word):
                raise Exception("Original word is not a Word instance: " + str(type(w)))    
            elif w.sentence() != self:
                raise Exception("Original not found as member of sentence!")               
        for w in newwords:            
            if not isinstance(w, Word):
                raise Exception("New word is not a Word instance: " + str(type(w)))                    
        if 'suggest' in kwargs and kwargs['suggest']:
            del kwargs['suggest']
            return self.correct(suggestion=newwords,current=originalwords, **kwargs)
        else:
            return self.correct(original=originalwords, new=newwords, **kwargs)

        
        
    def splitword(self, originalword, *newwords, **kwargs):
        if isinstance(originalword, str) or isinstance(originalword, unicode):
            originalword = self.doc[originalword]
        return self.correctwords([originalword], newwords, **kwargs)
            
            

    def mergewords(self, newword, *originalwords, **kwargs):
        return self.correctwords(originalwords, newword, **kwargs)
            
    def deleteword(self, word, **kwargs):
        if isinstance(word, str) or isinstance(word, unicode):
            word = self.doc[word]   
        return self.correctwords([word], [], **kwargs)
                
        
    def insertword(self, newword, prevword, **kwargs):
        #TODO: Refactor
        if isinstance(prevword, str) or isinstance(prevword, unicode):
            prevword = self.doc[prevword]            
        if not prevword in self or not isinstance(prevword, Word):
            raise Exception("Previous word not found or not instance of Word!")
        if not isinstance(newword, Word):
            raise Exception("New word no instance of Word!")
        
        insertindex = self.data.index(prevword)
    
        
        if 'suggest' in kwargs and kwargs['suggest']:            
            kwargs['suggestion'] = newword
        else:
            kwargs['original'] = []
            kwargs['new'] = newword
        
        if not 'id' in kwargs and not 'generate_id_in' in kwargs:
            kwargs['generate_id_in'] = self
            
        if 'suggest' in kwargs:
            del kwargs['suggest']            
            
        c = Correction(self.doc, **kwargs)
        self.data.insert( insertindex, c )
        c.parent = self
        return c 



Quote.ACCEPTED_DATA = (Word, Sentence, Quote, TextContent, Description)        

class Paragraph(AbstractStructureElement):    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Sentence, AbstractExtendedTokenAnnotation, Correction, TextContent, Description)
    XMLTAG = 'p'
    TEXTDELIMITER = "\n"
    
    def sentences(self):
        return self.select(Sentence)
        
    def words(self):
        return self.select(Word)    
                              
                
class Head(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Sentence,Description)
    OCCURRENCES = 1
    TEXTDELIMITER = ' '
    XMLTAG = 'head'          
        
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
        return text

    def create(self, Class, *args, **kwargs):
        """Create an element associated with this Document"""
        return Class(self, *args, **kwargs)

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
        
        

class Content(AbstractElement):     #used for raw content, subelement for Gap
    OCCURENCES = 1
    XMLTAG = 'content'
    
    def __init__(self,doc, *args, **kwargs):
        if 'value' in kwargs:
            if isinstance(kwargs['value'], unicode):
                self.value = kwargs['value']
            elif isinstance(kwargs['value'], str):
                self.value = unicode(kwargs['value'],'utf-8')
            else:
                raise Exception("value= parameter must be unicode or str instance")
        else:
            raise Exception("Description expects value= parameter")
        super(AbstractElement,self).__init__(doc, *args, **kwargs)
    
    def __nonzero__(self):
        return bool(self.value)
        
    def __unicode__(self):
        return self.value
        
    def __str__(self):
        return self.value.encode('utf-8')  

    def xml(self, attribs = None,elements = None, skipchildren = False):   
        global NSFOLIA
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})

        if not attribs:
            attribs = {}  
                    
        return E.content(self.value, **attribs)        
        
    @classmethod
    def parsexml(Class, node, doc):
        global NSFOLIA
        kwargs = {}
        kwargs['value'] = node.text
        return Content(doc, **kwargs)            
    
class Gap(AbstractElement):    
    ACCEPTED_DATA = (Content, Description)
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

    def content(self):
        for e in self:
            if isinstance(e, Content):
                return e.value
        raise NoSuchAnnotation
            
    
class ListItem(AbstractStructureElement):
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    #ACCEPTED_DATA = (List, Sentence) #Defined below
    XMLTAG = 'listitem'
    
    
class List(AbstractStructureElement):    
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    ACCEPTED_DATA = (ListItem,Description)
    XMLTAG = 'list'
    

ListItem.ACCEPTED_DATA = (List, Sentence, Description)


class Figure(AbstractStructureElement):    
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    ACCEPTED_DATA = (Sentence, Description)
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

            
    def head(self):
        for e in self.data:
            if isinstance(e, Head):
                return e
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

Division.ACCEPTED_DATA = (Division, Head, Paragraph, Sentence, List, Figure, AbstractExtendedTokenAnnotation, Description)

class Text(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Gap, Division, Paragraph, Sentence, List, Figure, AbstractExtendedTokenAnnotation, Description)
    XMLTAG = 'text' 
    TEXTDELIMITER = "\n\n"
        
    def paragraphs(self):            
        return self.select(Paragraph)
    
    def sentences(self):
        return self.select(Sentence)
        
    def words(self):
        return self.select(Word)        


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


