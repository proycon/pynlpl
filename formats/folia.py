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
from datetime import datetime
#from dateutil.parser import parse as parse_datetime
import pynlpl.math
import inspect
import glob
import os
import re

NSFOLIA = "http://ilk.uvt.nl/folia"
NSDCOI = "http://lands.let.ru.nl/projects/d-coi/ns/1.0"

class AnnotatorType:
    UNSET = 0
    AUTO = 1
    MANUAL = 2
    

class Attrib:
    ID, CLASS, ANNOTATOR, CONFIDENCE, N, DATETIME = range(6)

class AnnotationType:
    TOKEN, DIVISION, POS, LEMMA, DOMAIN, SENSE, SYNTAX, CHUNKING, ENTITY, CORRECTION, SUGGESTION, ERRORDETECTION, ALTERNATIVE, PHON, SUBJECTIVITY, MORPHOLOGICAL, SUBENTITY = range(17)
    
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
    
class DuplicateIDError(Exception):
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
        
        if doc and (not (annotationtype in doc.annotationdefaults) or not (object.set in doc.annotationdefaults[annotationtype])):
            raise ValueError("Set '" + object.set + "' is used but has no declaration!")            
    elif annotationtype in doc.annotationdefaults and len(doc.annotationdefaults[annotationtype]) == 1:
        object.set = doc.annotationdefaults[annotationtype].keys()[0]
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
    elif doc and annotationtype in doc.annotationdefaults and object.set in doc.annotationdefaults[annotationtype] and 'annotator' in doc.annotationdefaults[annotationtype][object.set]:
        object.annotator = doc.annotationdefaults[annotationtype][object.set]['annotator']
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
    elif doc and annotationtype in doc.annotationdefaults and object.set in doc.annotationdefaults[annotationtype] and 'annotatortype' in doc.annotationdefaults[annotationtype][object.set]:
        object.annotatortype = doc.annotationdefaults[annotationtype][object.set]['annotatortype']
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

    if 'datetime' in kwargs:
        if not Attrib.DATETIME in supported:
            raise ValueError("Datetime is not supported")
        if isinstance(kwargs['datetime'], datetime):
            object.datetime = kwargs['datetime']
        else:
            
            #try:
            object.datetime = parse_datetime(kwargs['datetime'])            
            #except:
            #    raise ValueError("Unable to parse datetime: " + str(repr(kwargs['datetime'])))
        del kwargs['datetime']                
    elif Attrib.DATETIME in required:
        raise ValueError("Datetime is required")
    else:
        object.datetime = None        
    
    
    if 'text' in kwargs:
        object.settext(kwargs['text'])
        del kwargs['text']
    if 'correctedtext' in kwargs:
        object.settext(kwargs['text'], TextCorrectionLevel.CORRECTED)
        del kwargs['correctedtext']
    if 'uncorrectedtext' in kwargs:
        object.settext(kwargs['text'], TextCorrectionLevel.UNCORRECTED)        
        del kwargs['uncorrectedtext']
        
    if doc and doc.debug >= 2:
        print >>stderr, "   @id           = ", repr(object.id)
        print >>stderr, "   @set          = ", repr(object.set)
        print >>stderr, "   @class        = ", repr(object.cls)
        print >>stderr, "   @annotator    = ", repr(object.annotator)
        print >>stderr, "   @annotatortype= ", repr(object.annotatortype)
        print >>stderr, "   @confidence   = ", repr(object.confidence)
        print >>stderr, "   @n            = ", repr(object.n)
        print >>stderr, "   @datetime     = ", repr(object.datetime)
        
                
    #set index
    if object.id and doc:
        if object.id in doc.index:
            if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Duplicate ID not permitted:" + object.id
            raise DuplicateIDError("Duplicate ID not permitted: " + object.id)
        else:
            if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Adding to index: " + object.id
            doc.index[object.id] = object

    
    return kwargs
    
        

def parse_datetime(s): #source: http://stackoverflow.com/questions/2211362/how-to-parse-xsddatetime-format
  """Returns (datetime, tz offset in minutes) or (None, None)."""
  m = re.match(""" ^
    (?P<year>-?[0-9]{4}) - (?P<month>[0-9]{2}) - (?P<day>[0-9]{2})
    T (?P<hour>[0-9]{2}) : (?P<minute>[0-9]{2}) : (?P<second>[0-9]{2})
    (?P<microsecond>\.[0-9]{1,6})?
    (?P<tz>
      Z | (?P<tz_hr>[-+][0-9]{2}) : (?P<tz_min>[0-9]{2})
    )?
    $ """, s, re.X)
  if m is not None:
    values = m.groupdict()
    if values["tz"] in ("Z", None):
      tz = 0
    else:
      tz = int(values["tz_hr"]) * 60 + int(values["tz_min"])
    if values["microsecond"] is None:
      values["microsecond"] = 0
    else:
      values["microsecond"] = values["microsecond"][1:]
      values["microsecond"] += "0" * (6 - len(values["microsecond"]))
    values = dict((k, int(v)) for k, v in values.iteritems()
                  if not k.startswith("tz"))
    try:
        
      return datetime(**values) # , tz
    except ValueError:
      pass
  return None


        
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
        if not isinstance(doc, Document) and not doc is None:
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
        """Obtain the description associated with the element, will raise NoDescription if there is none"""
        for e in self:
            if isinstance(e, Description):
                return e.value
        raise NoDescription
        
    def text(self, corrected=None):
        """Get the text associated with this element, will always be a unicode instance. 
        
         Text content always has a certain *correction level* associated with it, determining whether the text is corrected or not.
         A correction level can be specified if you want to fetch only text prior- or post- correction.
        
         If no desired correctionlevel is specified 
           the *best* level will be selected automatically in the following fashion:
            * Will first grab the corrected textcontent explicitly associated with the element
            * If not found, it will descend into the children and build text dynamically
            * If that yields no text, it will resort to the original uncorrected text
            * If none is found, a NoSuchText exception is raised.
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
                #print "NEW S"
                for e in self:
                    try:                  
                        delimiter = e.overridetextdelimiter()
                        if delimiter is None:
                            delimiter = self.TEXTDELIMITER #default delimiter set by parent                        
                        a =  unicode(e) + delimiter
                        #print "ADDING: ", a, " ( delimiter "+str(type(self))+ ": ", delimiter,')'
                        s += a
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
        """Alias for retrieving the original uncorrect text"""
        return self.text(TextCorrectionLevel.UNCORRECTED)
        
    def overridetextdelimiter(self):
        """May return a customised text delimiter that overrides the default text delimiter set by the parent. Defaults to None (do not override). Mostly for internal use."""
        return None #do not override

    def __ne__(self, other):
        return not (self == other)
            
    def __eq__(self, other):
        if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - " + repr(self) + " vs " + repr(other)
        
        #Check if we are of the same time
        if type(self) != type(other):
            if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Type mismatch: " + str(type(self)) + " vs " + str(type(other))
            return False
            
        #Check FoLiA attributes
        if self.id != other.id:
            if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - ID mismatch: " + str(self.id) + " vs " + str(other.id)
            return False            
        if self.set != other.set:
            if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Set mismatch: " + str(self.set) + " vs " + str(other.set)
            return False
        if self.cls != other.cls:
            if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Class mismatch: " + repr(self.cls) + " vs " + repr(other.cls)
            return False            
        if self.annotator != other.annotator:
            if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Annotator mismatch: " + repr(self.annotator) + " vs " + repr(other.annotator)
            return False            
        if self.annotatortype != other.annotatortype:
            if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Annotator mismatch: " + repr(self.annotatortype) + " vs " + repr(other.annotatortype)
            return False                                     
                
        #Check if we have same amount of children:
        mychildren = list(self)
        yourchildren = list(other)
        if len(mychildren) != len(yourchildren):
            if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Unequal amount of children"
            return False
                    
        #Now check equality of children        
        for mychild, yourchild in zip(mychildren, yourchildren):
            if mychild != yourchild:
                if self.doc and self.doc.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Child mismatch: " + repr(mychild) + " vs " + repr(yourchild) + " (in " + repr(self) + ", id: " + str(self.id) + ")"
                return False

        #looks like we made it! \o/
        return True
    
    def __len__(self):
        """Returns the number of child elements under the current element"""
        return len(self.data)
        
    def __nonzero__(self):
        return True #any instance evaluates to True in boolean tests!! (important to distinguish from uninstantianted None values!)
        
    def __iter__(self):
        """Iterate over all children of this element"""
        return iter(self.data)

    def __contains__(self, element):
        """Tests if the specified element is part of the children of the element"""
        return element in self.data
            
    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise

    def __unicode__(self):
        """Alias for text()"""
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
        """Does this element have text? May specify a correctionlevel to test for texts of a particular correctionlevel (see text() for more information)"""
        if corrected is None:
            #regardless of correctionlevel:
            return (len(self.select(TextContent,None,False)) > 0)
        else:
            return (len([ x for x in self.select(TextContent,None,False) if x.corrected == corrected]) > 0)            
    
            
    def settext(self, text, corrected=None):
        """Set the text for this element. You may specificy an explicit correctionlevel if desired. (see ``text()`` for more information)"""
        if corrected is None:
            corrected = self.MINTEXTCORRECTIONLEVEL
        self.replace(TextContent, value=text, corrected=corrected) 

    def setdocument(self, doc):
        """Associate a document with this element"""
        assert isinstance(doc, Document)
        
        if not self.doc:
            self.doc = doc
            if self.id:
                if self.id in doc:
                    raise DuplicateIDError(self.id)
                else:    
                    self.doc.index[id] = self
        
        for e in self: #recursive for all children
            e.setdocument(doc)

    @classmethod
    def addable(Class, parent, set=None, raiseexceptions=True):
        """Tests whether a new element of this class can be added to the parent. Returns a boolean or raises ValueError exceptions (unless set to ignore)!
        
         This will use ``OCCURRENCES``, but may be overidden for more customised behaviour.
         
         This method is mostly for internal use.
         """
        
        
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
        """This method will be called after an element is added to another. It can do extra checks and if necessary raise exceptions to prevent addition. By default makes sure the right document is associated.
        
        This method is mostly for internal use.
        """
        
        #If the element was not associated with a document yet, do so now (and for all unassociated children:
        if not self.doc and self.parent.doc:
            self.setdocument(self.parent.doc)
        
                
    def append(self, child, *args, **kwargs):
        """Append a child element. Returns the added element     

        Arguments:   
            * ``child``            - Instance or class
            
        If an *instance* is passed as first argument, it will be appended
        If a *class* derived from AbstractElement is passed as first argument, an instance will first be created and then appended.            
                    
        Keyword arguments:
            * ``alternative=``     - If set to True, the element will be made into an alternative. 
            * ``corrected=``       - Used only when passing strings to be made into TextContent elements.
            
        Generic example, passing a pre-generated instance::
        
            word.append( folia.LemmaAnnotation(doc,  cls="house", annotator="proycon", annotatortype=folia.AnnotatorType.MANUAL ) )
            
        Generic example, passing a class to be generated::
            
            word.append( folia.LemmaAnnotation, cls="house", annotator="proycon", annotatortype=folia.AnnotatorType.MANUAL )
        
        Generic example, setting text of a specific correctionlevel::
        
            word.append( "house", corrected=folia.TextCorrectionLevel.CORRECTED )
            
            
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
        
    def insert(self, index, child, *args, **kwargs):
        """Insert a child element at specified index. Returns the added element 
        
        If an *instance* is passed as first argument, it will be appended
        If a *class* derived from AbstractElement is passed as first argument, an instance will first be created and then appended.
                    
        Arguments:   
            * index                 
            * ``child``            - Instance or class
                    
        Keyword arguments:
            * ``alternative=``     - If set to True, the element will be made into an alternative. 
            * ``corrected=``       - Used only when passing strings to be made into TextContent elements.
            
        Generic example, passing a pre-generated instance::
        
            word.insert( 3, folia.LemmaAnnotation(doc,  cls="house", annotator="proycon", annotatortype=folia.AnnotatorType.MANUAL ) )
            
        Generic example, passing a class to be generated::
            
            word.insert( 3, folia.LemmaAnnotation, cls="house", annotator="proycon", annotatortype=folia.AnnotatorType.MANUAL )
        
        Generic example, setting text of a specific correctionlevel::
        
            word.insert( 3, "house", corrected=folia.TextCorrectionLevel.CORRECTED )
            
            
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
            self.data.insert(index, child)
            child.parent = self
        elif Class or (isinstance(child, AbstractElement) and child.__class__.addable(self, set)): #(prevents calling addable again if already done above)
            if 'alternative' in kwargs and kwargs['alternative']:
                child = Alternative(self.doc, child, generate_id_in=self)
            self.data.insert(index, child)
            child.parent = self                
        else:
            raise ValueError("Unable to append object of type " + child.__class__.__name__ + " to " + self.__class__.__name__ + ". Type not allowed as child.")
                
        child.postappend()
        return child        
            
    @classmethod
    def findreplacables(Class, parent, set=None,**kwargs):
        """Find replacable elements. Auxiliary function used by replace(). Can be overriden for more fine-grained control. Mostly for internal use."""
        return parent.select(Class,set,False)       
        


    def replace(self, child, *args, **kwargs):
        """Appends a child element like ``append()``, but replaces any existing child element of the same type and set. If no such child element exists, this will act the same as append()
        
        Keyword arguments:
            * ``alternative`` - If set to True, the *replaced* element will be made into an alternative. Simply use ``append()`` if you want the added element
            to be an alternative.        
            
        See ``append()`` for more information.
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
            if 'alternative' in kwargs and kwargs['alternative']: 
                #old version becomes alternative
                if replace[0] in self.data:
                    self.data.remove(replace[0])
                alt = self.append(Alternative)
                alt.append(replace[0])
                del kwargs['alternative'] #has other meaning in append()
            else: 
                #remove old version competely
                self.remove(replace[0])
            return self.append(child, *args, **kwargs)
                

    def xml(self, attribs = None,elements = None, skipchildren = False):  
        """Return an XML Element for this element and all its children."""
        global NSFOLIA
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
        
        if not attribs: attribs = {}
        if not elements: elements = []
        
        if self.id:
            attribs['{http://www.w3.org/XML/1998/namespace}id'] = self.id
            
        #Some attributes only need to be added if they are not the same as what's already set in the declaration    
        try:
            if self.set:
                if len(self.doc.annotationdefaults[self.ANNOTATIONTYPE]) != 1 or self.doc.annotationdefaults[self.ANNOTATIONTYPE].keys()[0] != self.set:
                    attribs['{' + NSFOLIA + '}set'] = self.set        
        except AttributeError:
            pass
        
        try:
            if self.cls:
                attribs['{' + NSFOLIA + '}class'] = self.cls
        except AttributeError:
            pass        
                        
        try:
            if self.annotator and ((not (self.ANNOTATIONTYPE in self.doc.annotationdefaults)) or (not ( 'annotator' in self.doc.annotationdefaults[self.ANNOTATIONTYPE][self.set])) or (self.annotator != self.doc.annotationdefaults[self.ANNOTATIONTYPE][self.set]['annotator'])):
                attribs['{' + NSFOLIA + '}annotator'] = self.annotator
            if self.annotatortype and ((not (self.ANNOTATIONTYPE in self.doc.annotationdefaults)) or (not ('annotatortype' in self.doc.annotationdefaults[self.ANNOTATIONTYPE][self.set])) or (self.annotatortype != self.doc.annotationdefaults[self.ANNOTATIONTYPE][self.set]['annotatortype'])):
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
            
        try:
            if self.datetime:
                attribs['{' + NSFOLIA + '}datetime'] = self.datetime.strftime("%Y-%m-%dT%H:%M:%S") #TODO: format string                
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

    def xmlstring(self, pretty_print=False):
        """Return a string with XML presentation for this element and all its children."""
        s = ElementTree.tostring(self.xml(), xml_declaration=False, pretty_print=pretty_print, encoding='utf-8')        
        s = s.replace('ns0:','') #ugly patch to get rid of namespace prefix
        s = s.replace(':ns0','')
        return s
        
        
    def select(self, Class, set=None, recursive=True,  ignorelist=['Original','Suggestion','Alternative'], node=None):
        """Select child elements of the specified class. 
        
        A further restriction can be made based on set. Whether or not to apply recursively (by default enabled) can also be configured, optionally with a list of elements never to recurse into. 
        
        Arguments:
            * ``Class``: The class to select; any python class subclassed off `'AbstractElement``
            * ``set``: The set to match against, only elements pertaining to this set will be returned. If set to None (default), all elements regardless of set will be returned.
            * ``recursive``: Select recursively? Descending into child elements? Boolean defaulting to True.
            * ``ignorelist``: A list of Classes (subclassed off ``AbstractElement``) not to recurse into. It is common not to want to recurse into the following elements: ``folia.Alternative``, ``folia.Suggestion``, and ``folia.Original``. As elements contained in these are never *authorative*.
            * ``node``: Reserved for internal usage, used in recursion.
            
        Returns:
            A list of elements (instances)
            
        Example::
            
            text.select(folia.Sense, 'cornetto', True, [folia.Original, folia.Suggestion, folia.Alternative] )        
            
        """
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
        
            if isinstance(e, Class):                
                if not set is None:
                    try:
                        if e.set != set:
                            continue
                    except:
                        continue
                l.append(e)
            if recursive:
                for e2 in e.select(Class, set, recursive, ignorelist, e):
                    if not set is None:
                        try:
                            if e2.set != set:
                                continue
                        except:
                            continue
                    l.append(e2)
        return l
        

    def xselect(self, Class, recursive=True, node=None):
        """Same as ``select()``, but this is a generator instead of returning a list"""
        if not node:
            node = self
        for e in self:
            if isinstance(e, Class):
                if not set is None:
                    try:
                        if e.set != set:
                            continue
                    except:
                        continue 
                yield e
            elif recursive:
                for e2 in e.select(Class, recursive, e):
                    if not set is None:
                        try:
                            if e2.set != set:
                                continue
                        except:
                            continue
                    yield e2

    def items(self, founditems=[]):
        """Returns a depth-first flat list of *all* items below this element (not limited to AbstractElement)"""        
        l = []
        for e in self.data:
            if not e in founditems: #prevent going in recursive loops
                l.append(e)
                if isinstance(e, AbstractElement):
                    l += e.items(l)                    
        return l
        
    
    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
            global NSFOLIA
            E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })
            
            
            preamble = []
            try:
                if cls.__doc__:
                    E2 = ElementMaker(namespace="http://relaxng.org/ns/annotation/0.9", nsmap={'a':'http://relaxng.org/ns/annotation/0.9'} )                    
                    preamble.append(E2.documentation(cls.__doc__))
            except AttributeError:
                pass
            

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
            if Attrib.DATETIME in cls.REQUIRED_ATTRIBS:
               attribs.append( E.attribute(E.data(type='dateTime',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'), name='datetime') )
            elif Attrib.DATETIME in cls.OPTIONAL_ATTRIBS:
               attribs.append( E.optional( E.attribute( E.data(type='dateTime',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'),  name='datetime') ) )

            
            #if cls.ALLOWTEXT:
            #    attribs.append( E.optional( E.ref(name='t') ) ) #yes, not actually an attrib, I know, but should go here
                        
            if extraattribs:
                    for e in extraattribs:
                        attribs.append(e) #s
            
            
            elements = [] #(including attributes)
            done = {}
            if includechildren:
                for c in cls.ACCEPTED_DATA:
                    if c.__name__[:8] == 'Abstract' and inspect.isclass(c):
                        for c2 in globals().values():
                            if inspect.isclass(c2) and issubclass(c2, c):
                                try:
                                    if c2.XMLTAG and not (c2.XMLTAG in done):
                                        if c2.OCCURRENCES == 1:
                                            elements.append( E.optional( E.ref(name=c2.XMLTAG) ) )
                                        else:
                                            elements.append( E.zeroOrMore( E.ref(name=c2.XMLTAG) ) )
                                        done[c2.XMLTAG] = True
                                except AttributeError:
                                    continue
                    else:
                        try:
                            if c.XMLTAG and not (c.XMLTAG in done):
                                if c.OCCURRENCES == 1:
                                    elements.append( E.optional( E.ref(name=c.XMLTAG) ) )                                    
                                else:
                                    elements.append( E.zeroOrMore( E.ref(name=c.XMLTAG) ) )                                    
                                done[c.XMLTAG] = True
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
                    
            if not attribs:
                attribs.append( E.empty() )
                
            return E.define( E.element(*(preamble + attribs), **{'name': cls.XMLTAG}), name=cls.XMLTAG, ns=NSFOLIA)
    
    @classmethod
    def parsexml(Class, node, doc):
        """Internal class method used for turning an XML element into an instance of the Class.
        
        Args:
            * ``node`' - XML Element
            * ``doc`` - Document
            
        Returns:
            An instance of the current Class.
        """
        
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
            elif Class is Division and  key == 'type':
                key = 'cls'
                    
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
            instance.correct(generate_id_in=instance, cls=dcoicorrection, original=dcoicorrectionoriginal, new=text)
        return instance        
            
    def resolveword(self, id):
        return None
        
    def remove(self, child):
        """Removes the child element"""
        if not isinstance(child, AbstractElement):
            raise ValueError("Expected AbstractElement, got " + str(type(child)))
        child.parent = None
        self.data.remove(child)
        #delete from index
        if child.id and self.doc and child.id in self.doc.index:
            del self.doc.index[child.id]

class Description(AbstractElement):
    """Description is an element that can be used to associate a description with almost any
    other FoLiA element"""
    XMLTAG = 'desc'
    OCCURRENCES = 1
    
    def __init__(self,doc, *args, **kwargs):
        """Required keyword arguments:
        
                * ``value=``: The text content for the description (``str`` or ``unicode``)  
        
        """
        
        if 'value' in kwargs:
            if isinstance(kwargs['value'], unicode):
                self.value = kwargs['value']
            elif isinstance(kwargs['value'], str):
                self.value = unicode(kwargs['value'],'utf-8')
            elif kwargs['value'] is None:
                self.value = u""
            else:
                raise Exception("value= parameter must be unicode or str instance, got " + str(type(kwargs['value'])))
            del kwargs['value']
        else:
            raise Exception("Description expects value= parameter")
        super(Description,self).__init__(doc, *args, **kwargs)
    
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
        
    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        global NSFOLIA
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.text(), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)                
    
    
class AllowCorrections(object):
    def correct(self, **kwargs):
        """Apply a correction (TODO: documentation to be written still)"""
        
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
            
            if 'new' in kwargs and c.hascurrent():
                #can't add new if there's current, so first set original to current, and then delete current
                
                if 'current' in kwargs:
                    raise Exception("Can't set both new= and current= !") 
                if not 'original' in kwargs:
                    kwargs['original'] = c.current()
                
                c.remove(c.current())                
        else:
            if not 'id' in kwargs and not 'generate_id_in' in kwargs:
                kwargs['generate_id_in'] = self                        
            kwargs2 = copy(kwargs)
            for x in ['new','original','suggestion', 'suggestions','current', 'insertindex']:
                if x in kwargs2:
                    del kwargs2[x]
            c = Correction(self.doc, **kwargs2)                        

        addnew = False
        if 'insertindex' in kwargs:
            insertindex = int(kwargs['insertindex'])
            del kwargs['insertindex']
        else:
            insertindex = -1 #append

        if 'current' in kwargs:
            if 'original' in kwargs or 'new' in kwargs: raise Exception("When setting current=, original= and new= can not be set!") 
            if not isinstance(kwargs['current'], list) and not isinstance(kwargs['current'], tuple): kwargs['current'] = [kwargs['current']] #support both lists (for multiple elements at once), as well as single element
            c.replace(Current(self.doc, *kwargs['current']))
            for o in kwargs['current']: #delete current from current element
                if o in self and isinstance(o, AbstractElement):
                    if insertindex == -1: insertindex = self.data.index(o)
                    self.remove(o) 
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
                if o in self and isinstance(o, AbstractElement):
                    if insertindex == -1: insertindex = self.data.index(o)
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
                elif isinstance(suggestion, list) or isinstance(suggestion, tuple):
                    c.append(Suggestion(self.doc, *suggestion))                   
                else:
                    c.append(Suggestion(self.doc, suggestion))                        
            del kwargs['suggestions']
            
            
        

        if 'reuse' in kwargs:
            if addnew and suggestionsonly:        
                #What was previously only a suggestion, now becomes a real correction
                #If annotator, annotatortypes
                #are associated with the correction as a whole, move it to the suggestions
                #correction-wide annotator, annotatortypes might be overwritten
                for suggestion in c.suggestions():
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
            if insertindex == -1:
                self.append(c)
            else:
                self.insert(insertindex, c)
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
            
    def annotations(self,Class,set=None):        
        """Obtain annotations. Very similar to ``select()`` but raises an error if the annotation was not found.
        
        Arguments:
            * ``Class`` - The Class you want to retrieve (e.g. PosAnnotation)
            * ``set``   - The set you want to retrieve (defaults to None, which selects irregardless of set)
            
        Returns:
            A list of elements
            
        Raises:
            ``NoSuchAnnotation`` if the specified annotation does not exist.
        """
        l = self.select(Class,set,True,['Original','Suggestion','Alternative'])
        if not l:
            raise NoSuchAnnotation()
        else:
            return l
    
    def hasannotation(self,Class,set=None):
        """Returns an integer indicating whether such as annotation exists, and if so, how many. See ``annotations()`` for a description of the parameters."""
        l = self.select(Class,set,True,['Original','Suggestion','Alternative'])
        return len(l)

    def annotation(self, type, set=None):
        """Will return a **single** annotation (even if there are multiple). Raises a ``NoSuchAnnotation`` exception if none was found"""
        l = self.select(type,set,True,['Original','Suggestion','Alternative'])
        if len(l) >= 1:
            return l[0]
        else:
            raise NoSuchAnnotation()            

    def alternatives(self, annotationtype=None, set=None):
        """Obtain a list of alternatives, either all or only of a specific annotation type, and possibly restrained also by set.
        
        Arguments:
            * ``annotationtype`` - The kind of annotation to retrieve: member of the AnnotationType class. Or None to select alternatives regardless of the annotations they contain.
            * ``set``   - The set you want to retrieve (defaults to None, which selects irregardless of set)
            
        Returns:
            List of Alternative elements
        """
        l = []
        if inspect.isclass(annotationtype): annotationtype = annotationtype.ANNOTATIONTYPE
        for e in self.select(Alternative,None, True, ['Original','Suggestion']):
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
            if self.id:
                id = self.id
            else:
                #this element has no ID, fall back to closest parent ID:
                e = self
                while e.parent:                    
                    if e.id:
                        id = e.id
                        break
                    e = e.parent                
            id = id + '.' + xmltag + '.' + str(self._getmaxid(xmltag) + i)
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
        """See ``AbstractElement.append()``"""
        e = super(AbstractStructureElement,self).append(child, *args, **kwargs)
        self._setmaxid(child)     
        return e
                

    def words(self, index = None):
        """Returns a list of Word elements found (recursively) under this element.
        
        Arguments:
            * ``index``: If set to an integer, will retrieve and return the n'th element (starting at 0) instead of returning the list of all
        """
        if index is None:
            return self.select(Word,None,True,['Original','Suggestion','Alternative'])
        else:
            return self.select(Word,None,True,['Original','Suggestion','Alternative'])[index]            
            
                   
    def paragraphs(self, index = None):
        """Returns a list of Paragraph elements found (recursively) under this element.

        Arguments:
            * ``index``: If set to an integer, will retrieve and return the n'th element (starting at 0) instead of returning the list of all        
        """
        if index is None:
            return self.select(Paragraph,None,True,['Original','Suggestion','Alternative'])
        else:
            return self.select(Paragraph,None,True,['Original','Suggestion','Alternative'])[index]
    
    def sentences(self, index = None):
        """Returns a list of Sentence elements found (recursively) under this element
        
        Arguments:
            * ``index``: If set to an integer, will retrieve and return the n'th element (starting at 0) instead of returning the list of all
        """
        if index is None:
            return self.select(Sentence,None,True,['Quote','Original','Suggestion','Alternative'])
        else:
            return self.select(Sentence,None,True,['Quote','Original','Suggestion','Alternative'])[index]
            
    def __eq__(self, other):
        return super(AbstractStructureElement, self).__eq__(other)

class AbstractAnnotation(AbstractElement):
    def feat(self,subset):
        """Obtain the feature value of the specific subset.
        
        Example::
        
            sense = word.annotation(folia.Sense)
            synset = sense.feat('synset')        
        """
        
        for f in self:
            if isinstance(f, Feature) and f.subset == subset:
                return f.cls

class AbstractTokenAnnotation(AbstractAnnotation, AllowGenerateID): 
    """Abstract element, all token annotation elements are derived from this class"""

    OCCURRENCESPERSET = 1 #Do not allow duplicates within the same set

    def append(self, child, *args, **kwargs):
        """See ``AbstractElement.append()``"""
        e = super(AbstractTokenAnnotation,self).append(child, *args, **kwargs)
        self._setmaxid(child)
        return e

class AbstractExtendedTokenAnnotation(AbstractTokenAnnotation): 
    pass

class TextContent(AbstractElement):
    """Text content element (``t``), holds text to be associated with whatever element the text content element is a child of.
    
    Text content elements have an associated correction level, indicating whether the text they hold is in a pre-corrected or post-corrected state. There can be only once of each level. Text content elements
    on structure elements like ``Paragraph`` and ``Sentence`` are by definition untokenised. Only on ``Word`` level and deeper they are by definition tokenised.
    
    Text content elements can specify offset that refer to text at a higher parent level. Use the following keyword arguments:
        * ``ref=``: The instance to point to, this points to the element holding the text content element, not the text content element itself.
        * ``offset=``: The offset where this text is found, offsets start at 0
        * ``length=``: The length of the text found, only needs to be specified if different from the current length.
        * ``newoffset=``: The new offset, after correction, where this text is found, offsets start at 0.         
    """
    XMLTAG = 't'
    
    def __init__(self, doc, *args, **kwargs):
        """Required keyword arguments:
            
                * ``value=``: Set to a unicode or str containing the text
                * ``corrected=``: Correction level, can be set to TextCorrectionLevel.UNCORRECTED or TextCorrectionLevel.CORRECTED
            
            Example::
            
                text = folia.TextContent(doc, value='test', corrected=folia.TextCorrectionLevel.CORRECTED)
            
        """
        
        
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
        elif not kwargs['value']:
            kwargs['value'] = u""
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
        """Obtain the text (unicode instance)"""
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
        """This method is not implemented on purpose"""
        raise NotImplementedError #on purpose
        
        
    def postappend(self):
        """(Method for internal usage, see ``AbstractElement.postappend()``)"""
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
        
        super(TextContent, self).postappend()
        
    
    def __iter__(self):
        """Iterate over the text string (character by character)"""
        return iter(self.value)
    
    def __len__(self): 
        """Get the length of the text"""
        return len(self.value)
    
    @classmethod
    def findreplacables(Class, parent, set, **kwargs):
        """(Method for internal usage, see AbstractElement)"""
        #some extra behaviour for text content elements, replace also based on the 'corrected' attribute:
        if not 'corrected' in kwargs:
            if 'instance' in kwargs:
                kwargs['corrected'] = instance.corrected
            elif Class.MINTEXTCORRECTIONLEVEL == TextCorrectionLevel.UNCORRECTED:
                kwargs['corrected'] = TextCorrectionLevel.UNCORRECTED
            else:
                kwargs['corrected'] = TextCorrectionLevel.CORRECTED
        replace = super(TextContent, Class).findreplacables(parent, set, **kwargs)
        replace = [ x for x in replace if x.corrected == kwargs['corrected']]
        del kwargs['corrected'] #always delete what we processed
        return replace
        
        
    @classmethod
    def parsexml(Class, node, doc):
        """(Method for internal usage, see AbstractElement)"""
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
        
        if node.text:
            kwargs['value'] = node.text
        else:
            kwargs['value'] = ""
            
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
        elif self.corrected == TextCorrectionLevel.CORRECTED and self.parent and self.parent.MINTEXTCORRECTIONLEVEL < TextCorrectionLevel.CORRECTED:
            attribs['{' + NSFOLIA + '}corrected'] = 'yes'
            
        return E.t(self.value, **attribs)
        
    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
            global NSFOLIA
            E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
            return E.define( E.element(E.text(), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)

class Linebreak(AbstractStructureElement):
    """Line break element, signals a line break"""
    REQUIRED_ATTRIBS = ()
    ACCEPTED_DATA = ()
    XMLTAG = 'br'
    
class Whitespace(AbstractStructureElement):
    """Whitespace element, signals a vertical whitespace"""
    REQUIRED_ATTRIBS = ()
    ACCEPTED_DATA = ()
    XMLTAG = 'whitespace'    
        
class Word(AbstractStructureElement, AllowCorrections):
    """Word (aka token) element. Holds a word/token and all its related token annotations."""
    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    XMLTAG = 'w'
    ANNOTATIONTYPE = AnnotationType.TOKEN
    #ACCEPTED_DATA DEFINED LATER (after Correction)
    
    MINTEXTCORRECTIONLEVEL = TextCorrectionLevel.CORRECTED
    TEXTDELIMITER = " "
    
    def __init__(self, doc, *args, **kwargs):
        """Keyword arguments:
        
            * ``space=``: Boolean indicating whether this token is followed by a space (defaults to True)
            
            Example::
                
                sentence.append( folia.Word, 'This')
                sentence.append( folia.Word, 'is')
                sentence.append( folia.Word, 'a')
                sentence.append( folia.Word, 'test', space=False)
                sentence.append( folia.Word, '.')
        """
        self.space = True
                      
        if 'space' in kwargs:            
            self.space = kwargs['space']
            del kwargs['space']
        super(Word,self).__init__(doc, *args, **kwargs)
                        

    def sentence(self):
        """Obtain the sentence this word is a part of, otherwise return None"""
        e = self;
        while e.parent: 
            if isinstance(e, Sentence):
                return e
            e = e.parent
        return None
        
        
    def paragraph(self):
        """Obtain the paragraph this word is a part of, otherwise return None"""
        e = self;
        while e.parent: 
            if isinstance(e, Paragraph):
                return e
            e = e.parent  
        return None        
        
    def division(self):
        """Obtain the deepest division this word is a part of, otherwise return None"""
        e = self;
        while e.parent: 
            if isinstance(e, Division):
                return e
            e = e.parent  
        return None
                
        

    def incorrection(self):
        """Is this word part of a correction? If it is, it returns the Correction element (evaluating to True), otherwise it returns None"""
        e = self
                
        while not e.parent is None:            
                if isinstance(e, Correction):
                    return e
                if isinstance(e, Sentence):
                    break
                e = e.parent
            
        return None
        
        

    def pos(self,set=None):
        """Shortcut: returns the FoLiA class of the PoS annotation (will return only one if there are multiple!)"""
        return self.annotation(PosAnnotation,set).cls
            
    def lemma(self, set=None):
        """Shortcut: returns the FoLiA class of the lemma annotation (will return only one if there are multiple!)"""        
        return self.annotation(LemmaAnnotation,set).cls

    def sense(self,set=None):
        """Shortcut: returns the FoLiA class of the sense annotation (will return only one if there are multiple!)"""        
        return self.annotation(SenseAnnotation,set).cls
        
    def domain(self,set=None):
        """Shortcut: returns the FoLiA class of the domain annotation (will return only one if there are multiple!)"""        
        return self.annotation(DomainAnnotation,set).cls     

    def overridetextdelimiter(self):
        """May return a customised text delimiter that overrides the default text delimiter set by the parent. Defaults to None (do not override). Mostly for internal use."""
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


    def next(self):
        """Returns the next word in the sentence, or None if no next word was found. This method does not cross sentence boundaries."""
        words = self.sentence().words()
        i = words.index(self) + 1
        if i < len(words):
            return words[i]
        else:
            return None
        

    def previous(self):
        """Returns the previous word in the sentence, or None if no next word was found. This method does not cross sentence boundaries."""
        words = self.sentence().words()
        i = words.index(self) - 1
        if i >= 0:    
            return words[i]
        else:
            return None
            
    def leftcontext(self, size, placeholder=None):
        """Returns the left context for a word. This method crosses sentence/paragraph boundaries"""
        if size == 0: return [] #for efficiency                
        words = self.doc.words()
        i = words.index(self)
        begin = i - size
        if begin < 0: 
            return [placeholder] * (begin * -1) + words[0:i]
        else:
            return words[begin:i]
        
    def rightcontext(self, size, placeholder=None):
        """Returns the right context for a word. This method crosses sentence/paragraph boundaries"""
        if size == 0: return [] #for efficiency                
        words = self.doc.words()
        i = words.index(self)
        begin = i+1
        end = begin + size
        rightcontext = words[begin:end]
        if len(rightcontext) < size:
            rightcontext += (size - len(rightcontext)) * [placeholder]
        return rightcontext
        
        
    def context(self, size, placeholder=None):
        """Returns this word in context, {size} words to the left, the current word, and {size} words to the right"""
        return self.leftcontext(size, placeholder) + [self] + self.rightcontext(size, placeholder)
    

class Feature(AbstractElement):
    """Feature elements can be used to associate subsets and subclasses with almost any
    annotation element"""
    
    XMLTAG = 'feat'
    XMLATTRIB = None
    SUBSET = None
    
    def __init__(self,doc, *args, **kwargs):
        """Required keyword arguments:
        
           * ``subset=``: the subset
           * ``cls=``: the class
        """
        
        self.id = None
        self.set = None
        self.data = []
        self.annotator = None
        self.annotatortype = None
        self.confidence = None
        self.n = None
        self.datetime = None
        if not isinstance(doc, Document) and not (doc is None):
            raise Exception("First argument of Feature constructor must be a Document instance, not " + str(type(doc)))
        self.doc = doc
        
        
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
    def relaxng(cls, includechildren=True, extraattribs = None, extraelements=None):
        global NSFOLIA
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.attribute(name='subset'), E.attribute(name='class'),name=cls.XMLTAG), name=cls.XMLTAG,ns=NSFOLIA)


class AbstractSubtokenAnnotation(AbstractAnnotation, AllowGenerateID): 
    """Abstract element, all subtoken annotation elements are derived from this class"""
    OCCURRENCESPERSET = 0 #Allow duplicates within the same set
    
    
class AbstractSpanAnnotation(AbstractAnnotation, AllowGenerateID): 
    """Abstract element, all span annotation elements are derived from this class"""
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
            

class AbstractAnnotationLayer(AbstractElement, AllowGenerateID):
    """Annotation layers for Span Annotation are derived from this abstract base class"""
    OPTIONAL_ATTRIBS = (Attrib.CLASS,)
    PRINTABLE = False
    
    def __init__(self, doc, *args, **kwargs):
        if 'set' in kwargs:
            self.set = kwargs['set']
            del kwargs['set']
        super(AbstractAnnotationLayer,self).__init__(doc, *args, **kwargs)
        
class AbstractSubtokenAnnotationLayer(AbstractElement, AllowGenerateID):
    """Annotation layers for Subtoken Annotation are derived from this abstract base class"""        
    OPTIONAL_ATTRIBS = (Attrib.CLASS,)
    PRINTABLE = False
    
    def __init__(self, doc, *args, **kwargs):
        if 'set' in kwargs:
            self.set = kwargs['set']
            del kwargs['set']
        super(AbstractSubtokenAnnotationLayer,self).__init__(doc, *args, **kwargs)
                
        
class AbstractCorrectionChild(AbstractElement):
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ACCEPTED_DATA = (AbstractTokenAnnotation, Word, TextContent, Description)
    TEXTDELIMITER = ""

class ErrorDetection(AbstractExtendedTokenAnnotation):
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
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
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
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
            
class Correction(AbstractExtendedTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ACCEPTED_DATA = (New,Original,Current, Suggestion, Description)
    ANNOTATIONTYPE = AnnotationType.CORRECTION
    XMLTAG = 'correction'
    OCCURRENCESPERSET = 0 #Allow duplicates within the same set (0= unlimited)
    TEXTDELIMITER = ""
    
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
    """Element grouping alternative token annotation(s). Multiple alternative elements may occur, each denoting a different alternative. Elements grouped inside an alternative block are considered dependent."""
    REQUIRED_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (AbstractTokenAnnotation, Correction)
    ANNOTATIONTYPE = AnnotationType.ALTERNATIVE
    XMLTAG = 'alt'
    PRINTABLE = False    


Word.ACCEPTED_DATA = (AbstractTokenAnnotation, TextContent, Alternative, Description, AbstractSubtokenAnnotationLayer)


class AlternativeLayers(AbstractElement):
    """Element grouping alternative subtoken annotation(s). Multiple altlayers elements may occur, each denoting a different alternative. Elements grouped inside an alternative block are considered dependent."""
    REQUIRED_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (AbstractAnnotationLayer,)    
    XMLTAG = 'altlayers'
    PRINTABLE = False    
    

class WordReference(AbstractElement):
    """Word reference. Use to refer to words from span annotation elements. The Python class will only be used when word reference can not be resolved, if they can, Word objects will be used"""
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
        self.datetime = None
        self.data = []
    
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
            return WordReference(doc, id=id)    

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
            global NSFOLIA
            E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
            return E.define( E.element(E.attribute(E.text(), name='id'), E.optional(E.attribute(E.text(), name='t')), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)

            
class AlignReference(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    XMLTAG = 'aref'    
    pass #TODO: IMPLEMENT
        
    
    
    
        
class SyntacticUnit(AbstractSpanAnnotation):
    """Syntactic Unit, span annotation element to be used in SyntaxLayer"""
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ANNOTATIONTYPE = AnnotationType.SYNTAX
    XMLTAG = 'su'
    
SyntacticUnit.ACCEPTED_DATA = (SyntacticUnit,WordReference, Description, Feature)

class Chunk(AbstractSpanAnnotation):
    """Chunk element, span annotation element to be used in ChunkingLayer"""
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ACCEPTED_DATA = (WordReference, Description, Feature)
    ANNOTATIONTYPE = AnnotationType.CHUNKING
    XMLTAG = 'chunk'

class Entity(AbstractSpanAnnotation):
    """Entity element, for named entities, span annotation element to be used in EntitiesLayer"""
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ACCEPTED_DATA = (WordReference, Description, Feature)
    ANNOTATIONTYPE = AnnotationType.ENTITY
    XMLTAG = 'entity'
    
class Morpheme(AbstractSubtokenAnnotation):
    """Morpheme element, represents one morpheme in morphological analysis, subtoken annotation element to be used in MorphologyLayer"""
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ACCEPTED_DATA = (Feature,TextContent)
    ANNOTATIONTYPE = AnnotationType.MORPHOLOGICAL
    XMLTAG = 'morpheme'

class Subentity(AbstractSubtokenAnnotation):
    """Subentity element, for named entities within a single token, subtoken annotation element to be used in SubentitiesLayer"""
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ACCEPTED_DATA = (Feature,TextContent)
    ANNOTATIONTYPE = AnnotationType.SUBENTITY
    XMLTAG = 'subentity'
        
    
class SyntaxLayer(AbstractAnnotationLayer):
    """Syntax Layer: Annotation layer for SyntacticUnit span annotation elements"""
    ACCEPTED_DATA = (SyntacticUnit,Description)
    XMLTAG = 'syntax'

class ChunkingLayer(AbstractAnnotationLayer):
    """Chunking Layer: Annotation layer for Chunk span annotation elements"""
    ACCEPTED_DATA = (Chunk,Description)    
    XMLTAG = 'chunking'

class EntitiesLayer(AbstractAnnotationLayer):
    """Entities Layer: Annotation layer for Entity span annotation elements. For named entities."""
    ACCEPTED_DATA = (Entity,Description)
    XMLTAG = 'entities'

class MorphologyLayer(AbstractSubtokenAnnotationLayer):
    """Morphology Layer: Annotation layer for Morpheme subtoken annotation elements. For morphological analysis."""
    ACCEPTED_DATA = (Morpheme,)
    XMLTAG = 'morphology'    

class SubentitiesLayer(AbstractSubtokenAnnotationLayer):
    """Subentities Layer: Annotation layer for Subentity subtoken annotation elements. For named entities within a single token."""
    ACCEPTED_DATA = (Subentity,)
    XMLTAG = 'subentities'
        
    
    
class PosAnnotation(AbstractTokenAnnotation):
    """Part-of-Speech annotation:  a token annotation element"""
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ANNOTATIONTYPE = AnnotationType.POS
    ACCEPTED_DATA = (Feature,Description)
    XMLTAG = 'pos'

class LemmaAnnotation(AbstractTokenAnnotation):
    """Lemma annotation:  a token annotation element"""
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ANNOTATIONTYPE = AnnotationType.LEMMA
    ACCEPTED_DATA = (Feature,Description)
    XMLTAG = 'lemma'
    
class PhonAnnotation(AbstractTokenAnnotation):
    """Phonetic annotation:  a token annotation element"""
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ANNOTATIONTYPE = AnnotationType.PHON
    ACCEPTED_DATA = (Feature,Description)
    XMLTAG = 'phon'


class DomainAnnotation(AbstractExtendedTokenAnnotation):
    """Domain annotation:  an extended token annotation element"""
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ANNOTATIONTYPE = AnnotationType.DOMAIN
    ACCEPTED_DATA = (Feature,Description)
    XMLTAG = 'domain'

class SynsetFeature(Feature):
    """Synset feature, to be used within Sense"""
    XMLATTRIB = 'synset' #allow feature as attribute
    XMLTAG = 'synset'
    ANNOTATIONTYPE = AnnotationType.SENSE
    SUBSET = 'synset' #associated subset
    

class SenseAnnotation(AbstractTokenAnnotation):
    """Sense annotation: a token annotation element"""
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ANNOTATIONTYPE = AnnotationType.SENSE
    ACCEPTED_DATA = (Feature,SynsetFeature, Description)
    XMLTAG = 'sense'
    
class SubjectivityAnnotation(AbstractTokenAnnotation):
    """Subjectivity annotation: a token annotation element"""
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.DATETIME)
    ANNOTATIONTYPE = AnnotationType.SUBJECTIVITY
    ACCEPTED_DATA = (Feature, Description)
    XMLTAG = 'subjectivity'
    

class Quote(AbstractStructureElement):
    """Quote: a structure element. For quotes/citations. May hold words or sentences."""
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = (Attrib.ID,)    
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
    """Sentence element. A structure element. Represents a sentence and holds all its words (and possibly other structure such as LineBreaks, Whitespace and Quotes)"""
    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Word, Quote, AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Correction, TextContent, Description,  Linebreak, Whitespace)
    XMLTAG = 's'
    TEXTDELIMITER = ' '
    
    def __init__(self,  doc, *args, **kwargs):
        """
        
            Example 1::
            
                sentence = paragraph.append( folia.Sentence)
                
                sentence.append( folia.Word, 'This')
                sentence.append( folia.Word, 'is')
                sentence.append( folia.Word, 'a')
                sentence.append( folia.Word, 'test', space=False)
                sentence.append( folia.Word, '.')
                
            Example 2::
            
                sentence = folia.Sentence( doc, folia.Word(doc, 'This'),  folia.Word(doc, 'is'),  folia.Word(doc, 'a'),  folia.Word(doc, 'test', space=False),  folia.Word(doc, '.') )
                paragraph.append(sentence)
                
        """
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
        """Obtain the paragraph this sentence is a part of (None otherwise)"""
        e = self;
        while e.parent: 
            if isinstance(e, Paragraph):
                return e
            e = e.parent  
        return None
 
    def division(self):
        """Obtain the division this sentence is a part of (None otherwise)"""
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
        """TODO: Write documentation"""
        if isinstance(originalword, str) or isinstance(originalword, unicode):
            originalword = self.doc[originalword]
        return self.correctwords([originalword], newwords, **kwargs)
            
            

    def mergewords(self, newword, *originalwords, **kwargs):
        """TODO: Write documentation"""
        return self.correctwords(originalwords, [newword], **kwargs)
            
    def deleteword(self, word, **kwargs):
        """TODO: Write documentation"""
        if isinstance(word, str) or isinstance(word, unicode):
            word = self.doc[word]   
        return self.correctwords([word], [], **kwargs)
                
        
    def insertword(self, newword, prevword, **kwargs):
        if prevword:
            if isinstance(prevword, str) or isinstance(prevword, unicode):
                prevword = self.doc[prevword]            
            if not prevword in self or not isinstance(prevword, Word):
                raise Exception("Previous word not found or not instance of Word!")
            if not isinstance(newword, Word):
                raise Exception("New word no instance of Word!")
            
            kwargs['insertindex'] = self.data.index(prevword) + 1
        else:
            kwargs['insertindex'] = 0
        return self.correctwords([], [newword], **kwargs)



Quote.ACCEPTED_DATA = (Word, Sentence, Quote, TextContent, Description)        

class Paragraph(AbstractStructureElement):    
    """Paragraph element. A structure element. Represents a paragraph and holds all its sentences (and possibly other structure Whitespace and Quotes)."""

    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Sentence, AbstractExtendedTokenAnnotation, Correction, TextContent, Description, Linebreak, Whitespace)
    XMLTAG = 'p'
    TEXTDELIMITER = "\n"
            
                
class Head(AbstractStructureElement):
    """Head element. A structure element. Acts as the header/title of a division. There may be one per division. Contains sentences."""
    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Sentence,Description)
    OCCURRENCES = 1
    TEXTDELIMITER = ' '
    XMLTAG = 'head'          
        
#class Query(object):
#    """An XPath query on a FoLiA document"""
#    def __init__(self, files, expression):
#        if not isinstance(files, list) and not isinstance(files, tuple):
#            self.files = [files]
#        else:
#            self.files = files
#        expression = expression.replace("active()", "(not(ancestor::original) and not(ancestor::suggestion) and not(ancestor::alternative))")
#        self.expression = expression
#        
#    def __iter__(self):
#        for filename in files:
#            doc = Document(partial=filename)
#            
#    
#        raise NotImplementedError

class RegExp(object):
    def __init__(self, regexp):
        self.regexp = re.compile(regexp)
        
    def __eq__(self, value):
        return self.regexp.match(value)
        
        
class Pattern(object):
    def __init__(self, *args, **kwargs):
        if not all( ( (x is True or isinstance(x,RegExp) or isinstance(x, str) or isinstance(x, unicode) or isinstance(x, list) or isinstance(x, tuple)) for x in args )):
            raise TypeError
        self.sequence = args
        
        if 'matchannotation' in kwargs:
            self.matchannotation = kwargs['matchannotation']
            del kwargs['matchannotation']
        else:
            self.matchannotation = None
        if 'matchannotationset' in kwargs:
            self.matchannotationset = kwargs['matchannotationset']
            del kwargs['matchannotationset']
        else:
            self.matchannotationset = None
        if 'casesensitive' in kwargs:
            self.casesensitive = bool(kwargs['casesensitive'])
            del kwargs['casesensitive']
        else:
            self.casesensitive = False
        for key in kwargs.keys():
            raise Exception("Unknown keyword parameter: " + key)            
            
        if not self.casesensitive:
            if all( ( isinstance(x, str) or isinstance(x, unicode) for x in self.sequence) ):
                self.sequence = [ x.lower() for x in self.sequence ]

    def __nonzero__(self):
        return True
        
    def __len__(self):
        return len(self.sequence)
        
    def __getitem__(self, index):
        return self.sequence[index]        

    def __getslice__(self, begin,end):
        return self.sequence[begin:end]   
        
    def variablesize(self):
        return ('*' in self.sequence)
        
    def variablewildcards(self):
        wildcards = []
        for i,x in enumerate(self.sequence):
            if x == '*':
                wildcards.append(i)
        return wildcards
            
        
    def __repr__(self):
        return repr(self.sequence)

        
    def resolve(self,size, distribution):
        """Resolve a variable sized pattern to all patterns of a certain fixed size"""
        if not self.variablesize():
            raise Exception("Can only resize patterns with * wildcards")
                
        nrofwildcards = 0
        for i,x in enumerate(self.sequence):
            if x == '*':
                nrofwildcards += 1
            
        assert (len(distribution) == nrofwildcards)
        
        wildcardnr = 0        
        newsequence = []
        for i,x in enumerate(self.sequence):
            if x == '*':
                newsequence += [True] * distribution[wildcardnr]
                wildcardnr += 1
            else:
                newsequence.append(x)
        d = { 'matchannotation':self.matchannotation, 'matchannotationset':self.matchannotationset, 'casesensitive':self.casesensitive }
        yield Pattern(*newsequence, **d )
    

        
class Document(object):
    """This is the FoLiA Document, all elements have to be associated with a FoLiA document. Besides holding elements, the document hold metadata including declaration, and an index of all IDs."""
    
    IDSEPARATOR = '.'
    
    def __init__(self, *args, **kwargs):
        """Start/load a FoLiA document:
        
        There are four ways of loading a FoLiA document::
        
        1) Create a new document by specifying an *ID*::
        
            doc = folia.Document(id='test')
        
        2) Load a document from FoLiA or D-Coi XML file::
        
            doc = folia.Document(file='/path/to/doc.xml')

        3) Load a document from an XML string::
        
            doc = folia.Document(string='<FoLiA>....</FoLiA>')
        
        4) Load a document by passing a parse xml tree (lxml.etree):
    
            doc = folia.Document(tree=xmltree)
    
        Optional keyword arguments:
        
            ``debug=``:  Boolean to enable/disable debug
        """
        
        
        
        
        self.data = [] #will hold all texts (usually only one)
        
        self.annotationdefaults = {}
        self.annotations = [] #Ordered list of incorporated annotations ['token','pos', etc..]
        self.index = {} #all IDs go here
        
        self.metadata = {} #will point to XML Element holding IMDI or CMDI metadata
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
        """Load a FoLiA or D-Coi XML file"""
        self.tree = ElementTree.parse(filename)
        self.parsexml(self.tree.getroot())

    def items(self):
        """Returns a depth-first flat list of all items in the document"""
        l = []
        for e in self.data:
            l += e.items()
        return l
            
    def xpath(self, query):
        """Run Xpath expression and parse the resulting elements"""
        for result in self.tree.xpath(query,namespaces={'f': 'http://ilk.uvt.nl/folia','folia': 'http://ilk.uvt.nl/folia' }):
            yield self.parsexml(result)
            
            
    def findwords(self, *args, **kwargs):
        if 'leftcontext' in kwargs:
            leftcontext = kwargs['leftcontext']
            del kwargs['leftcontext']
        else:
            leftcontext = 0
        if 'rightcontext' in kwargs:
            rightcontext =  kwargs['rightcontext']            
            del kwargs['rightcontext']
        else:
            rightcontext = 0
        if 'maxgapsize' in kwargs:
            maxgapsize = kwargs['maxgapsize']
            del kwargs['maxgapsize']
        else:
            maxgapsize = 10
        for key in kwargs.keys():
            raise Exception("Unknown keyword parameter: " + key)
                
        matchcursor = 0
        matched = []
        
        #shortcut for when no Pattern is passed, make one on the fly
        if len(args) == 1 and not isinstance(args[0], Pattern):
            if not isinstance(args[0], list) and not  isinstance(args[0], tuple):
                args[0] = [args[0]] 
            args[0] = Pattern(*args[0])
                
        
        
        unsetwildcards = False
        variablewildcards = None
        prevsize = -1
        minsize = 99999
        #sanity check
        for i, pattern in enumerate(args):
            if not isinstance(pattern, Pattern):
                raise TypeError("You must pass instances of Sequence to findwords")
            if prevsize > -1 and len(pattern) != prevsize:                
                raise Exception("If multiple patterns are provided, they must all have the same length!")
            if pattern.variablesize():   
                if not variablewildcards and i > 0:
                    unsetwildcards = True
                else:
                    if variablewildcards and pattern.variablewildcards() != variablewildcards:
                        raise Exception("If multiple patterns are provided with variable wildcards, then these wildcards must all be in the same positions!")                        
                    variablewildcards = pattern.variablewildcards()
            elif variablewildcards:
                unsetwildcards = True
            prevsize = len(pattern)
                            
        if unsetwildcards:
            #one pattern determines a fixed length whilst others are variable, rewrite all to fixed length
            #converting multi-span * wildcards into single-span 'True' wildcards
            for pattern in args:
                if pattern.variablesize():
                    pattern.sequence = [ True if x == '*' else x for x in pattern.sequence ]
            variablesize = False
            
        if variablewildcards:
            #one or more items have a * wildcard, which may span multiple tokens. Resolve this to a wider range of simpler patterns
            
            #we're not commited to a particular size, expand to various ones
            for size in range(len(variablewildcards), maxgapsize+1):
                for distribution in  pynlpl.math.sum_to_n(size, len(variablewildcards)): #gap distributions, (amount) of 'True' wildcards
                    patterns = []
                    for pattern in args:
                        if pattern.variablesize():
                            patterns += list(pattern.resolve(size,distribution))
                        else:
                            patterns.append( pattern )
                    for match in self.findwords(*patterns, **{'leftcontext':leftcontext,'rightcontext':rightcontext}):
                        yield match
                                            
        else:                
            patterns = args
            buffers = []
            
            for word in self.words():
                buffers.append( [] ) #Add a new empty buffer for every word
                match = [None] * len(buffers)
                for pattern in patterns:
                    #find value to match against
                    if not pattern.matchannotation:
                        value = word.text()
                    else:
                        if pattern.matchannotationset:
                            items = word.select(pattern.matchannotation, pattern.matchannotationset, True, [Original, Suggestion, Alternative] )                            
                        else:
                            try:
                                set = self.defaultset(pattern.matchannotation.ANNOTATIONTYPE)                            
                                items = word.select(pattern.matchannotation, set, True, [Original, Suggestion, Alternative] )        
                            except KeyError:
                                continue
                        if len(items) == 1:
                            value = items[0].cls
                        else:
                            continue
                            
                    if not pattern.casesensitive:
                        value = value.lower()

                    
                    for i, buffer in enumerate(buffers):
                        if match[i] is False:
                            continue
                        matchcursor = len(buffer)
                        if (value == pattern.sequence[matchcursor] or pattern.sequence[matchcursor] is True or (isinstance(pattern.sequence[matchcursor], tuple) and value in pattern.sequence[matchcursor])):
                            match[i] = True
                        else:
                            match[i] = False
                    
                        
                for buffer, matches in zip(buffers, match):
                    if matches:
                        buffer.append(word) #add the word
                        if len(buffer) == len(pattern.sequence):
                            yield buffer[0].leftcontext(leftcontext) + buffer + buffer[-1].rightcontext(rightcontext)
                            buffers.remove(buffer)
                    else:
                        buffers.remove(buffer) #remove buffer
            
            
    def save(self, filename=None):
        """Save the document to FoLiA XML.
        
        Arguments:
            * ``filename=``: The filename to save to. If not set (None), saves to the same file as loaded from.
        """
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
        self.metadata = {}
        #TODO: Parse CMDI
        
        
    def __len__(self):
        return len(self.data)
        
    def __nonzero__(self):
        return True #documents always evaluate to True!
    
    def __iter__(self):
        for text in self.data:
            yield text   
        
    def __getitem__(self, key):
        """Obtain an element by ID from the document index.
        
        Example::
        
            word = doc['example.p.4.s.10.w.3']        
        """
        try:
            if isinstance(key, int):
                return self.data[key]
            else:
                return self.index[key]
        except KeyError:
            raise
            
    def append(self,text):
        """Add a text to the document:
                
        Example 1::
        
            doc.append(folia.Text)
        
        Example 2::        
            doc.append( folia.Text(doc, id='example.text') )
                    
        
        """
        if text is Text:
            text = Text(id=self.id + '.text.' + str(count(self.data)) )            
        else:
            assert isinstance(text, Text)        
        self.data.append(text)
        return text

    def create(self, Class, *args, **kwargs):
        """Create an element associated with this Document. This method may be obsolete and removed later."""
        return Class(self, *args, **kwargs)

    def xmldeclarations(self):
        l = []
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        
        for annotationtype, set in self.annotations:
            label = None
            #Find the 'label' for the declarations dynamically (aka: AnnotationType --> String)
            for key, value in vars(AnnotationType).items():
                if value == annotationtype:
                    label = key
                    break
            #gather attribs
            
            attribs = {}
            if set:
                attribs['{' + NSFOLIA + '}set'] = set

            for key, value in self.annotationdefaults[annotationtype][set].items():                
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
            if not self.metadatafile:
                for key, value in self.metadata.items():
                    e.append(E.meta(value,id=key) )
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
                    
                if 'set' in subnode.attrib and subnode.attrib['set']:
                    set = subnode.attrib['set']
                else:
                    set = None
                self.annotations.append( (type, set) )
                
                defaults = {}
                if 'annotator' in subnode.attrib:
                    defaults['annotator'] = subnode.attrib['annotator']
                if 'annotatortype' in subnode.attrib:
                    if subnode.attrib['annotatortype'] == 'auto':
                        defaults['annotatortype'] = AnnotatorType.AUTO
                    else:
                        defaults['annotatortype'] = AnnotatorType.MANUAL                                                
                if not type in self.annotationdefaults:
                    self.annotationdefaults[type] = {}
                self.annotationdefaults[type][set] = defaults
                
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
        
    def declare(self, annotationtype, set, **kwargs):
        if inspect.isclass(annotationtype):
            annotationtype = annotationtype.ANNOTATIONTYPE 
        if not (annotationtype, set) in self.annotations:
            self.annotations.append( (annotationtype,set) )
        if not annotationtype in self.annotationdefaults:
            self.annotationdefaults[annotationtype] = {}
        self.annotationdefaults[annotationtype][set] = kwargs
    
    def declared(self, annotationtype, set):
        if inspect.isclass(annotationtype) and isinstance(annotationtype,AbstractElement): annotationtype = annotationtype.ANNOTATIONTYPE
        return ( (annotationtype,set) in self.annotations)
        
        
    def defaultset(self, annotationtype):
        if inspect.isclass(annotationtype) and isinstance(annotationtype,AbstractElement): annotationtype = annotationtype.ANNOTATIONTYPE
        try:
            return self.annotationdefaults[annotationtype].keys()[0]
        except IndexError:
            raise NoDefaultError
        
    
    def defaultannotator(self, annotationtype, set=None):
        if inspect.isclass(annotationtype) and isinstance(annotationtype,AbstractElement): annotationtype = annotationtype.ANNOTATIONTYPE
        try:
            return self.annotationdefaults[annotationtype][set]['annotator']        
        except KeyError:
            raise NoDefaultError
            
    def defaultannotatortype(self, annotationtype,set=None):
        try:
            return self.annotationdefaults[annotationtype][set]['annotatortype']        
        except KeyError:
            raise NoDefaultError
            

            
        
    def title(self, value=None):
        """No arguments: Get the document's title from metadata
           Argument: Set the document's title in metadata
        """ 
        if not (value is None):
            if (self.metadatatype == MetaDataType.NATIVE):
                 self.metadata['title'] = value                
            else:
                self._title = value  
        if (self.metadatatype == MetaDataType.NATIVE):      
            if 'title' in self.metadata:
                return self.metadata['title']
            else:
                return None
        else:
            return self._title
        
    def date(self, value=None):
        """No arguments: Get the document's date from metadata
           Argument: Set the document's date in metadata
        """         
        if not (value is None):
            if (self.metadatatype == MetaDataType.NATIVE):
                 self.metadata['date'] = value                
            else:
                self._date = value  
        if (self.metadatatype == MetaDataType.NATIVE):      
            if 'date' in self.metadata:
                return self.metadata['date']
            else:
                return None
        else:
            return self._date       
       
    def publisher(self, value=None):
        """No arguments: Get the document's publisher from metadata
           Argument: Set the document's publisher in metadata
        """                 
        if not (value is None):
            if (self.metadatatype == MetaDataType.NATIVE):
                 self.metadata['publisher'] = value                
            else:
                self._publisher = value  
        if (self.metadatatype == MetaDataType.NATIVE):      
            if 'publisher' in self.metadata:
                return self.metadata['publisher']
            else:
                return None
        else:
            return self._publisher
            
    def license(self, value=None):
        """No arguments: Get the document's license from metadata
           Argument: Set the document's license in metadata
        """                         
        if not (value is None):
            if (self.metadatatype == MetaDataType.NATIVE):
                 self.metadata['license'] = value                
            else:
                self._license = value  
        if (self.metadatatype == MetaDataType.NATIVE):      
            if 'license' in self.metadata:
                return self.metadata['license']
            else:
                return None
        else:
            return self._license
        
    def language(self, value=None):
        """No arguments: Get the document's language (ISO-639-3) from metadata
           Argument: Set the document's language (ISO-639-3) in metadata
        """                                 
        if not (value is None):
            if (self.metadatatype == MetaDataType.NATIVE):
                 self.metadata['language'] = value                
            else:
                self._language = value  
        if (self.metadatatype == MetaDataType.NATIVE):      
            if 'language' in self.metadata:
                return self.metadata['language']
            else:
                return None
        else:
            return self._language     
           

    def parsexml(self, node):
        """Main XML parser, will invoke class-specific XML parsers. For internal use."""
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
                    if 'type' in subnode.attrib and subnode.attrib['type'] == 'imdi':
                        self.metadatatype = MetaDataType.IMDI
                    elif 'type' in subnode.attrib and  subnode.attrib['type'] == 'cmdi':                        
                        self.metadatatype = MetaDataType.IMDI 
                    elif 'type' in subnode.attrib and subnode.attrib['type'] == 'native':                        
                        self.metadatatype = MetaDataType.NATIVE
                    else:
                        #no type specified, default to native
                        self.metadatatype = MetaDataType.NATIVE                        
                    
                    
                    self.metadata = {}
                    self.metadatafile = None
                    
                    if 'src' in subnode.attrib:
                        self.metadatafile =  subnode.attrib['src']
                                                                                                                                                 
                    for subsubnode in subnode:
                        if subsubnode.tag == '{http://www.mpi.nl/IMDI/Schema/IMDI}METATRANSCRIPT':
                            self.metadatatype = MetaDataType.IMDI
                            self.setimdi(subsubnode)
                        if subsubnode.tag == '{' + NSFOLIA + '}annotations':
                            self.parsexmldeclarations(subsubnode)
                        if subsubnode.tag == '{' + NSFOLIA + '}meta':
                            if subsubnode.text:
                                self.metadata[subsubnode.attrib['id']] = subsubnode.text
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
        """Return a list of all paragraphs found in the document.
        
        If an index is specified, return the n'th paragraph only (starting at 0)"""
        if index is None:
            return sum([ t.select(Paragraph) for t in self.data ],[])
        else:
            return sum([ t.select(Paragraph) for t in self.data ],[])[index]
    
    def sentences(self, index = None):
        """Return a list of all sentence found in the document.
        
        If an index is specified, return the n'th sentence only (starting at 0)"""
        if index is None:
            return sum([ t.select(Sentence,None,True,[Quote]) for t in self.data ],[])
        else:
            return sum([ t.select(Sentence,None,True,[Quote]) for t in self.data ],[])[index]

        
    def words(self, index = None):
        """Return a list of all words found in the document.
        
        If an index is specified, return the n'th word only (starting at 0)"""        
        if index is None:            
            return sum([ t.select(Word,None,True,[AbstractSpanAnnotation]) for t in self.data ],[])
        else:
            return sum([ t.select(Word,None,True,[AbstractSpanAnnotation]) for t in self.data ],[])[index]
            

    def text(self):
        """Returns the text of the entire document (returns a unicode instance)"""
        return unicode(self)
       
    def xmlstring(self):
        return ElementTree.tostring(self.xml(), xml_declaration=True, pretty_print=True, encoding='utf-8')

    def __unicode__(self):
        """Returns the text of the entire document"""
        s = u""
        for c in self.data:
            if s: s += "\n\n"
            try:
                s += unicode(c)
            except:
                continue
        return s

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        if len(self.data) != len(other.data):
            if self.debug: print >>stderr, "[PyNLPl FoLiA DEBUG] Equality check - Documents have unequal amount of children"
            return False
        for e,e2 in zip(self.data,other.data):
            if e != e2:            
                return False
        return True
        
        
    def __str__(self):    
        """Returns the text of the entire document (UTF-8 encoded)"""
        return unicode(self).encode('utf-8')
        
        

class Content(AbstractElement):     #used for raw content, subelement for Gap
    OCCURRENCES = 1
    XMLTAG = 'content'
    
    def __init__(self,doc, *args, **kwargs):
        if 'value' in kwargs:
            if isinstance(kwargs['value'], unicode):
                self.value = kwargs['value']
            elif isinstance(kwargs['value'], str):
                self.value = unicode(kwargs['value'],'utf-8')
            elif kwargs['value'] is None:
                self.value = u""
            else:
                raise Exception("value= parameter must be unicode or str instance")
            del kwargs['value']
        else:
            raise Exception("Description expects value= parameter")
        super(Content,self).__init__(doc, *args, **kwargs)
    
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
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        global NSFOLIA
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.text(), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)        
        
    @classmethod
    def parsexml(Class, node, doc):
        global NSFOLIA
        kwargs = {}
        kwargs['value'] = node.text
        return Content(doc, **kwargs)            
    
class Gap(AbstractElement):
    """Gap element. Represents skipped portions of the text. Contains Content and Desc elements"""
    ACCEPTED_DATA = (Content, Description)
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE,Attrib.N,)
    XMLTAG = 'gap'
    
    def __init__(self, doc, *args, **kwargs):
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
        return ""
            
    

class Caption(AbstractStructureElement):    
    """Element used for captions for figures or tables, contains sentences"""
    OPTIONAL_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (Sentence, Description)
    OCCURRENCES = 1
    XMLTAG = 'caption'

    
class Label(AbstractStructureElement):    
    """Element used for labels. Mostly in within list item. Contains words."""
    OPTIONAL_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (Word, Description)
    XMLTAG = 'label'

class ListItem(AbstractStructureElement):
    """Single element in a List. Structure element. Contained within List element."""
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    #ACCEPTED_DATA = (List, Sentence) #Defined below
    XMLTAG = 'listitem'
    
    
class List(AbstractStructureElement):    
    """Element for enumeration/itemisation. Structure element. Contains ListItem elements."""
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    ACCEPTED_DATA = (ListItem,Description, Caption)
    XMLTAG = 'list'
    

ListItem.ACCEPTED_DATA = (List, Sentence, Description, Label)

class Figure(AbstractStructureElement):    
    """Element for the representation of a graphical figure. Structure element."""
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    ACCEPTED_DATA = (Sentence, Description, Caption)
    XMLTAG = 'figure'
    #TODO: relaxNG
    
    def __init__(self, doc, *args, **kwargs):
        if 'url' in kwargs:
            self.url = kwargs['url']
            del kwargs['url']
        else:
            self.url = None 
        super(Figure, self).__init__(doc, *args, **kwargs)
        


class Division(AbstractStructureElement):    
    """Structure element representing some kind of division. Divisions may be nested at will, and may include almost all kinds of other structure elements."""
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.N)
    XMLTAG = 'div'
    ANNOTATIONTYPE = AnnotationType.DIVISION
            
    def head(self):
        for e in self.data:
            if isinstance(e, Head):
                return e
        raise NoSuchAnnotation()
              
Division.ACCEPTED_DATA = (Division, Gap, Head, Paragraph, Sentence, List, Figure, AbstractExtendedTokenAnnotation, Description, Linebreak, Whitespace)

class Text(AbstractStructureElement):
    """A full text. This is a high-level element (not to be confused with TextContent!). This element may contain divisions, paragraphs, sentences, etc.."""
    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Gap, Division, Paragraph, Sentence, List, Figure, AbstractExtendedTokenAnnotation, Description)
    XMLTAG = 'text' 
    TEXTDELIMITER = "\n\n"        

class Corpus:
    """A corpus of various FoLiA document"""
    
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


class CorpusFiles(Corpus):
    def __iter__(self):
        if not self.restrict_to_collection:
            for f in glob.glob(self.corpusdir+"/*." + self.extension):
                if self.conditionf(f):
                    try:
                        yield f
                    except:
                        print >>sys.stderr, "Error, unable to parse " + f
                        if not self.ignoreerrors:
                            raise
        for d in glob.glob(self.corpusdir+"/*"):
            if (not self.restrict_to_collection or self.restrict_to_collection == os.path.basename(d)) and (os.path.isdir(d)):
                for f in glob.glob(d+ "/*." + self.extension):
                    if self.conditionf(f):
                        try:
                            yield f
                        except:
                            print >>sys.stderr, "Error, unable to parse " + f
                            if not self.ignoreerrors:
                                raise
    

class SetType:
    CLOSED, OPEN, MIXED = range(3)

class AbstractDefinition(object):
    pass
        
class ConstraintDefinition(object):
    def __init__(self, id,  restrictions = {}, exceptions = {}):
        self.id = id
        self.restrictions = restrictions
        self.exceptions = exceptions
    
    @classmethod
    def parsexml(Class, node, constraintindex):        
        global NSFOLIA
        assert node.tag == '{' + NSFOLIA + '}constraint' 
        
        if 'ref' in node.attrib:
            try:
                return constraintindex[node.attrib['ref']]
            except KeyError:
                raise KeyError("Unresolvable constraint: " + node.attrib['ref'])


            
        restrictions = []
        exceptions = []
        for subnode in node:
            if subnode.tag == '{' + NSFOLIA + '}restrict':
                if 'subset' in subnode.attrib:
                    restrictions.append( (subnode.attrib['subset'], subnode.attrib['class']) )
                else:
                    restrictions.append( (None, subnode.attrib['class']) )
            elif subnode.tag == '{' + NSFOLIA + '}except':
                if 'subset' in subnode.attrib:
                    exceptions.append( (subnode.attrib['subset'], subnode.attrib['class']) )
                else:
                    exceptions.append( (None, subnode.attrib['class']) )
            
        if '{http://www.w3.org/XML/1998/namespace}id' in node.attrib:
            id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
            instance = Constraint(id, restrictions,exceptions)
            constraintindex[id] = instance
        else:
            instance = Constraint(None, restrictions,exceptions)
        return instance
            
    
class ClassDefinition(AbstractDefinition):
    def __init__(self,id, type,label, constraints=[]):
        self.id = id
        self.type = type
        self.label = label
        self.constraints = constraints

    @classmethod
    def parsexml(Class, node, constraintindex):        
        global NSFOLIA
        assert node.tag == '{' + NSFOLIA + '}class' 
        if 'label' in node.attrib:
            label = node.attrib['label']
        else:
            label = ""
        
        if 'type' in node.attrib:
            if node.attrib['type'] == 'open':
                type = SetType.OPEN
            elif node.attrib['type'] == 'closed':
                type = SetType.CLOSED
            elif node.attrib['type'] == 'mixed':
                type = SetType.MIXED                
            else: 
                raise Exception("Invalid set type: ", type)
        else:
            type = SetType.MIXED
            
        constraints = []
        for subnode in node:
            if subnode.tag == '{' + NSFOLIA + '}constraint':
                constraints.append( Constraint.parsexml(subnode, constraintindex) )
            elif subnode.tag[:len(NSFOLIA) +2] == '{' + NSFOLIA + '}':
                raise Exception("Invalid tag in Class definition: " + subnode.tag)            
                
        return ClassDefinition(node.attrib['{http://www.w3.org/XML/1998/namespace}id'],type, label, constraints)

class SubsetDefinition(AbstractDefinition):
    def __init__(self, id, type, classes = [], subsets = []):
        self.id = id
        self.type = type
        self.classes = classes
        self.constraints = constraints

    def parsexml(Class, node, constraintindex= {}):        
        global NSFOLIA
        assert node.tag == '{' + NSFOLIA + '}subset' 
        
        if 'type' in node.attrib:
            if node.attrib['type'] == 'open':
                type = SetType.OPEN
            elif node.attrib['type'] == 'closed':
                type = SetType.CLOSED
            elif node.attrib['type'] == 'mixed':
                type = SetType.MIXED                
            else: 
                raise Exception("Invalid set type: ", type)
        else:
            type = SetType.MIXED
        
        classes = []
        constraints = []
        for subnode in node:
            if subnode.tag == '{' + NSFOLIA + '}class':
                classes.append( ClassDefinition.parsexml(subnode, constraintindex) )
            elif subnode.tag == '{' + NSFOLIA + '}constraint':
                constraints.append( Constraint.parsexml(subnode, constraintindex) )
            elif subnode.tag[:len(NSFOLIA) +2] == '{' + NSFOLIA + '}':
                raise Exception("Invalid tag in Set definition: " + subnode.tag)
                
        return SubsetDefinition(node.attrib['{http://www.w3.org/XML/1998/namespace}id'],type,classes, constraints)
        

class SetDefinition(AbstractDefinition):
    def __init__(self, id, classes = [], subsets = [], constraintindex = {}):
        self.id = id
        self.classes = classes
        self.subsets = subsets
        self.constraintindex = constraintindex
                
    @classmethod
    def parsexml(Class, node):        
        global NSFOLIA
        assert node.tag == '{' + NSFOLIA + '}set' 
        classes = []
        subsets= []
        contstraintindex = {}
        for subnode in node:
            if subnode.tag == '{' + NSFOLIA + '}class':
                classes.append( ClassDefinition.parsexml(subnode) )
            elif subnode.tag == '{' + NSFOLIA + '}subset':
                subsets.append( ClassDefinition.parsexml(subnode) )
            elif subnode.tag[:len(NSFOLIA) +2] == '{' + NSFOLIA + '}':
                raise Exception("Invalid tag in Set definition: " + subnode.tag)
                
        return SetDefinition(node.attrib['{http://www.w3.org/XML/1998/namespace}id'],classes, subsets, constraintindex)
        
        
def loadsetdefinition(filename):
    global NSFOLIA
    tree = ElementTree.parse(filename)
    root = self.tree.getroot()
    if root.tag != '{' + NSFOLIA + '}set':
        raise Exception("Not a FoLiA Set Definition! Unexpected root tag:"+ root.tag)
    
    return Set.parsexml(root)            
        

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
                    E.optional(E.attribute(name='type')),
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
        f.write( ElementTree.tostring(relaxng(),pretty_print=True).replace("</define>","</define>\n\n") )
        f.close()

    return grammar

#class WordIndexer(object):
#    def __init__(self, doc, *args, **kwargs)
#        self.doc = doc
#        
#    def __iter__(self):
#        
#                
#    def savecsv(self, filename):
#        
#        
#    def savesql(self, filename):


def validate(filename,schema=None):
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
    
    if not schema:
        schema = ElementTree.RelaxNG(relaxng())
    else:
        schema.assertValid(doc) #will raise exceptions


XML2CLASS = {}
for c in vars().values():
    try:
        if c.XMLTAG:
            XML2CLASS[c.XMLTAG] = c
    except: 
        continue


