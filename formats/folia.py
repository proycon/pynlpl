# -*- coding: utf-8 -*-
#----------------------------------------------------------------
# PyNLPl - FoLiA Format Module
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

from copy import copy, deepcopy
from datetime import datetime
import inspect
import itertools
import glob
import os
import re
try:
    import io
except ImportError:
    #old-Python 2.6 fallback
    import codecs as io
import multiprocessing
import bz2
import gzip
import random



from lxml import etree as ElementTree

from lxml.builder import ElementMaker
if sys.version < '3':
    from StringIO import StringIO #pylint: disable=import-error,wrong-import-order
    from urllib import urlopen #pylint: disable=no-name-in-module,wrong-import-order
else:
    from io import StringIO,  BytesIO #pylint: disable=wrong-import-order,ungrouped-imports
    from urllib.request import urlopen #pylint: disable=E0611,wrong-import-order,ungrouped-imports

if sys.version < '3':
    from codecs import getwriter #pylint: disable=wrong-import-order,ungrouped-imports
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout

from pynlpl.common import u, isstring
import pynlpl.algorithms


LXE=True #use lxml instead of built-in ElementTree (default)

#foliaspec:version:FOLIAVERSION
#The FoLiA version
FOLIAVERSION = "1.2.0"

LIBVERSION = FOLIAVERSION + '.77' #== FoLiA version + library revision

#0.9.1.31 is the first version with Python 3 support

#foliaspec:namespace:NSFOLIA
#The FoLiA XML namespace
NSFOLIA = "http://ilk.uvt.nl/folia"

NSDCOI = "http://lands.let.ru.nl/projects/d-coi/ns/1.0"
nslen = len(NSFOLIA) + 2
nslendcoi = len(NSDCOI) + 2

TMPDIR = "/tmp/" #will be used for downloading temporary data (external subdocuments)


ILLEGAL_UNICODE_CONTROL_CHARACTERS = {} #XML does not like unicode control characters
for ordinal in range(0x20):
    if chr(ordinal) not in '\t\r\n':
        ILLEGAL_UNICODE_CONTROL_CHARACTERS[ordinal] = None

class Mode:
    MEMORY = 0 #The entire FoLiA structure will be loaded into memory. This is the default and is required for any kind of document manipulation.
    XPATH = 1 #The full XML structure will be loaded into memory, but conversion to FoLiA objects occurs only upon querying. The full power of XPath is available.

class AnnotatorType:
    UNSET = 0
    AUTO = 1
    MANUAL = 2


#foliaspec:attributes
#Defines all common FoLiA attributes (as part of the Attrib enumeration)
class Attrib:
    ID, CLASS, ANNOTATOR, CONFIDENCE, N, DATETIME, BEGINTIME, ENDTIME, SRC, SPEAKER = range(10)

#foliaspec:annotationtype
#Defines all annotation types (as part of the AnnotationType enumeration)
class AnnotationType:
    TEXT, TOKEN, DIVISION, PARAGRAPH, LIST, FIGURE, WHITESPACE, LINEBREAK, SENTENCE, POS, LEMMA, DOMAIN, SENSE, SYNTAX, CHUNKING, ENTITY, CORRECTION, ERRORDETECTION, PHON, SUBJECTIVITY, MORPHOLOGICAL, EVENT, DEPENDENCY, TIMESEGMENT, GAP, NOTE, ALIGNMENT, COMPLEXALIGNMENT, COREFERENCE, SEMROLE, METRIC, LANG, STRING, TABLE, STYLE, PART, UTTERANCE, ENTRY, TERM, DEFINITION, EXAMPLE, PHONOLOGICAL = range(42)


    #Alternative is a special one, not declared and not used except for ID generation

class TextCorrectionLevel: #THIS IS NOW COMPLETELY OBSOLETE AND ONLY HERE FOR BACKWARD COMPATIBILITY!
    CORRECTED, UNCORRECTED, ORIGINAL, INLINE = range(4)

class MetaDataType: #THIS IS NOW COMPLETELY OBSOLETE AND ONLY HERE FOR BACKWARD COMPATIBILITY! Metadata type is a free-fill field with only native predefined
    NATIVE = "native"
    CMDI = "cmdi"
    IMDI = "imdi"

class NoSuchAnnotation(Exception):
    """Exception raised when the requested type of annotation does not exist for the selected element"""
    pass

class NoSuchText(Exception):
    """Exception raised when the requested type of text content does not exist for the selected element"""
    pass

class NoSuchPhon(Exception):
    """Exception raised when the requested type of phonetic content does not exist for the selected element"""
    pass

class DuplicateAnnotationError(Exception):
    pass

class DuplicateIDError(Exception):
    """Exception raised when an identifier that is already in use is assigned again to another element"""
    pass

class NoDefaultError(Exception):
    pass


class UnresolvableTextContent(Exception):
    pass

class MalformedXMLError(Exception):
    pass

class DeepValidationError(Exception):
    pass

class SetDefinitionError(DeepValidationError):
    pass

class ModeError(Exception):
    pass

class MetaDataError(Exception):
    pass

class DocumentNotLoaded(Exception): #for alignments to external documents
    pass

class GenerateIDException(Exception):
    pass

class CorrectionHandling:
    EITHER,CURRENT, ORIGINAL = range(3)




def parsetime(s):
    #parses time in HH:MM:SS.mmm format, returns a four-tuple
    try:
        fields = s.split('.')
        subfields = fields[0].split(':')
        H = int(subfields[0])
        M = int(subfields[1])
        S = int(subfields[2])
        if len(subfields) > 3:
            m = int(subfields[3])
        else:
            m = 0
        if len(fields) > 1:
            m = int(fields[1])
        return (H,M,S,m)
    except:
        raise ValueError("Invalid timestamp, must be in HH:MM:SS.mmm format: " + s)


def parsecommonarguments(object, doc, annotationtype, required, allowed, **kwargs):
    """Internal function, parses common FoLiA attributes and sets up the instance accordingly"""

    object.doc = doc #The FoLiA root document

    if required is None:
        required = tuple()
    if allowed is None:
        allowed = tuple()

    supported = required + allowed


    if 'generate_id_in' in kwargs:
        try:
            kwargs['id'] = kwargs['generate_id_in'].generate_id(object.__class__)
        except GenerateIDException:
            pass #ID could not be generated, just skip
        del kwargs['generate_id_in']



    if 'id' in kwargs:
        if Attrib.ID not in supported:
            raise ValueError("ID is not supported on " + object.__class__.__name__)
        isncname(kwargs['id'])
        object.id = kwargs['id']
        del kwargs['id']
    elif Attrib.ID in required:
        raise ValueError("ID is required for " + object.__class__.__name__)
    else:
        object.id = None

    if 'set' in kwargs:
        if Attrib.CLASS not in supported and not object.SETONLY:
            raise ValueError("Set is not supported on " + object.__class__.__name__)
        if not kwargs['set']:
            object.set ="undefined"
        else:
            object.set = kwargs['set']
        del kwargs['set']

        if object.set:
            if doc and (not (annotationtype in doc.annotationdefaults) or not (object.set in doc.annotationdefaults[annotationtype])):
                if doc.autodeclare:
                    doc.annotations.append( (annotationtype, object.set ) )
                    doc.annotationdefaults[annotationtype] = {object.set: {} }
                else:
                    raise ValueError("Set '" + object.set + "' is used for " + object.__class__.__name__ + ", but has no declaration!")
    elif annotationtype in doc.annotationdefaults and len(doc.annotationdefaults[annotationtype]) == 1:
        object.set = list(doc.annotationdefaults[annotationtype].keys())[0]
    elif object.ANNOTATIONTYPE == AnnotationType.TEXT:
        object.set = "undefined" #text content needs never be declared (for backward compatibility) and is in set 'undefined'
    elif Attrib.CLASS in required: #or (hasattr(object,'SETONLY') and object.SETONLY):
        raise ValueError("Set is required for " + object.__class__.__name__)


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

    if object.cls and not object.set:
        if doc and doc.autodeclare:
            if not (annotationtype, 'undefined') in doc.annotations:
                doc.annotations.append( (annotationtype, 'undefined') )
                doc.annotationdefaults[annotationtype] = {'undefined': {} }
            object.set = 'undefined'
        else:
            raise ValueError("Set is required for " + object.__class__.__name__ +  ". Class '" + object.cls + "' assigned without set.")





    if 'annotator' in kwargs:
        if not Attrib.ANNOTATOR in supported:
            raise ValueError("Annotator is not supported for " + object.__class__.__name__)
        object.annotator = kwargs['annotator']
        del kwargs['annotator']
    elif doc and annotationtype in doc.annotationdefaults and object.set in doc.annotationdefaults[annotationtype] and 'annotator' in doc.annotationdefaults[annotationtype][object.set]:
        object.annotator = doc.annotationdefaults[annotationtype][object.set]['annotator']
    elif Attrib.ANNOTATOR in required:
        raise ValueError("Annotator is required for " + object.__class__.__name__)


    if 'annotatortype' in kwargs:
        if not Attrib.ANNOTATOR in supported:
            raise ValueError("Annotatortype is not supported for " + object.__class__.__name__)
        if kwargs['annotatortype'] == 'auto' or kwargs['annotatortype'] == AnnotatorType.AUTO:
            object.annotatortype = AnnotatorType.AUTO
        elif kwargs['annotatortype'] == 'manual' or kwargs['annotatortype']  == AnnotatorType.MANUAL:
            object.annotatortype = AnnotatorType.MANUAL
        else:
            raise ValueError("annotatortype must be 'auto' or 'manual', got "  + repr(kwargs['annotatortype']))
        del kwargs['annotatortype']
    elif doc and annotationtype in doc.annotationdefaults and object.set in doc.annotationdefaults[annotationtype] and 'annotatortype' in doc.annotationdefaults[annotationtype][object.set]:
        object.annotatortype = doc.annotationdefaults[annotationtype][object.set]['annotatortype']
    elif Attrib.ANNOTATOR in required:
        raise ValueError("Annotatortype is required for " + object.__class__.__name__)


    if 'confidence' in kwargs:
        if not Attrib.CONFIDENCE in supported:
            raise ValueError("Confidence is not supported")
        try:
            object.confidence = float(kwargs['confidence'])
            assert object.confidence >= 0.0 and object.confidence <= 1.0
        except:
            raise ValueError("Confidence must be a floating point number between 0 and 1, got " + repr(kwargs['confidence']) )
        del kwargs['confidence']
    elif Attrib.CONFIDENCE in required:
        raise ValueError("Confidence is required for " + object.__class__.__name__)



    if 'n' in kwargs:
        if not Attrib.N in supported:
            raise ValueError("N is not supported for " + object.__class__.__name__)
        object.n = kwargs['n']
        del kwargs['n']
    elif Attrib.N in required:
        raise ValueError("N is required for " + object.__class__.__name__)

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
    elif doc and annotationtype in doc.annotationdefaults and object.set in doc.annotationdefaults[annotationtype] and 'datetime' in doc.annotationdefaults[annotationtype][object.set]:
        object.datetime = doc.annotationdefaults[annotationtype][object.set]['datetime']
    elif Attrib.DATETIME in required:
        raise ValueError("Datetime is required for " + object.__class__.__name__)

    if 'src' in kwargs:
        if not Attrib.SRC in supported:
            raise ValueError("Source is not supported for " + object.__class__.__name__)
        object.src = kwargs['src']
        del kwargs['src']
    elif Attrib.SRC in required:
        raise ValueError("Source is required for " + object.__class__.__name__)

    if 'begintime' in kwargs:
        if not Attrib.BEGINTIME in supported:
            raise ValueError("Begintime is not supported for " + object.__class__.__name__)
        object.begintime = parsetime(kwargs['begintime'])
        del kwargs['begintime']
    elif Attrib.BEGINTIME in required:
        raise ValueError("Begintime is required for " + object.__class__.__name__)

    if 'endtime' in kwargs:
        if not Attrib.ENDTIME in supported:
            raise ValueError("Endtime is not supported for " + object.__class__.__name__)
        object.endtime = parsetime(kwargs['endtime'])
        del kwargs['endtime']
    elif Attrib.ENDTIME in required:
        raise ValueError("Endtime is required for " + object.__class__.__name__)


    if 'speaker' in kwargs:
        if not Attrib.SPEAKER in supported:
            raise ValueError("Speaker is not supported for " + object.__class__.__name__)
        object.speaker = kwargs['speaker']
        del kwargs['speaker']
    elif Attrib.SPEAKER in required:
        raise ValueError("Speaker is required for " + object.__class__.__name__)

    if 'auth' in kwargs:
        if kwargs['auth'] in ('no','false'):
            object.auth = False
        else:
            object.auth = bool(kwargs['auth'])
        del kwargs['auth']
    else:
        object.auth = object.__class__.AUTH



    if 'text' in kwargs:
        if kwargs['text']:
            object.settext(kwargs['text'])
        del kwargs['text']

    if 'phon' in kwargs:
        if kwargs['phon']:
            object.setphon(kwargs['phon'])
        del kwargs['phon']

    if object.XLINK:
        if 'href' in kwargs:
            object.href =kwargs['href']
            del kwargs['href']
        if 'xlinktype' in kwargs:
            object.xlinktype = kwargs['xlinktype']
            del kwargs['xlinktype']
        if 'xlinkrole' in kwargs:
            object.xlinkrole = kwargs['xlinkrole']
            del kwargs['xlinkrole']
        if 'xlinklabel' in kwargs:
            object.xlinklabel = kwargs['xlinklabel']
            del kwargs['xlinklabel']
        if 'xlinkshow' in kwargs:
            object.xlinkshow = kwargs['xlinkshow']
            del kwargs['xlinklabel']
        if 'xlinktitle' in kwargs:
            object.xlinktitle = kwargs['xlinktitle']
            del kwargs['xlinktitle']

    if doc and doc.debug >= 2:
        print("   @id           = ", repr(object.id),file=stderr)
        print("   @set          = ", repr(object.set),file=stderr)
        print("   @class        = ", repr(object.cls),file=stderr)
        print("   @annotator    = ", repr(object.annotator),file=stderr)
        print("   @annotatortype= ", repr(object.annotatortype),file=stderr)
        print("   @confidence   = ", repr(object.confidence),file=stderr)
        print("   @n            = ", repr(object.n),file=stderr)
        print("   @datetime     = ", repr(object.datetime),file=stderr)



    #set index
    if object.id and doc:
        if object.id in doc.index:
            if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] Duplicate ID not permitted:" + object.id,file=stderr)
            raise DuplicateIDError("Duplicate ID not permitted: " + object.id)
        else:
            if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] Adding to index: " + object.id,file=stderr)
            doc.index[object.id] = object

    #Parse feature attributes (shortcut for feature specification for some elements)
    for c in object.ACCEPTED_DATA:
        if issubclass(c, Feature):
            if c.SUBSET in kwargs:
                if kwargs[c.SUBSET]:
                    object.append(c,cls=kwargs[c.SUBSET])
                del kwargs[c.SUBSET]

    return kwargs



def parse_datetime(s): #source: http://stackoverflow.com/questions/2211362/how-to-parse-xsddatetime-format
    """Returns (datetime, tz offset in minutes) or (None, None)."""
    m = re.match(r""" ^
        (?P<year>-?[0-9]{4}) - (?P<month>[0-9]{2}) - (?P<day>[0-9]{2})
        T (?P<hour>[0-9]{2}) : (?P<minute>[0-9]{2}) : (?P<second>[0-9]{2})
        (?P<microsecond>\.[0-9]{1,6})?
        (?P<tz>
        Z | (?P<tz_hr>[-+][0-9]{2}) : (?P<tz_min>[0-9]{2})
        )?
        $ """, s, re.X)
    if m is not None:
        values = m.groupdict()
        #if values["tz"] in ("Z", None):
        #    tz = 0
        #else:
        #    tz = int(values["tz_hr"]) * 60 + int(values["tz_min"])
        if values["microsecond"] is None:
            values["microsecond"] = 0
        else:
            values["microsecond"] = values["microsecond"][1:]
            values["microsecond"] += "0" * (6 - len(values["microsecond"]))
        values = dict((k, int(v)) for k, v in values.items() if not k.startswith("tz"))
        try:
            return datetime(**values) # , tz
        except ValueError:
            pass
    return None


def xmltreefromstring(s):
    #Internal method, deals with different Python versions, unicode strings versus bytes, and with the leak bug in lxml
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

def xmltreefromfile(filename):
    try:
        return ElementTree.parse(filename, ElementTree.XMLParser(collect_ids=False))
    except TypeError:
        return ElementTree.parse(filename, ElementTree.XMLParser()) #older lxml, may leak!!

def makeelement(E, tagname, **kwargs):
    if sys.version < '3':
        try:
            kwargs2 = {}
            for k,v in kwargs.items():
                kwargs2[k.encode('utf-8')] = v.encode('utf-8')
                #return E._makeelement(tagname.encode('utf-8'), **{ k.encode('utf-8'): v.encode('utf-8') for k,v in kwargs.items() } )   #In one go fails on some older Python 2.6s
            return E._makeelement(tagname.encode('utf-8'), **kwargs2 ) #pylint: disable=protected-access
        except ValueError as e:
            try:
                #older versions of lxml may misbehave, compensate:
                e =  E._makeelement(tagname.encode('utf-8')) #pylint: disable=protected-access
                for k,v in kwargs.items():
                    e.attrib[k.encode('utf-8')] = v
                return e
            except ValueError:
                print(e,file=stderr)
                print("tagname=",tagname,file=stderr)
                print("kwargs=",kwargs,file=stderr)
                raise e
    else:
        return E._makeelement(tagname,**kwargs) #pylint: disable=protected-access


def commonancestors(Class, *args):
    """Generator over common ancestors, of the Class specified, of the current element and the other specified elements"""
    commonancestors = None #pylint: disable=redefined-outer-name
    for sibling in args:
        ancestors = list( sibling.ancestors(Class) )
        if commonancestors is None:
            commonancestors = copy(ancestors)
        else:
            removeancestors = []
            for a in commonancestors: #pylint: disable=not-an-iterable
                if not a in ancestors:
                    removeancestors.append(a)
            for a in removeancestors:
                commonancestors.remove(a)
    if commonancestors:
        for commonancestor in commonancestors:
            yield commonancestor

class AbstractElement(object):
    """This is the abstract base class from which all FoLiA elements are derived. This class should not be instantiated directly, but can useful if you want to check if a variable is an instance of any FoLiA element: isinstance(x, AbstractElement). It contains methods and variables also commonly inherited."""

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
            if key[0] == '{': #this is a parameter in a different alien namespace, ignore it
                continue
            else:
                raise ValueError("Parameter '" + key + "' not supported by " + self.__class__.__name__)


    def __getattr__(self, attr):
        #overriding getattr so we can get defaults here rather than needing a copy on each element, saves memory
        if attr in ('set','cls','confidence','annotator','annotatortype','datetime','n','href','src','speaker','begintime','endtime','xlinktype','xlinktitle','xlinklabel','xlinkrole','xlinkshow'):
            return None
        else:
            return super(AbstractElement, self).__getattribute__(attr)


    #def __del__(self):
    #    if self.doc and self.doc.debug:
    #        print >>stderr, "[PyNLPl FoLiA DEBUG] Removing " + repr(self)
    #    for child in self.data:
    #        del child
    #    self.doc = None
    #    self.parent = None
    #    del self.data


    def description(self):
        """Obtain the description associated with the element, will raise NoDescription if there is none"""
        for e in self:
            if isinstance(e, Description):
                return e.value
        raise NoSuchAnnotation

    def textcontent(self, cls='current', correctionhandling=CorrectionHandling.CURRENT):
        """Get the text explicitly associated with this element (of the specified class).
        Returns the TextContent instance rather than the actual text. Raises NoSuchText exception if
        not found.

        Unlike text(), this method does not recurse into child elements (with the sole exception of the Correction/New element), and it returns the TextContent instance rather than the actual text!

        The correctionhandling argument specifies what text to retrieve when corrections are encountered. The default is CorrectionHandling.CURRENT, which will retrieve the corrected/current text. You can set this to ORIGINAL if you want the text prior to correction, and EITHER if you don't care.
        """
        if not self.PRINTABLE: #only printable elements can hold text
            raise NoSuchText


        #Find explicit text content (same class)
        for e in self:
            if isinstance(e, TextContent):
                if cls is None or e.cls == cls:
                    return e
            elif isinstance(e, Correction):
                try:
                    return e.textcontent(cls, correctionhandling)
                except NoSuchText:
                    pass
        raise NoSuchText



    def stricttext(self, cls='current'):
        """Alias for text() with strict=True"""
        return self.text(cls,strict=True)

    def toktext(self,cls='current'):
        """Alias for text() with retaintokenisation=True"""
        return self.text(cls,retaintokenisation=True)

    def text(self, cls='current', retaintokenisation=False, previousdelimiter="",strict=False, correctionhandling=CorrectionHandling.CURRENT):
        """Get the text associated with this element (of the specified class)  (will always be a unicode instance in python 2)

        The text will be constructed from child-elements whereever possible, as they are more specific.
        If no text can be obtained from the children and the element has itself text associated with
        it, then that will be used. If no text is found at all, a NoSuchText exception is raised.

        If you are strictly interested in the text explicitly associated with the element, without recursing into children, use ``strict=True``

        If retaintokenisation is True, the space attribute on words will be ignored, otherwise it will be adhered to and text will be detokenised as much as possible.

        The correctionhandling argument specifies what text to retrieve when corrections are encountered. The default is CorrectionHandling.CURRENT, which will retrieve the corrected/current text. You can set this to ORIGINAL if you want the text prior to correction, and EITHER if you don't care.
        """

        if strict:
            return self.textcontent(cls, correctionhandling).text()

        if self.TEXTCONTAINER:
            s = ""
            for e in self:
                if isstring(e):
                    s += e
                else:
                    if s: s += e.TEXTDELIMITER #for AbstractMarkup, will usually be ""
                    s += e.text()
            return s
        elif not self.PRINTABLE: #only printable elements can hold text
            raise NoSuchText
        else:
            #Get text from children first
            delimiter = ""
            s = ""
            for e in self:
                if e.PRINTABLE and not isinstance(e, TextContent) and not isinstance(e, String):
                    try:
                        s += e.text(cls,retaintokenisation, delimiter,False,correctionhandling)

                        #delimiter will be buffered and only printed upon next iteration, this prevents the delimiter being outputted at the end of a sequence and to be compounded with other delimiters
                        delimiter = e.gettextdelimiter(retaintokenisation)
                    except NoSuchText:
                        #No text, that's okay, just continue
                        continue

            if not s and self.hastext(cls, correctionhandling):
                s = self.textcontent(cls, correctionhandling).text()

            if s and previousdelimiter:
                return previousdelimiter + s
            elif s:
                return s
            else:
                #No text found at all :`(
                raise NoSuchText

    def phoncontent(self, cls='current', correctionhandling=CorrectionHandling.CURRENT):
        """Get the phonetic content explicitly associated with this element (of the specified class).
        Returns the PhonContent instance rather than the actual text. Raises NoSuchPhon exception if
        not found.

        Unlike phon(), this method does not recurse into child elements (with the sole exception of the Correction/New element), and it returns the PhonContent instance rather than the actual text!
        """
        if not self.SPEAKABLE: #only printable elements can hold text
            raise NoSuchPhon


        #Find explicit text content (same class)
        for e in self:
            if isinstance(e, PhonContent):
                if cls is None or e.cls == cls:
                    return e
            elif isinstance(e, Correction):
                try:
                    return e.phoncontent(cls, correctionhandling)
                except NoSuchPhon:
                    pass
        raise NoSuchPhon


    def speech_src(self):
        """Retrieves the URL/filename of the audio or video file associated with the element. The source is inherited from ancestor elements if none is specified. For this reason, always use this method rather than access the ``src`` attribute directly. Returns None if not found."""
        if self.src:
            return self.src
        elif self.parent:
            return self.parent.speech_src()
        else:
            return None

    def speech_speaker(self):
        """Retrieves the speaker of the audio or video file associated with the element. The source is inherited from ancestor elements if none is specified. For this reason, always use this method rather than access the ``src`` attribute directly. Returns None if not found."""
        if self.speaker:
            return self.speaker
        elif self.parent:
            return self.parent.speech_speaker()
        else:
            return None



    def phon(self, cls='current', previousdelimiter="", strict=False,correctionhandling=CorrectionHandling.CURRENT):
        """Get the phonetic representation associated with this element (of the specified class), will always be a unicode instance.
        If no text is directly associated with the element, it will be obtained from the children. If that doesn't result
        in any text either, a NoSuchPhon exception will be raised.

        If you are strictly interested in the phonetic context explicitly associated with the element, without recursing into children, use ``strict=True``

        If retaintokenisation is True, the space attribute on words will be ignored, otherwise it will be adhered to and text will be detokenised as much as possible.
        """


        if strict:
            return self.phoncontent(cls,correctionhandling).phon()

        if self.PHONCONTAINER:
            s = ""
            for e in self:
                if isstring(e):
                    s += e
                else:
                    try:
                        if s: s += e.TEXTDELIMITER #We use TEXTDELIMITER for phon too
                    except AttributeError:
                        pass
                    s += e.phon()
            return s
        elif not self.SPEAKABLE: #only readable elements can hold phonetic content
            raise NoSuchPhon
        else:
            #Get text from children first
            delimiter = ""
            s = ""
            for e in self:
                if e.SPEAKABLE and not isinstance(e, PhonContent) and not isinstance(e,String):
                    try:
                        s += e.phon(cls, delimiter,False,correctionhandling)

                        #delimiter will be buffered and only printed upon next iteration, this prevents the delimiter being outputted at the end of a sequence and to be compounded with other delimiters
                        delimiter = e.gettextdelimiter() #We use TEXTDELIMITER for phon too
                    except NoSuchPhon:
                        #No text, that's okay, just continue
                        continue

            if not s and self.hasphon(cls):
                s = self.phoncontent(cls,correctionhandling).phon()

            if s and previousdelimiter:
                return previousdelimiter + s
            elif s:
                return s
            else:
                #No text found at all :`(
                raise NoSuchPhon

    def originaltext(self,cls='original'):
        """Alias for retrieving the original uncorrect text"""
        return self.text(cls,correctionhandling=CorrectionHandling.ORIGINAL)


    def gettextdelimiter(self, retaintokenisation=False):
        """May return a customised text delimiter instead of the default for this class."""
        if self.TEXTDELIMITER is None:
            #no text delimiter of itself, recurse into children to inherit delimiter
            for child in reversed(self):
                if isinstance(child, AbstractElement):
                    return child.gettextdelimiter(retaintokenisation)
            return ""
        else:
            return self.TEXTDELIMITER

    def feat(self,subset):
        """Obtain the feature value of the specific subset. If a feature occurs multiple times, the values will be returned in a list.

        Example::

            sense = word.annotation(folia.Sense)
            synset = sense.feat('synset')
        """
        r = None
        for f in self:
            if isinstance(f, Feature) and f.subset == subset:
                if r: #support for multiclass features
                    if isinstance(r,list):
                        r.append(f.cls)
                    else:
                        r = [r, f.cls]
                else:
                    r = f.cls
        if r is None:
            raise NoSuchAnnotation
        else:
            return r

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other): #pylint: disable=too-many-return-statements
        if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - " + repr(self) + " vs " + repr(other),file=stderr)

        #Check if we are of the same time
        if type(self) != type(other): #pylint: disable=unidiomatic-typecheck
            if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Type mismatch: " + str(type(self)) + " vs " + str(type(other)),file=stderr)
            return False

        #Check FoLiA attributes
        if self.id != other.id:
            if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - ID mismatch: " + str(self.id) + " vs " + str(other.id),file=stderr)
            return False
        if self.set != other.set:
            if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Set mismatch: " + str(self.set) + " vs " + str(other.set),file=stderr)
            return False
        if self.cls != other.cls:
            if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Class mismatch: " + repr(self.cls) + " vs " + repr(other.cls),file=stderr)
            return False
        if self.annotator != other.annotator:
            if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Annotator mismatch: " + repr(self.annotator) + " vs " + repr(other.annotator),file=stderr)
            return False
        if self.annotatortype != other.annotatortype:
            if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Annotator mismatch: " + repr(self.annotatortype) + " vs " + repr(other.annotatortype),file=stderr)
            return False

        #Check if we have same amount of children:
        mychildren = list(self)
        yourchildren = list(other)
        if len(mychildren) != len(yourchildren):
            if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Unequal amount of children",file=stderr)
            return False

        #Now check equality of children
        for mychild, yourchild in zip(mychildren, yourchildren):
            if mychild != yourchild:
                if self.doc and self.doc.debug: print("[PyNLPl FoLiA DEBUG] AbstractElement Equality Check - Child mismatch: " + repr(mychild) + " vs " + repr(yourchild) + " (in " + repr(self) + ", id: " + str(self.id) + ")",file=stderr)
                return False

        #looks like we made it! \o/
        return True

    def __len__(self):
        """Returns the number of child elements under the current element"""
        return len(self.data)

    def __nonzero__(self): #Python 2.x
        return True

    def __bool__(self):
        return True

    def __hash__(self):
        if self.id:
            return hash(self.id)
        else:
            raise TypeError("FoLiA elements are only hashable if they have an ID")

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

    def __unicode__(self): #Python 2 only
        """Alias for text()"""
        return self.text()

    def __str__(self):
        return self.text()

    def copy(self, newdoc=None, idsuffix=""):
        """Make a deep copy of this element and all its children. If idsuffix is a string, if set to True, a random idsuffix will be generated including a random 32-bit hash"""
        if idsuffix is True: idsuffix = ".copy." + "%08x" % random.getrandbits(32) #random 32-bit hash for each copy, same one will be reused for all children
        c = deepcopy(self)
        if idsuffix:
            c.addidsuffix(idsuffix)
        c.setparents()
        c.setdoc(newdoc)
        return c

    def copychildren(self, newdoc=None, idsuffix=""):
        """Generator creating a deep copy of the children of this element. If idsuffix is a string, if set to True, a random idsuffix will be generated including a random 32-bit hash"""
        if idsuffix is True: idsuffix = ".copy." + "%08x" % random.getrandbits(32) #random 32-bit hash for each copy, same one will be reused for all children
        for c in self:
            if isinstance(c, AbstractElement):
                yield c.copy(newdoc,idsuffix)


    def addidsuffix(self, idsuffix, recursive = True):
        if self.id: self.id += idsuffix
        if recursive:
            for e in self:
                try:
                    e.addidsuffix(idsuffix, recursive)
                except Exception:
                    pass

    def setparents(self):
        """Correct all parent relations for elements within the scope, usually no need to call this directly, invoked implicitly by copy()"""
        for c in self:
            if isinstance(c, AbstractElement):
                c.parent = self
                c.setparents()

    def setdoc(self,newdoc):
        """Set a different document, usually no need to call this directly, invoked implicitly by copy()"""
        self.doc = newdoc
        if self.doc and self.id:
            self.doc.index[self.id] = self
        for c in self:
            if isinstance(c, AbstractElement):
                c.setdoc(newdoc)

    def hastext(self,cls='current',strict=True, correctionhandling=CorrectionHandling.CURRENT): #pylint: disable=too-many-return-statements
        """Does this element have text (of the specified class)

        By default, this checks strictly, i.e. the element itself must have the text and it is not inherited from its children.
        Set strict=False to allow checking whether the children have the text.
        """
        if not self.PRINTABLE: #only printable elements can hold text
            return False
        elif self.TEXTCONTAINER:
            return True
        else:
            try:
                if strict:
                    self.textcontent(cls, correctionhandling) #will raise NoSuchTextException when not found
                    return True
                else:
                    #Check children
                    for e in self:
                        if e.PRINTABLE and not isinstance(e, TextContent):
                            if e.hastext(cls, strict, correctionhandling):
                                return True

                    self.textcontent(cls, correctionhandling)  #will raise NoSuchTextException when not found
                    return True
            except NoSuchText:
                return False

    def hasphon(self,cls='current',strict=True,correctionhandling=CorrectionHandling.CURRENT): #pylint: disable=too-many-return-statements
        """Does this element have phonetic content (of the specified class)

        By default, this checks strictly, i.e. the element itself must have the text and it is not inherited from its children.
        Set strict=False to allow checking whether the children have the text.
        """
        if not self.SPEAKABLE: #only printable elements can hold text
            return False
        elif self.PHONCONTAINER:
            return True
        else:
            try:
                if strict:
                    self.phoncontent(cls, correctionhandling)
                    return True
                else:
                    #Check children
                    for e in self:
                        if e.SPEAKABLE and not isinstance(e, PhonContent):
                            if e.hasphon(cls, strict, correctionhandling):
                                return True

                    self.phoncontent(cls)  #will raise NoSuchTextException when not found
                    return True
            except NoSuchPhon:
                return False

    def settext(self, text, cls='current'):
        """Set the text for this element (and class)"""
        self.replace(TextContent, value=text, cls=cls)

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
            if isinstance(e,AbstractElement): e.setdocument(doc)

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
            except Exception:
                pass
            if not found:
                if raiseexceptions:
                    if parent.id:
                        extra = ' (id=' + parent.id + ')'
                    else:
                        extra = ''
                    raise ValueError("Unable to add object of type " + Class.__name__ + " to " + parent.__class__.__name__ + " " + extra + ". Type not allowed as child.")
                else:
                    return False



        if Class.OCCURRENCES > 0:
            #check if the parent doesn't have too many already
            count = parent.count(Class,None,True,[True, AbstractStructureElement]) #never descend into embedded structure annotatioton
            if count >= Class.OCCURRENCES:
                if raiseexceptions:
                    if parent.id:
                        extra = ' (id=' + parent.id + ')'
                    else:
                        extra = ''
                    raise DuplicateAnnotationError("Unable to add another object of type " + Class.__name__ + " to " + parent.__class__.__name__ + " " + extra + ". There are already " + str(count) + " instances of this class, which is the maximum.")
                else:
                    return False

        if Class.OCCURRENCES_PER_SET > 0 and set and Class.REQUIRED_ATTRIBS and Attrib.CLASS in Class.REQUIRED_ATTRIBS:
            count = parent.count(Class,set,True, [True, AbstractStructureElement])
            if count >= Class.OCCURRENCES_PER_SET:
                if raiseexceptions:
                    if parent.id:
                        extra = ' (id=' + parent.id + ')'
                    else:
                        extra = ''
                    raise DuplicateAnnotationError("Unable to add another object of set " + set + " and type " + Class.__name__ + " to " + parent.__class__.__name__ + " " + extra + ". There are already " + str(count) + " instances of this class, which is the maximum for the set.")
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

        if self.doc and self.doc.deepvalidation:
            self.deepvalidation()

    def addtoindex(self,norecurse=[]):
        """Makes sure this element (and all subelements), are properly added to the index"""
        if self.id:
            self.doc.index[self.id] = self
        for e in self.data:
            if all([not isinstance(e, C) for C in norecurse]):
                try:
                    e.addtoindex(norecurse)
                except AttributeError:
                    pass

    def deepvalidation(self):
        if self.doc and self.doc.deepvalidation and self.set and self.set[0] != '_':
            try:
                self.doc.setdefinitions[self.set].testclass(self.cls)
            except KeyError:
                if not self.doc.allowadhocsets:
                    raise DeepValidationError("Set definition for " + self.set + " not loaded!")

    def append(self, child, *args, **kwargs):
        """Append a child element. Returns the added element

        Arguments:
            * ``child``            - Instance or class

        If an *instance* is passed as first argument, it will be appended
        If a *class* derived from AbstractElement is passed as first argument, an instance will first be created and then appended.

        Keyword arguments:
            * ``alternative=``     - If set to True, the element will be made into an alternative.

        Generic example, passing a pre-generated instance::

            word.append( folia.LemmaAnnotation(doc,  cls="house", annotator="proycon", annotatortype=folia.AnnotatorType.MANUAL ) )

        Generic example, passing a class to be generated::

            word.append( folia.LemmaAnnotation, cls="house", annotator="proycon", annotatortype=folia.AnnotatorType.MANUAL )

        Generic example, setting text with a class:

            word.append( "house", cls='original' )


        """



        #obtain the set (if available, necessary for checking addability)
        if 'set' in kwargs:
            set = kwargs['set']
        else:
            try:
                set = child.set
            except AttributeError:
                set = None

        #Check if a Class rather than an instance was passed
        Class = None #do not set to child.__class__
        if inspect.isclass(child):
            Class = child
            if Class.addable(self, set):
                if 'id' not in kwargs and 'generate_id_in' not in kwargs and ((Class.REQUIRED_ATTRIBS and (Attrib.ID in Class.REQUIRED_ATTRIBS)) or Class.AUTO_GENERATE_ID):
                    kwargs['generate_id_in'] = self
                child = Class(self.doc, *args, **kwargs)
        elif args:
            raise Exception("Too many arguments specified. Only possible when first argument is a class and not an instance")


        dopostappend = True

        #Do the actual appending
        if not Class and isstring(child):
            if self.TEXTCONTAINER or self.PHONCONTAINER:
                #element is a text/phon container and directly allows strings as content, add the string as such:
                self.data.append(u(child))
                dopostappend = False
            elif TextContent in self.ACCEPTED_DATA:
                #you can pass strings directly (just for convenience), will be made into textcontent automatically.
                child = TextContent(self.doc, child )
                self.data.append(child)
                child.parent = self
            elif PhonContent in self.ACCEPTED_DATA:
                #you can pass strings directly (just for convenience), will be made into phoncontent automatically (note that textcontent always takes precedence, so you most likely will have to do it explicitly)
                child = PhonContent(self.doc, child ) #pylint: disable=redefined-variable-type 
                self.data.append(child)
                child.parent = self
            else:
                raise ValueError("Unable to append object of type " + child.__class__.__name__ + " to " + self.__class__.__name__ + ". Type not allowed as child.")
        elif Class or (isinstance(child, AbstractElement) and child.__class__.addable(self, set)): #(prevents calling addable again if already done above)
            if 'alternative' in kwargs and kwargs['alternative']:
                child = Alternative(self.doc, child, generate_id_in=self)
            self.data.append(child)
            child.parent = self
        else:
            raise ValueError("Unable to append object of type " + child.__class__.__name__ + " to " + self.__class__.__name__ + ". Type not allowed as child.")

        if dopostappend: child.postappend()
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

        Generic example, setting text::

            word.insert( 3, "house" )


        """

        #obtain the set (if available, necessary for checking addability)
        if 'set' in kwargs:
            set = kwargs['set']
        else:
            try:
                set = child.set
            except AttributeError:
                set = None

        #Check if a Class rather than an instance was passed
        Class = None #do not set to child.__class__
        if inspect.isclass(child):
            Class = child
            if Class.addable(self, set):
                if 'id' not in kwargs and 'generate_id_in' not in kwargs and ((Class.REQUIRED_ATTRIBS and Attrib.ID in Class.REQUIRED_ATTRIBS) or (Class.OPTIONAL_ATTRIBS and Attrib.ID in Class.OPTIONAL_ATTRIBS)):
                    kwargs['generate_id_in'] = self
                child = Class(self.doc, *args, **kwargs)
        elif args:
            raise Exception("Too many arguments specified. Only possible when first argument is a class and not an instance")

        #Do the actual appending
        if not Class and (isinstance(child,str) or (sys.version < '3' and isinstance(child,unicode))) and TextContent in self.ACCEPTED_DATA: #pylint: disable=undefined-variable
            #you can pass strings directly (just for convenience), will be made into textcontent automatically.
            child = TextContent(self.doc, child )
            self.data.insert(index, child)
            child.parent = self
        elif Class or (isinstance(child, AbstractElement) and child.__class__.addable(self, set)): #(prevents calling addable again if already done above)
            if 'alternative' in kwargs and kwargs['alternative']:
                child = Alternative(self.doc, child, generate_id_in=self) #pylint: disable=redefined-variable-type
            self.data.insert(index, child)
            child.parent = self
        else:
            raise ValueError("Unable to append object of type " + child.__class__.__name__ + " to " + self.__class__.__name__ + ". Type not allowed as child.")

        child.postappend()
        return child

    def add(self, child, *args, **kwargs):
        """High level function that adds (appends) an annotation to an element, it will simply call append() for token annotation elements that fit within the scope. For span annotation, it will create and find or create the proper annotation layer and insert the element there"""
        addspanfromspanned = False
        if isinstance(self,AbstractStructureElement):
            if inspect.isclass(child):
                if issubclass(child, AbstractSpanAnnotation):
                    layerclass = ANNOTATIONTYPE2LAYERCLASS[child.ANNOTATIONTYPE]
                    addspanfromspanned = True
            elif isinstance(child, AbstractSpanAnnotation):
                layerclass = ANNOTATIONTYPE2LAYERCLASS[child.ANNOTATIONTYPE]
                addspanfromspanned = True

        if not addspanfromspanned: #pylint: disable=too-many-nested-blocks
            return self.append(child,*args,**kwargs)
        else:
            #collect ancestors of the current element,
            allowedparents = [self] + list(self.ancestors(AbstractStructureElement))
            #find common ancestors of structure elements in the arguments, and check whether it has the required annotation layer, create one if necessary
            for e in commonancestors(AbstractStructureElement,  *[ x for x in args if isinstance(x, AbstractStructureElement)] ):
                if e in allowedparents: #is the element in the list of allowed parents according to this element?
                    if AbstractAnnotationLayer in e.ACCEPTED_DATA or layerclass in e.ACCEPTED_DATA:
                        if 'set' in kwargs:
                            set = kwargs['set']
                        else:
                            try:
                                set = self.doc.defaultset(layerclass)
                            except KeyError:
                                raise Exception("No set defined when adding span annotation and none could be inferred")
                        try:
                            layer = next(e.select(layerclass,set,True))
                        except StopIteration:
                            layer = e.append(layerclass)
                        return layer.append(child,*args,**kwargs)

            raise Exception("Unable to find suitable common ancestor to create annotation layer")




    @classmethod
    def findreplaceables(Class, parent, set=None,**kwargs):
        """Find replaceable elements. Auxiliary function used by replace(). Can be overriden for more fine-grained control. Mostly for internal use."""
        return list(parent.select(Class,set,False))



    def updatetext(self):
        """Internal method, recompute textual value. Only for elements that are a TEXTCONTAINER"""
        if self.TEXTCONTAINER:
            s = ""
            for child in self:
                if isinstance(child, AbstractElement):
                    child.updatetext()
                    s += child.text()
                elif isstring(child):
                    s += child
            self.data = [s]

    def replace(self, child, *args, **kwargs):
        """Appends a child element like ``append()``, but replaces any existing child element of the same type and set. If no such child element exists, this will act the same as append()

        Keyword arguments:
            * ``alternative`` - If set to True, the *replaced* element will be made into an alternative. Simply use ``append()`` if you want the added element
            to be an alternative.

        See ``append()`` for more information.
        """

        if 'set' in kwargs:
            set = kwargs['set']
            del kwargs['set']
        else:
            try:
                set = child.set
            except AttributeError:
                set = None

        if inspect.isclass(child):
            Class = child
            replace = Class.findreplaceables(self, set, **kwargs)
        elif (self.TEXTCONTAINER or self.PHONCONTAINER) and isstring(child):
            #replace will replace ALL text content, removing text markup along the way!
            self.data = []
            return self.append(child, *args,**kwargs)
        else:
            Class = child.__class__
            kwargs['instance'] = child
            replace = Class.findreplaceables(self,set,**kwargs)
            del kwargs['instance']

        kwargs['set'] = set #was deleted temporarily for findreplaceables

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
            e = self.append(child, *args, **kwargs)
            self.updatetext()
            return e

    def ancestors(self, Class=None):
        """Generator yielding all ancestors of this element, effectively back-tracing its path to the root element. A tuple of multiple classes may be specified."""
        e = self
        while e:
            if e.parent:
                e = e.parent
                if not Class or isinstance(e,Class):
                    yield e
                elif isinstance(Class, tuple):
                    for C in Class:
                        if isinstance(e,C):
                            yield e
            else:
                break

    def ancestor(self, *Classes):
        """Find the most immediate ancestor of the specified type, multiple classes may be specified"""
        for e in self.ancestors(tuple(Classes)):
            return e
        raise NoSuchAnnotation


    def xml(self, attribs = None,elements = None, skipchildren = False):
        """Serialises the FoLiA element to XML, by returning an XML Element (in lxml.etree) for this element and all its children. For string output, consider the xmlstring() method instead."""
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})

        if not attribs: attribs = {}
        if not elements: elements = []

        if self.id:
            attribs['{http://www.w3.org/XML/1998/namespace}id'] = self.id

        #Some attributes only need to be added if they are not the same as what's already set in the declaration
        if not isinstance(self, AbstractAnnotationLayer):
            if '{' + NSFOLIA + '}set' not in attribs: #do not override if overloaded function already set it
                try:
                    if self.set:
                        if not self.ANNOTATIONTYPE in self.doc.annotationdefaults or len(self.doc.annotationdefaults[self.ANNOTATIONTYPE]) != 1 or list(self.doc.annotationdefaults[self.ANNOTATIONTYPE].keys())[0] != self.set:
                            if self.set != None:
                                attribs['{' + NSFOLIA + '}set'] = self.set
                except AttributeError:
                    pass

        if '{' + NSFOLIA + '}class' not in attribs: #do not override if caller already set it
            try:
                if self.cls:
                    attribs['{' + NSFOLIA + '}class'] = self.cls
            except AttributeError:
                pass

        if '{' + NSFOLIA + '}annotator' not in attribs: #do not override if caller already set it
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

        if '{' + NSFOLIA + '}confidence' not in attribs: #do not override if caller already set it
            if self.confidence:
                attribs['{' + NSFOLIA + '}confidence'] = str(self.confidence)

        if '{' + NSFOLIA + '}n' not in attribs: #do not override if caller already set it
            if self.n:
                attribs['{' + NSFOLIA + '}n'] = str(self.n)

        if '{' + NSFOLIA + '}auth' not in attribs: #do not override if caller already set it
            try:
                if not self.AUTH or not self.auth: #(former is static, latter isn't)
                    attribs['{' + NSFOLIA + '}auth'] = 'no'
            except AttributeError:
                pass

        if '{' + NSFOLIA + '}datetime' not in attribs: #do not override if caller already set it
            if self.datetime and ((not (self.ANNOTATIONTYPE in self.doc.annotationdefaults)) or (not ( 'datetime' in self.doc.annotationdefaults[self.ANNOTATIONTYPE][self.set])) or (self.datetime != self.doc.annotationdefaults[self.ANNOTATIONTYPE][self.set]['datetime'])):
                attribs['{' + NSFOLIA + '}datetime'] = self.datetime.strftime("%Y-%m-%dT%H:%M:%S")

        if '{' + NSFOLIA + '}src' not in attribs: #do not override if caller already set it
            if self.src:
                attribs['{' + NSFOLIA + '}src'] = self.src

        if '{' + NSFOLIA + '}speaker' not in attribs: #do not override if caller already set it
            if self.speaker:
                attribs['{' + NSFOLIA + '}speaker'] = self.speaker

        if '{' + NSFOLIA + '}begintime' not in attribs: #do not override if caller already set it
            if self.begintime:
                attribs['{' + NSFOLIA + '}begintime'] = "%02d:%02d:%02d.%03d" % self.begintime

        if '{' + NSFOLIA + '}endtime' not in attribs: #do not override if caller already set it
            if self.endtime:
                attribs['{' + NSFOLIA + '}endtime'] = "%02d:%02d:%02d.%03d" % self.endtime


        if self.XLINK:
            if self.href:
                attribs['{http://www.w3.org/1999/xlink}href'] = self.href
                if not self.xlinktype:
                    attribs['{http://www.w3.org/1999/xlink}type'] = "simple"
            if self.xlinktype:
                attribs['{http://www.w3.org/1999/xlink}type'] = self.xlinktype
            if self.xlinklabel:
                attribs['{http://www.w3.org/1999/xlink}label'] = self.xlinklabel
            if self.xlinkrole:
                attribs['{http://www.w3.org/1999/xlink}role'] = self.xlinkrole
            if self.xlinkshow:
                attribs['{http://www.w3.org/1999/xlink}show'] = self.xlinkshow
            if self.xlinktitle:
                attribs['{http://www.w3.org/1999/xlink}title'] = self.xlinktitle

        omitchildren =  []

        #Are there predetermined Features in ACCEPTED_DATA?
        for c in self.ACCEPTED_DATA:
            if issubclass(c, Feature) and c.SUBSET:
                #Do we have any of those?
                for c2 in self.data:
                    if c2.__class__ is c and c.SUBSET == c2.SUBSET and c2.cls:
                        #Yes, serialize them as attributes
                        attribs[c2.SUBSET] = c2.cls
                        omitchildren.append(c2) #and skip them as elements
                        break #only one

        e  = makeelement(E, '{' + NSFOLIA + '}' + self.XMLTAG, **attribs)



        if not skipchildren and self.data:
            #append children,
            # we want make sure that text elements are in the right order, 'current' class first
            # so we first put them in  a list
            textelements = []
            otherelements = []
            for child in self:
                if isinstance(child, TextContent):
                    if child.cls == 'current':
                        textelements.insert(0, child)
                    else:
                        textelements.append(child)
                elif not child in omitchildren:
                    otherelements.append(child)
            for child in textelements+otherelements:
                if (self.TEXTCONTAINER or self.PHONCONTAINER) and isstring(child):
                    if len(e) == 0:
                        if e.text:
                            e.text += child
                        else:
                            e.text = child
                    else:
                        #add to tail of last child
                        if e[-1].tail:
                            e[-1].tail += child
                        else:
                            e[-1].tail = child

                else:
                    xml = child.xml() #may return None in rare occassions, meaning we wan to skip
                    if not xml is None:
                        e.append(xml)

        if elements: #extra elements
            for e2 in elements:
                e.append(e2)
        return e


    def json(self, attribs=None, recurse=True, ignorelist=False):
        jsonnode = {}

        jsonnode['type'] = self.XMLTAG
        if self.id:
            jsonnode['id'] = self.id
        if self.set:
            jsonnode['set'] = self.set
        if self.cls:
            jsonnode['class'] = self.cls
        if self.annotator:
            jsonnode['annotator'] = self.annotator
        if self.annotatortype:
            if self.annotatortype == AnnotatorType.AUTO:
                jsonnode['annotatortype'] = "auto"
            elif self.annotatortype == AnnotatorType.MANUAL:
                jsonnode['annotatortype'] = "manual"
        if self.confidence:
            jsonnode['confidence'] = self.confidence
        if self.n:
            jsonnode['n'] = self.n
        if self.auth:
            jsonnode['auth'] = self.auth
        if self.datetime:
            jsonnode['datetime'] = self.datetime.strftime("%Y-%m-%dT%H:%M:%S")

        if recurse: #pylint: disable=too-many-nested-blocks
            jsonnode['children'] = []
            if self.TEXTCONTAINER:
                jsonnode['text'] = self.text()
            if self.PHONCONTAINER:
                jsonnode['phon'] = self.phon()
            for child in self:
                if self.TEXTCONTAINER and isstring(child):
                    jsonnode['children'].append(child)
                elif not self.PHONCONTAINER:
                    #check ignore list
                    ignore = False
                    if ignorelist:
                        for e in ignorelist:
                            if isinstance(child,e):
                                ignore = True
                                break
                    if not ignore:
                        jsonnode['children'].append(child.json(attribs,recurse,ignorelist))

        if attribs:
            for attrib in attribs:
                jsonnode[attrib] = attribs

        return jsonnode



    def xmlstring(self, pretty_print=False):
        """Serialises this FoLiA element to XML, returns a (unicode) string with XML representation for this element and all its children."""
        s = ElementTree.tostring(self.xml(), xml_declaration=False, pretty_print=pretty_print, encoding='utf-8')
        if sys.version < '3':
            if isinstance(s, str):
                s = unicode(s,'utf-8') #pylint: disable=undefined-variable
        else:
            if isinstance(s,bytes):
                s = str(s,'utf-8')

        s = s.replace('ns0:','') #ugly patch to get rid of namespace prefix
        s = s.replace(':ns0','')
        return s


    def select(self, Class, set=None, recursive=True,  ignore=True, node=None): #pylint: disable=bad-classmethod-argument,redefined-builtin
        """Select child elements of the specified class.

        A further restriction can be made based on set. Whether or not to apply recursively (by default enabled) can also be configured, optionally with a list of elements never to recurse into.

        Arguments:
            * ``Class``: The class to select; any python class subclassed off `'AbstractElement``
            * ``set``: The set to match against, only elements pertaining to this set will be returned. If set to None (default), all elements regardless of set will be returned.
            * ``recursive``: Select recursively? Descending into child
              elements? Boolean defaulting to True.
            * ``ignore``: A list of Classes to ignore, if set to True instead
                of a list, all non-authoritative elements will be skipped (this is the default behaviour).
                It is common not to
               want to recurse into the following elements:
               ``folia.Alternative``, ``folia.AlternativeLayer``,
               ``folia.Suggestion``, and ``folia.Original``. These elements
               contained in these are never *authorative*.
               set to the boolean True rather than a list, this will be the default list. You may also include the boolean True as a member of a list, if you want to skip additional tags along non-authoritative ones.
            * ``node``: Reserved for internal usage, used in recursion.

        Returns:
            A generator of elements (instances)

        Example::

            text.select(folia.Sense, 'cornetto', True, [folia.Original, folia.Suggestion, folia.Alternative] )

        """

        #if ignorelist is True:
        #    ignorelist = default_ignore

        if not node:
            node = self
        for e in self.data: #pylint: disable=too-many-nested-blocks
            if (not self.TEXTCONTAINER and not self.PHONCONTAINER) or isinstance(e, AbstractElement):
                if ignore is True:
                    try:
                        if not e.auth:
                            continue
                    except AttributeError:
                        #not all elements have auth attribute..
                        pass
                elif ignore: #list
                    doignore = False
                    for c in ignore:
                        if c is True:
                            try:
                                if not e.auth:
                                    doignore =True
                                    break
                            except AttributeError:
                                #not all elements have auth attribute..
                                pass
                        elif c == e.__class__ or issubclass(e.__class__,c):
                            doignore = True
                            break
                    if doignore:
                        continue

                if isinstance(e, Class):
                    if not set is None:
                        try:
                            if e.set != set:
                                continue
                        except AttributeError:
                            continue
                    yield e
                if recursive:
                    for e2 in e.select(Class, set, recursive, ignore, e):
                        if not set is None:
                            try:
                                if e2.set != set:
                                    continue
                            except AttributeError:
                                continue
                        yield e2

    def count(self, Class, set=None, recursive=True,  ignore=True, node=None):
        """Like select, but instead of returning the elements, it merely counts them"""
        return sum(1 for i in self.select(Class,set,recursive,ignore,node) )

    def items(self, founditems=[]): #pylint: disable=dangerous-default-value
        """Returns a depth-first flat list of *all* items below this element (not limited to AbstractElement)"""
        l = []
        for e in self.data:
            if  e not in founditems: #prevent going in recursive loops
                l.append(e)
                if isinstance(e, AbstractElement):
                    l += e.items(l)
        return l

    def getindex(self, child, recursive=True, ignore=True):
        """returns the index at which an element occurs, recursive by default!"""

        #breadth first search
        for i, c in enumerate(self.data):
            if c is child:
                return i
        if recursive:  #pylint: disable=too-many-nested-blocks
            for i, c in enumerate(self.data):
                if ignore is True:
                    try:
                        if not c.auth:
                            continue
                    except AttributeError:
                        #not all elements have auth attribute..
                        pass
                elif ignore: #list
                    doignore = False
                    for e in ignore:
                        if e is True:
                            try:
                                if not c.auth:
                                    doignore =True
                                    break
                            except AttributeError:
                                #not all elements have auth attribute..
                                pass
                        elif e == c.__class__ or issubclass(c.__class__,e):
                            doignore = True
                            break
                    if doignore:
                        continue
                if isinstance(c, AbstractElement):
                    j = c.getindex(child, recursive)
                    if j != -1:
                        return i #yes, i ... not j!
        return -1


    def next(self, Class=True, scope=True, reverse=False):
        """Returns the next element, if it is of the specified type and if it does not cross the boundary of the defined scope. Returns None if no next element is found. Non-authoritative elements are never returned.

        Arguments:
            * ``Class``: The class to select; any python class subclassed off `'AbstractElement``, may also be a tuple of multiple classes. Set to ``True`` to constrain to the same class as that of the current instance, set to ``None`` to not constrain at all
            * ``scope``: A list of classes which are never crossed looking for a next element. Set to ``True`` to constrain to a default list of structure elements (Sentence,Paragraph,Division,Event, ListItem,Caption), set to ``None`` to not constrain at all.

        """
        if Class is True: Class = self.__class__
        if scope is True: scope = STRUCTURESCOPE

        structural = Class is not None and issubclass(Class,AbstractStructureElement)

        if reverse:
            order = reversed
            descendindex = -1
        else:
            order = lambda x: x #pylint: disable=redefined-variable-type
            descendindex = 0

        child = self
        parent = self.parent
        while parent: #pylint: disable=too-many-nested-blocks
            if len(parent) > 1:
                returnnext = False
                for e in order(parent):
                    if e is child:
                        returnnext = True
                    elif returnnext and e.auth and not isinstance(e,AbstractAnnotationLayer) and (not structural or (structural and (not isinstance(e,(AbstractTokenAnnotation,TextContent)) ) )):
                        if structural and isinstance(e,Correction):
                            if not list(e.select(AbstractStructureElement)): #skip-over non-structural correction
                                continue

                        if Class is None or (isinstance(Class,tuple) and (any(isinstance(e,C) for C in Class))) or isinstance(e,Class):
                            return e
                        else:
                            #this is not yet the element of the type we are looking for, we are going to descend again in the very leftmost (rightmost if reversed) branch only
                            while e.data:
                                e = e.data[descendindex]
                                if not isinstance(e, AbstractElement):
                                    return None #we've gone too far
                                if e.auth and not isinstance(e,AbstractAnnotationLayer):
                                    if Class is None or (isinstance(Class,tuple) and (any(isinstance(e,C) for C in Class))) or isinstance(e,Class):
                                        return e
                                    else:
                                        #descend deeper
                                        continue
                        return None

            #generational iteration
            child = parent
            if scope is not None and child in scope:
                #you shall not pass!
                break
            parent = parent.parent

        return None



    def previous(self, Class=True, scope=True):
        """Returns the previous element, if it is of the specified type and if it does not cross the boundary of the defined scope. Returns None if no next element is found. Non-authoritative elements are never returned.

        Arguments:
            * ``Class``: The class to select; any python class subclassed off `'AbstractElement``. Set to ``True`` to constrain to the same class as that of the current instance, set to ``None`` to not constrain at all
            * ``scope``: A list of classes which are never crossed looking for a next element. Set to ``True`` to constrain to a default list of structure elements (Sentence,Paragraph,Division,Event, ListItem,Caption), set to ``None`` to not constrain at all.

        """
        return self.next(Class,scope, True)

    def leftcontext(self, size, placeholder=None, scope=None):
        """Returns the left context for an element, as a list. This method crosses sentence/paragraph boundaries by default, which can be restricted by setting scope"""

        if size == 0: return [] #for efficiency

        context = []
        e = self
        while len(context) < size:
            e = e.previous(True,scope)
            if not e: break
            context.append(e)

        if placeholder:
            while len(context) < size:
                context.append(placeholder)

        context.reverse()
        return context


    def rightcontext(self, size, placeholder=None, scope=None):
        """Returns the right context for an element, as a list. This method crosses sentence/paragraph boundaries by default, which can be restricted by setting scope"""

        if size == 0: return [] #for efficiency

        context = []
        e = self
        while len(context) < size:
            e = e.next(True,scope)
            if not e: break
            context.append(e)

        if placeholder:
            while len(context) < size:
                context.append(placeholder)

        return context

    def context(self, size, placeholder=None, scope=None):
        """Returns this word in context, {size} words to the left, the current word, and {size} words to the right"""
        return self.leftcontext(size, placeholder,scope) + [self] + self.rightcontext(size, placeholder,scope)

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None, origclass = None):
        """Returns a RelaxNG definition for this element (as an XML element (lxml.etree) rather than a string)"""

        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })

        if origclass: cls = origclass

        preamble = []
        try:
            if cls.__doc__:
                E2 = ElementMaker(namespace="http://relaxng.org/ns/annotation/0.9", nsmap={'a':'http://relaxng.org/ns/annotation/0.9'} )
                preamble.append(E2.documentation(cls.__doc__))
        except AttributeError:
            pass

        if cls.REQUIRED_ATTRIBS is None: cls.REQUIRED_ATTRIBS = () #bit hacky
        if cls.OPTIONAL_ATTRIBS is None: cls.OPTIONAL_ATTRIBS = () #bit hacky


        attribs = [ ]
        if cls.REQUIRED_ATTRIBS and Attrib.ID in cls.REQUIRED_ATTRIBS:
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
            attribs.append(  E.attribute(E.data(type='double',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'), name='confidence') )
        elif Attrib.CONFIDENCE in cls.OPTIONAL_ATTRIBS:
            attribs.append(  E.optional( E.attribute(E.data(type='double',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'), name='confidence') ) )
        if Attrib.N in cls.REQUIRED_ATTRIBS:
            attribs.append( E.attribute( name='n') )
        elif Attrib.N in cls.OPTIONAL_ATTRIBS:
            attribs.append( E.optional( E.attribute( name='n') ) )
        if Attrib.DATETIME in cls.REQUIRED_ATTRIBS:
            attribs.append( E.attribute(E.data(type='dateTime',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'), name='datetime') )
        elif Attrib.DATETIME in cls.OPTIONAL_ATTRIBS:
            attribs.append( E.optional( E.attribute( E.data(type='dateTime',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'),  name='datetime') ) )
        if Attrib.BEGINTIME in cls.REQUIRED_ATTRIBS:
            attribs.append(E.attribute(name='begintime') )
        elif Attrib.BEGINTIME in cls.OPTIONAL_ATTRIBS:
            attribs.append( E.optional( E.attribute(name='begintime') ) )
        if Attrib.ENDTIME in cls.REQUIRED_ATTRIBS:
            attribs.append(E.attribute(name='endtime') )
        elif Attrib.ENDTIME in cls.OPTIONAL_ATTRIBS:
            attribs.append( E.optional( E.attribute(name='endtime') ) )
        if Attrib.SRC in cls.REQUIRED_ATTRIBS:
            attribs.append(E.attribute(name='src') )
        elif Attrib.SRC in cls.OPTIONAL_ATTRIBS:
            attribs.append( E.optional( E.attribute(name='src') ) )
        if Attrib.SPEAKER in cls.REQUIRED_ATTRIBS:
            attribs.append(E.attribute(name='speaker') )
        elif Attrib.SPEAKER in cls.OPTIONAL_ATTRIBS:
            attribs.append( E.optional( E.attribute(name='speaker') ) )
        if cls.XLINK:
            attribs += [ #loose interpretation of specs, not checking whether xlink combinations are valid
                    E.optional(E.attribute(name='href',ns="http://www.w3.org/1999/xlink"),E.attribute(name='type',ns="http://www.w3.org/1999/xlink") ),
                    E.optional(E.attribute(name='role',ns="http://www.w3.org/1999/xlink")),
                    E.optional(E.attribute(name='title',ns="http://www.w3.org/1999/xlink")),
                    E.optional(E.attribute(name='label',ns="http://www.w3.org/1999/xlink")),
                    E.optional(E.attribute(name='show',ns="http://www.w3.org/1999/xlink")),
            ]

        attribs.append( E.optional( E.attribute( name='auth' ) ) )



        if extraattribs:
            for e in extraattribs:
                attribs.append(e) #s

        attribs.append( E.ref(name="allow_foreign_attributes") )


        elements = [] #(including attributes)
        if cls.TEXTCONTAINER or cls.PHONCONTAINER:
            elements.append( E.text() )
        done = {}
        if includechildren and cls.ACCEPTED_DATA: #pylint: disable=too-many-nested-blocks
            for c in cls.ACCEPTED_DATA:
                if c.__name__[:8] == 'Abstract' and inspect.isclass(c):
                    for c2 in globals().values():
                        try:
                            if inspect.isclass(c2) and issubclass(c2, c):
                                try:
                                    if c2.XMLTAG and c2.XMLTAG not in done:
                                        if c2.OCCURRENCES == 1:
                                            elements.append( E.optional( E.ref(name=c2.XMLTAG) ) )
                                        else:
                                            elements.append( E.zeroOrMore( E.ref(name=c2.XMLTAG) ) )
                                            if c2.XMLTAG == 'item': #nasty hack for backward compatibility with deprecated listitem element
                                                elements.append( E.zeroOrMore( E.ref(name='listitem') ) ) 
                                        done[c2.XMLTAG] = True
                                except AttributeError:
                                    continue
                        except TypeError:
                            pass
                elif issubclass(c, Feature) and c.SUBSET:
                    attribs.append( E.optional( E.attribute(name=c.SUBSET)))  #features as attributes
                else:
                    try:
                        if c.XMLTAG and c.XMLTAG not in done:
                            if cls.REQUIRED_DATA and c in cls.REQUIRED_DATA:
                                if c.OCCURRENCES == 1:
                                    elements.append( E.ref(name=c.XMLTAG) )
                                else:
                                    elements.append( E.oneOrMore( E.ref(name=c.XMLTAG) ) )
                            elif c.OCCURRENCES == 1:
                                elements.append( E.optional( E.ref(name=c.XMLTAG) ) )
                            else:
                                elements.append( E.zeroOrMore( E.ref(name=c.XMLTAG) ) )
                                if c.XMLTAG == 'item':
                                    #nasty hack for backward compatibility with deprecated listitem element
                                    elements.append( E.zeroOrMore( E.ref(name='listitem') )  )
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
    def parsexml(Class, node, doc): #pylint: disable=bad-classmethod-argument
        """Internal class method used for turning an XML element into an instance of the Class.

        Args:
            * ``node`' - XML Element
            * ``doc`` - Document

        Returns:
            An instance of the current Class.
        """

        assert issubclass(Class, AbstractElement)

        if doc.preparsexmlcallback:
            result = doc.preparsexmlcallback(node)
            if not result:
                return None
            if isinstance(result, AbstractElement):
                return result



        dcoi = node.tag.startswith('{' + NSDCOI + '}')
        args = []
        kwargs = {}
        text = None #for dcoi support
        if (Class.TEXTCONTAINER or Class.PHONCONTAINER) and node.text:
            args.append(node.text)


        for subnode in node: #pylint: disable=too-many-nested-blocks
            #don't trip over comments
            if not isinstance(subnode, ElementTree._Comment): #pylint: disable=protected-access
                if subnode.tag.startswith('{' + NSFOLIA + '}'):
                    if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] Processing subnode " + subnode.tag[nslen:],file=stderr)
                    e = doc.parsexml(subnode, Class)
                    if e is not None:
                        args.append(e)
                    if (Class.TEXTCONTAINER or Class.PHONCONTAINER) and subnode.tail:
                        args.append(subnode.tail)
                elif subnode.tag.startswith('{' + NSDCOI + '}'):
                    #Dcoi support
                    if Class is Text and subnode.tag[nslendcoi:] == 'body':
                        for subsubnode in subnode:
                            if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] Processing DCOI subnode " + subnode.tag[nslendcoi:],file=stderr)
                            e = doc.parsexml(subsubnode, Class)
                            if e is not None:
                                args.append(e)
                    else:
                        if doc.debug >= 1: print( "[PyNLPl FoLiA DEBUG] Processing DCOI subnode " + subnode.tag[nslendcoi:],file=stderr)
                        e = doc.parsexml(subnode, Class)
                        if e is not None:
                            args.append(e)
                elif doc.debug >= 1:
                    print("[PyNLPl FoLiA DEBUG] Ignoring subnode outside of FoLiA namespace: " + subnode.tag,file=stderr)



        if dcoi:
            dcoipos = dcoilemma = dcoicorrection = dcoicorrectionoriginal = None
        for key, value in node.attrib.items():
            if key[0] == '{' or key =='XMLid':
                if key == '{http://www.w3.org/XML/1998/namespace}id' or key == 'XMLid':
                    key = 'id'
                elif key.startswith( '{' + NSFOLIA + '}'):
                    key = key[nslen:]
                    if key == 'id':
                        #ID in FoLiA namespace is always a reference, passed in kwargs as follows:
                        key = 'idref'
                elif Class.XLINK and key.startswith('{http://www.w3.org/1999/xlink}'):
                    key = key[30:]
                    if key != 'href':
                        key = 'xlink' + key #xlinktype, xlinkrole, xlinklabel, xlinkshow, etc..
                elif key.startswith('{' + NSDCOI + '}'):
                    key = key[nslendcoi:]

            #D-Coi support:
            if dcoi:
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
        if dcoi and TextContent in Class.ACCEPTED_DATA and node.text:
            text = node.text.strip()

            kwargs['text'] = text
            if not AnnotationType.TOKEN in doc.annotationdefaults:
                doc.declare(AnnotationType.TOKEN, set='http://ilk.uvt.nl/folia/sets/ilktok.foliaset')

        if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] Found " + node.tag[nslen:],file=stderr)
        instance = Class(doc, *args, **kwargs)
        #if id:
        #    if doc.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Adding to index: " + id
        #    doc.index[id] = instance
        if dcoi:
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

        if doc.parsexmlcallback:
            result = doc.parsexmlcallback(instance)
            if not result:
                return None
            if isinstance(result, AbstractElement):
                return result

        return instance

    def resolveword(self, id):
        return None

    def remove(self, child):
        """Removes the child element"""
        if not isinstance(child, AbstractElement):
            raise ValueError("Expected AbstractElement, got " + str(type(child)))
        if child.parent == self:
            child.parent = None
        self.data.remove(child)
        #delete from index
        if child.id and self.doc and child.id in self.doc.index:
            del self.doc.index[child.id]

    def incorrection(self):
        """Is this element part of a correction? If it is, it returns the Correction element (evaluating to True), otherwise it returns None"""
        e = self.parent

        while e:
            if isinstance(e, Correction):
                return e
            if isinstance(e, AbstractStructureElement):
                break
            e = e.parent
        return None

class Description(AbstractElement):
    """Description is an element that can be used to associate a description with almost any other FoLiA element"""

    def __init__(self,doc, *args, **kwargs):
        """Required keyword arguments:
                * ``value=``: The text content for the description (``str`` or ``unicode``)
        """
        if 'value' in kwargs:
            if kwargs['value'] is None:
                self.value = ""
            elif isstring(kwargs['value']):
                self.value = u(kwargs['value'])
            else:
                if sys.version < '3':
                    raise Exception("value= parameter must be unicode or str instance, got " + str(type(kwargs['value'])))
                else:
                    raise Exception("value= parameter must be str instance, got " + str(type(kwargs['value'])))
            del kwargs['value']
        else:
            raise Exception("Description expects value= parameter")
        super(Description,self).__init__(doc, *args, **kwargs)

    def __nonzero__(self): #Python 2.x
        return bool(self.value)

    def __bool__(self):
        return bool(self.value)

    def __unicode__(self):
        return self.value

    def __str__(self):
        return self.value


    def xml(self, attribs = None,elements = None, skipchildren = False):
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})

        if not attribs:
            attribs = {}

        return E.desc(self.value, **attribs)

    def json(self,attribs =None, recurse=True, ignorelist=False):
        jsonnode = {'type': self.XMLTAG, 'value': self.value}
        if attribs:
            for attrib in attribs:
                jsonnode[attrib] = attrib
        return jsonnode

    @classmethod
    def parsexml(Class, node, doc):
        kwargs = {}
        kwargs['value'] = node.text
        return Description(doc, **kwargs)


    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.text(), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)

class AllowCorrections(object):
    def correct(self, **kwargs):
        """Apply a correction (TODO: documentation to be written still)"""

        if 'insertindex_offset' in kwargs:
            del kwargs['insertindex_offset'] #dealt with in an earlier stage

        if 'confidence' in kwargs and kwargs['confidence'] is None:
            del kwargs['confidence']

        if 'reuse' in kwargs:
            #reuse an existing correction instead of making a new one
            if isinstance(kwargs['reuse'], Correction):
                c = kwargs['reuse']
            else: #assume it's an index
                try:
                    c = self.doc.index[kwargs['reuse']]
                    assert isinstance(c, Correction)
                except:
                    raise ValueError("reuse= must point to an existing correction (id or instance)! Got " + str(kwargs['reuse']))

            suggestionsonly = (not c.hasnew(True) and not c.hasoriginal(True) and c.hassuggestions(True))

            if 'new' in kwargs and c.hascurrent():
                #can't add new if there's current, so first set original to current, and then delete current

                if 'current' in kwargs:
                    raise Exception("Can't set both new= and current= !")
                if 'original' not in kwargs:
                    kwargs['original'] = c.current()

                c.remove(c.current())
        else:
            if 'id' not in kwargs and 'generate_id_in' not in kwargs:
                kwargs['generate_id_in'] = self
            kwargs2 = copy(kwargs)
            for x in ['new','original','suggestion', 'suggestions','current', 'insertindex','nooriginal']:
                if x in kwargs2:
                    del kwargs2[x]
            c = Correction(self.doc, **kwargs2)

        addnew = False
        if 'insertindex' in kwargs:
            insertindex = int(kwargs['insertindex'])
            del kwargs['insertindex']
        else:
            insertindex = -1 #append

        if 'nooriginal' in kwargs and kwargs['nooriginal']:
            nooriginal = True
            del kwargs['nooriginal']
        else:
            nooriginal = False

        if 'current' in kwargs:
            if 'original' in kwargs or 'new' in kwargs: raise Exception("When setting current=, original= and new= can not be set!")
            if not isinstance(kwargs['current'], list) and not isinstance(kwargs['current'], tuple): kwargs['current'] = [kwargs['current']] #support both lists (for multiple elements at once), as well as single element
            c.replace(Current(self.doc, *kwargs['current']))
            for o in kwargs['current']: #delete current from current element
                if o in self and isinstance(o, AbstractElement): #pylint: disable=unsupported-membership-test
                    if insertindex == -1: insertindex = self.data.index(o)
                    self.remove(o)
            del kwargs['current']
        if 'new' in kwargs:
            if not isinstance(kwargs['new'], list) and not isinstance(kwargs['new'], tuple): kwargs['new'] = [kwargs['new']] #support both lists (for multiple elements at once), as well as single element
            addnew = New(self.doc, *kwargs['new']) #pylint: disable=redefined-variable-type
            c.replace(addnew)
            for current in c.select(Current): #delete current if present
                c.remove(current)
            del kwargs['new']
        if 'original' in kwargs and kwargs['original']:
            if not isinstance(kwargs['original'], list) and not isinstance(kwargs['original'], tuple): kwargs['original'] = [kwargs['original']] #support both lists (for multiple elements at once), as well as single element
            c.replace(Original(self.doc, *kwargs['original']))
            for o in kwargs['original']: #delete original from current element
                if o in self and isinstance(o, AbstractElement): #pylint: disable=unsupported-membership-test
                    if insertindex == -1: insertindex = self.data.index(o)
                    self.remove(o)
            for o in kwargs['original']: #make sure IDs are still properly set after removal
                o.addtoindex()
            for current in c.select(Current):  #delete current if present
                c.remove(current)
            del kwargs['original']
        elif addnew and not nooriginal:
            #original not specified, find automagically:
            original = []
            for new in addnew:
                kwargs2 = {}
                if isinstance(new, TextContent):
                    kwargs2['cls'] = new.cls
                try:
                    set = new.set
                except AttributeError:
                    set = None
                #print("DEBUG: Finding replaceables within " + str(repr(self)) + " for ", str(repr(new)), " set " ,set , " args " ,repr(kwargs2),file=sys.stderr)
                replaceables = new.__class__.findreplaceables(self, set, **kwargs2)
                #print("DEBUG: " , len(replaceables) , " found",file=sys.stderr)
                original += replaceables
            if not original:
                #print("DEBUG: ", self.xmlstring(),file=sys.stderr)
                raise Exception("No original= specified and unable to automatically infer on " + str(repr(self)) + " for " + str(repr(new)) + " with set " + set)
            else:
                c.replace( Original(self.doc, *original))
                for current in c.select(Current):  #delete current if present
                    c.remove(current)

        if addnew and not nooriginal:
            for original in c.original():
                if original in self: #pylint: disable=unsupported-membership-test
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
                c.annotator = kwargs['annotator'] #pylint: disable=attribute-defined-outside-init
            if 'annotatortype' in kwargs:
                c.annotatortype = kwargs['annotatortype'] #pylint: disable=attribute-defined-outside-init
            if 'confidence' in kwargs:
                c.confidence = float(kwargs['confidence']) #pylint: disable=attribute-defined-outside-init
            c.addtoindex()
            del kwargs['reuse']
        else:
            c.addtoindex()
            if insertindex == -1:
                self.append(c)
            else:
                self.insert(insertindex, c)
        return c



class AllowTokenAnnotation(AllowCorrections):
    """Elements that allow token annotation (including extended annotation) must inherit from this class"""


    def annotations(self,Class,set=None):
        """Obtain annotations. Very similar to ``select()`` but raises an error if the annotation was not found.

        Arguments:
            * ``Class`` - The Class you want to retrieve (e.g. PosAnnotation)
            * ``set``   - The set you want to retrieve (defaults to None, which selects irregardless of set)

        Returns:
            A generator of elements

        Raises:
            ``NoSuchAnnotation`` if the specified annotation does not exist.
        """
        found = False
        for e in self.select(Class,set,True,default_ignore_annotations):
            found = True
            yield e
        if not found:
            raise NoSuchAnnotation()

    def hasannotation(self,Class,set=None):
        """Returns an integer indicating whether such as annotation exists, and if so, how many. See ``annotations()`` for a description of the parameters."""
        return sum( 1 for _ in self.select(Class,set,True,default_ignore_annotations))

    def annotation(self, type, set=None):
        """Will return a **single** annotation (even if there are multiple). Raises a ``NoSuchAnnotation`` exception if none was found"""
        for e in self.select(type,set,True,default_ignore_annotations):
            return e
        raise NoSuchAnnotation()

    def alternatives(self, Class=None, set=None):
        """Generator over alternatives, either all or only of a specific annotation type, and possibly restrained also by set.

        Arguments:
            * ``Class`` - The Class you want to retrieve (e.g. PosAnnotation). Or set to None to select all alternatives regardless of what type they are.
            * ``set``   - The set you want to retrieve (defaults to None, which selects irregardless of set)

        Returns:
            Generator of Alternative elements
        """

        for e in self.select(Alternative,None, True, []): #pylint: disable=too-many-nested-blocks
            if Class is None:
                yield e
            elif len(e) >= 1: #child elements?
                for e2 in e:
                    try:
                        if isinstance(e2, Class):
                            try:
                                if set is None or e2.set == set:
                                    yield e #not e2
                                    break #yield an alternative only once (in case there are multiple matches)
                            except AttributeError:
                                continue
                    except AttributeError:
                        continue


class AllowGenerateID(object):
    """Classes inherited from this class allow for automatic ID generation, using the convention of adding a period, the name of the element , another period, and a sequence number"""

    def _getmaxid(self, xmltag):
        try:
            if xmltag in self.maxid:
                return self.maxid[xmltag]
            else:
                return 0
        except AttributeError:
            return 0


    def _setmaxid(self, child):
        #print "set maxid on " + repr(self) + " for " + repr(child)
        try:
            self.maxid
        except AttributeError:
            self.maxid = {}#pylint: disable=attribute-defined-outside-init
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
                raise GenerateIDException("Unable to generate ID, expected a class such as Alternative, Correction, etc...")


        maxid = self._getmaxid(xmltag)

        id = None
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

            if id is None:
                raise GenerateIDException("Unable to generate ID, no parent ID could be found")

        origid = id

        while True:
            maxid += 1
            id = origid + '.' + xmltag + '.' + str(maxid)
            if not self.doc or id not in self.doc.index: #extra check
                break

        try:
            self.maxid
        except AttributeError:
            self.maxid = {}#pylint: disable=attribute-defined-outside-init
        self.maxid[xmltag] = maxid #Set MAX ID
        return id


class AbstractStructureElement(AbstractElement, AllowTokenAnnotation, AllowGenerateID):
    """Abstract element, all structure elements inherit from this class. Never instantiated directly."""



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
        self._setmaxid(e)
        return e


    def words(self, index = None):
        """Returns a generator of Word elements found (recursively) under this element.

        Arguments:
            * ``index``: If set to an integer, will retrieve and return the n'th element (starting at 0) instead of returning the list of all
        """
        if index is None:
            return self.select(Word,None,True,default_ignore_structure)
        else:
            if index < 0:
                index = self.count(Word,None,True,default_ignore_structure) + index
            for i, e in enumerate(self.select(Word,None,True,default_ignore_structure)):
                if i == index:
                    return e
            raise IndexError


    def paragraphs(self, index = None):
        """Returns a generator of Paragraph elements found (recursively) under this element.

        Arguments:
            * ``index``: If set to an integer, will retrieve and return the n'th element (starting at 0) instead of returning the generator of all
        """
        if index is None:
            return self.select(Paragraph,None,True,default_ignore_structure)
        else:
            if index < 0:
                index = self.count(Paragraph,None,True,default_ignore_structure) + index
            for i,e in enumerate(self.select(Paragraph,None,True,default_ignore_structure)):
                if i == index:
                    return e
            raise IndexError

    def sentences(self, index = None):
        """Returns a generator of Sentence elements found (recursively) under this element

        Arguments:
            * ``index``: If set to an integer, will retrieve and return the n'th element (starting at 0) instead of returning a generator of all
        """
        if index is None:
            return self.select(Sentence,None,True,default_ignore_structure)
        else:
            if index < 0:
                index = self.count(Sentence,None,True,default_ignore_structure) + index
            for i,e in enumerate(self.select(Sentence,None,True,default_ignore_structure)):
                if i == index:
                    return e
            raise IndexError

    def layers(self, annotationtype=None,set=None):
        """Returns a list of annotation layers found *directly* under this element, does not include alternative layers"""
        if inspect.isclass(annotationtype): annotationtype = annotationtype.ANNOTATIONTYPE
        return [ x for x in self.select(AbstractAnnotationLayer,set,False,True) if annotationtype is None or x.ANNOTATIONTYPE == annotationtype ]

    def hasannotationlayer(self, annotationtype=None,set=None):
        """Does the specified annotation layer exist?"""
        l = self.layers(annotationtype, set)
        return (len(l) > 0)

    def __eq__(self, other):
        return super(AbstractStructureElement, self).__eq__(other)


class AbstractTokenAnnotation(AbstractElement, AllowGenerateID):
    """Abstract element, all token annotation elements are derived from this class"""


    def append(self, child, *args, **kwargs):
        """See ``AbstractElement.append()``"""
        e = super(AbstractTokenAnnotation,self).append(child, *args, **kwargs)
        self._setmaxid(e)
        return e

class AbstractExtendedTokenAnnotation(AbstractTokenAnnotation):
    pass


class AbstractTextMarkup(AbstractElement):

    def __init__(self, doc, *args, **kwargs):
        if 'idref' in kwargs:
            self.idref = kwargs['idref']
            del kwargs['idref']
        else:
            self.idref = None

        if 'value' in kwargs:
            #for backward compatibility
            kwargs['text'] = kwargs['value']
            del kwargs['value']

        super(AbstractTextMarkup,self).__init__(doc, *args, **kwargs)

        #if self.value and (self.value != self.value.translate(ILLEGAL_UNICODE_CONTROL_CHARACTERS)):
        #    raise ValueError("There are illegal unicode control characters present in Text Markup Content: " + repr(self.value))

    def settext(self, text):
        self.data = [text]
        if not self.data:
            raise ValueError("Empty text content elements are not allowed")

    def resolve(self):
        if self.idref:
            return self.doc[self.idref]
        else:
            return self

    def xml(self, attribs = None,elements = None, skipchildren = False):
        if not attribs: attribs = {}
        if self.idref:
            attribs['id'] = self.idref
        return super(AbstractTextMarkup,self).xml(attribs,elements, skipchildren)

    def json(self,attribs =None, recurse=True, ignorelist=False):
        if not attribs: attribs = {}
        if self.idref:
            attribs['id'] = self.idref
        return super(AbstractTextMarkup,self).json(attribs,recurse, ignorelist)

    @classmethod
    def parsexml(Class, node, doc):
        if 'id' in node.attrib:
            idref = node.attrib['id']
            del node.attrib['id']
        else:
            idref = None
        instance = super(AbstractTextMarkup,Class).parsexml(node, doc)
        if idref:
            instance.idref = idref
        return instance

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })
        if not extraattribs: extraattribs = []
        extraattribs.append( E.optional(E.attribute(name='id' ))) #id reference
        return super(AbstractTextMarkup, cls).relaxng(includechildren, extraattribs, extraelements)


class TextMarkupString(AbstractTextMarkup):
    pass

class TextMarkupGap(AbstractTextMarkup):
    pass

class TextMarkupCorrection(AbstractTextMarkup):

    def __init__(self, doc, *args, **kwargs):
        if 'original' in kwargs:
            self.original = kwargs['original']
            del kwargs['original']
        else:
            self.original = None
        super(TextMarkupCorrection,self).__init__(doc, *args, **kwargs)

    def xml(self, attribs = None,elements = None, skipchildren = False):
        if not attribs: attribs = {}
        if self.original:
            attribs['original'] = self.original
        return super(TextMarkupCorrection,self).xml(attribs,elements, skipchildren)

    def json(self,attribs =None, recurse=True, ignorelist=False):
        if not attribs: attribs = {}
        if self.original:
            attribs['original'] = self.original
        return super(TextMarkupCorrection,self).json(attribs,recurse,ignorelist)

    @classmethod
    def parsexml(Class, node, doc):
        if 'original' in node.attrib:
            original = node.attrib['original']
            del node.attrib['original']
        else:
            original = None
        instance = super(TextMarkupCorrection,Class).parsexml(node, doc)
        if original:
            instance.original = original
        return instance

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })
        if not extraattribs: extraattribs = []
        extraattribs.append( E.optional(E.attribute(name='original' )))
        return super(TextMarkupCorrection, cls).relaxng(includechildren, extraattribs, extraelements)


class TextMarkupError(AbstractTextMarkup):
    pass

class TextMarkupStyle(AbstractTextMarkup):
    pass





class TextContent(AbstractElement):
    """Text content element (``t``), holds text to be associated with whatever element the text content element is a child of.

    Text content elements
    on structure elements like ``Paragraph`` and ``Sentence`` are by definition untokenised. Only on ``Word`` level and deeper they are by definition tokenised.

    Text content elements can specify offset that refer to text at a higher parent level. Use the following keyword arguments:
        * ``ref=``: The instance to point to, this points to the element holding the text content element, not the text content element itself.
        * ``offset=``: The offset where this text is found, offsets start at 0
    """


    def __init__(self, doc, *args, **kwargs):
        """Example::

                text = folia.TextContent(doc, 'test')

                text = folia.TextContent(doc, 'test',cls='original')

        """

        #for backward compatibility:
        if 'value' in kwargs:
            kwargs['text'] = kwargs['value']
            del kwargs['value']


        if 'offset' in kwargs: #offset
            self.offset = int(kwargs['offset'])
            del kwargs['offset']
        else:
            self.offset = None

        if 'ref' in kwargs: #reference to offset
            if isinstance(kwargs['ref'], AbstractElement):
                self.ref = kwargs['ref']
            else:
                try:
                    self.ref = doc.index[kwargs['ref']]
                except:
                    raise UnresolvableTextContent("Unable to resolve textcontent reference: " + kwargs['ref'] + " (class=" + self.cls+")")
            del kwargs['ref']
        else:
            self.ref = None #will be set upon parent.append()


        #If no class is specified, it defaults to 'current'. (FoLiA uncharacteristically predefines two classes for t: current and original)
        if 'cls' not in kwargs and 'class' not in kwargs:
            kwargs['cls'] = 'current'

        super(TextContent,self).__init__(doc, *args, **kwargs)

        doc.textclasses.add(self.cls)

        if not self.data:
            raise ValueError("Empty text content elements are not allowed")
        #if isstring(self.data[0]) and (self.data[0] != self.data[0].translate(ILLEGAL_UNICODE_CONTROL_CHARACTERS)):
        #    raise ValueError("There are illegal unicode control characters present in TextContent: " + repr(self.data[0]))


    def text(self):
        """Obtain the text (unicode instance)"""
        return super(TextContent,self).text() #AbstractElement will handle it now, merely overridden to get rid of parameters that dont make sense in this context

    def settext(self, text):
        self.data = [text]
        if not self.data:
            raise ValueError("Empty text content elements are not allowed")
        #if isstring(self.data[0]) and (self.data[0] != self.data[0].translate(ILLEGAL_UNICODE_CONTROL_CHARACTERS)):
        #    raise ValueError("There are illegal unicode control characters present in TextContent: " + repr(self.data[0]))


    def validateref(self):
        """Validates the Text Content's references. Raises UnresolvableTextContent when invalid"""

        if self.offset is None: return True #nothing to test
        if self.ref:
            ref = self.ref
        else:
            ref = self.finddefaultreference()

        if not ref:
            raise UnresolvableTextContent("Default reference for textcontent not found!")
        elif ref.hastext(self.cls):
            raise UnresolvableTextContent("Reference has no such text (class=" + self.cls+")")
        elif self.text() != ref.textcontent(self.cls).text()[self.offset:self.offset+len(self.data[0])]:
            raise UnresolvableTextContent("Referenced found but does not match!")
        else:
            #finally, we made it!
            return True






    def __unicode__(self):
        return self.text()

    def __str__(self):
        return self.text()

    def __eq__(self, other):
        if isinstance(other, TextContent):
            return self.text() == other.text()
        elif isstring(other):
            return self.text() == u(other)
        else:
            return False



    def finddefaultreference(self):
        """Find the default reference for text offsets:
          The parent of the current textcontent's parent (counting only Structure Elements and Subtoken Annotation Elements)

          Note: This returns not a TextContent element, but its parent. Whether the textcontent actually exists is checked later/elsewhere
        """

        depth = 0
        e = self
        while True:
            if e.parent:
                e = e.parent #pylint: disable=redefined-variable-type
            else:
                #no parent, breaking
                return False

            if isinstance(e,AbstractStructureElement) or isinstance(e,AbstractSubtokenAnnotation):
                depth += 1
                if depth == 2:
                    return e


        return False

    #Change in behaviour (FoLiA 0.10), iter() no longer iterates over the text itself!!


    #Change in behaviour (FoLiA 0.10), len() no longer return the length of the text!!


    @classmethod
    def findreplaceables(Class, parent, set, **kwargs):
        """(Method for internal usage, see AbstractElement)"""
        #some extra behaviour for text content elements, replace also based on the 'corrected' attribute:
        if 'cls' not in kwargs:
            kwargs['cls'] = 'current'
        replace = super(TextContent, Class).findreplaceables(parent, set, **kwargs)
        replace = [ x for x in replace if x.cls == kwargs['cls']]
        del kwargs['cls'] #always delete what we processed
        return replace


    @classmethod
    def parsexml(Class, node, doc):
        """(Method for internal usage, see AbstractElement)"""
        e = super(TextContent,Class).parsexml(node,doc)
        if 'offset' in node.attrib:
            e.offset = int(node.attrib['offset'])
        if 'ref' in node.attrib:
            e.ref = node.attrib['ref']
        return e



    def xml(self, attribs = None,elements = None, skipchildren = False):
        attribs = {}
        if not self.offset is None:
            attribs['{' + NSFOLIA + '}offset'] = str(self.offset)
        if self.parent and self.ref:
            attribs['{' + NSFOLIA + '}ref'] = self.ref.id

        #if self.cls != 'current' and not (self.cls == 'original' and any( isinstance(x, Original) for x in self.ancestors() )  ):
        #    attribs['{' + NSFOLIA + '}class'] = self.cls
        #else:
        #    if '{' + NSFOLIA + '}class' in attribs:
        #        del attribs['{' + NSFOLIA + '}class']
        #return E.t(self.value, **attribs)

        e = super(TextContent,self).xml(attribs,elements,skipchildren)
        if '{' + NSFOLIA + '}class' in e.attrib and e.attrib['{' + NSFOLIA + '}class'] == "current":
            #delete 'class=current'
            del e.attrib['{' + NSFOLIA + '}class']

        return e

    def json(self, attribs =None, recurse =True,ignorelist=False):
        attribs = {}
        if not self.offset is None:
            attribs['offset'] = self.offset
        if self.parent and self.ref:
            attribs['ref'] = self.ref.id
        return super(TextContent,self).json(attribs, recurse,ignorelist)


    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })
        if not extraattribs: extraattribs = []
        extraattribs.append( E.optional(E.attribute(name='offset' )))
        extraattribs.append( E.optional(E.attribute(name='ref' )))
        return super(TextContent, cls).relaxng(includechildren, extraattribs, extraelements)



class PhonContent(AbstractElement):
    """Phonetic content element (``ph``), holds a phonetic representation to be associated with whatever element the phonetic content element is a child of.

    Phonetic content elements behave much like text content elements

    Phonetic content elements can specify offset that refer to phonetic content at a higher parent level. Use the following keyword arguments:
        * ``ref=``: The instance to point to, this points to the element holding the text content element, not the text content element itself.
        * ``offset=``: The offset where this text is found, offsets start at 0
    """

    def __init__(self, doc, *args, **kwargs):
        """Example::

                phon = folia.PhonContent(doc, 'hɛˈləʊ̯')
                phon = folia.PhonContent(doc, 'hɛˈləʊ̯', cls="original")

        """

        if 'offset' in kwargs: #offset
            self.offset = int(kwargs['offset'])
            del kwargs['offset']
        else:
            self.offset = None

        if 'ref' in kwargs: #reference to offset
            if isinstance(kwargs['ref'], AbstractElement):
                self.ref = kwargs['ref']
            else:
                try:
                    self.ref = doc.index[kwargs['ref']]
                except:
                    raise UnresolvableTextContent("Unable to resolve phonetic content reference: " + kwargs['ref'] + " (class=" + self.cls+")")
            del kwargs['ref']
        else:
            self.ref = None #will be set upon parent.append()


        #If no class is specified, it defaults to 'current'. (FoLiA uncharacteristically predefines two classes for t: current and original)
        if 'cls' not in kwargs and 'class' not in kwargs:
            kwargs['cls'] = 'current'

        super(PhonContent,self).__init__(doc, *args, **kwargs)

        if not self.data:
            raise ValueError("Empty phonetic content elements are not allowed")
        #if isstring(self.data[0]) and (self.data[0] != self.data[0].translate(ILLEGAL_UNICODE_CONTROL_CHARACTERS)):
        #    raise ValueError("There are illegal unicode control characters present in TextContent: " + repr(self.data[0]))



    def phon(self):
        """Obtain the actual phonetic representation (unicode/str instance)"""
        return super(PhonContent,self).phon() #AbstractElement will handle it now, merely overridden to get rid of parameters that dont make sense in this context

    def setphon(self, phon):
        """Set the representation for the phonetic content (unicode instance), called whenever phon= is passed as a keyword argument to an element constructor  """
        self.data = [phon]
        if not self.data:
            raise ValueError("Empty phonetic content elements are not allowed")
        #if isstring(self.data[0]) and (self.data[0] != self.data[0].translate(ILLEGAL_UNICODE_CONTROL_CHARACTERS)):
        #    raise ValueError("There are illegal unicode control characters present in TextContent: " + repr(self.data[0]))


    def validateref(self):
        """Validates the Phonetic Content's references. Raises UnresolvableTextContent when invalid"""

        if self.offset is None: return True #nothing to test
        if self.ref:
            ref = self.ref
        else:
            ref = self.finddefaultreference()

        if not ref:
            raise UnresolvableTextContent("Default reference for phonetic content not found!")
        elif ref.hasphon(self.cls):
            raise UnresolvableTextContent("Reference has no such phonetic content (class=" + self.cls+")")
        elif self.phon() != ref.textcontent(self.cls).phon()[self.offset:self.offset+len(self.data[0])]:
            raise UnresolvableTextContent("Referenced found but does not match!")
        else:
            #finally, we made it!
            return True



    def __unicode__(self):
        return self.phon()

    def __str__(self):
        return self.phon()

    def __eq__(self, other):
        if isinstance(other, PhonContent):
            return self.phon() == other.phon()
        elif isstring(other):
            return self.phon() == u(other)
        else:
            return False

    #append is implemented, the default suffices

    def postappend(self):
        """(Method for internal usage, see ``AbstractElement.postappend()``)"""
        if isinstance(self.parent, Original):
            if self.cls == 'current': self.cls = 'original' #pylint: disable=attribute-defined-outside-init

        super(PhonContent, self).postappend()


    def finddefaultreference(self):
        """Find the default reference for text offsets:
          The parent of the current textcontent's parent (counting only Structure Elements and Subtoken Annotation Elements)

          Note: This returns not a TextContent element, but its parent. Whether the textcontent actually exists is checked later/elsewhere
        """

        depth = 0
        e = self
        while True:
            if e.parent:
                e = e.parent #pylint: disable=redefined-variable-type
            else:
                #no parent, breaking
                return False

            if isinstance(e,AbstractStructureElement) or isinstance(e,AbstractSubtokenAnnotation):
                depth += 1
                if depth == 2:
                    return e


        return False

    #Change in behaviour (FoLiA 0.10), iter() no longer iterates over the text itself!!


    #Change in behaviour (FoLiA 0.10), len() no longer return the length of the text!!


    @classmethod
    def findreplaceables(Class, parent, set, **kwargs):#pylint: disable=bad-classmethod-argument
        """(Method for internal usage, see AbstractElement)"""
        #some extra behaviour for text content elements, replace also based on the 'corrected' attribute:
        if 'cls' not in kwargs:
            kwargs['cls'] = 'current'
        replace = super(PhonContent, Class).findreplaceables(parent, set, **kwargs)
        replace = [ x for x in replace if x.cls == kwargs['cls']]
        del kwargs['cls'] #always delete what we processed
        return replace


    @classmethod
    def parsexml(Class, node, doc):#pylint: disable=bad-classmethod-argument
        """(Method for internal usage, see AbstractElement)"""
        e = super(PhonContent,Class).parsexml(node,doc)
        if e and 'offset' in node.attrib:
            e.offset = int(node.attrib['offset'])
        if e and 'ref' in node.attrib:
            e.ref = node.attrib['ref']
        return e



    def xml(self, attribs = None,elements = None, skipchildren = False):
        attribs = {}
        if not self.offset is None:
            attribs['{' + NSFOLIA + '}offset'] = str(self.offset)
        if self.parent and self.ref:
            attribs['{' + NSFOLIA + '}ref'] = self.ref.id

        #if self.cls != 'current' and not (self.cls == 'original' and any( isinstance(x, Original) for x in self.ancestors() )  ):
        #    attribs['{' + NSFOLIA + '}class'] = self.cls
        #else:
        #    if '{' + NSFOLIA + '}class' in attribs:
        #        del attribs['{' + NSFOLIA + '}class']
        #return E.t(self.value, **attribs)

        e = super(PhonContent,self).xml(attribs,elements,skipchildren)
        if '{' + NSFOLIA + '}class' in e.attrib and e.attrib['{' + NSFOLIA + '}class'] == "current":
            #delete 'class=current'
            del e.attrib['{' + NSFOLIA + '}class']

        return e

    def json(self, attribs =None, recurse =True,ignorelist=False):
        attribs = {}
        if not self.offset is None:
            attribs['offset'] = self.offset
        if self.parent and self.ref:
            attribs['ref'] = self.ref.id
        return super(PhonContent,self).json(attribs, recurse, ignorelist)


    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })
        if not extraattribs: extraattribs = []
        extraattribs.append( E.optional(E.attribute(name='offset' )))
        extraattribs.append( E.optional(E.attribute(name='ref' )))
        return super(PhonContent, cls).relaxng(includechildren, extraattribs, extraelements)

class Content(AbstractElement):     #used for raw content, subelement for Gap

    def __init__(self,doc, *args, **kwargs):
        if 'value' in kwargs:
            if isstring(kwargs['value']):
                self.value = u(kwargs['value'])
            elif kwargs['value'] is None:
                self.value = ""
            else:
                raise Exception("value= parameter must be unicode or str instance")
            del kwargs['value']
        else:
            raise Exception("Content expects value= parameter")
        super(Content,self).__init__(doc, *args, **kwargs)

    def __nonzero__(self):
        return bool(self.value)

    def __bool__(self):
        return bool(self.value)

    def __unicode__(self):
        return self.value

    def __str__(self):
        return self.value

    def xml(self, attribs = None,elements = None, skipchildren = False):
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})

        if not attribs:
            attribs = {}

        return E.content(self.value, **attribs)

    def json(self,attribs =None, recurse=True, ignorelist=False):
        jsonnode = {'type': self.XMLTAG, 'value': self.value}
        if attribs:
            for attrib in attribs:
                jsonnode[attrib] = attrib
        return jsonnode


    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.text(), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)

    @classmethod
    def parsexml(Class, node, doc):#pylint: disable=bad-classmethod-argument
        kwargs = {}
        kwargs['value'] = node.text
        return Content(doc, **kwargs)

class Part(AbstractStructureElement):
    pass


class Gap(AbstractElement):
    """Gap element. Represents skipped portions of the text. Contains Content and Desc elements"""

    def __init__(self, doc, *args, **kwargs):
        if 'content' in kwargs:
            self.value = kwargs['content']
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


class Linebreak(AbstractStructureElement, AbstractTextMarkup): #this element has a double role!!
    """Line break element, signals a line break"""

    def __init__(self, doc, *args, **kwargs):
        if 'linenr' in kwargs:
            self.linenr = kwargs['linenr']
            del kwargs['linenr']
        else:
            self.linenr = None
        if 'pagenr' in kwargs:
            self.pagenr = kwargs['pagenr']
            del kwargs['pagenr']
        else:
            self.pagenr = None
        if 'newpage' in kwargs and kwargs['newpage']:
            self.newpage = True
            del kwargs['newpage']
        else:
            self.newpage = False
        super(Linebreak, self).__init__(doc, *args, **kwargs)


    def text(self, cls='current', retaintokenisation=False, previousdelimiter="", strict=False, correctionhandling=None):
        return previousdelimiter.strip(' ') + "\n"

    @classmethod
    def parsexml(Class, node, doc):#pylint: disable=bad-classmethod-argument
        kwargs = {}
        if 'linenr' in node.attrib:
            kwargs['linenr'] = node.attrib['linenr']
        if 'pagenr' in node.attrib:
            kwargs['pagenr'] = node.attrib['pagenr']
        if 'newpage' in node.attrib and node.attrib['newpage'] == 'yes':
            kwargs['newpage'] = True
        return Linebreak(doc, **kwargs)

    def xml(self, attribs = None,elements = None, skipchildren = False):
        if attribs is None: attribs = {}
        if self.linenr is not None:
            attribs['{' + NSFOLIA + '}linenr'] = str(self.linenr)
        if self.pagenr is not None:
            attribs['{' + NSFOLIA + '}pagenr'] = str(self.pagenr)
        if self.newpage:
            attribs['{' + NSFOLIA + '}newpage'] = "yes"
        return super(Linebreak, self).xml(attribs,elements,skipchildren)

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        attribs = []
        attribs.append(E.optional(E.attribute(name='pagenr')))
        attribs.append(E.optional(E.attribute(name='linenr')))
        attribs.append(E.optional(E.attribute(name='newpage')))
        return super(Linebreak,cls).relaxng(includechildren,attribs,extraelements)

class Whitespace(AbstractStructureElement):
    """Whitespace element, signals a vertical whitespace"""

    def text(self, cls='current', retaintokenisation=False, previousdelimiter="", strict=False,correctionhandling=None):
        return previousdelimiter.strip(' ') + "\n\n"


class Word(AbstractStructureElement, AllowCorrections):
    """Word (aka token) element. Holds a word/token and all its related token annotations."""

    #will actually be determined by gettextdelimiter()

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
        return self.ancestor(Sentence)


    def paragraph(self):
        """Obtain the paragraph this word is a part of, otherwise return None"""
        return self.ancestor(Paragraph)

    def division(self):
        """Obtain the deepest division this word is a part of, otherwise return None"""
        return self.ancestor(Division)




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

    def morphemes(self,set=None):
        """Generator yielding all morphemes (in a particular set if specified). For retrieving one specific morpheme by index, use morpheme() instead"""
        for layer in self.select(MorphologyLayer):
            for m in layer.select(Morpheme, set):
                yield m

    def phonemes(self,set=None):
        """Generator yielding all phonemes (in a particular set if specified). For retrieving one specific morpheme by index, use morpheme() instead"""
        for layer in self.select(PhonologyLayer):
            for p in layer.select(Phoneme, set):
                yield p

    def morpheme(self,index, set=None):
        """Returns a specific morpheme, the n'th morpheme (given the particular set if specified)."""
        for layer in self.select(MorphologyLayer):
            for i, m in enumerate(layer.select(Morpheme, set)):
                if index == i:
                    return m
        raise NoSuchAnnotation


    def phoneme(self,index, set=None):
        """Returns a specific phoneme, the n'th morpheme (given the particular set if specified)."""
        for layer in self.select(PhonologyLayer):
            for i, p in enumerate(layer.select(Phoneme, set)):
                if index == i:
                    return p
        raise NoSuchAnnotation

    def gettextdelimiter(self, retaintokenisation=False):
        """Returns the text delimiter"""
        if self.space or retaintokenisation:
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
    def parsexml(Class, node, doc):#pylint: disable=bad-classmethod-argument
        assert Class is Word
        instance = super(Word,Class).parsexml(node, doc)
        if 'space' in node.attrib and instance:
            if node.attrib['space'] == 'no':
                instance.space = False
        return instance


    def xml(self, attribs = None,elements = None, skipchildren = False):
        if not attribs: attribs = {}
        if not self.space:
            attribs['space'] = 'no'
        return super(Word,self).xml(attribs,elements, False)

    def json(self,attribs =None, recurse=True, ignorelist=False):
        if not attribs: attribs = {}
        if not self.space:
            attribs['space'] = 'no'
        return super(Word,self).json(attribs, recurse)

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        if not extraattribs:
            extraattribs = [ E.optional(E.attribute(name='space')) ]
        else:
            extraattribs.append( E.optional(E.attribute(name='space')) )
        return AbstractStructureElement.relaxng(includechildren, extraattribs, extraelements, cls)



    def split(self, *newwords, **kwargs):
        self.sentence().splitword(self, *newwords, **kwargs)




    def findspans(self, type,set=None):
        """Find span annotation of the specified type that includes this word"""
        if issubclass(type, AbstractAnnotationLayer):
            layerclass = type
        else:
            layerclass = ANNOTATIONTYPE2LAYERCLASS[type.ANNOTATIONTYPE]
        e = self
        while True:
            if not e.parent: break
            e = e.parent
            for layer in e.select(layerclass,set,False):
                for e2 in layer:
                    if (type is layerclass and isinstance(e2, AbstractSpanAnnotation)) or (type is not layerclass and isinstance(e2, type)):
                        if self in e2.wrefs():
                            yield e2


class Feature(AbstractElement):
    """Feature elements can be used to associate subsets and subclasses with almost any
    annotation element"""


    def __init__(self,doc, *args, **kwargs): #pylint: disable=super-init-not-called
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
        self.auth = True


        if self.SUBSET:
            self.subset = self.SUBSET
        elif 'subset' in kwargs:
            self.subset = kwargs['subset']
        else:
            raise Exception("No subset specified for " + + self.__class__.__name__)
        if 'cls' in kwargs:
            self.cls = kwargs['cls']
        elif 'class' in kwargs:
            self.cls = kwargs['class']
        else:
            raise Exception("No class specified for " + self.__class__.__name__)

        if isinstance(self.cls, datetime):
            self.cls = self.cls.strftime("%Y-%m-%dT%H:%M:%S")

    def xml(self):
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
        attribs = {}
        if self.subset != self.SUBSET:
            attribs['{' + NSFOLIA + '}subset'] = self.subset
        attribs['{' + NSFOLIA + '}class'] =  self.cls
        return makeelement(E,'{' + NSFOLIA + '}' + self.XMLTAG, **attribs)

    def json(self,attribs=None, recurse=True, ignorelist=False):
        jsonnode= {'type': self.XMLTAG}
        jsonnode['subset'] = self.subset
        jsonnode['class'] = self.cls
        return jsonnode

    @classmethod
    def relaxng(cls, includechildren=True, extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.attribute(name='subset'), E.attribute(name='class'),name=cls.XMLTAG), name=cls.XMLTAG,ns=NSFOLIA)


class ValueFeature(Feature):
    """Value feature, to be used within Metric"""
    pass

class Metric(AbstractElement):
    """Metric elements allow the annotatation of any kind of metric with any kind of annotation element. Allowing for example statistical measures to be added to elements as annotation,"""
    pass

class AbstractSubtokenAnnotation(AbstractElement, AllowGenerateID):
    """Abstract element, all subtoken annotation elements are derived from this class"""
    pass

class AbstractSpanAnnotation(AbstractElement, AllowGenerateID, AllowCorrections):
    """Abstract element, all span annotation elements are derived from this class"""

    def xml(self, attribs = None,elements = None, skipchildren = False):
        if not attribs: attribs = {}
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        e = super(AbstractSpanAnnotation,self).xml(attribs, elements, True)
        for child in self:
            if isinstance(child, Word) or isinstance(child, Morpheme) or isinstance(child, Phoneme):
                #Include REFERENCES to word items instead of word items themselves
                attribs['{' + NSFOLIA + '}id'] = child.id
                if child.PRINTABLE and child.hastext():
                    attribs['{' + NSFOLIA + '}t'] = child.text()
                e.append( E.wref(**attribs) )
            elif not (isinstance(child, Feature) and child.SUBSET): #Don't add pre-defined features, they are already added as attributes
                e.append( child.xml() )
        return e



    def append(self, child, *args, **kwargs):
        if (isinstance(child, Word) or isinstance(child, Morpheme) or isinstance(child, Phoneme))  and WordReference in self.ACCEPTED_DATA:
            #Accept Word instances instead of WordReference, references will be automagically used upon serialisation
            self.data.append(child)
            return child
        else:
            return super(AbstractSpanAnnotation,self).append(child, *args, **kwargs)

    def setspan(self, *args):
        """Sets the span of the span element anew, erases all data inside"""
        self.data = []
        for child in args:
            self.append(child)

    def add(self, child, *args, **kwargs): #alias for append
        return self.append(child, *args, **kwargs)

    def hasannotation(self,Class,set=None):
        """Returns an integer indicating whether such as annotation exists, and if so, how many. See ``annotations()`` for a description of the parameters."""
        return self.count(Class,set,True,default_ignore_annotations)

    def annotation(self, type, set=None):
        """Will return a **single** annotation (even if there are multiple). Raises a ``NoSuchAnnotation`` exception if none was found"""
        l = self.count(type,set,True,default_ignore_annotations)
        if len(l) >= 1:
            return l[0]
        else:
            raise NoSuchAnnotation()

    def _helper_wrefs(self, targets):
        """Internal helper function"""
        for c in self:
            if isinstance(c,Word) or isinstance(c,Morpheme) or isinstance(c, Phoneme):
                targets.append(c)
            elif isinstance(c,WordReference):
                try:
                    targets.append(self.doc[c.id]) #try to resolve
                except KeyError:
                    targets.append(c) #add unresolved
            elif isinstance(c, AbstractSpanAnnotation):
                #recursion
                c._helper_wrefs(targets) #pylint: disable=protected-access
            elif isinstance(c, Correction) and c.auth: #recurse into corrections
                for e in c:
                    if isinstance(e, AbstractCorrectionChild) and e.auth:
                        for e2 in e:
                            if isinstance(e2, AbstractSpanAnnotation):
                                #recursion
                                e2._helper_wrefs(targets) #pylint: disable=protected-access

    def wrefs(self, index = None):
        """Returns a list of word references, these can be Words but also Morphemes or Phonemes.

        Arguments:
            * ``index``: If set to an integer, will retrieve and return the n'th element (starting at 0) instead of returning the list of all
        """
        targets =[]
        self._helper_wrefs(targets)
        if index is None:
            return targets
        else:
            return targets[index]

    def addtoindex(self,norecurse=None):
        """Makes sure this element (and all subelements), are properly added to the index"""
        if not norecurse: norecurse = (Word, Morpheme, Phoneme)
        if self.id:
            self.doc.index[self.id] = self
        for e in self.data:
            if all([not isinstance(e, C) for C in norecurse]):
                try:
                    e.addtoindex(norecurse)
                except AttributeError:
                    pass


    def copychildren(self, newdoc=None, idsuffix=""):
        """Generator creating a deep copy of the children of this element. If idsuffix is a string, if set to True, a random idsuffix will be generated including a random 32-bit hash"""
        if idsuffix is True: idsuffix = ".copy." + "%08x" % random.getrandbits(32) #random 32-bit hash for each copy, same one will be reused for all children
        for c in self:
            if isinstance(c, Word):
                yield WordReference(newdoc, id=c.id)
            else:
                yield c.copy(newdoc,idsuffix)


class AbstractAnnotationLayer(AbstractElement, AllowGenerateID, AllowCorrections):
    """Annotation layers for Span Annotation are derived from this abstract base class"""

    def __init__(self, doc, *args, **kwargs):
        if 'set' in kwargs:
            self.set = kwargs['set']
        elif self.ANNOTATIONTYPE in doc.annotationdefaults and len(doc.annotationdefaults[self.ANNOTATIONTYPE]) == 1:
            self.set = list(doc.annotationdefaults[self.ANNOTATIONTYPE].keys())[0]
        else:
            self.set = False
            # ok, let's not raise an error yet, may may still be able to derive a set from elements that are appended
        super(AbstractAnnotationLayer,self).__init__(doc, *args, **kwargs)


    def xml(self, attribs = None,elements = None, skipchildren = False):
        if self.set is False or self.set is None:
            if len(self.data) == 0: #just skip if there are no children
                return None
            else:
                raise ValueError("No set specified or derivable for annotation layer " + self.__class__.__name__)
        return super(AbstractAnnotationLayer, self).xml(attribs, elements, skipchildren)

    def append(self, child, *args, **kwargs):
        #if no set is associated with the layer yet, we learn it from span annotation elements that are added
        if self.set is False or self.set is None:
            if inspect.isclass(child):
                if issubclass(child,AbstractSpanAnnotation):
                    if 'set' in kwargs:
                        self.set = kwargs['set']
            elif isinstance(child, AbstractSpanAnnotation):
                if child.set:
                    self.set = child.set
            elif isinstance(child, Correction):
                #descend into corrections to find the proper set for this layer (derived from span annotation elements)
                for e in itertools.chain( child.new(), child.original(), child.suggestions() ):
                    if isinstance(e, AbstractSpanAnnotation) and e.set:
                        self.set = e.set
                        break

        return super(AbstractAnnotationLayer, self).append(child, *args, **kwargs)

    def add(self, child, *args, **kwargs): #alias for append
        return self.append(child, *args, **kwargs)

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
        found = False
        for e in self.select(Class,set,True,default_ignore_annotations):
            found = True
            yield e
        if not found:
            raise NoSuchAnnotation()

    def hasannotation(self,Class,set=None):
        """Returns an integer indicating whether such as annotation exists, and if so, how many. See ``annotations()`` for a description of the parameters."""
        return self.count(Class,set,True,default_ignore_annotations)

    def annotation(self, type, set=None):
        """Will return a **single** annotation (even if there are multiple). Raises a ``NoSuchAnnotation`` exception if none was found"""
        for e in self.select(type,set,True,default_ignore_annotations):
            return e
        raise NoSuchAnnotation()

    def alternatives(self, Class=None, set=None):
        """Generator over alternatives, either all or only of a specific annotation type, and possibly restrained also by set.

        Arguments:
            * ``Class`` - The Class you want to retrieve (e.g. PosAnnotation). Or set to None to select all alternatives regardless of what type they are.
            * ``set``   - The set you want to retrieve (defaults to None, which selects irregardless of set)

        Returns:
            Generator over Alternative elements
        """

        for e in self.select(AlternativeLayers,None, True, ['Original','Suggestion']): #pylint: disable=too-many-nested-blocks
            if Class is None:
                yield e
            elif len(e) >= 1: #child elements?
                for e2 in e:
                    try:
                        if isinstance(e2, Class):
                            try:
                                if set is None or e2.set == set:
                                    yield e #not e2
                                    break #yield an alternative only once (in case there are multiple matches)
                            except AttributeError:
                                continue
                    except AttributeError:
                        continue

    def findspan(self, *words):
        """Returns the span element which spans over the specified words or morphemes"""

        for span in self.select(AbstractSpanAnnotation,None,True):
            if tuple(span.wrefs()) == words:
                return span
        raise NoSuchAnnotation

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None, origclass = None):
        """Returns a RelaxNG definition for this element (as an XML element (lxml.etree) rather than a string)"""
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })
        if not extraattribs:
            extraattribs = []
        extraattribs.append(E.optional(E.attribute(E.text(), name='set')) )
        return AbstractElement.relaxng(includechildren, extraattribs, extraelements, cls)

# class AbstractSubtokenAnnotationLayer(AbstractElement, AllowGenerateID):
    # """Annotation layers for Subtoken Annotation are derived from this abstract base class"""
    # OPTIONAL_ATTRIBS = ()
    # PRINTABLE = False

    # def __init__(self, doc, *args, **kwargs):
        # if 'set' in kwargs:
            # self.set = kwargs['set']
            # del kwargs['set']
        # super(AbstractSubtokenAnnotationLayer,self).__init__(doc, *args, **kwargs)



class String(AbstractElement, AllowTokenAnnotation):
    """String"""
    pass

class AbstractCorrectionChild(AbstractElement):
    def generate_id(self, cls):
        #Delegate ID generation to parent
        return self.parent.generate_id(cls)

class Reference(AbstractStructureElement):

    def __init__(self, doc, *args, **kwargs):
        if 'idref' in kwargs:
            self.idref = kwargs['idref']
            del kwargs['idref']
        else:
            self.idref = None
        if 'type' in kwargs:
            self.type = kwargs['type']
            del kwargs['type']
        else:
            self.type = None
        if 'format' in kwargs:
            self.format = kwargs['format']
            del kwargs['format']
        else:
            self.format = "text/folia+xml"
        super(Reference,self).__init__(doc, *args, **kwargs)

    def xml(self, attribs = None,elements = None, skipchildren = False):
        if not attribs: attribs = {}
        if self.idref:
            attribs['id'] = self.idref
        if self.type:
            attribs['type'] = self.type
        if self.format and self.format != "text/folia+xml":
            attribs['format'] = self.format
        return super(Reference,self).xml(attribs,elements, skipchildren)

    def json(self, attribs=None, recurse=True, ignorelist=False):
        if attribs is None: attribs = {}
        if self.idref:
            attribs['idref'] = self.idref
        if self.type:
            attribs['type'] = self.type
        if self.format:
            attribs['format'] = self.format
        return super(Reference,self).json(attribs,recurse,ignorelist)

    def resolve(self):
        if self.idref:
            return self.doc[self.idref]
        else:
            return self

    @classmethod
    def parsexml(Class, node, doc):#pylint: disable=bad-classmethod-argument
        if 'id' in node.attrib:
            idref = node.attrib['id']
            del node.attrib['id']
        else:
            idref = None
        if 'type' in node.attrib:
            t = node.attrib['type']
            del node.attrib['type']
        else:
            idref = None
        if 'format' in node.attrib:
            f = node.attrib['format']
            del node.attrib['format']
        else:
            f = None
        instance = super(Reference,Class).parsexml(node, doc)
        if instance:
            if idref:
                instance.idref = idref
            if t:
                instance.type =  t
            if f:
                instance.format = f
        return instance


    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })
        if not extraattribs: extraattribs = []
        extraattribs.append( E.attribute(name='id')) #id reference
        extraattribs.append( E.optional(E.attribute(name='type' )))
        extraattribs.append( E.optional(E.attribute(name='format' )))
        return super(Reference, cls).relaxng(includechildren, extraattribs, extraelements)

class AlignReference(AbstractElement):

    def __init__(self, doc, *args, **kwargs): #pylint: disable=super-init-not-called
        #Special constructor, not calling super constructor
        if 'id' not in kwargs:
            raise Exception("ID required for AlignReference")
        if 'type' in kwargs:
            if isinstance(kwargs['type'], AbstractElement) or inspect.isclass(kwargs['type']):
                self.type = kwargs['type'].XMLTAG
            else:
                self.type = kwargs['type']
        else:
            self.type = None
        if 't' in kwargs:
            self.t = kwargs['t']
        else:
            self.t = None
        assert(isinstance(doc,Document))
        self.doc = doc
        self.id = kwargs['id']
        self.annotator = None
        self.annotatortype = None
        self.confidence = None
        self.n = None
        self.datetime = None
        self.auth = False
        self.set = None
        self.cls = None
        self.data = []



    @classmethod
    def parsexml(Class, node, doc):#pylint: disable=bad-classmethod-argument
        assert Class is AlignReference or issubclass(Class, AlignReference)

        #special handling for word references
        kwargs = {'id':node.attrib['id']}
        if not 'type' in node.attrib:
            raise ValueError("No type in alignment reference")
        if 't' in node.attrib:
            kwargs['t'] = node.attrib['t']
        try:
            kwargs['type'] = node.attrib['type']
        except KeyError:
            raise ValueError("No such type: " + node.attrib['type'])
        return AlignReference(doc,**kwargs)

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.attribute(E.text(), name='id'), E.optional(E.attribute(E.text(), name='t')), E.optional(E.attribute(E.text(), name='type')), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)

    def resolve(self, alignmentcontext=None, documents={}):
        if not alignmentcontext or not hasattr(alignmentcontext, 'href') or not alignmentcontext.href:
            #no target document, same document
            return self.doc[self.id]
        else:
            #other document
            if alignmentcontext.href in documents:
                return documents[alignmentcontext.href][self.id]
            else:
                raise DocumentNotLoaded()

    def xml(self, attribs = None,elements = None, skipchildren = False):
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})

        if not attribs:
            attribs = {}
        attribs['id'] = self.id
        if self.type:
            attribs['type'] = self.type
        if self.t: attribs['t'] = self.t

        return E.aref( **attribs)

    def json(self, attribs=None, recurse=True, ignorelist=False):
        return {} #alignment not supported yet, TODO


class Alignment(AbstractElement):

    def __init__(self, doc, *args, **kwargs):
        if 'format' in kwargs:
            self.format = kwargs['format']
            del kwargs['format']
        else:
            self.format = "text/folia+xml"
        super(Alignment,self).__init__(doc, *args, **kwargs)

    @classmethod
    def parsexml(Class, node, doc):#pylint: disable=bad-classmethod-argument
        if 'format' in node.attrib:
            format = node.attrib['format']
            del node.attrib['format']
        else:
            format = None
        instance = super(Alignment,Class).parsexml(node, doc)
        if instance:
            if format:
                instance.format = format
        return instance

    def xml(self, attribs = None,elements = None, skipchildren = False):
        if not attribs: attribs = {}
        if self.format and self.format != "text/folia+xml":
            attribs['format'] = self.format
        return super(Alignment,self).xml(attribs,elements, skipchildren)

    def json(self, attribs =None, recurse=True, ignorelist=False):
        return {} #alignment not supported yet, TODO

    def resolve(self, documents=None):
        if documents is None: documents = {}
        #documents is a dictionary of urls to document instances, to aid in resolving cross-document alignments
        for x in self.select(AlignReference,None,True,False):
            yield x.resolve(self, documents)

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        if extraattribs is None: extraattribs = []
        extraattribs.append(E.optional(E.attribute(name="format")))
        return super(Alignment,cls).relaxng(includechildren, extraattribs, extraelements)


class ErrorDetection(AbstractExtendedTokenAnnotation):
    pass



class Suggestion(AbstractCorrectionChild):

    def __init__(self,  doc, *args, **kwargs):
        if 'split' in kwargs:
            self.split = kwargs['split']
            del kwargs['split']
        else:
            self.split = None
        if 'merge' in kwargs:
            self.merge = kwargs['merge']
            del kwargs['merge']
        else:
            self.merge = None
        super(Suggestion,self).__init__(doc, *args, **kwargs)

    @classmethod
    def parsexml(Class, node, doc): #pylint: disable=bad-classmethod-argument
        e = super(Suggestion,Class).parsexml(node, doc)
        if 'split' in node.attrib:
            e.split = node.attrib['split']
        if 'merge' in node.attrib:
            e.merge = node.attrib['merge']
        return e

    def xml(self, attribs = None,elements = None, skipchildren = False):
        if not attribs: attribs= {}

        if self.split: attribs['split']  = self.split
        if self.merge: attribs['merge']  = self.merge

        return super(Suggestion, self).xml(attribs, elements, skipchildren)

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace",'a':"http://relaxng.org/ns/annotation/0.9" })
        if not extraattribs: extraattribs = []
        extraattribs.append( E.optional(E.attribute(name='split' )))
        extraattribs.append( E.optional(E.attribute(name='merge' )))
        return super(Suggestion, cls).relaxng(includechildren, extraattribs, extraelements)

    def json(self, attribs = None, recurse=True,ignorelist=False):
        if self.split:
            if not attribs: attribs = {}
            attribs['split'] = self.split
        if self.merge:
            if not attribs: attribs = {}
            attribs['merge'] = self.merge
        return super(Suggestion, self).json(attribs, recurse, ignorelist)

class New(AbstractCorrectionChild):

    @classmethod
    def addable(Class, parent, set=None, raiseexceptions=True):#pylint: disable=bad-classmethod-argument
        if not super(New,Class).addable(parent,set,raiseexceptions): return False
        if any( ( isinstance(c, Current) for c in parent ) ):
            if raiseexceptions:
                raise ValueError("Can't add New element to Correction if there is a Current item")
            else:
                return False
        return True

    def correct(self, **kwargs):
        return self.parent.correct(**kwargs)

class Original(AbstractCorrectionChild):

    @classmethod
    def addable(Class, parent, set=None, raiseexceptions=True):#pylint: disable=bad-classmethod-argument
        if not super(Original,Class).addable(parent,set,raiseexceptions): return False
        if any( ( isinstance(c, Current)  for c in parent ) ):
            if raiseexceptions:
                raise Exception("Can't add Original item to Correction if there is a Current item")
            else:
                return False
        return True


class Current(AbstractCorrectionChild):

    @classmethod
    def addable(Class, parent, set=None, raiseexceptions=True):
        if not super(Current,Class).addable(parent,set,raiseexceptions): return False
        if any( ( isinstance(c, New) or isinstance(c, Original) for c in parent ) ):
            if raiseexceptions:
                raise Exception("Can't add Current element to Correction if there is a New or Original element")
            else:
                return False
        return True

    def correct(self, **kwargs):
        return self.parent.correct(**kwargs)

class Correction(AbstractElement, AllowGenerateID):

    def append(self, child, *args, **kwargs):
        """See ``AbstractElement.append()``"""
        e = super(Correction,self).append(child, *args, **kwargs)
        self._setmaxid(e)
        return e

    def hasnew(self,allowempty=False):
        for e in  self.select(New,None,False, False):
            if not allowempty and len(e) == 0: continue
            return True
        return False

    def hasoriginal(self,allowempty=False):
        for e in self.select(Original,None,False, False):
            if not allowempty and len(e) == 0: continue
            return True
        return False

    def hascurrent(self, allowempty=False):
        for e in self.select(Current,None,False, False):
            if not allowempty and len(e) == 0: continue
            return True
        return False

    def hassuggestions(self,allowempty=False):
        for e in self.select(Suggestion,None,False, False):
            if not allowempty and len(e) == 0: continue
            return True
        return False

    def textcontent(self, cls='current', correctionhandling=CorrectionHandling.CURRENT):
        """Get the text explicitly associated with this element (of the specified class).
        Returns the TextContent instance rather than the actual text. Raises NoSuchText exception if
        not found.

        Unlike text(), this method does not recurse into child elements (with the sole exception of the Correction/New element), and it returns the TextContent instance rather than the actual text!
        """
        if cls == 'original': correctionhandling = CorrectionHandling.ORIGINAL #backward compatibility
        if correctionhandling in (CorrectionHandling.CURRENT, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, New) or isinstance(e, Current):
                    return e.textcontent(cls,correctionhandling)
        if correctionhandling in (CorrectionHandling.ORIGINAL, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, Original):
                    return e.textcontent(cls,correctionhandling)
        raise NoSuchText


    def phoncontent(self, cls='current', correctionhandling=CorrectionHandling.CURRENT):
        """Get the phonetic content explicitly associated with this element (of the specified class).
        Returns the PhonContent instance rather than the actual text. Raises NoSuchPhon exception if
        not found.

        Unlike phon(), this method does not recurse into child elements (with the sole exception of the Correction/New element), and it returns the PhonContent instance rather than the actual text!
        """
        if cls == 'original': correctionhandling = CorrectionHandling.ORIGINAL #backward compatibility
        if correctionhandling in (CorrectionHandling.CURRENT, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, New) or isinstance(e, Current):
                    return e.phoncontent(cls, correctionhandling)
        if correctionhandling in (CorrectionHandling.ORIGINAL, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, Original):
                    return e.phoncontent(cls, correctionhandling)
        raise NoSuchPhon


    def hastext(self, cls='current',strict=True, correctionhandling=CorrectionHandling.CURRENT):
        if cls == 'original': correctionhandling = CorrectionHandling.ORIGINAL #backward compatibility
        if correctionhandling in (CorrectionHandling.CURRENT, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, New) or isinstance(e, Current):
                    return e.hastext(cls,strict, correctionhandling)
        if correctionhandling in (CorrectionHandling.ORIGINAL, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, Original):
                    return e.hastext(cls,strict, correctionhandling)
        return False

    def text(self, cls = 'current', retaintokenisation=False, previousdelimiter="",strict=False, correctionhandling=CorrectionHandling.CURRENT):
        if cls == 'original': correctionhandling = CorrectionHandling.ORIGINAL #backward compatibility
        if correctionhandling in (CorrectionHandling.CURRENT, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, New) or isinstance(e, Current):
                    return previousdelimiter + e.text(cls, retaintokenisation,"", strict, correctionhandling)
        if correctionhandling in (CorrectionHandling.ORIGINAL, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, Original):
                    return previousdelimiter + e.text(cls, retaintokenisation,"", strict, correctionhandling)
        raise NoSuchText

    def hasphon(self, cls='current',strict=True, correctionhandling=CorrectionHandling.CURRENT):
        if cls == 'original': correctionhandling = CorrectionHandling.ORIGINAL #backward compatibility
        if correctionhandling in (CorrectionHandling.CURRENT, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, New) or isinstance(e, Current):
                    return e.hasphon(cls,strict, correctionhandling)
        if correctionhandling in (CorrectionHandling.ORIGINAL, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, Original):
                    return e.hasphon(cls,strict, correctionhandling)
        return False

    def phon(self, cls = 'current', previousdelimiter="",strict=False, correctionhandling=CorrectionHandling.CURRENT):
        if cls == 'original': correctionhandling = CorrectionHandling.ORIGINAL #backward compatibility
        if correctionhandling in (CorrectionHandling.CURRENT, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, New) or isinstance(e, Current):
                    return previousdelimiter + e.phon(cls, "", strict, correctionhandling)
        if correctionhandling in (CorrectionHandling.ORIGINAL, CorrectionHandling.EITHER):
            for e in self:
                if isinstance(e, Original):
                    return previousdelimiter + e.phon(cls, "", correctionhandling)
        raise NoSuchPhon

    def gettextdelimiter(self, retaintokenisation=False):
        """May return a customised text delimiter instead of the default for this class."""
        for e in self:
            if isinstance(e, New) or isinstance(e, Current):
                return e.gettextdelimiter(retaintokenisation)
        return ""


    def new(self,index = None):
        if index is None:
            try:
                return next(self.select(New,None,False))
            except StopIteration:
                raise NoSuchAnnotation
        else:
            for e in self.select(New,None,False):
                return e[index]
            raise NoSuchAnnotation

    def original(self,index=None):
        if index is None:
            try:
                return next(self.select(Original,None,False, False))
            except StopIteration:
                raise NoSuchAnnotation
        else:
            for e in self.select(Original,None,False, False):
                return e[index]
            raise NoSuchAnnotation

    def current(self,index=None):
        if index is None:
            try:
                return next(self.select(Current,None,False))
            except StopIteration:
                raise NoSuchAnnotation
        else:
            for e in self.select(Current,None,False):
                return e[index]
            raise NoSuchAnnotation

    def suggestions(self,index=None):
        if index is None:
            return self.select(Suggestion,None,False, False)
        else:
            for i, e in enumerate(self.select(Suggestion,None,False, False)):
                if index == i:
                    return e
            raise IndexError


    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.text(self, 'current', False, "",False, CorrectionHandling.EITHER)

    def correct(self, **kwargs):
        if 'new' in kwargs:
            if 'nooriginal' not in kwargs: #if not an insertion
                kwargs['original'] = self
        elif 'current' in kwargs:
            kwargs['current'] = self

        if 'insertindex' in kwargs:
            #recompute insertindex
            index = self.parent.getindex(self)
            if index != -1:
                kwargs['insertindex'] = index
                if 'insertindex_offset' in kwargs:
                    kwargs['insertindex'] += kwargs['insertindex_offset']
                    del kwargs['insetindex_offset']
            else:
                raise Exception("Can't find insertion point for higher-order correction")
        return self.parent.correct(**kwargs)

    #obsolete
    #def select(self, cls, set=None, recursive=True,  ignorelist=[], node=None):
    #    """Select on Correction only descends in either "NEW" or "CURRENT" branch"""
    #    if ignorelist is False:
    #        #to override and go into all branches, set ignorelist explictly to False
    #        return super(Correction,self).select(cls,set,recursive, ignorelist, node)
    #    else:
    #        if ignorelist is True:
    #            ignorelist = copy(default_ignore)
    #        else:
    #            ignorelist = copy(ignorelist) #we don't want to alter a passed ignorelist (by ref)
    #        ignorelist.append(Original)
    #        ignorelist.append(Suggestion)
    #        return super(Correction,self).select(cls,set,recursive, ignorelist, node)





class Alternative(AbstractElement, AllowTokenAnnotation, AllowGenerateID):
    """Element grouping alternative token annotation(s). Multiple alternative elements may occur, each denoting a different alternative. Elements grouped inside an alternative block are considered dependent."""
    pass



class AlternativeLayers(AbstractElement):
    """Element grouping alternative subtoken annotation(s). Multiple altlayers elements may occur, each denoting a different alternative. Elements grouped inside an alternative block are considered dependent."""
    pass



class External(AbstractElement):

    def __init__(self, doc, *args, **kwargs): #pylint: disable=super-init-not-called
        #Special constructor, not calling super constructor
        if 'source' not in kwargs:
            raise Exception("Source required for External")
        assert(isinstance(doc,Document))
        self.doc = doc
        self.id = None
        self.source = kwargs['source']
        if 'include' in kwargs and kwargs['include'] != 'no':
            self.include = bool(kwargs['include'])
        else:
            self.include = False
        self.annotator = None
        self.annotatortype = None
        self.confidence = None
        self.n = None
        self.datetime = None
        self.auth = False
        self.data = []
        self.subdoc = None

        if self.include:
            if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] Loading subdocument for inclusion: " + self.source,file=stderr)
            #load subdocument

            #check if it is already loaded, if multiple references are made to the same doc we reuse the instance
            if self.source in self.doc.subdocs:
                self.subdoc = self.doc.subdocs[self.source]
            elif self.source[:7] == 'http://' or self.source[:8] == 'https://':
                #document is remote, download (in memory)
                try:
                    f = urlopen(self.source)
                except:
                    raise DeepValidationError("Unable to download subdocument for inclusion: " + self.source)
                try:
                    content = u(f.read())
                except IOError:
                    raise DeepValidationError("Unable to download subdocument for inclusion: " + self.source)
                f.close()
                self.subdoc = Document(string=content, parentdoc = self.doc, setdefinitions=self.doc.setdefinitions)
            elif os.path.exists(self.source):
                #document is on disk:
                self.subdoc = Document(file=self.source, parentdoc = self.doc, setdefinitions=self.doc.setdefinitions)
            else:
                #document not found
                raise DeepValidationError("Unable to find subdocument for inclusion: " + self.source)

            self.subdoc.parentdoc = self.doc
            self.doc.subdocs[self.source] = self.subdoc
            #TODO: verify there are no clashes in declarations between parent and child
            #TODO: check validity of elements under subdoc/text with respect to self.parent


    @classmethod
    def parsexml(Class, node, doc):
        assert Class is External or issubclass(Class, External)
        #special handling for external
        source = node.attrib['src']
        if 'include' in node.attrib:
            include = node.attrib['include']
        else:
            include = False
        if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] Found external",file=stderr)
        return External(doc, source=source, include=include)

    def xml(self, attribs = None,elements = None, skipchildren = False):
        if not attribs:
            attribs= {}

        attribs['src'] = self.source

        if self.include:
            attribs['include']  = 'yes'
        else:
            attribs['include']  = 'no'

        return super(External, self).xml(attribs, elements, skipchildren)

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.attribute(E.text(), name='src'), E.optional(E.attribute(E.text(), name='include')), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)


    def select(self, Class, set=None, recursive=True,  ignore=True, node=None):
        if self.include:
            return self.subdoc.data[0].select(Class,set,recursive, ignore, node) #pass it on to the text node of the subdoc
        else:
            return iter([])


class WordReference(AbstractElement):
    """Word reference. Used to refer to words or morphemes from span annotation elements. The Python class will only be used when word reference can not be resolved, if they can, Word or Morpheme objects will be used"""
    #REQUIRED_ATTRIBS = (Attrib.ID,)  #TODO: See if this is handled correctly in new scheme

    def __init__(self, doc, *args, **kwargs): #pylint: disable=super-init-not-called
        #Special constructor, not calling super constructor
        if 'idref' not in kwargs and 'id' not in kwargs:
            raise Exception("ID required for WordReference")
        assert isinstance(doc,Document)
        self.doc = doc
        if 'idref' in kwargs:
            self.id = kwargs['idref']
        else:
            self.id = kwargs['id']
        self.annotator = None
        self.annotatortype = None
        self.confidence = None
        self.n = None
        self.datetime = None
        self.data = []
        self.set = None
        self.cls = None
        self.auth = True

    @classmethod
    def parsexml(Class, node, doc):#pylint: disable=bad-classmethod-argument
        assert Class is WordReference or issubclass(Class, WordReference)
        #special handling for word references
        id = node.attrib['id']
        if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] Found word reference",file=stderr)
        try:
            return doc[id]
        except KeyError:
            if doc.debug >= 1: print("[PyNLPl FoLiA DEBUG] ...Unresolvable!",file=stderr)
            return WordReference(doc, id=id)

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.attribute(E.text(), name='id'), E.optional(E.attribute(E.text(), name='t')), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)


    def xml(self, attribs = None,elements = None, skipchildren = False):
        """Serialises the FoLiA element to XML, by returning an XML Element (in lxml.etree) for this element and all its children. For string output, consider the xmlstring() method instead."""
        E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})

        if not attribs: attribs = {}
        if not elements: elements = []

        if self.id:
            attribs['id'] = self.id
            try:
                w = self.doc[self.id]
                attribs['t'] = w.text()
            except KeyError:
                pass

        e  = makeelement(E, '{' + NSFOLIA + '}' + self.XMLTAG, **attribs)
        return e

class SyntacticUnit(AbstractSpanAnnotation):
    """Syntactic Unit, span annotation element to be used in SyntaxLayer"""
    pass


class Chunk(AbstractSpanAnnotation):
    """Chunk element, span annotation element to be used in ChunkingLayer"""
    pass

class Entity(AbstractSpanAnnotation):
    """Entity element, for named entities, span annotation element to be used in EntitiesLayer"""
    pass

class AbstractSpanRole(AbstractSpanAnnotation):
    pass

class Headspan(AbstractSpanRole): #generic head element
    pass

DependencyHead = Headspan #alias, backwards compatibility with FoLiA 0.8


class DependencyDependent(AbstractSpanRole):
    pass

class Dependency(AbstractSpanAnnotation):
    def head(self):
        """Returns the head of the dependency relation. Instance of DependencyHead"""
        return next(self.select(DependencyHead))

    def dependent(self):
        """Returns the dependent of the dependency relation. Instance of DependencyDependent"""
        return next(self.select(DependencyDependent))


class ModalityFeature(Feature):
    """Modality feature, to be used with coreferences"""

class TimeFeature(Feature):
    """Time feature, to be used with coreferences"""

class LevelFeature(Feature):
    """Level feature, to be used with coreferences"""

class CoreferenceLink(AbstractSpanRole):
    """Coreference link. Used in coreferencechain."""

class CoreferenceChain(AbstractSpanAnnotation):
    """Coreference chain. Consists of coreference links."""

class SemanticRole(AbstractSpanAnnotation):
    """Semantic Role"""

class ComplexAlignment(AbstractElement):
    """Complex Alignment"""

    #same as for AbstractSpanAnnotation, which this technically is not (hence copy)
    def hasannotation(self,Class,set=None):
        """Returns an integer indicating whether such as annotation exists, and if so, how many. See ``annotations()`` for a description of the parameters."""
        return self.count(Class,set,True,default_ignore_annotations)

    #same as for AbstractSpanAnnotation, which this technically is not (hence copy)
    def annotation(self, type, set=None):
        """Will return a **single** annotation (even if there are multiple). Raises a ``NoSuchAnnotation`` exception if none was found"""
        l = self.count(type,set,True,default_ignore_annotations)
        if len(l) >= 1:
            return l[0]
        else:
            raise NoSuchAnnotation()

class FunctionFeature(Feature):
    """Function feature, to be used with morphemes"""

class Morpheme(AbstractStructureElement):
    """Morpheme element, represents one morpheme in morphological analysis, subtoken annotation element to be used in MorphologyLayer"""

    def findspans(self, type,set=None):
        """Find span annotation of the specified type that include this word"""
        if issubclass(type, AbstractAnnotationLayer):
            layerclass = type
        else:
            layerclass = ANNOTATIONTYPE2LAYERCLASS[type.ANNOTATIONTYPE]
        e = self
        while True:
            if not e.parent: break
            e = e.parent
            for layer in e.select(layerclass,set,False):
                for e2 in layer:
                    if isinstance(e2, AbstractSpanAnnotation):
                        if self in e2.wrefs():
                            yield e2


class Phoneme(AbstractStructureElement):
    """Morpheme element, represents one morpheme in morphological analysis, subtoken annotation element to be used in MorphologyLayer"""

    def findspans(self, type,set=None): #TODO: this is a copy of the methods in Morpheme in Word, abstract into separate class and inherit
        """Find span annotation of the specified type that include this phoneme"""
        if issubclass(type, AbstractAnnotationLayer):
            layerclass = type
        else:
            layerclass = ANNOTATIONTYPE2LAYERCLASS[type.ANNOTATIONTYPE]
        e = self
        while True:
            if not e.parent: break
            e = e.parent
            for layer in e.select(layerclass,set,False):
                for e2 in layer:
                    if isinstance(e2, AbstractSpanAnnotation):
                        if self in e2.wrefs():
                            yield e2

#class Subentity(AbstractSubtokenAnnotation):
#    """Subentity element, for named entities within a single token, subtoken annotation element to be used in SubentitiesLayer"""
#    ACCEPTED_DATA = (Feature,TextContent, Metric)
#    ANNOTATIONTYPE = AnnotationType.SUBENTITY
#    XMLTAG = 'subentity'




class SyntaxLayer(AbstractAnnotationLayer):
    """Syntax Layer: Annotation layer for SyntacticUnit span annotation elements"""

class ChunkingLayer(AbstractAnnotationLayer):
    """Chunking Layer: Annotation layer for Chunk span annotation elements"""

class EntitiesLayer(AbstractAnnotationLayer):
    """Entities Layer: Annotation layer for Entity span annotation elements. For named entities."""

class DependenciesLayer(AbstractAnnotationLayer):
    """Dependencies Layer: Annotation layer for Dependency span annotation elements. For dependency entities."""

class MorphologyLayer(AbstractAnnotationLayer):
    """Morphology Layer: Annotation layer for Morpheme subtoken annotation elements. For morphological analysis."""

class PhonologyLayer(AbstractAnnotationLayer):
    """Phonology Layer: Annotation layer for phonemes subtoken annotation elements. For phonetic analysis."""

class CoreferenceLayer(AbstractAnnotationLayer):
    """Syntax Layer: Annotation layer for SyntacticUnit span annotation elements"""

class SemanticRolesLayer(AbstractAnnotationLayer):
    """Syntax Layer: Annotation layer for SemanticRole span annotation elements"""

class ComplexAlignmentLayer(AbstractAnnotationLayer):
    """Complex alignment layer"""
    ACCEPTED_DATA = (ComplexAlignment,Description,Correction)
    XMLTAG = 'complexalignments'
    ANNOTATIONTYPE = AnnotationType.COMPLEXALIGNMENT

class HeadFeature(Feature):
    """Head feature, to be used within PosAnnotation"""

class PosAnnotation(AbstractTokenAnnotation):
    """Part-of-Speech annotation:  a token annotation element"""

class LemmaAnnotation(AbstractTokenAnnotation):
    """Lemma annotation:  a token annotation element"""

class LangAnnotation(AbstractExtendedTokenAnnotation):
    """Language annotation:  an extended token annotation element"""

#class PhonAnnotation(AbstractTokenAnnotation): #DEPRECATED in v0.9
#    """Phonetic annotation:  a token annotation element"""
#    ANNOTATIONTYPE = AnnotationType.PHON
#    ACCEPTED_DATA = (Feature,Description, Metric)
#    XMLTAG = 'phon'


class DomainAnnotation(AbstractExtendedTokenAnnotation):
    """Domain annotation:  an extended token annotation element"""

class SynsetFeature(Feature):
    """Synset feature, to be used within Sense"""

class ActorFeature(Feature):
    """Actor feature, to be used within Event"""

class BegindatetimeFeature(Feature):
    """Begindatetime feature, to be used within Event"""

class EnddatetimeFeature(Feature):
    """Enddatetime feature, to be used within Event"""

class StyleFeature(Feature):
    pass

class Note(AbstractStructureElement):
    pass

class Definition(AbstractStructureElement):
    pass

class Term(AbstractStructureElement):
    pass

class Example(AbstractStructureElement):
    pass

class Entry(AbstractStructureElement):
    pass


class TimeSegment(AbstractSpanAnnotation):
    pass

TimedEvent = TimeSegment #alias for FoLiA 0.8 compatibility

class TimingLayer(AbstractAnnotationLayer):
    """Dependencies Layer: Annotation layer for Dependency span annotation elements. For dependency entities."""


class SenseAnnotation(AbstractTokenAnnotation):
    """Sense annotation: a token annotation element"""

class SubjectivityAnnotation(AbstractTokenAnnotation):
    """Subjectivity annotation/Sentiment analysis: a token annotation element"""


class Quote(AbstractStructureElement):
    """Quote: a structure element. For quotes/citations. May hold words, sentences or paragraphs."""

    def __init__(self,  doc, *args, **kwargs):
        super(Quote,self).__init__(doc, *args, **kwargs)


    def resolveword(self, id):
        for child in self:
            r =  child.resolveword(id)
            if r:
                return r
        return None

    def append(self, child, *args, **kwargs):
        #Quotes have some more complex ACCEPTED_DATA behaviour depending on what lever they are used on

        #Note that Sentences under quotes may occur if the parent of the quote is a sentence already
        insentence = len(list(self.ancestors(Sentence))) > 0
        inparagraph = len(list(self.ancestors(Paragraph))) > 0
        if inspect.isclass(child):
            if (insentence or inparagraph) and (child is Paragraph or child is Division):
                raise Exception("Can't add paragraphs or divisions to a quote when the quote is in a sentence or paragraph!")
        else:
            if (insentence or inparagraph) and (isinstance(child, Paragraph) or isinstance(child, Division)):
                raise Exception("Can't add paragraphs or divisions to a quote when the quote is in a sentence or paragraph!")

        return super(Quote, self).append(child, *args, **kwargs)

    def gettextdelimiter(self, retaintokenisation=False):
        #no text delimiter of itself, recurse into children to inherit delimiter
        for child in reversed(self):
            if isinstance(child, Sentence):
                return "" #if a quote ends in a sentence, we don't want any delimiter
            else:
                return child.gettextdelimiter(retaintokenisation)
        return self.TEXTDELIMITER


class Sentence(AbstractStructureElement):
    """Sentence element. A structure element. Represents a sentence and holds all its words (and possibly other structure such as LineBreaks, Whitespace and Quotes)"""

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
        return self.ancestor(Paragraph)

    def division(self):
        """Obtain the division this sentence is a part of (None otherwise)"""
        return self.ancestor(Division)


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
        if isstring(originalword):
            originalword = self.doc[u(originalword)]
        return self.correctwords([originalword], newwords, **kwargs)



    def mergewords(self, newword, *originalwords, **kwargs):
        """TODO: Write documentation"""
        return self.correctwords(originalwords, [newword], **kwargs)

    def deleteword(self, word, **kwargs):
        """TODO: Write documentation"""
        if isstring(word):
            word = self.doc[u(word)]
        return self.correctwords([word], [], **kwargs)


    def insertword(self, newword, prevword, **kwargs):
        if prevword:
            if isstring(prevword):
                prevword = self.doc[u(prevword)]
            if not prevword in self or not isinstance(prevword, Word):
                raise Exception("Previous word not found or not instance of Word!")
            if isinstance(newword, list) or isinstance(newword, tuple):
                if not all([ isinstance(x, Word) for x in newword ]):
                    raise Exception("New word (iterable) constains non-Word instances!")
            elif not isinstance(newword, Word):
                raise Exception("New word no instance of Word!")

            kwargs['insertindex'] = self.getindex(prevword) + 1
        else:
            kwargs['insertindex'] = 0
        kwargs['nooriginal'] = True
        if isinstance(newword, list) or isinstance(newword, tuple):
            return self.correctwords([], newword, **kwargs)
        else:
            return self.correctwords([], [newword], **kwargs)


    def insertwordleft(self, newword, nextword, **kwargs):
        if nextword:
            if isstring(nextword):
                nextword = self.doc[u(nextword)]
            if not nextword in self or not isinstance(nextword, Word):
                raise Exception("Next word not found or not instance of Word!")
            if isinstance(newword, list) or isinstance(newword, tuple):
                if not all([ isinstance(x, Word) for x in newword ]):
                    raise Exception("New word (iterable) constains non-Word instances!")
            elif not isinstance(newword, Word):
                raise Exception("New word no instance of Word!")

            kwargs['insertindex'] = self.getindex(nextword)
        else:
            kwargs['insertindex'] = 0
        kwargs['nooriginal'] = True
        if isinstance(newword, list) or isinstance(newword, tuple):
            return self.correctwords([], newword, **kwargs)
        else:
            return self.correctwords([], [newword], **kwargs)


    def gettextdelimiter(self, retaintokenisation=False):
        #no text delimiter of itself, recurse into children to inherit delimiter
        for child in reversed(self):
            if isinstance(child, Linebreak) or isinstance(child, Whitespace):
                return "" #if a sentence ends in a linebreak, we don't want any delimiter
            else:
                break
        return self.TEXTDELIMITER

class Utterance(AbstractStructureElement):
    """Utterance element. A structure element for speech annotation."""

class Event(AbstractStructureElement):
    pass

class Caption(AbstractStructureElement):
    """Element used for captions for figures or tables, contains sentences"""


class Label(AbstractStructureElement):
    """Element used for labels. Mostly in within list item. Contains words."""


class ListItem(AbstractStructureElement):
    """Single element in a List. Structure element. Contained within List element."""

class List(AbstractStructureElement):
    """Element for enumeration/itemisation. Structure element. Contains ListItem elements."""


class Figure(AbstractStructureElement):
    """Element for the representation of a graphical figure. Structure element."""

    def json(self, attribs = None, recurse=True,ignorelist=False):
        if self.src:
            if not attribs: attribs = {}
            attribs['src'] = self.src
        return super(Figure, self).json(attribs, recurse, ignorelist)

    def caption(self):
        try:
            caption = next(self.select(Caption))
            return caption.text()
        except:
            raise NoSuchText





class Head(AbstractStructureElement):
    """Head element. A structure element. Acts as the header/title of a division. There may be one per division. Contains sentences."""

class Paragraph(AbstractStructureElement):
    """Paragraph element. A structure element. Represents a paragraph and holds all its sentences (and possibly other structure Whitespace and Quotes)."""


class Cell(AbstractStructureElement):
    pass

class Row(AbstractStructureElement):
    pass


class TableHead(AbstractStructureElement):
    pass


class Table(AbstractStructureElement):
    pass


class Division(AbstractStructureElement):
    """Structure element representing some kind of division. Divisions may be nested at will, and may include almost all kinds of other structure elements."""

    def head(self):
        for e in self.data:
            if isinstance(e, Head):
                return e
        raise NoSuchAnnotation()


class Speech(AbstractStructureElement):
    """A full speech. This is a high-level element. This element may contain divisions, paragraphs, sentences, etc.."""
    # (both SPEAKABLE and PRINTABLE)

class Text(AbstractStructureElement):
    """A full text. This is a high-level element (not to be confused with TextContent!). This element may contain divisions, paragraphs, sentences, etc.."""
    # (both SPEAKABLE and PRINTABLE)


class ForeignData(AbstractElement):
    def __init__(self, doc, *args, **kwargs): #pylint: disable=super-init-not-called
        self.data = []
        if 'node' not in kwargs:
            raise ValueError("Expected a node= keyword argument for foreign-data")
        if not isinstance(kwargs['node'],ElementTree._Element):
            raise ValueError("foreign-data node should be ElementTree.Element instance, got " + str(type(kwargs['node'])))
        self.node = kwargs['node']
        for subnode in self.node:
            self._checknamespace(subnode)
        self.doc = doc
        self.id = None
        #do not call superconstructor

    def _checknamespace(self, node):
        #namespace must be foreign
        for subnode in node:
            if node.tag and node.tag.startswith('{'+NSFOLIA+'}'):
                raise ValueError("foreign-data may not include elements in the FoLiA namespace, a foreign XML namespace is mandatory")
            self._checknamespace(subnode)

    @classmethod
    def parsexml(Class, node, doc):
        return ForeignData(doc, node=node)

    def select(self, Class, set=None, recursive=True,  ignore=True, node=None): #pylint: disable=bad-classmethod-argument,redefined-builtin
        #select can never descend into ForeignData, empty generator:
        return
        yield

    def xml(self, attribs = None,elements = None, skipchildren = False):
        return self.node

    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
        E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        return E.define( E.element(E.ref(name="any_content"), name=cls.XMLTAG), name=cls.XMLTAG, ns=NSFOLIA)




#===================================================================================================================


class Query(object):
    """An XPath query on one or more FoLiA documents"""
    def __init__(self, files, expression):
        if isstring(files):
            self.files = [u(files)]
        else:
            assert hasattr(files,'__iter__')
            self.files = files
        self.expression = expression

    def __iter__(self):
        for filename in self.files:
            doc = Document(file=filename, mode=Mode.XPATH)
            for result in doc.xpath(self.expression):
                yield result

class RegExp(object):
    def __init__(self, regexp):
        self.regexp = re.compile(regexp)

    def __eq__(self, value):
        return self.regexp.match(value)


class Pattern(object):
    """
    This class describes a pattern over words to be searched for. The
``Document.findwords()`` method can subsequently be called with this pattern,
and it will return all the words that match. An example will best illustrate
this, first a trivial example of searching for one word::

        for match in doc.findwords( folia.Pattern('house') ):
            for word in match:
                print word.id
            print "----"

    The same can be done for a sequence::

        for match in doc.findwords( folia.Pattern('a','big', 'house') ):
            for word in match:
                print word.id
            print "----"

    The boolean value ``True`` acts as a wildcard, matching any word::

        for match in doc.findwords( folia.Pattern('a',True,'house') ):
            for word in match:
                print word.id, word.text()
            print "----"

    Alternatively, and more constraning, you may also specify a tuple of alternatives::


        for match in doc.findwords( folia.Pattern('a',('big','small'),'house') ):
            for word in match:
                print word.id, word.text()
            print "----"

    Or even a regular expression using the ``folia.RegExp`` class::


        for match in doc.findwords( folia.Pattern('a', folia.RegExp('b?g'),'house') ):
            for word in match:
                print word.id, word.text()
            print "----"


    Rather than searching on the text content of the words, you can search on the
    classes of any kind of token annotation using the keyword argument
    ``matchannotation=``::

        for match in doc.findwords( folia.Pattern('det','adj','noun',matchannotation=folia.PosAnnotation ) ):
            for word in match:
                print word.id, word.text()
            print "----"

    The set can be restricted by adding the additional keyword argument
    ``matchannotationset=``. Case sensitivity, by default disabled, can be enabled by setting ``casesensitive=True``.

    Things become even more interesting when different Patterns are combined. A
    match will have to satisfy all patterns::

        for match in doc.findwords( folia.Pattern('a', True, 'house'), folia.Pattern('det','adj','noun',matchannotation=folia.PosAnnotation ) ):
            for word in match:
                print word.id, word.text()
            print "----"


    The ``findwords()`` method can be instructed to also return left and/or right context for any match. This is done using the ``leftcontext=`` and ``rightcontext=`` keyword arguments, their values being an integer number of the number of context words to include in each match. For instance, we can look for the word house and return its immediate neighbours as follows::

        for match in doc.findwords( folia.Pattern('house') , leftcontext=1, rightcontext=1):
            for word in match:
                print word.id
            print "----"

    A match here would thus always consist of three words instead of just one.

    Last, ``Pattern`` also has support for variable-width gaps, the asterisk symbol
    has special meaning to this end::


        for match in doc.findwords( folia.Pattern('a','*','house') ):
            for word in match:
                print word.id
            print "----"

    Unlike the pattern ``('a',True,'house')``, which by definition is a pattern of
    three words, the pattern in the example above will match gaps of any length (up
    to a certain built-in maximum), so this might include matches such as *a very
    nice house*.

    Some remarks on these methods of querying are in order. These searches are
    pretty exhaustive and are done by simply iterating over all the words in the
    document. The entire document is loaded in memory and no special indices are involved.
    For single documents this is okay, but when iterating over a corpus of
    thousands of documents, this method is too slow, especially for real-time
    applications. For huge corpora, clever indexing and database management systems
    will be required. This however is beyond the scope of this library.

    """


    def __init__(self, *args, **kwargs):
        if not all( ( (x is True or isinstance(x,RegExp) or isstring(x) or isinstance(x, list) or isinstance(x, tuple)) for x in args )):
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
            if all( ( isstring(x) for x in self.sequence) ):
                self.sequence = [ u(x).lower() for x in self.sequence ]

    def __nonzero__(self): #Python 2.x
        return True

    def __bool__(self):
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
        for x in self.sequence:
            if x == '*':
                nrofwildcards += 1

        assert (len(distribution) == nrofwildcards)

        wildcardnr = 0
        newsequence = []
        for x in self.sequence:
            if x == '*':
                newsequence += [True] * distribution[wildcardnr]
                wildcardnr += 1
            else:
                newsequence.append(x)
        d = { 'matchannotation':self.matchannotation, 'matchannotationset':self.matchannotationset, 'casesensitive':self.casesensitive }
        yield Pattern(*newsequence, **d )



class NativeMetaData(object):
    def __init__(self, *args, **kwargs):
        self.data = {}
        self.order = []
        for key, value in kwargs.items():
            self[key] = value

    def __setitem__(self, key, value):
        exists = key in self.data
        self.data[key] = value
        if not exists: self.order.append(key)

    def __iter__(self):
        for x in self.order:
            yield x

    def __contains__(self, x):
        return x in self.data

    def items(self):
        for key in self.order:
            yield key, self.data[key]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self,key):
        del self.data[key]
        self.order.remove(key)


class Document(object):
    """This is the FoLiA Document, all elements have to be associated with a FoLiA document. Besides holding elements, the document hold metadata including declaration, and an index of all IDs."""

    IDSEPARATOR = '.'

    def __init__(self, *args, **kwargs):
        """Start/load a FoLiA document:

        There are four sources of input for loading a FoLiA document::

        1) Create a new document by specifying an *ID*::

            doc = folia.Document(id='test')

        2) Load a document from FoLiA or D-Coi XML file::

            doc = folia.Document(file='/path/to/doc.xml')

        3) Load a document from an XML string::

            doc = folia.Document(string='<FoLiA>....</FoLiA>')

        4) Load a document by passing a parse xml tree (lxml.etree):

            doc = folia.Document(tree=xmltree)

        Additionally, there are three modes that can be set with the ``mode=`` keyword argument:

             * folia.Mode.MEMORY - The entire FoLiA Document will be loaded into memory. This is the default mode and the only mode in which documents can be manipulated and saved again.
             * folia.Mode.XPATH - The full XML tree will still be loaded into memory, but conversion to FoLiA classes occurs only when queried. This mode can be used when the full power of XPath is required.


        Optional keyword arguments:

            ``setdefinition=``:  A dictionary of set definitions, the key corresponds to the set name, the value is a SetDefinition instance
            ``loadsetdefinitions=``:  Boolean, download and load set definitions (default: False)
            ``deepvalidation=``:  Boolean, do deep validation of the document (default: False), implies ``loadsetdefinitions``
            ``preparsexmlcallback=``:  Callback for a function taking one argument (``node``, an lxml node). Will be called whenever an XML element is parsed into FoLiA. The function should return an instance inherited from folia.AbstractElement, or None to abort parsing this element (and all its children)
            ``parsexmlcallback=``:  Callback for a function taking one argument (``element``, a FoLiA element). Will be called whenever an XML element is parsed into FoLiA. The function should return an instance inherited from folia.AbstractElement, or None to abort adding this element (and all its children)
            ``debug=``:  Boolean to enable/disable debug
        """


        self.version = FOLIAVERSION

        self.data = [] #will hold all texts (usually only one)

        self.annotationdefaults = {}
        self.annotations = [] #Ordered list of incorporated annotations ['token','pos', etc..]

        #Add implicit declaration for TextContent
        self.annotations.append( (AnnotationType.TEXT,'undefined') )
        self.annotationdefaults[AnnotationType.TEXT] = {'undefined': {} }
        #Add implicit declaration for PhonContent
        self.annotations.append( (AnnotationType.PHON,'undefined') )
        self.annotationdefaults[AnnotationType.PHON] = {'undefined': {} }

        self.index = {} #all IDs go here
        self.declareprocessed = False # Will be set to True when declarations have been processed

        self.metadata = NativeMetaData() #will point to XML Element holding native metadata
        self.metadatatype = MetaDataType.NATIVE
        self.metadatafile = None #reference to external metadata file



        self.textclasses = set() #will contain the text classes found

        self.autodeclare = False #Automatic declarations in case of undeclared elements (will be enabled for DCOI, since DCOI has no declarations)

        if 'setdefinitions' in kwargs:
            self.setdefinitions = kwargs['setdefinitions'] #to re-use a shared store
        else:
            self.setdefinitions = {} #key: set name, value: SetDefinition instance (only used when deepvalidation=True)

        #The metadata fields FoLiA is directly aware of:
        self._title = self._date = self._publisher = self._license = self._language = None


        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            self.debug = False

        if 'mode' in kwargs:
            self.mode = int(kwargs['mode'])
        else:
            self.mode = Mode.MEMORY #Load all in memory


        if 'parentdoc' in kwargs:  #for subdocuments
            assert isinstance(kwargs['parentdoc'], Document)
            self.parentdoc = kwargs['parentdoc']
        else:
            self.parentdoc = None

        self.subdocs = {} #will hold all subdocs (sourcestring => document) , needed so the index can resolve IDs in subdocs
        self.standoffdocs = {} #will hold all standoffdocs (type => set => sourcestring => document)

        if 'external' in kwargs:
            self.external = kwargs['external']
        else:
            self.external = False

        if self.external and not self.parentdoc:
            raise DeepValidationError("Document is marked as external and should not be loaded independently. However, no parentdoc= has been specified!")


        if 'loadsetdefinitions' in kwargs:
            self.loadsetdefinitions = bool(kwargs['loadsetdefinitions'])
        else:
            self.loadsetdefinitions = False

        if 'deepvalidation' in kwargs:
            self.deepvalidation = bool(kwargs['deepvalidation'])
            self.loadsetdefinitions = True
        else:
            self.deepvalidation = False

        if 'allowadhocsets' in kwargs:
            self.allowadhocsets = bool(kwargs['allowadhocsets'])
        else:
            if self.deepvalidation:
                self.allowadhocsets = False
            else:
                self.allowadhocsets = True

        if 'autodeclare' in kwargs:
            self.autodeclare = True

        if 'bypassleak' in kwargs:
            self.bypassleak = False #obsolete now

        if 'preparsexmlcallback' in kwargs:
            self.preparsexmlcallback = kwargs['parsexmlcallback']
        else:
            self.preparsexmlcallback = None

        if 'parsexmlcallback' in kwargs:
            self.parsexmlcallback = kwargs['parsexmlcallback']
        else:
            self.parsexmlcallback = None

        if 'id' in kwargs:
            isncname(kwargs['id'])
            self.id = kwargs['id']
        elif 'file' in kwargs:
            self.filename = kwargs['file']
            if self.filename[-4:].lower() == '.bz2':
                f = bz2.BZ2File(self.filename)
                contents = f.read()
                f.close()
                self.tree = xmltreefromstring(contents)
                del contents
                self.parsexml(self.tree.getroot())
            elif self.filename[-3:].lower() == '.gz':
                f = gzip.GzipFile(self.filename) #pylint: disable=redefined-variable-type
                contents = f.read()
                f.close()
                self.tree = xmltreefromstring(contents)
                del contents
                self.parsexml(self.tree.getroot())
            else:
                self.load(self.filename)
        elif 'string' in kwargs:
            self.tree = xmltreefromstring(kwargs['string'])
            del kwargs['string']
            self.parsexml(self.tree.getroot())
            if self.mode != Mode.XPATH:
                #XML Tree is now obsolete (only needed when partially loaded for xpath queries)
                self.tree = None
        elif 'tree' in kwargs:
            self.parsexml(kwargs['tree'])
        else:
            raise Exception("No ID, filename or tree specified")

        if self.mode != Mode.XPATH:
            #XML Tree is now obsolete (only needed when partially loaded for xpath queries), free memory
            self.tree = None

    #def __del__(self):
    #    del self.index
    #    for child in self.data:
    #        del child
    #    del self.data

    def load(self, filename):
        """Load a FoLiA or D-Coi XML file"""
        #if LXE and self.mode != Mode.XPATH:
        #    #workaround for xml:id problem (disabled)
        #    #f = open(filename)
        #    #s = f.read().replace(' xml:id=', ' id=')
        #    #f.close()
        #    self.tree = ElementTree.parse(filename)
        #else:
        self.tree = xmltreefromfile(filename)
        self.parsexml(self.tree.getroot())
        if self.mode != Mode.XPATH:
            #XML Tree is now obsolete (only needed when partially loaded for xpath queries)
            self.tree = None

    def items(self):
        """Returns a depth-first flat list of all items in the document"""
        l = []
        for e in self.data:
            l += e.items()
        return l

    def xpath(self, query):
        """Run Xpath expression and parse the resulting elements. Don't forget to use the FoLiA namesapace in your expressions, using folia: or the short form f: """
        for result in self.tree.xpath(query,namespaces={'f': 'http://ilk.uvt.nl/folia','folia': 'http://ilk.uvt.nl/folia' }):
            yield self.parsexml(result)


    def findwords(self, *args, **kwargs):
        for x in findwords(self,self.words,*args,**kwargs):
            yield x

    def save(self, filename=None):
        """Save the document to FoLiA XML.

        Arguments:
            * ``filename=``: The filename to save to. If not set (None), saves to the same file as loaded from.
        """
        if not filename:
            filename = self.filename
        if not filename:
            raise Exception("No filename specified")
        if filename[-4:].lower() == '.bz2':
            f = bz2.BZ2File(filename,'wb')
            f.write(self.xmlstring().encode('utf-8'))
            f.close()
        elif filename[-3:].lower() == '.gz':
            f = gzip.GzipFile(filename,'wb') #pylint: disable=redefined-variable-type
            f.write(self.xmlstring().encode('utf-8'))
            f.close()
        else:
            f = io.open(filename,'w',encoding='utf-8')
            f.write(self.xmlstring())
            f.close()



    def __len__(self):
        return len(self.data)

    def __nonzero__(self): #Python 2.x
        return True

    def __bool__(self):
        return True

    def __iter__(self):
        for text in self.data:
            yield text


    def __contains__(self, key):
        """Tests if the specified ID is in the document index"""
        if key in self.index:
            return True
        elif self.subdocs:
            for subdoc in self.subdocs.values():
                if key in subdoc:
                    return True
            return False
        else:
            return False

    def __getitem__(self, key):
        """Obtain an element by ID from the document index.

        Example::

            word = doc['example.p.4.s.10.w.3']
        """
        if isinstance(key, int):
            return self.data[key]
        else:
            try:
                return self.index[key]
            except KeyError:
                if self.subdocs: #perhaps the key is in one of our subdocs?
                    for subdoc in self.subdocs.values():
                        try:
                            return subdoc[key]
                        except KeyError:
                            pass
                else:
                    raise KeyError("No such key: " + key)


    def append(self,text):
        """Add a text (or speech) to the document:

        Example 1::

            doc.append(folia.Text)

        Example 2::
            doc.append( folia.Text(doc, id='example.text') )

        Example 3::

            doc.append(folia.Speech)

        """
        if text is Text:
            text = Text(self, id=self.id + '.text.' + str(len(self.data)+1) )
        elif text is Speech:
            text = Speech(self, id=self.id + '.speech.' + str(len(self.data)+1) ) #pylint: disable=redefined-variable-type
        else:
            assert isinstance(text, Text) or isinstance(text, Speech)
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

            if (annotationtype == AnnotationType.TEXT or annotationtype == AnnotationType.PHON) and set == 'undefined' and len(self.annotationdefaults[annotationtype][set]) == 0:
                #this is the implicit TextContent declaration, no need to output it explicitly
                continue

            attribs = {}
            if set and set != 'undefined':
                attribs['{' + NSFOLIA + '}set'] = set


            for key, value in self.annotationdefaults[annotationtype][set].items():
                if key == 'annotatortype':
                    if value == AnnotatorType.MANUAL:
                        attribs['{' + NSFOLIA + '}' + key] = 'manual'
                    elif value == AnnotatorType.AUTO:
                        attribs['{' + NSFOLIA + '}' + key] = 'auto'
                elif key == 'datetime':
                    attribs['{' + NSFOLIA + '}' + key] = value.strftime("%Y-%m-%dT%H:%M:%S") #proper iso-formatting
                elif value:
                    attribs['{' + NSFOLIA + '}' + key] = value
            if label:
                l.append( makeelement(E,'{' + NSFOLIA + '}' + label.lower() + '-annotation', **attribs) )
            else:
                raise Exception("Invalid annotation type")
        return l

    def jsondeclarations(self):
        l = []
        for annotationtype, set in self.annotations:
            label = None
            #Find the 'label' for the declarations dynamically (aka: AnnotationType --> String)
            for key, value in vars(AnnotationType).items():
                if value == annotationtype:
                    label = key
                    break
            #gather attribs

            if (annotationtype == AnnotationType.TEXT or annotationtype == AnnotationType.PHON) and set == 'undefined' and len(self.annotationdefaults[annotationtype][set]) == 0:
                #this is the implicit TextContent declaration, no need to output it explicitly
                continue

            jsonnode = {'annotationtype': label.lower()}
            if set and set != 'undefined':
                jsonnode['set'] = set


            for key, value in self.annotationdefaults[annotationtype][set].items():
                if key == 'annotatortype':
                    if value == AnnotatorType.MANUAL:
                        jsonnode[key] = 'manual'
                    elif value == AnnotatorType.AUTO:
                        jsonnode[key] = 'auto'
                elif key == 'datetime':
                    jsonnode[key] = value.strftime("%Y-%m-%dT%H:%M:%S") #proper iso-formatting
                elif value:
                    jsonnode[key] = value
            if label:
                l.append( jsonnode  )
            else:
                raise Exception("Invalid annotation type")
        return l

    def xml(self):
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={'xml' : "http://www.w3.org/XML/1998/namespace", 'xlink':"http://www.w3.org/1999/xlink"})
        attribs = {}
        attribs['{http://www.w3.org/XML/1998/namespace}id'] = self.id

        if self.version:
            attribs['version'] = self.version
        else:
            attribs['version'] = FOLIAVERSION

        attribs['generator'] = 'pynlpl.formats.folia-v' + LIBVERSION

        metadataattribs = {}
        metadataattribs['{' + NSFOLIA + '}type'] = self.metadatatype
        if self.metadatafile: metadataattribs['{' + NSFOLIA + '}src'] = self.metadatafile

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

    def json(self):
        jsondoc = {'id': self.id, 'children': [], 'declarations': self.jsondeclarations() }
        if self.version:
            jsondoc['version'] = self.version
        else:
            jsondoc['version'] = FOLIAVERSION
        jsondoc['generator'] = 'pynlpl.formats.folia-v' + LIBVERSION

        for text in self.data:
            jsondoc['children'].append(text.json())
        return jsondoc

    def xmlmetadata(self):
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        if self.metadatatype == MetaDataType.NATIVE:
            e = []
            if not self.metadatafile:
                for key, value in self.metadata.items():
                    e.append(E.meta(value,id=key) )
            return e
        else:
            if self.metadatafile:
                return [] #external
            elif self.metadata is not None:
                return [self.metadata.xml()] #in-document
            else:
                return []




    def parsexmldeclarations(self, node):
        if self.debug >= 1:
            print("[PyNLPl FoLiA DEBUG] Processing Annotation Declarations",file=stderr)
        self.declareprocessed = True
        for subnode in node: #pylint: disable=too-many-nested-blocks
            if not isinstance(subnode.tag, str): continue
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
                    set = 'undefined'

                if (type,set) in self.annotations:
                    if type == AnnotationType.TEXT:
                        #explicit Text declaration, remove the implicit declaration:
                        a = []
                        for t,s in self.annotations:
                            if not (t == AnnotationType.TEXT and s == 'undefined'):
                                a.append( (t,s) )
                        self.annotations = a
                    #raise ValueError("Double declaration of " + subnode.tag + ", set '" + set + "' + is already declared")    //doubles are okay says Ko
                else:
                    self.annotations.append( (type, set) )

                #Load set definition
                if set and self.loadsetdefinitions and set not in self.setdefinitions:
                    if set[:7] == "http://" or set[:8] == "https://" or set[:6] == "ftp://":
                        try:
                            self.setdefinitions[set] = loadsetdefinition(set) #will raise exception on error
                        except DeepValidationError:
                            print("WARNING: Set " + set + " could not be downloaded, ignoring!",file=sys.stderr) #warning and ignore

                #Set defaults
                if type in self.annotationdefaults and set in self.annotationdefaults[type]:
                    #handle duplicate. If ambiguous: remove defaults
                    if 'annotator' in subnode.attrib:
                        if not ('annotator' in self.annotationdefaults[type][set]):
                            self.annotationdefaults[type][set]['annotator'] = subnode.attrib['annotator']
                        elif self.annotationdefaults[type][set]['annotator'] != subnode.attrib['annotator']:
                            del self.annotationdefaults[type][set]['annotator']
                    if 'annotatortype' in subnode.attrib:
                        if not ('annotatortype' in self.annotationdefaults[type][set]):
                            self.annotationdefaults[type][set]['annotatortype'] = subnode.attrib['annotatortype']
                        elif self.annotationdefaults[type][set]['annotatortype'] != subnode.attrib['annotatortype']:
                            del self.annotationdefaults[type][set]['annotatortype']
                else:
                    defaults = {}
                    if 'annotator' in subnode.attrib:
                        defaults['annotator'] = subnode.attrib['annotator']
                    if 'annotatortype' in subnode.attrib:
                        if subnode.attrib['annotatortype'] == 'auto':
                            defaults['annotatortype'] = AnnotatorType.AUTO
                        else:
                            defaults['annotatortype'] = AnnotatorType.MANUAL
                    if 'datetime' in subnode.attrib:
                        if isinstance(subnode.attrib['datetime'], datetime):
                            defaults['datetime'] = subnode.attrib['datetime']
                        else:
                            defaults['datetime'] = parse_datetime(subnode.attrib['datetime'])

                    if not type in self.annotationdefaults:
                        self.annotationdefaults[type] = {}
                    self.annotationdefaults[type][set] = defaults


                if 'external' in subnode.attrib and subnode.attrib['external']:
                    if self.debug >= 1:
                        print("[PyNLPl FoLiA DEBUG] Loading external document: " + subnode.attrib['external'],file=stderr)
                    if not type in self.standoffdocs:
                        self.standoffdocs[type] = {}
                    self.standoffdocs[type][set] = {}

                    #check if it is already loaded, if multiple references are made to the same doc we reuse the instance
                    standoffdoc = None
                    for t in self.standoffdocs:
                        for s in self.standoffdocs[t]:
                            for source in self.standoffdocs[t][s]:
                                if source == subnode.attrib['external']:
                                    standoffdoc = self.standoffdocs[t][s]
                                    break
                            if standoffdoc: break
                        if standoffdoc: break

                    if not standoffdoc:
                        if subnode.attrib['external'][:7] == 'http://' or subnode.attrib['external'][:8] == 'https://':
                            #document is remote, download (in memory)
                            try:
                                f = urlopen(subnode.attrib['external'])
                            except:
                                raise DeepValidationError("Unable to download standoff document: " + subnode.attrib['external'])
                            try:
                                content = u(f.read())
                            except IOError:
                                raise DeepValidationError("Unable to download standoff document: " + subnode.attrib['external'])
                            f.close()
                            standoffdoc = Document(string=content, parentdoc=self, setdefinitions=self.setdefinitions)
                        elif os.path.exists(subnode.attrib['external']):
                            #document is on disk:
                            standoffdoc = Document(file=subnode.attrib['external'], parentdoc=self, setdefinitions=self.setdefinitions)
                        else:
                            #document not found
                            raise DeepValidationError("Unable to find standoff document: " + subnode.attrib['external'])

                    self.standoffdocs[type][set][subnode.attrib['external']] = standoffdoc
                    standoffdoc.parentdoc = self

                if self.debug >= 1:
                    print("[PyNLPl FoLiA DEBUG] Found declared annotation " + subnode.tag + ". Defaults: " + repr(defaults),file=stderr)




    def setimdi(self, node): #OBSOLETE
        ns = {'imdi': 'http://www.mpi.nl/IMDI/Schema/IMDI'}
        self.metadatatype = MetaDataType.IMDI
        if LXE:
            self.metadata = ElementTree.tostring(node, xml_declaration=False, pretty_print=True, encoding='utf-8')
        else:
            self.metadata = ElementTree.tostring(node, encoding='utf-8')
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
            if set and self.loadsetdefinitions and not set in self.setdefinitions:
                if set[:7] == "http://" or set[:8] == "https://" or set[:6] == "ftp://":
                    self.setdefinitions[set] = loadsetdefinition(set) #will raise exception on error
        if not annotationtype in self.annotationdefaults:
            self.annotationdefaults[annotationtype] = {}
        self.annotationdefaults[annotationtype][set] = kwargs

    def declared(self, annotationtype, set):
        if inspect.isclass(annotationtype): annotationtype = annotationtype.ANNOTATIONTYPE
        return ( (annotationtype,set) in self.annotations)


    def defaultset(self, annotationtype):
        if inspect.isclass(annotationtype) or isinstance(annotationtype,AbstractElement): annotationtype = annotationtype.ANNOTATIONTYPE
        try:
            return list(self.annotationdefaults[annotationtype].keys())[0]
        except KeyError:
            raise NoDefaultError
        except IndexError:
            raise NoDefaultError


    def defaultannotator(self, annotationtype, set=None):
        if inspect.isclass(annotationtype) or isinstance(annotationtype,AbstractElement): annotationtype = annotationtype.ANNOTATIONTYPE
        if not set: set = self.defaultset(annotationtype)
        try:
            return self.annotationdefaults[annotationtype][set]['annotator']
        except KeyError:
            raise NoDefaultError

    def defaultannotatortype(self, annotationtype,set=None):
        if inspect.isclass(annotationtype) or isinstance(annotationtype,AbstractElement): annotationtype = annotationtype.ANNOTATIONTYPE
        if not set: set = self.defaultset(annotationtype)
        try:
            return self.annotationdefaults[annotationtype][set]['annotatortype']
        except KeyError:
            raise NoDefaultError


    def defaultdatetime(self, annotationtype,set=None):
        if inspect.isclass(annotationtype) or isinstance(annotationtype,AbstractElement): annotationtype = annotationtype.ANNOTATIONTYPE
        if not set: set = self.defaultset(annotationtype)
        try:
            return self.annotationdefaults[annotationtype][set]['datetime']
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

    def parsemetadata(self, node):
        if 'type' in node.attrib:
            self.metadatatype = node.attrib['type']
        else:
            #no type specified, default to native
            self.metadatatype = "native"

        if 'src' in node.attrib:
            self.metadatafile =  node.attrib['src']
        else:
            self.metadatafile = None

        if self.metadatatype == "native":
            self.metadata = NativeMetaData()
        else:
            self.metadata = None #will be set below

        for subnode in node:
            if subnode.tag == '{' + NSFOLIA + '}annotations':
                self.parsexmldeclarations(subnode)
            elif subnode.tag == '{' + NSFOLIA + '}meta':
                if self.metadatatype == "native":
                    if subnode.text:
                        self.metadata[subnode.attrib['id']] = subnode.text
                else:
                    raise MetaDataError("Encountered a meta element but metadata type is not native!")
            elif subnode.tag == '{' + NSFOLIA + '}foreign-data':
                if self.metadatatype == "native":
                    raise MetaDataError("Encountered a foreign-data element but metadata type is native!")
                elif self.metadata is not None:
                    raise MetaDataError("Multiple foreign-data elements are not allowed")
                else:
                    self.metadata = ForeignData(self, node=subnode)
            elif subnode.tag == '{http://www.mpi.nl/IMDI/Schema/IMDI}METATRANSCRIPT': #backward-compatibility for old IMDI without foreign-key
                E = ElementMaker(namespace=NSFOLIA,nsmap={None: NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
                self.metadatatype = "imdi"
                self.metadata = makeelement(E, '{'+NSFOLIA+'}foreign-data')
                self.metadata.append(subnode)



    def parsexml(self, node, ParentClass = None):
        """Main XML parser, will invoke class-specific XML parsers. For internal use."""
        if (LXE and isinstance(node,ElementTree._ElementTree)) or (not LXE and isinstance(node, ElementTree.ElementTree)): #pylint: disable=protected-access
            node = node.getroot()
        elif isstring(node):
            node = xmltreefromstring(node).getroot()

        if node.tag.startswith('{' + NSFOLIA + '}'):
            foliatag = node.tag[nslen:]
            if foliatag == "FoLiA":
                if self.debug >= 1: print("[PyNLPl FoLiA DEBUG] Found FoLiA document",file=stderr)
                try:
                    self.id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
                except KeyError:
                    try:
                        self.id = node.attrib['XMLid']
                    except KeyError:
                        try:
                            self.id = node.attrib['id']
                        except KeyError:
                            raise Exception("FoLiA Document has no ID!")
                if 'version' in node.attrib:
                    self.version = node.attrib['version']
                else:
                    self.version = None

                if 'external' in node.attrib:
                    self.external = (node.attrib['external'] == 'yes')

                    if self.external and not self.parentdoc:
                        raise DeepValidationError("Document is marked as external and should not be loaded independently. However, no parentdoc= has been specified!")


                for subnode in node:
                    if subnode.tag == '{' + NSFOLIA + '}metadata':
                        self.parsemetadata(subnode)
                    elif (subnode.tag == '{' + NSFOLIA + '}text' or subnode.tag == '{' + NSFOLIA + '}speech') and self.mode == Mode.MEMORY:
                        if self.debug >= 1: print("[PyNLPl FoLiA DEBUG] Found Text",file=stderr)
                        e = self.parsexml(subnode)
                        if e is not None:
                            self.data.append(e)
            else:
                #generic handling (FoLiA)
                if not foliatag in XML2CLASS:
                    raise Exception("Unknown FoLiA XML tag: " + foliatag)
                Class = XML2CLASS[foliatag]
                return Class.parsexml(node,self)
        elif node.tag == '{' + NSDCOI + '}DCOI':
            if self.debug >= 1: print("[PyNLPl FoLiA DEBUG] Found DCOI document",file=stderr)
            self.autodeclare = True
            try:
                self.id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
            except KeyError:
                try:
                    self.id = node.attrib['id']
                except KeyError:
                    try:
                        self.id = node.attrib['XMLid']
                    except KeyError:
                        raise Exception("D-Coi Document has no ID!")
            for subnode in node:
                if subnode.tag == '{http://www.mpi.nl/IMDI/Schema/IMDI}METATRANSCRIPT':
                    self.metadatatype = MetaDataType.IMDI
                    self.setimdi(subnode)
                elif subnode.tag == '{' + NSDCOI + '}text':
                    if self.debug >= 1: print("[PyNLPl FoLiA DEBUG] Found Text",file=stderr)
                    e = self.parsexml(subnode)
                    if e is not None:
                        self.data.append( e )
        elif node.tag.startswith('{' + NSDCOI + '}'):
            #generic handling (D-Coi)
            if node.tag[nslendcoi:] in XML2CLASS:
                Class = XML2CLASS[node.tag[nslendcoi:]]
                return Class.parsexml(node,self)
            elif node.tag[nslendcoi:][0:3] == 'div': #support for div0, div1, etc:
                Class = Division
                return Class.parsexml(node,self)
            elif node.tag[nslendcoi:] == 'item': #support for listitem
                Class = ListItem
                return Class.parsexml(node,self)
            elif node.tag[nslendcoi:] == 'figDesc': #support for description in figures
                Class = Description
                return Class.parsexml(node,self)
            else:
                raise Exception("Unknown DCOI XML tag: " + node.tag)
        else:
            raise Exception("Unknown FoLiA XML tag: " + node.tag)


    def select(self, Class, set=None, recursive=True,  ignore=True):
        if self.mode == Mode.MEMORY:
            for t in self.data:
                if Class.__name__ == 'Text':
                    yield t
                else:
                    for e in t.select(Class,set,recursive,ignore):
                        yield e

    def count(self, Class, set=None, recursive=True,ignore=True):
        if self.mode == Mode.MEMORY:
            s = 0
            for t in self.data:
                s +=  sum( 1 for e in t.select(Class,recursive,True ) )
            return s

    def paragraphs(self, index = None):
        """Return a generator of all paragraphs found in the document.

        If an index is specified, return the n'th paragraph only (starting at 0)"""
        if index is None:
            return self.select(Paragraph)
        else:
            if index < 0:
                index = sum(t.count(Paragraph) for t in self.data) + index
            for t in self.data:
                for i,e in enumerate(t.select(Paragraph)) :
                    if i == index:
                        return e
            raise IndexError

    def sentences(self, index = None):
        """Return a generator of all sentence found in the document. Except for sentences in quotes.

        If an index is specified, return the n'th sentence only (starting at 0)"""
        if index is None:
            return self.select(Sentence,None,True,[Quote])
        else:
            if index < 0:
                index = sum(t.count(Sentence,None,True,[Quote]) for t in self.data) + index
            for t in self.data:
                for i,e in enumerate(t.select(Sentence,None,True,[Quote])) :
                    if i == index:
                        return e
            raise IndexError


    def words(self, index = None):
        """Return a generator of all active words found in the document. Does not descend into annotation layers, alternatives, originals, suggestions.

        If an index is specified, return the n'th word only (starting at 0)"""
        if index is None:
            return self.select(Word,None,True,default_ignore_structure)
        else:
            if index < 0:
                index = sum(t.count(Word,None,True,default_ignore_structure) for t in self.data)  + index
            for t in self.data:
                for i, e in enumerate(t.select(Word,None,True,default_ignore_structure)):
                    if i == index:
                        return e
            raise IndexError



    def text(self, cls='current', retaintokenisation=False):
        """Returns the text of the entire document (returns a unicode instance)
        """

        #backward compatibility, old versions didn't have cls as first argument, so if a boolean is passed first we interpret it as the 2nd:
        if cls is True or cls is False:
            retaintokenisation = cls
            cls = 'current'

        s = ""
        for c in self.data:
            if s: s += "\n\n\n"
            try:
                s += c.text(cls, retaintokenisation)
            except NoSuchText:
                continue
        return s

    def xmlstring(self):
        s = ElementTree.tostring(self.xml(), xml_declaration=True, pretty_print=True, encoding='utf-8')
        if sys.version < '3':
            if isinstance(s, str):
                s = unicode(s,'utf-8') #pylint: disable=undefined-variable
        else:
            if isinstance(s,bytes):
                s = str(s,'utf-8')

        s = s.replace('ns0:','') #ugly patch to get rid of namespace prefix
        s = s.replace(':ns0','')
        return s


    def __unicode__(self):
        """Returns the text of the entire document"""
        return self.text()

    def __str__(self):
        """Returns the text of the entire document"""
        return self.text()

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        if len(self.data) != len(other.data):
            if self.debug: print("[PyNLPl FoLiA DEBUG] Equality check - Documents have unequal amount of children",file=stderr)
            return False
        for e,e2 in zip(self.data,other.data):
            if e != e2:
                return False
        return True











#==============================================================================

class Corpus:
    """A corpus of various FoLiA documents. Yields a Document on each iteration. Suitable for sequential processing."""

    def __init__(self,corpusdir, extension = 'xml', restrict_to_collection = "", conditionf=lambda x: True, ignoreerrors=False, **kwargs):
        self.corpusdir = corpusdir
        self.extension = extension
        self.restrict_to_collection = restrict_to_collection
        self.conditionf = conditionf
        self.ignoreerrors = ignoreerrors
        self.kwargs = kwargs

    def __iter__(self):
        if not self.restrict_to_collection:
            for f in glob.glob(os.path.join(self.corpusdir,"*." + self.extension)):
                if self.conditionf(f):
                    try:
                        yield Document(file=f, **self.kwargs )
                    except Exception as e: #pylint: disable=broad-except
                        print("Error, unable to parse " + f + ": " + e.__class__.__name__  + " - " + str(e),file=stderr)
                        if not self.ignoreerrors:
                            raise
        for d in glob.glob(os.path.join(self.corpusdir,"*")):
            if (not self.restrict_to_collection or self.restrict_to_collection == os.path.basename(d)) and (os.path.isdir(d)):
                for f in glob.glob(os.path.join(d ,"*." + self.extension)):
                    if self.conditionf(f):
                        try:
                            yield Document(file=f, **self.kwargs)
                        except Exception as e: #pylint: disable=broad-except
                            print("Error, unable to parse " + f + ": " + e.__class__.__name__  + " - " + str(e),file=stderr)
                            if not self.ignoreerrors:
                                raise


class CorpusFiles(Corpus):
    """A corpus of various FoLiA documents. Yields the filenames on each iteration."""

    def __iter__(self):
        if not self.restrict_to_collection:
            for f in glob.glob(os.path.join(self.corpusdir,"*." + self.extension)):
                if self.conditionf(f):
                    try:
                        yield f
                    except Exception as e: #pylint: disable=broad-except
                        print("Error, unable to parse " + f+ ": " + e.__class__.__name__  + " - " + str(e),file=stderr)
                        if not self.ignoreerrors:
                            raise
        for d in glob.glob(os.path.join(self.corpusdir,"*")):
            if (not self.restrict_to_collection or self.restrict_to_collection == os.path.basename(d)) and (os.path.isdir(d)):
                for f in glob.glob(os.path.join(d, "*." + self.extension)):
                    if self.conditionf(f):
                        try:
                            yield f
                        except Exception as e: #pylint: disable=broad-except
                            print("Error, unable to parse " + f+ ": " + e.__class__.__name__  + " - " + str(e),file=stderr)
                            if not self.ignoreerrors:
                                raise





class CorpusProcessor(object):
    """Processes a corpus of various FoLiA documents using a parallel processing. Calls a user-defined function with the three-tuple (filename, args, kwargs) for each file in the corpus. The user-defined function is itself responsible for instantiating a FoLiA document! args and kwargs, as received by the custom function, are set through the run() method, which yields the result of the custom function on each iteration."""

    def __init__(self,corpusdir, function, threads = None, extension = 'xml', restrict_to_collection = "", conditionf=lambda x: True, maxtasksperchild=100, preindex = False, ordered=True, chunksize = 1):
        self.function = function
        self.threads = threads #If set to None, will use all available cores by default
        self.corpusdir = corpusdir
        self.extension = extension
        self.restrict_to_collection = restrict_to_collection
        self.conditionf = conditionf
        self.ignoreerrors = True
        self.maxtasksperchild = maxtasksperchild #This should never be set too high due to lxml leaking memory!!!
        self.preindex = preindex
        self.ordered = ordered
        self.chunksize = chunksize
        if preindex:
            self.index = list(CorpusFiles(self.corpusdir, self.extension, self.restrict_to_collection, self.conditionf, True))
            self.index.sort()


    def __len__(self):
        if self.preindex:
            return len(self.index)
        else:
            return ValueError("Can only retrieve length if instantiated with preindex=True")

    def execute(self):
        for _ in self.run():
            pass

    def run(self, *args, **kwargs):
        if not self.preindex:
            self.index = CorpusFiles(self.corpusdir, self.extension, self.restrict_to_collection, self.conditionf, True) #generator
        pool = multiprocessing.Pool(self.threads,None,None, self.maxtasksperchild)
        if self.ordered:
            return pool.imap( self.function,  ( (filename, args, kwargs) for filename in self.index), self.chunksize)
        else:
            return pool.imap_unordered( self.function,  ( (filename, args, kwargs) for filename in self.index), self.chunksize)
        #pool.close()



    def __iter__(self):
        return self.run()



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
            instance = ConstraintDefinition(id, restrictions,exceptions)
            constraintindex[id] = instance
        else:
            instance = ConstraintDefinition(None, restrictions,exceptions)
        return instance


    def json(self):
        return {'id': self.id} #TODO: Implement

class ClassDefinition(AbstractDefinition):
    def __init__(self,id, label, constraints=[], subclasses=[]):
        self.id = id
        self.label = label
        self.constraints = constraints
        self.subclasses = subclasses

    @classmethod
    def parsexml(Class, node, constraintindex):
        assert node.tag == '{' + NSFOLIA + '}class'
        if 'label' in node.attrib:
            label = node.attrib['label']
        else:
            label = ""

        constraints = []
        subclasses= []
        for subnode in node:
            if subnode.tag == '{' + NSFOLIA + '}constraint':
                constraints.append( ConstraintDefinition.parsexml(subnode, constraintindex) )
            elif subnode.tag == '{' + NSFOLIA + '}class':
                subclasses.append( ClassDefinition.parsexml(subnode, constraintindex) )
            elif subnode.tag[:len(NSFOLIA) +2] == '{' + NSFOLIA + '}':
                raise Exception("Invalid tag in Class definition: " + subnode.tag)

        return ClassDefinition(node.attrib['{http://www.w3.org/XML/1998/namespace}id'],label, constraints, subclasses)


    def __iter__(self):
        for c in self.subclasses:
            yield c

    def json(self):
        jsonnode = {'id': self.id, 'label': self.label}
        jsonnode['constraints'] = []
        jsonnode['subclasses'] = []
        for constraint in self.constraints:
            jsonnode['constaints'].append(constraint.json())
        for subclass in self.subclasses:
            jsonnode['subclasses'].append(subclass.json())
        return jsonnode

class SubsetDefinition(AbstractDefinition):
    def __init__(self, id, type, classes = [], constraints = []):
        self.id = id
        self.type = type
        self.classes = classes
        self.constraints = constraints

    @classmethod
    def parsexml(Class, node, constraintindex= {}):
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
                constraints.append( ConstraintDefinition.parsexml(subnode, constraintindex) )
            elif subnode.tag[:len(NSFOLIA) +2] == '{' + NSFOLIA + '}':
                raise Exception("Invalid tag in Set definition: " + subnode.tag)

        return SubsetDefinition(node.attrib['{http://www.w3.org/XML/1998/namespace}id'],type,classes, constraints)


    def json(self):
        jsonnode = {'id': self.id}
        if self.type == SetType.OPEN:
            jsonnode['type'] = 'open'
        elif self.type == SetType.CLOSED:
            jsonnode['type'] = 'closed'
        elif self.type == SetType.MIXED:
            jsonnode['type'] = 'mixed'
        jsonnode['constraints'] = []
        for constraint in self.constraints:
            jsonnode['constraints'].append(constraint.json())
        jsonnode['classes'] = {}
        for c in self.classes:
            jsonnode['classes'][c.id] = c.json()
        return jsonnode

class SetDefinition(AbstractDefinition):
    def __init__(self, id, type, classes = [], subsets = [], constraintindex = {}):
        isncname(id)
        self.id = id
        self.type = type
        self.classes = classes
        self.subsets = subsets
        self.constraintindex = constraintindex


    @classmethod
    def parsexml(Class, node):
        assert node.tag == '{' + NSFOLIA + '}set'
        classes = []
        subsets= []
        constraintindex = {}
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

        for subnode in node:
            if subnode.tag == '{' + NSFOLIA + '}class':
                classes.append( ClassDefinition.parsexml(subnode, constraintindex) )
            elif subnode.tag == '{' + NSFOLIA + '}subset':
                subsets.append( ClassDefinition.parsexml(subnode, constraintindex) )
            elif subnode.tag[:len(NSFOLIA) +2] == '{' + NSFOLIA + '}':
                raise SetDefinitionError("Invalid tag in Set definition: " + subnode.tag)

        return SetDefinition(node.attrib['{http://www.w3.org/XML/1998/namespace}id'],type,classes, subsets, constraintindex)

    def testclass(self,cls):
        raise NotImplementedError #TODO, IMPLEMENT!

    def testsubclass(self, cls, subset, subclass):
        raise NotImplementedError #TODO, IMPLEMENT!

    def json(self):
        jsonnode = {'id': self.id}
        if self.type == SetType.OPEN:
            jsonnode['type'] = 'open'
        elif self.type == SetType.CLOSED:
            jsonnode['type'] = 'closed'
        elif self.type == SetType.MIXED:
            jsonnode['type'] = 'mixed'
        jsonnode['subsets'] = {}
        for subset in self.subsets:
            jsonnode['subsets'][subset.id] = subset.json()
        jsonnode['classes'] = {}
        jsonnode['classorder'] = []
        for c in sorted(self.classes, key=lambda x: x.label):
            jsonnode['classes'][c.id] = c.json()
            jsonnode['classorder'].append( c.id )
        return jsonnode



def loadsetdefinition(filename):
    if filename[0] == '/' or filename[0] == '.':
        try:
            tree = ElementTree.parse(filename, ElementTree.XMLParser(collect_ids=False))
        except TypeError:
            tree = ElementTree.parse(filename, ElementTree.XMLParser())
    else:
        try:
            f = urlopen(filename)
        except:
            raise DeepValidationError("Unable to download " + filename)
        try:
            tree = xmltreefromstring(f.read())
        except IOError:
            raise DeepValidationError("Unable to download " + filename)
        f.close()
    root = tree.getroot()
    if root.tag != '{' + NSFOLIA + '}set':
        raise SetDefinitionError("Not a FoLiA Set Definition! Unexpected root tag:"+ root.tag)

    return SetDefinition.parsexml(root)


def relaxng_declarations():
    E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
    for key in vars(AnnotationType).keys():
        if key[0] != '_':
            yield E.element( E.optional( E.attribute(name='set')) , E.optional(E.attribute(name='annotator')) , E.optional( E.attribute(name='annotatortype') ) , E.optional( E.attribute(name='datetime') )  , name=key.lower() + '-annotation')


def relaxng(filename=None):
    E = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0",nsmap={None:'http://relaxng.org/ns/structure/1.0' , 'folia': NSFOLIA, 'xml' : "http://www.w3.org/XML/1998/namespace"})
    grammar = E.grammar( E.start( E.element( #FoLiA
                E.attribute(name='id',ns="http://www.w3.org/XML/1998/namespace"),
                E.optional( E.attribute(name='version') ),
                E.optional( E.attribute(name='generator') ),
                E.element( #metadata
                    E.optional(E.attribute(name='type')),
                    E.optional(E.attribute(name='src')),
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
                E.interleave(
                    E.zeroOrMore(
                        E.ref(name='text'),
                    ),
                    E.zeroOrMore(
                        E.ref(name='speech'),
                    ),
                ),
                name='FoLiA',
                ns = NSFOLIA
            ) ),
            #definitions needed for ForeignData (allow any content) - see http://www.microhowto.info/howto/match_arbitrary_content_using_relax_ng.html
            E.define( E.interleave(E.zeroOrMore(E.ref(name="any_element")),E.text()), name="any_content"),
            E.define( E.element(E.anyName(), E.zeroOrMore(E.ref(name="any_attribute")), E.zeroOrMore(E.ref(name="any_content"))), name="any_element"),
            E.define( E.attribute(E.anyName()), name="any_attribute"),
            #Definition for allowing alien-namespace attributes on any element
            E.define( E.zeroOrMore(E.attribute(E.anyName(getattr(E,'except')(E.nsName(),E.nsName(ns=""),E.nsName(ns="http://www.w3.org/XML/1998/namespace"),E.nsName(ns="http://www.w3.org/1999/xlink"))))), name="allow_foreign_attributes")
            )

    done = {}
    for c in globals().values():
        if 'relaxng' in dir(c):
            if c.relaxng and c.XMLTAG and not c.XMLTAG in done:
                done[c.XMLTAG] = True
                definition = c.relaxng()
                grammar.append( definition )
                if c.XMLTAG == 'item': #nasty backward-compatibility hack to allow deprecated listitem element (actually called item)
                    definition_alias = c.relaxng()
                    definition_alias.set('name','listitem')
                    definition_alias[0].set('name','listitem')
                    grammar.append( definition_alias )

    #for e in relaxng_imdi():
    #    grammar.append(e)
    if filename:
        if sys.version < '3':
            f = io.open(filename,'w',encoding='utf-8')
        else:
            f = io.open(filename,'wb')
        if LXE:
            if sys.version < '3':
                f.write( ElementTree.tostring(relaxng(),pretty_print=True).replace("</define>","</define>\n\n") )
            else:
                f.write( ElementTree.tostring(relaxng(),pretty_print=True).replace(b"</define>",b"</define>\n\n") )
        else:
            f.write( ElementTree.tostring(relaxng()).replace("</define>","</define>\n\n") )
        f.close()

    return grammar



def findwords(doc, worditerator, *args, **kwargs):
    if 'leftcontext' in kwargs:
        leftcontext = int(kwargs['leftcontext'])
        del kwargs['leftcontext']
    else:
        leftcontext = 0
    if 'rightcontext' in kwargs:
        rightcontext =  int(kwargs['rightcontext'])
        del kwargs['rightcontext']
    else:
        rightcontext = 0
    if 'maxgapsize' in kwargs:
        maxgapsize = int(kwargs['maxgapsize'])
        del kwargs['maxgapsize']
    else:
        maxgapsize = 10
    for key in kwargs.keys():
        raise Exception("Unknown keyword parameter: " + key)

    matchcursor = 0

    #shortcut for when no Pattern is passed, make one on the fly
    if len(args) == 1 and not isinstance(args[0], Pattern):
        if not isinstance(args[0], list) and not isinstance(args[0], tuple):
            args[0] = [args[0]]
        args[0] = Pattern(*args[0])



    unsetwildcards = False
    variablewildcards = None
    prevsize = -1
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

    if variablewildcards: #pylint: disable=too-many-nested-blocks
        #one or more items have a * wildcard, which may span multiple tokens. Resolve this to a wider range of simpler patterns

        #we're not commited to a particular size, expand to various ones
        for size in range(len(variablewildcards), maxgapsize+1):
            for distribution in  pynlpl.algorithms.sum_to_n(size, len(variablewildcards)): #gap distributions, (amount) of 'True' wildcards
                patterns = []
                for pattern in args:
                    if pattern.variablesize():
                        patterns += list(pattern.resolve(size,distribution))
                    else:
                        patterns.append( pattern )
                for match in findwords(doc, worditerator,*patterns, **{'leftcontext':leftcontext,'rightcontext':rightcontext}):
                    yield match

    else:
        patterns = args #pylint: disable=redefined-variable-type
        buffers = []

        for word in worditerator():
            buffers.append( [] ) #Add a new empty buffer for every word
            match = [None] * len(buffers)
            for pattern in patterns:
                #find value to match against
                if not pattern.matchannotation:
                    value = word.text()
                else:
                    if pattern.matchannotationset:
                        items = list(word.select(pattern.matchannotation, pattern.matchannotationset, True, [Original, Suggestion, Alternative]))
                    else:
                        try:
                            set = doc.defaultset(pattern.matchannotation.ANNOTATIONTYPE)
                            items = list(word.select(pattern.matchannotation, set, True, [Original, Suggestion, Alternative] ))
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
                    match[i] = (value == pattern.sequence[matchcursor] or pattern.sequence[matchcursor] is True or (isinstance(pattern.sequence[matchcursor], tuple) and value in pattern.sequence[matchcursor]))


            for buffer, matches in list(zip(buffers, match)):
                if matches:
                    buffer.append(word) #add the word
                    if len(buffer) == len(pattern.sequence):
                        yield buffer[0].leftcontext(leftcontext) + buffer + buffer[-1].rightcontext(rightcontext)
                        buffers.remove(buffer)
                else:
                    buffers.remove(buffer) #remove buffer

class Reader(object):
    """Streaming FoLiA reader. The reader allows you to read a FoLiA Document without holding the whole tree structure in memory. The document will be read and the elements you seek returned as they are found. If you are querying a corpus of large FoLiA documents for a specific structure, then it is strongly recommend to use the Reader rather than the standard Document!"""


    def __init__(self, filename, target, *args, **kwargs):
        """Read a FoLiA document in a streaming fashion. You select a specific target element and all occurrences of this element, including all  contents (so all elements within), will be returned.

        Arguments:

            * ``filename``: The filename of the document to read
            * ``target``: The FoLiA element(s) you want to read (with everything contained in its scope). Passed as a class. For example: ``folia.Sentence``, or a tuple of multiple element classes. Can also be set to ``None`` to return all elements, but that would load the full tree structure into memory.

        """

        self.target = target
        if not (isinstance(self.target, tuple) or isinstance(self.target, list) or issubclass(self.target, AbstractElement)):
            raise ValueError("Target must be subclass of FoLiA element")
        if 'bypassleak' in kwargs:
            self.bypassleak = False
        self.stream = io.open(filename,'rb')
        self.initdoc()


    def findwords(self, *args, **kwargs):
        self.target = Word
        for x in findwords(self.doc,self.__iter__,*args,**kwargs):
            yield x

    def initdoc(self):
        self.doc = None
        metadata = False
        for action, node in ElementTree.iterparse(self.stream, events=("start","end")):
            if action == "start" and node.tag == "{" + NSFOLIA + "}FoLiA":
                if '{http://www.w3.org/XML/1998/namespace}id' in node.attrib:
                    id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
                self.doc = Document(id=id)
                if 'version' in node.attrib:
                    self.doc.version = node.attrib['version']
            if action == "end" and node.tag == "{" + NSFOLIA + "}metadata":
                if not self.doc:
                    raise MalformedXMLError("Metadata found, but no document? Impossible")
                metadata = True
                self.doc.parsemetadata(node)
                break


        if not self.doc:
            raise MalformedXMLError("No FoLiA Document found!")
        elif not metadata:
            raise MalformedXMLError("No metadata found!")

        self.stream.seek(0)


    def __iter__(self):
        """Iterating over a Reader instance will cause the FoLiA document to be read. This is a generator yielding instances of the object you specified"""

        if not isinstance(self.target, tuple) or isinstance(self.target,list):
            target = "{" + NSFOLIA + "}" + self.target.XMLTAG
            Class = self.target
            multitargets = False
        else:
            multitargets = True

        for action, node in ElementTree.iterparse(self.stream, events=("end",), tag=target):
            if not multitargets or (multitargets and node.tag.startswith('{' + NSFOLIA + '}')):
                if not multitargets: Class = XML2CLASS[node.tag[nslen:]]
                if not multitargets or (multitargets and Class in self.targets):
                    element = Class.parsexml(node, self.doc)
                    node.clear() #clean up children
                    # Also eliminate now-empty references from the root node to
                    # elem (http://www.ibm.com/developerworks/xml/library/x-hiperfparse/)
                    #for ancestor in node.xpath('ancestor-or-self::*'):
                    while node.getprevious() is not None:
                        del node.getparent()[0]  # clean up preceding siblings
                    yield element

    def __del__(self):
        self.stream.close()

def isncname(name):
    #not entirely according to specs http://www.w3.org/TR/REC-xml/#NT-Name , but simplified:
    for i, c in enumerate(name):
        if i == 0:
            if not c.isalpha():
                raise ValueError('Invalid XML NCName identifier: ' + name + ' (at position ' + str(i+1)+')')
        else:
            if not c.isalnum() and not (c in ['-','_','.']):
                raise ValueError('Invalid XML NCName identifier: ' + name + ' (at position ' + str(i+1)+')')
    return True



def validate(filename,schema=None,deep=False):
    if not os.path.exists(filename):
        raise IOError("No such file")

    try:
        try:
            doc = ElementTree.parse(filename, ElementTree.XMLParser(collect_ids=False) )
        except TypeError:
            doc = ElementTree.parse(filename, ElementTree.XMLParser() ) #older lxml, may leak!
    except:
        raise MalformedXMLError("Malformed XML!")

    #See if there's inline IMDI and strip it off prior to validation (validator doesn't do IMDI)
    m = doc.xpath('//folia:metadata', namespaces={'f': 'http://ilk.uvt.nl/folia','folia': 'http://ilk.uvt.nl/folia' })
    if m:
        metadata = m[0]
        m = metadata.find('{http://www.mpi.nl/IMDI/Schema/IMDI}METATRANSCRIPT')
        if m is not None:
            metadata.remove(m)

    if not schema:
        schema = ElementTree.RelaxNG(relaxng())


    schema.assertValid(doc) #will raise exceptions

    if deep:
        doc = Document(tree=doc, deepvalidation=True)

#================================= FOLIA SPECIFICATION ==========================================================

#foliaspec:header
#This file was last updated according to the FoLiA specification for version 1.2.0 on 2016-05-18 13:42:38, using foliaspec.py
#Code blocks after a foliaspec comment (until the next newline) are automatically generated. **DO NOT EDIT THOSE** and **DO NOT REMOVE ANY FOLIASPEC COMMENTS** !!!

#foliaspec:structurescope:STRUCTURESCOPE
#Structure scope above the sentence level, used by next() and previous() methods
STRUCTURESCOPE = (Sentence, Paragraph, Division, ListItem, Text, Event, Caption, Head,)

#foliaspec:annotationtype_xml_map
#A mapping from annotation types to xml tags (strings)
ANNOTATIONTYPE2XML = {
    AnnotationType.ALIGNMENT:  "alignment" ,
    AnnotationType.CHUNKING:  "chunk" ,
    AnnotationType.COMPLEXALIGNMENT:  "complexalignment" ,
    AnnotationType.COREFERENCE:  "coreferencechain" ,
    AnnotationType.CORRECTION:  "correction" ,
    AnnotationType.DEFINITION:  "def" ,
    AnnotationType.DEPENDENCY:  "dependency" ,
    AnnotationType.DIVISION:  "div" ,
    AnnotationType.DOMAIN:  "domain" ,
    AnnotationType.ENTITY:  "entity" ,
    AnnotationType.ENTRY:  "entry" ,
    AnnotationType.ERRORDETECTION:  "errordetection" ,
    AnnotationType.EVENT:  "event" ,
    AnnotationType.EXAMPLE:  "ex" ,
    AnnotationType.FIGURE:  "figure" ,
    AnnotationType.GAP:  "gap" ,
    AnnotationType.LANG:  "lang" ,
    AnnotationType.LEMMA:  "lemma" ,
    AnnotationType.LINEBREAK:  "br" ,
    AnnotationType.LIST:  "list" ,
    AnnotationType.METRIC:  "metric" ,
    AnnotationType.MORPHOLOGICAL:  "morpheme" ,
    AnnotationType.NOTE:  "note" ,
    AnnotationType.PARAGRAPH:  "p" ,
    AnnotationType.PART:  "part" ,
    AnnotationType.PHON:  "ph" ,
    AnnotationType.PHONOLOGICAL:  "phoneme" ,
    AnnotationType.POS:  "pos" ,
    AnnotationType.SEMROLE:  "semrole" ,
    AnnotationType.SENSE:  "sense" ,
    AnnotationType.SENTENCE:  "s" ,
    AnnotationType.STRING:  "str" ,
    AnnotationType.SUBJECTIVITY:  "subjectivity" ,
    AnnotationType.SYNTAX:  "su" ,
    AnnotationType.TABLE:  "table" ,
    AnnotationType.TERM:  "term" ,
    AnnotationType.TEXT:  "t" ,
    AnnotationType.CORRECTION:  "t-correction" ,
    AnnotationType.ERRORDETECTION:  "t-error" ,
    AnnotationType.GAP:  "t-gap" ,
    AnnotationType.STRING:  "t-str" ,
    AnnotationType.STYLE:  "t-style" ,
    AnnotationType.TIMESEGMENT:  "timesegment" ,
    AnnotationType.UTTERANCE:  "utt" ,
    AnnotationType.WHITESPACE:  "whitespace" ,
    AnnotationType.TOKEN:  "w" ,
}

#foliaspec:string_class_map
XML2CLASS = {
    "aref": AlignReference,
    "alignment": Alignment,
    "alt": Alternative,
    "altlayers": AlternativeLayers,
    "caption": Caption,
    "cell": Cell,
    "chunk": Chunk,
    "chunking": ChunkingLayer,
    "complexalignment": ComplexAlignment,
    "complexalignments": ComplexAlignmentLayer,
    "content": Content,
    "coreferencechain": CoreferenceChain,
    "coreferences": CoreferenceLayer,
    "coreferencelink": CoreferenceLink,
    "correction": Correction,
    "current": Current,
    "def": Definition,
    "dependencies": DependenciesLayer,
    "dependency": Dependency,
    "dep": DependencyDependent,
    "desc": Description,
    "div": Division,
    "domain": DomainAnnotation,
    "entities": EntitiesLayer,
    "entity": Entity,
    "entry": Entry,
    "errordetection": ErrorDetection,
    "event": Event,
    "ex": Example,
    "external": External,
    "feat": Feature,
    "figure": Figure,
    "foreign-data": ForeignData,
    "gap": Gap,
    "head": Head,
    "hd": Headspan,
    "label": Label,
    "lang": LangAnnotation,
    "lemma": LemmaAnnotation,
    "br": Linebreak,
    "list": List,
    "item": ListItem,
    "metric": Metric,
    "morpheme": Morpheme,
    "morphology": MorphologyLayer,
    "new": New,
    "note": Note,
    "original": Original,
    "p": Paragraph,
    "part": Part,
    "ph": PhonContent,
    "phoneme": Phoneme,
    "phonology": PhonologyLayer,
    "pos": PosAnnotation,
    "quote": Quote,
    "ref": Reference,
    "row": Row,
    "semrole": SemanticRole,
    "semroles": SemanticRolesLayer,
    "sense": SenseAnnotation,
    "s": Sentence,
    "speech": Speech,
    "str": String,
    "subjectivity": SubjectivityAnnotation,
    "suggestion": Suggestion,
    "su": SyntacticUnit,
    "syntax": SyntaxLayer,
    "table": Table,
    "tablehead": TableHead,
    "term": Term,
    "text": Text,
    "t": TextContent,
    "t-correction": TextMarkupCorrection,
    "t-error": TextMarkupError,
    "t-gap": TextMarkupGap,
    "t-str": TextMarkupString,
    "t-style": TextMarkupStyle,
    "timesegment": TimeSegment,
    "timing": TimingLayer,
    "utt": Utterance,
    "whitespace": Whitespace,
    "w": Word,
    "wref": WordReference,
}

XML2CLASS['listitem'] = ListItem #backward compatibility for erroneous old FoLiA versions (XML tag is 'item' now, consistent with manual)

#foliaspec:annotationtype_layerclass_map
ANNOTATIONTYPE2LAYERCLASS = {
    AnnotationType.CHUNKING:  ChunkingLayer ,
    AnnotationType.COMPLEXALIGNMENT:  ComplexAlignmentLayer ,
    AnnotationType.COREFERENCE:  CoreferenceLayer ,
    AnnotationType.DEPENDENCY:  DependenciesLayer ,
    AnnotationType.ENTITY:  EntitiesLayer ,
    AnnotationType.MORPHOLOGICAL:  MorphologyLayer ,
    AnnotationType.PHONOLOGICAL:  PhonologyLayer ,
    AnnotationType.SEMROLE:  SemanticRolesLayer ,
    AnnotationType.SYNTAX:  SyntaxLayer ,
    AnnotationType.TIMESEGMENT:  TimingLayer ,
}

#foliaspec:default_ignore
#Default ignore list for the select() method, do not descend into these
default_ignore = ( Original, Suggestion, Alternative, AlternativeLayers, ForeignData,)

#foliaspec:default_ignore_annotations
#Default ignore list for token annotation
default_ignore_annotations = ( Original, Suggestion, Alternative, AlternativeLayers, MorphologyLayer, PhonologyLayer,)

#foliaspec:default_ignore_structure
#Default ignore list for structure annotation
default_ignore_structure = ( Original, Suggestion, Alternative, AlternativeLayers, AbstractAnnotationLayer,)

#foliaspec:defaultproperties
#Default properties which all elements inherit
AbstractElement.ACCEPTED_DATA = (Description,)
AbstractElement.ANNOTATIONTYPE = None
AbstractElement.AUTH = True
AbstractElement.AUTO_GENERATE_ID = False
AbstractElement.OCCURRENCES = 0
AbstractElement.OCCURRENCES_PER_SET = 0
AbstractElement.OPTIONAL_ATTRIBS = None
AbstractElement.PHONCONTAINER = False
AbstractElement.PRIMARYELEMENT = True
AbstractElement.PRINTABLE = False
AbstractElement.REQUIRED_ATTRIBS = None
AbstractElement.REQUIRED_DATA = None
AbstractElement.SETONLY = False
AbstractElement.SPEAKABLE = False
AbstractElement.SUBSET = None
AbstractElement.TEXTCONTAINER = False
AbstractElement.TEXTDELIMITER = None
AbstractElement.XLINK = False
AbstractElement.XMLTAG = None

#foliaspec:setelementproperties
#Sets all element properties for all elements
#------ AbstractAnnotationLayer -------
AbstractAnnotationLayer.ACCEPTED_DATA = (Correction, Description, ForeignData,)
AbstractAnnotationLayer.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.ANNOTATOR, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.N,)
AbstractAnnotationLayer.PRINTABLE = False
AbstractAnnotationLayer.SETONLY = True
AbstractAnnotationLayer.SPEAKABLE = False
#------ AbstractCorrectionChild -------
AbstractCorrectionChild.ACCEPTED_DATA = (AbstractSpanAnnotation, AbstractStructureElement, AbstractTokenAnnotation, Correction, Description, ForeignData, Metric, PhonContent, String, TextContent,)
AbstractCorrectionChild.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.ANNOTATOR, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.N,)
AbstractCorrectionChild.PRINTABLE = True
AbstractCorrectionChild.SPEAKABLE = True
AbstractCorrectionChild.TEXTDELIMITER = None
#------ AbstractExtendedTokenAnnotation -------
#------ AbstractSpanAnnotation -------
AbstractSpanAnnotation.ACCEPTED_DATA = (Alignment, Description, ForeignData, Metric,)
AbstractSpanAnnotation.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
AbstractSpanAnnotation.PRINTABLE = True
AbstractSpanAnnotation.SPEAKABLE = True
#------ AbstractSpanRole -------
AbstractSpanRole.ACCEPTED_DATA = (Alignment, Description, Feature, ForeignData, Metric, WordReference,)
AbstractSpanRole.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.ANNOTATOR, Attrib.N, Attrib.DATETIME,)
#------ AbstractStructureElement -------
AbstractStructureElement.ACCEPTED_DATA = (AbstractAnnotationLayer, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Metric, Part,)
AbstractStructureElement.AUTO_GENERATE_ID = True
AbstractStructureElement.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
AbstractStructureElement.PRINTABLE = True
AbstractStructureElement.REQUIRED_ATTRIBS = None
AbstractStructureElement.SPEAKABLE = True
AbstractStructureElement.TEXTDELIMITER = "\n\n"
#------ AbstractTextMarkup -------
AbstractTextMarkup.ACCEPTED_DATA = (AbstractTextMarkup, Description,)
AbstractTextMarkup.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
AbstractTextMarkup.PRIMARYELEMENT = False
AbstractTextMarkup.PRINTABLE = True
AbstractTextMarkup.TEXTCONTAINER = True
AbstractTextMarkup.TEXTDELIMITER = ""
AbstractTextMarkup.XLINK = True
#------ AbstractTokenAnnotation -------
AbstractTokenAnnotation.ACCEPTED_DATA = (Description, Feature, ForeignData, Metric,)
AbstractTokenAnnotation.OCCURRENCES_PER_SET = 1
AbstractTokenAnnotation.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
AbstractTokenAnnotation.REQUIRED_ATTRIBS = (Attrib.CLASS,)
#------ ActorFeature -------
ActorFeature.SUBSET = "actor"
ActorFeature.XMLTAG = None
#------ AlignReference -------
AlignReference.XMLTAG = "aref"
#------ Alignment -------
Alignment.ACCEPTED_DATA = (AlignReference, Description, Feature, ForeignData, Metric,)
Alignment.ANNOTATIONTYPE = AnnotationType.ALIGNMENT
Alignment.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
Alignment.PRINTABLE = False
Alignment.REQUIRED_ATTRIBS = None
Alignment.SPEAKABLE = False
Alignment.XLINK = True
Alignment.XMLTAG = "alignment"
#------ Alternative -------
Alternative.ACCEPTED_DATA = (AbstractTokenAnnotation, Correction, Description, ForeignData, MorphologyLayer, PhonologyLayer,)
Alternative.AUTH = False
Alternative.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
Alternative.PRINTABLE = False
Alternative.REQUIRED_ATTRIBS = None
Alternative.SPEAKABLE = False
Alternative.XMLTAG = "alt"
#------ AlternativeLayers -------
AlternativeLayers.ACCEPTED_DATA = (AbstractAnnotationLayer, Description, ForeignData,)
AlternativeLayers.AUTH = False
AlternativeLayers.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
AlternativeLayers.PRINTABLE = False
AlternativeLayers.REQUIRED_ATTRIBS = None
AlternativeLayers.SPEAKABLE = False
AlternativeLayers.XMLTAG = "altlayers"
#------ BegindatetimeFeature -------
BegindatetimeFeature.SUBSET = "begindatetime"
BegindatetimeFeature.XMLTAG = None
#------ Caption -------
Caption.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Gap, Linebreak, Metric, Part, PhonContent, Reference, Sentence, String, TextContent, Whitespace,)
Caption.OCCURRENCES = 1
Caption.XMLTAG = "caption"
#------ Cell -------
Cell.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Entry, Event, Example, Feature, ForeignData, Gap, Head, Linebreak, Metric, Note, Paragraph, Part, Reference, Sentence, String, TextContent, Whitespace, Word,)
Cell.TEXTDELIMITER = " | "
Cell.XMLTAG = "cell"
#------ Chunk -------
Chunk.ACCEPTED_DATA = (Alignment, Description, Feature, ForeignData, Metric, WordReference,)
Chunk.ANNOTATIONTYPE = AnnotationType.CHUNKING
Chunk.XMLTAG = "chunk"
#------ ChunkingLayer -------
ChunkingLayer.ACCEPTED_DATA = (Chunk, Correction, Description, ForeignData,)
ChunkingLayer.ANNOTATIONTYPE = AnnotationType.CHUNKING
ChunkingLayer.PRIMARYELEMENT = False
ChunkingLayer.XMLTAG = "chunking"
#------ ComplexAlignment -------
ComplexAlignment.ACCEPTED_DATA = (Alignment, Description, Feature, ForeignData, Metric,)
ComplexAlignment.ANNOTATIONTYPE = AnnotationType.COMPLEXALIGNMENT
ComplexAlignment.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
ComplexAlignment.PRINTABLE = False
ComplexAlignment.REQUIRED_ATTRIBS = None
ComplexAlignment.SPEAKABLE = False
ComplexAlignment.XMLTAG = "complexalignment"
#------ ComplexAlignmentLayer -------
ComplexAlignmentLayer.ACCEPTED_DATA = (ComplexAlignment, Correction, Description, ForeignData,)
ComplexAlignmentLayer.ANNOTATIONTYPE = AnnotationType.COMPLEXALIGNMENT
ComplexAlignmentLayer.PRIMARYELEMENT = False
ComplexAlignmentLayer.XMLTAG = "complexalignments"
#------ Content -------
Content.OCCURRENCES = 1
Content.XMLTAG = "content"
#------ CoreferenceChain -------
CoreferenceChain.ACCEPTED_DATA = (Alignment, CoreferenceLink, Description, ForeignData, Metric,)
CoreferenceChain.ANNOTATIONTYPE = AnnotationType.COREFERENCE
CoreferenceChain.REQUIRED_DATA = (CoreferenceLink,)
CoreferenceChain.XMLTAG = "coreferencechain"
#------ CoreferenceLayer -------
CoreferenceLayer.ACCEPTED_DATA = (CoreferenceChain, Correction, Description, ForeignData,)
CoreferenceLayer.ANNOTATIONTYPE = AnnotationType.COREFERENCE
CoreferenceLayer.PRIMARYELEMENT = False
CoreferenceLayer.XMLTAG = "coreferences"
#------ CoreferenceLink -------
CoreferenceLink.ACCEPTED_DATA = (Alignment, Description, Feature, ForeignData, Headspan, LevelFeature, Metric, ModalityFeature, TimeFeature, WordReference,)
CoreferenceLink.ANNOTATIONTYPE = AnnotationType.COREFERENCE
CoreferenceLink.PRIMARYELEMENT = False
CoreferenceLink.XMLTAG = "coreferencelink"
#------ Correction -------
Correction.ACCEPTED_DATA = (Current, Description, ErrorDetection, Feature, ForeignData, Metric, New, Original, Suggestion,)
Correction.ANNOTATIONTYPE = AnnotationType.CORRECTION
Correction.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
Correction.PRINTABLE = True
Correction.SPEAKABLE = True
Correction.TEXTDELIMITER = None
Correction.XMLTAG = "correction"
#------ Current -------
Current.OCCURRENCES = 1
Current.OPTIONAL_ATTRIBS = None
Current.XMLTAG = "current"
#------ Definition -------
Definition.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, Figure, ForeignData, List, Metric, Paragraph, Part, PhonContent, Reference, Sentence, String, Table, TextContent, Utterance, Word,)
Definition.ANNOTATIONTYPE = AnnotationType.DEFINITION
Definition.XMLTAG = "def"
#------ DependenciesLayer -------
DependenciesLayer.ACCEPTED_DATA = (Correction, Dependency, Description, ForeignData,)
DependenciesLayer.ANNOTATIONTYPE = AnnotationType.DEPENDENCY
DependenciesLayer.PRIMARYELEMENT = False
DependenciesLayer.XMLTAG = "dependencies"
#------ Dependency -------
Dependency.ACCEPTED_DATA = (Alignment, DependencyDependent, Description, Feature, ForeignData, Headspan, Metric,)
Dependency.ANNOTATIONTYPE = AnnotationType.DEPENDENCY
Dependency.REQUIRED_DATA = (DependencyDependent, Headspan,)
Dependency.XMLTAG = "dependency"
#------ DependencyDependent -------
DependencyDependent.XMLTAG = "dep"
#------ Description -------
Description.OCCURRENCES = 1
Description.XMLTAG = "desc"
#------ Division -------
Division.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Division, Entry, Event, Example, Feature, Figure, ForeignData, Gap, Head, Linebreak, List, Metric, Note, Paragraph, Part, PhonContent, Quote, Reference, Sentence, Table, TextContent, Utterance, Whitespace,)
Division.ANNOTATIONTYPE = AnnotationType.DIVISION
Division.TEXTDELIMITER = "\n\n\n"
Division.XMLTAG = "div"
#------ DomainAnnotation -------
DomainAnnotation.ANNOTATIONTYPE = AnnotationType.DOMAIN
DomainAnnotation.OCCURRENCES_PER_SET = 0
DomainAnnotation.XMLTAG = "domain"
#------ EnddatetimeFeature -------
EnddatetimeFeature.SUBSET = "enddatetime"
EnddatetimeFeature.XMLTAG = None
#------ EntitiesLayer -------
EntitiesLayer.ACCEPTED_DATA = (Correction, Description, Entity, ForeignData,)
EntitiesLayer.ANNOTATIONTYPE = AnnotationType.ENTITY
EntitiesLayer.PRIMARYELEMENT = False
EntitiesLayer.XMLTAG = "entities"
#------ Entity -------
Entity.ACCEPTED_DATA = (Alignment, Description, Feature, ForeignData, Metric, WordReference,)
Entity.ANNOTATIONTYPE = AnnotationType.ENTITY
Entity.XMLTAG = "entity"
#------ Entry -------
Entry.ACCEPTED_DATA = (AbstractAnnotationLayer, Alignment, Alternative, AlternativeLayers, Correction, Definition, Description, Example, Feature, ForeignData, Metric, Part, Term,)
Entry.ANNOTATIONTYPE = AnnotationType.ENTRY
Entry.XMLTAG = "entry"
#------ ErrorDetection -------
ErrorDetection.ANNOTATIONTYPE = AnnotationType.ERRORDETECTION
ErrorDetection.OCCURRENCES_PER_SET = 0
ErrorDetection.XMLTAG = "errordetection"
#------ Event -------
Event.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, ActorFeature, Alignment, Alternative, AlternativeLayers, BegindatetimeFeature, Correction, Description, Division, EnddatetimeFeature, Event, Example, Feature, Figure, ForeignData, Head, Linebreak, List, Metric, Paragraph, Part, PhonContent, Reference, Sentence, String, Table, TextContent, Utterance, Whitespace, Word,)
Event.ANNOTATIONTYPE = AnnotationType.EVENT
Event.XMLTAG = "event"
#------ Example -------
Example.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, Figure, ForeignData, Linebreak, List, Metric, Paragraph, Part, PhonContent, Reference, Sentence, String, Table, TextContent, Utterance, Whitespace, Word,)
Example.ANNOTATIONTYPE = AnnotationType.EXAMPLE
Example.XMLTAG = "ex"
#------ External -------
External.ACCEPTED_DATA = (Description,)
External.AUTH = True
External.OPTIONAL_ATTRIBS = None
External.PRINTABLE = True
External.REQUIRED_ATTRIBS = (Attrib.SRC,)
External.SPEAKABLE = False
External.XMLTAG = "external"
#------ Feature -------
Feature.XMLTAG = "feat"
#------ Figure -------
Figure.ACCEPTED_DATA = (AbstractAnnotationLayer, Alignment, Alternative, AlternativeLayers, Caption, Correction, Description, Feature, ForeignData, Metric, Part, Sentence, String, TextContent,)
Figure.ANNOTATIONTYPE = AnnotationType.FIGURE
Figure.SPEAKABLE = False
Figure.TEXTDELIMITER = "\n\n"
Figure.XMLTAG = "figure"
#------ ForeignData -------
ForeignData.XMLTAG = "foreign-data"
#------ FunctionFeature -------
FunctionFeature.SUBSET = "function"
FunctionFeature.XMLTAG = None
#------ Gap -------
Gap.ACCEPTED_DATA = (Content, Description, Feature, ForeignData, Metric, Part,)
Gap.ANNOTATIONTYPE = AnnotationType.GAP
Gap.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME,)
Gap.XMLTAG = "gap"
#------ Head -------
Head.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Event, Feature, ForeignData, Gap, Linebreak, Metric, Part, PhonContent, Reference, Sentence, String, TextContent, Whitespace, Word,)
Head.OCCURRENCES = 1
Head.TEXTDELIMITER = "\n\n"
Head.XMLTAG = "head"
#------ HeadFeature -------
HeadFeature.SUBSET = "head"
HeadFeature.XMLTAG = None
#------ Headspan -------
Headspan.XMLTAG = "hd"
#------ Label -------
Label.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Metric, Part, PhonContent, Reference, String, TextContent, Word,)
Label.XMLTAG = "label"
#------ LangAnnotation -------
LangAnnotation.ANNOTATIONTYPE = AnnotationType.LANG
LangAnnotation.XMLTAG = "lang"
#------ LemmaAnnotation -------
LemmaAnnotation.ANNOTATIONTYPE = AnnotationType.LEMMA
LemmaAnnotation.XMLTAG = "lemma"
#------ LevelFeature -------
LevelFeature.SUBSET = "level"
LevelFeature.XMLTAG = None
#------ Linebreak -------
Linebreak.ANNOTATIONTYPE = AnnotationType.LINEBREAK
Linebreak.TEXTDELIMITER = ""
Linebreak.XMLTAG = "br"
#------ List -------
List.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Caption, Correction, Description, Event, Feature, ForeignData, ListItem, Metric, Note, Part, PhonContent, Reference, String, TextContent,)
List.ANNOTATIONTYPE = AnnotationType.LIST
List.TEXTDELIMITER = "\n\n"
List.XMLTAG = "list"
#------ ListItem -------
ListItem.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Event, Feature, ForeignData, Gap, Label, Linebreak, List, Metric, Note, Part, PhonContent, Reference, Sentence, String, TextContent, Whitespace,)
ListItem.TEXTDELIMITER = "\n"
ListItem.XMLTAG = "item"
#------ Metric -------
Metric.ACCEPTED_DATA = (Description, Feature, ForeignData, ValueFeature,)
Metric.ANNOTATIONTYPE = AnnotationType.METRIC
Metric.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.N, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME, Attrib.SPEAKER,)
Metric.XMLTAG = "metric"
#------ ModalityFeature -------
ModalityFeature.SUBSET = "modality"
ModalityFeature.XMLTAG = None
#------ Morpheme -------
Morpheme.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, FunctionFeature, Metric, Morpheme, Part, PhonContent, String, TextContent,)
Morpheme.ANNOTATIONTYPE = AnnotationType.MORPHOLOGICAL
Morpheme.TEXTDELIMITER = ""
Morpheme.XMLTAG = "morpheme"
#------ MorphologyLayer -------
MorphologyLayer.ACCEPTED_DATA = (Correction, Description, ForeignData, Morpheme,)
MorphologyLayer.ANNOTATIONTYPE = AnnotationType.MORPHOLOGICAL
MorphologyLayer.PRIMARYELEMENT = False
MorphologyLayer.XMLTAG = "morphology"
#------ New -------
New.OCCURRENCES = 1
New.OPTIONAL_ATTRIBS = None
New.XMLTAG = "new"
#------ Note -------
Note.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Example, Feature, Figure, ForeignData, Head, Linebreak, List, Metric, Paragraph, Part, PhonContent, Reference, Sentence, String, Table, TextContent, Utterance, Whitespace, Word,)
Note.ANNOTATIONTYPE = AnnotationType.NOTE
Note.XMLTAG = "note"
#------ Original -------
Original.AUTH = False
Original.OCCURRENCES = 1
Original.OPTIONAL_ATTRIBS = None
Original.XMLTAG = "original"
#------ Paragraph -------
Paragraph.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Entry, Event, Example, Feature, Figure, ForeignData, Gap, Head, Linebreak, List, Metric, Note, Part, PhonContent, Quote, Reference, Sentence, String, TextContent, Whitespace, Word,)
Paragraph.ANNOTATIONTYPE = AnnotationType.PARAGRAPH
Paragraph.TEXTDELIMITER = "\n\n"
Paragraph.XMLTAG = "p"
#------ Part -------
Part.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, AbstractStructureElement, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Metric, Part,)
Part.ANNOTATIONTYPE = AnnotationType.PART
Part.TEXTDELIMITER = None
Part.XMLTAG = "part"
#------ PhonContent -------
PhonContent.ACCEPTED_DATA = (Description,)
PhonContent.ANNOTATIONTYPE = AnnotationType.PHON
PhonContent.OCCURRENCES = 0
PhonContent.OPTIONAL_ATTRIBS = (Attrib.CLASS, Attrib.ANNOTATOR, Attrib.CONFIDENCE, Attrib.DATETIME,)
PhonContent.PHONCONTAINER = True
PhonContent.PRINTABLE = False
PhonContent.SPEAKABLE = True
PhonContent.XMLTAG = "ph"
#------ Phoneme -------
Phoneme.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, FunctionFeature, Metric, Part, PhonContent, Phoneme, String, TextContent,)
Phoneme.ANNOTATIONTYPE = AnnotationType.PHONOLOGICAL
Phoneme.TEXTDELIMITER = ""
Phoneme.XMLTAG = "phoneme"
#------ PhonologyLayer -------
PhonologyLayer.ACCEPTED_DATA = (Correction, Description, ForeignData, Phoneme,)
PhonologyLayer.ANNOTATIONTYPE = AnnotationType.PHONOLOGICAL
PhonologyLayer.PRIMARYELEMENT = False
PhonologyLayer.XMLTAG = "phonology"
#------ PosAnnotation -------
PosAnnotation.ACCEPTED_DATA = (Description, Feature, ForeignData, HeadFeature, Metric,)
PosAnnotation.ANNOTATIONTYPE = AnnotationType.POS
PosAnnotation.XMLTAG = "pos"
#------ Quote -------
Quote.ACCEPTED_DATA = (AbstractAnnotationLayer, Alignment, Alternative, AlternativeLayers, Correction, Description, Division, Feature, ForeignData, Gap, Metric, Paragraph, Part, Quote, Sentence, String, TextContent, Utterance, Word,)
Quote.XMLTAG = "quote"
#------ Reference -------
Reference.ACCEPTED_DATA = (AbstractAnnotationLayer, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Metric, Paragraph, Part, PhonContent, Quote, Sentence, String, TextContent, Utterance, Word,)
Reference.TEXTDELIMITER = None
Reference.XMLTAG = "ref"
#------ Row -------
Row.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Cell, Correction, Description, Feature, ForeignData, Metric, Part,)
Row.TEXTDELIMITER = "\n"
Row.XMLTAG = "row"
#------ SemanticRole -------
SemanticRole.ACCEPTED_DATA = (Alignment, Description, Feature, ForeignData, Headspan, Metric, WordReference,)
SemanticRole.ANNOTATIONTYPE = AnnotationType.SEMROLE
SemanticRole.REQUIRED_ATTRIBS = (Attrib.CLASS,)
SemanticRole.XMLTAG = "semrole"
#------ SemanticRolesLayer -------
SemanticRolesLayer.ACCEPTED_DATA = (Correction, Description, ForeignData, SemanticRole,)
SemanticRolesLayer.ANNOTATIONTYPE = AnnotationType.SEMROLE
SemanticRolesLayer.PRIMARYELEMENT = False
SemanticRolesLayer.XMLTAG = "semroles"
#------ SenseAnnotation -------
SenseAnnotation.ACCEPTED_DATA = (Description, Feature, ForeignData, Metric, SynsetFeature,)
SenseAnnotation.ANNOTATIONTYPE = AnnotationType.SENSE
SenseAnnotation.XMLTAG = "sense"
#------ Sentence -------
Sentence.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Entry, Event, Example, Feature, ForeignData, Gap, Linebreak, Metric, Note, Part, PhonContent, Quote, Reference, String, TextContent, Whitespace, Word,)
Sentence.ANNOTATIONTYPE = AnnotationType.SENTENCE
Sentence.TEXTDELIMITER = " "
Sentence.XMLTAG = "s"
#------ Speech -------
Speech.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Division, Entry, Event, Example, External, Feature, ForeignData, Gap, List, Metric, Note, Paragraph, Part, PhonContent, Quote, Reference, Sentence, String, TextContent, Utterance, Word,)
Speech.TEXTDELIMITER = "\n\n\n"
Speech.XMLTAG = "speech"
#------ String -------
String.ACCEPTED_DATA = (AbstractExtendedTokenAnnotation, Alignment, Correction, Description, Feature, ForeignData, Metric, PhonContent, TextContent,)
String.ANNOTATIONTYPE = AnnotationType.STRING
String.OCCURRENCES = 0
String.OPTIONAL_ATTRIBS = (Attrib.ID, Attrib.CLASS, Attrib.ANNOTATOR, Attrib.CONFIDENCE, Attrib.DATETIME, Attrib.N, Attrib.SRC, Attrib.BEGINTIME, Attrib.ENDTIME,)
String.PRINTABLE = True
String.XMLTAG = "str"
#------ StyleFeature -------
StyleFeature.SUBSET = "style"
StyleFeature.XMLTAG = None
#------ SubjectivityAnnotation -------
SubjectivityAnnotation.ANNOTATIONTYPE = AnnotationType.SUBJECTIVITY
SubjectivityAnnotation.XMLTAG = "subjectivity"
#------ Suggestion -------
Suggestion.AUTH = False
Suggestion.OCCURRENCES = 0
Suggestion.XMLTAG = "suggestion"
#------ SynsetFeature -------
SynsetFeature.SUBSET = "synset"
SynsetFeature.XMLTAG = None
#------ SyntacticUnit -------
SyntacticUnit.ACCEPTED_DATA = (Alignment, Description, Feature, ForeignData, Metric, SyntacticUnit, WordReference,)
SyntacticUnit.ANNOTATIONTYPE = AnnotationType.SYNTAX
SyntacticUnit.XMLTAG = "su"
#------ SyntaxLayer -------
SyntaxLayer.ACCEPTED_DATA = (Correction, Description, ForeignData, SyntacticUnit,)
SyntaxLayer.ANNOTATIONTYPE = AnnotationType.SYNTAX
SyntaxLayer.PRIMARYELEMENT = False
SyntaxLayer.XMLTAG = "syntax"
#------ Table -------
Table.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Metric, Part, Row, TableHead,)
Table.ANNOTATIONTYPE = AnnotationType.TABLE
Table.XMLTAG = "table"
#------ TableHead -------
TableHead.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Metric, Part, Row,)
TableHead.XMLTAG = "tablehead"
#------ Term -------
Term.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Event, Feature, Figure, ForeignData, Gap, List, Metric, Paragraph, Part, PhonContent, Reference, Sentence, String, Table, TextContent, Utterance, Word,)
Term.ANNOTATIONTYPE = AnnotationType.TERM
Term.XMLTAG = "term"
#------ Text -------
Text.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Division, Entry, Event, Example, External, Feature, Figure, ForeignData, Gap, List, Metric, Note, Paragraph, Part, PhonContent, Quote, Reference, Sentence, String, Table, TextContent, Word,)
Text.TEXTDELIMITER = "\n\n\n"
Text.XMLTAG = "text"
#------ TextContent -------
TextContent.ACCEPTED_DATA = (AbstractTextMarkup, Description, Linebreak,)
TextContent.ANNOTATIONTYPE = AnnotationType.TEXT
TextContent.OCCURRENCES = 0
TextContent.OPTIONAL_ATTRIBS = (Attrib.CLASS, Attrib.ANNOTATOR, Attrib.CONFIDENCE, Attrib.DATETIME,)
TextContent.PRINTABLE = True
TextContent.SPEAKABLE = False
TextContent.TEXTCONTAINER = True
TextContent.XLINK = True
TextContent.XMLTAG = "t"
#------ TextMarkupCorrection -------
TextMarkupCorrection.ANNOTATIONTYPE = AnnotationType.CORRECTION
TextMarkupCorrection.XMLTAG = "t-correction"
#------ TextMarkupError -------
TextMarkupError.ANNOTATIONTYPE = AnnotationType.ERRORDETECTION
TextMarkupError.XMLTAG = "t-error"
#------ TextMarkupGap -------
TextMarkupGap.ANNOTATIONTYPE = AnnotationType.GAP
TextMarkupGap.XMLTAG = "t-gap"
#------ TextMarkupString -------
TextMarkupString.ANNOTATIONTYPE = AnnotationType.STRING
TextMarkupString.XMLTAG = "t-str"
#------ TextMarkupStyle -------
TextMarkupStyle.ANNOTATIONTYPE = AnnotationType.STYLE
TextMarkupStyle.XMLTAG = "t-style"
#------ TimeFeature -------
TimeFeature.SUBSET = "time"
TimeFeature.XMLTAG = None
#------ TimeSegment -------
TimeSegment.ACCEPTED_DATA = (ActorFeature, Alignment, BegindatetimeFeature, Description, EnddatetimeFeature, Feature, ForeignData, Metric, WordReference,)
TimeSegment.ANNOTATIONTYPE = AnnotationType.TIMESEGMENT
TimeSegment.XMLTAG = "timesegment"
#------ TimingLayer -------
TimingLayer.ACCEPTED_DATA = (Correction, Description, ForeignData, TimeSegment,)
TimingLayer.ANNOTATIONTYPE = AnnotationType.TIMESEGMENT
TimingLayer.PRIMARYELEMENT = False
TimingLayer.XMLTAG = "timing"
#------ Utterance -------
Utterance.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractExtendedTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Gap, Metric, Note, Part, PhonContent, Quote, Reference, Sentence, String, TextContent, Word,)
Utterance.ANNOTATIONTYPE = AnnotationType.UTTERANCE
Utterance.TEXTDELIMITER = " "
Utterance.XMLTAG = "utt"
#------ ValueFeature -------
ValueFeature.SUBSET = "value"
ValueFeature.XMLTAG = None
#------ Whitespace -------
Whitespace.ANNOTATIONTYPE = AnnotationType.WHITESPACE
Whitespace.TEXTDELIMITER = ""
Whitespace.XMLTAG = "whitespace"
#------ Word -------
Word.ACCEPTED_DATA = (AbstractAnnotationLayer, AbstractTokenAnnotation, Alignment, Alternative, AlternativeLayers, Correction, Description, Feature, ForeignData, Metric, Part, PhonContent, Reference, String, TextContent,)
Word.ANNOTATIONTYPE = AnnotationType.TOKEN
Word.TEXTDELIMITER = " "
Word.XMLTAG = "w"
#------ WordReference -------
WordReference.XMLTAG = "wref"

#EOF
