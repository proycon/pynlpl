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

class AnnotatorType:
    AUTO = 0
    MANUAL = 1
    

class Attrib:
    ID, CLASS, ANNOTATOR, CONFIDENCE, N = (0,1,2,3,4)

class AnnotationType:
    TOKEN, DIVISION, POS, LEMMA, DOMAIN, SENSE, SYNTAX, CHUNKING, ENTITY, CORRECTION, ALTERNATIVE = range(11)
    
    #Alternative is a special one, not declared and not used except for ID generation
          
class MetaDataType:
    NATIVE, CMDI, IMDI = range(3)     


def parsecommonarguments(object, doc, annotationtype, required, allowed, **kwargs):
    object.doc = doc #The FoLiA root document
    supported = required + allowed
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
        object.set = doc.annotationdefaults[annotationtype]['annotator']
    elif Attrib.ANNOTATOR in required:
        raise ValueError("Annotator is required for " + object.__class__.__name__)
    else:
        object.annotator = None        
    
        
    if 'annotatortype' in kwargs:
        if not Attrib.ANNOTATOR in supported:
            raise ValueError("Annotatortype is not supported for " + object.__class__.__name__)
        if kwargs['annotatortype'] == 'auto':
            object.annotatortype = AnnotatorType.AUTO
        elif kwargs['annotatortype'] == 'manual':
            object.annotatortype = AnnotatorType.MANUAL
        else:
            raise ValueError("annotatortype must be 'auto' or 'manual'")                
        del kwargs['annotatortype']
    elif annotationtype in doc.annotationdefaults and 'annotator' in doc.annotationdefaults[annotationtype]:
        object.set = doc.annotationdefaults[annotationtype]['annotatortype']            
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
    
    if object.doc and object.id:
        object.doc.index[object.id] = object
    
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
            if 'text' in kwargs:
                self.text = kwargs['text']
                del kwargs['text']
            else:
                self.text = None 
        
        kwargs = parsecommonarguments(self, doc, self.ANNOTATIONTYPE, self.REQUIRED_ATTRIBS, self.OPTIONAL_ATTRIBS,**kwargs)
        for child in args:
            self.append(child)
        for key in kwargs:
            raise ValueError("Parameter '" + key + "' not supported by " + self.__class__.__name__)        
        
    def __eq__(self, other):
        return self.id == other.id

    def __len__(self):
        return len(self.data)
        
    def __iter__(self):
        """Iterate over children"""
        for child in self.data:
            yield child

    def __contains__(self, child):
        return child in self.data
            
    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise

    def __unicode__(self):
        if self.ALLOWTEXT:
            return self.text
        else:
            raise NotImplementedError #on purpose
    
    def __str__(self):
        if self.ALLOWTEXT:
            return unicode(self).encode('utf-8')
        else:
            raise NotImplementedError #on purpose    
        
            
    def append(self, child):
        if child.__class__ in self.ACCEPTED_DATA or child.__base__ in self.ACCEPTED_DATA:
            self.data.append(child)
            child.parent = self
        else:
            raise ValueError("Unable to append object of type " + child.__class__.__name__)

    def xml(self, attribs = None,elements = None, skipchildren = False):  
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        
        if not attribs: attribs = {}
        if not elements: elements = []
        
        if self.id:
            attribs['{http://www.w3.org/XML/1998/namespace}id'] = self.id
            
        #Some attributes only need to be added if they are not the same as what's already set in the declaration    
        try:
            if self.set and (not 'set' in self.doc.annotationdefaults or self.set != self.doc.annotationdefaults['set']):
                attribs['set'] = self.set
        except AttributeError:
            pass
        try:
            if self.cls:
                attribs['{http://ilk.uvt.nl/folia}class'] = self.cls
        except AttributeError:
            pass            
        try:            
            if self.annotator and (not 'annotator' in self.doc.annotationdefaults or self.annotator != self.doc.annotationdefaults['annotator']):
                attribs['{http://ilk.uvt.nl/folia}annotator'] = self.annotator
            if self.annotatortype and (not 'annotatortype' in self.doc.annotationdefaults or self.annotatortype != self.doc.annotationdefaults['annotatortype']):
                if self.annotatortype == AnnotatorType.AUTO:
                    attribs['{http://ilk.uvt.nl/folia}annotatortype'] = 'auto'
                elif self.annotatortype == AnnotatorType.MANUAL:
                    attribs['{http://ilk.uvt.nl/folia}annotatortype'] = 'manual'
        except AttributeError:
            pass       
        try:
            if self.confidence:
                attribs['{http://ilk.uvt.nl/folia}confidence'] = str(self.confidence)
        except AttributeError:
            pass
        try:
            if self.n:
                attribs['{http://ilk.uvt.nl/folia}n'] = str(self.n)
        except AttributeError:
            pass
            
        e  = E._makeelement('{http://ilk.uvt.nl/folia}' + self.XMLTAG, **attribs)        
        
        try:
            if self.ALLOWTEXT and self.text:
                e.append( E.t(self.text) )
        except AttributeError:
            pass                
            
        #append children:
        if not skipchildren:
            for child in self:
                e.append(child.xml())
        if elements:
            for e2 in elements:
                e.append(e2)
        return e
        
        
        
    def select(self, cls, recursive=True, node=None):
        if not node:
            node = self
        for e in self:
            if isinstance(e, cls):
                yield e
            elif recursive:
                for e2 in e.select(cls, recursive, e):
                    yield e2                
    
    @classmethod
    def relaxng(cls, includechildren=True,extraattribs = None, extraelements=None):
            
            
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
               attribs.append(  E.attribute(E.data(type='double',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'), name='confidence') )
            elif Attrib.CONFIDENCE in cls.OPTIONAL_ATTRIBS:
               attribs.append(  E.optional( E.attribute(E.data(type='double',datatypeLibrary='http://www.w3.org/2001/XMLSchema-datatypes'), name='confidence') ) )
            if Attrib.N in cls.REQUIRED_ATTRIBS:
               attribs.append( E.optional( E.attribute( name='n' ) ) )
            elif Attrib.N in cls.OPTIONAL_ATTRIBS:
               attribs.append( E.optional( E.attribute( name='n' ) ) )
            
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
                            elements.append( E.ref(name=c.XMLTAG) )
                    except AttributeError:
                        continue
                        
            if extraelements:
                    for e in extraelements:
                        elements.append(e)                                                            

            return E.define(
                E.element( E.group( *attribs ) , E.zeroOrMore(*elements), name=cls.XMLTAG),
            name=cls.XMLTAG)
            
            
    def resolveword(self, id):
        return None
        
    def remove(self, child):
        self.data.remove(child)
            
class AbstractStructureElement(AbstractElement):
    def __init__(self, doc, *args, **kwargs):    
        self.maxid = {}
        super(AbstractStructureElement,self).__init__(doc, *args, **kwargs)
    
    def resolveword(self, id): 
        for child in self:
            r =  child.resolveword(id)            
            if r:
                return r
        return None          
        
        
    def _setmaxid(self, child):
        try:
            if child.id and child.XMLTAG:
                fields = child.id.split(self.doc.IDSEPARATOR)
                if len(fields) > 1 and fields[-1].isdigit():
                    if not child.XMLTAG in self.maxid:
                        self.maxid[child.XMLTAG] = int(fields[-1])
                    else:
                        if self.maxid[child.XMLTAG] < int(fields[-1]):
                           self.maxid[child.XMLTAG] = int(fields[-1]) 
        except AttributeError:
            pass        

                 
    def append(self, child):
        super(AbstractStructureElement,self).append(child)
        self._setmaxid(child)  
                
    def generate_id(self, cls):
        if isinstance(cls,str):
            xmltag = cls
        else:
            try:
                xmltag = cls.XMLTAG
            except:
                raise Exception("Expected a class such as Alternative, Correction, etc...")
        
        if xmltag in self.maxid:
            return self.parent.id + '.' + xmltag + '.' + str(self.maxid[xmltag] + 1)
        else:
            return self.parent.id + '.' + xmltag + '.1'
        

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
        if isinstance(child, AbstractTokenAnnotation) or isinstance(child, Alternative):
            self.data.append(child)
            child.parent = self
            self._setmaxid(child)
        else:
            raise TypeError("Invalid type")

    def annotations(self, annotationtype=None):
        for e in self:
            try:
                if annotationtype is None or e.ANNOTATIONTYPE == annotationtype:
                    yield e
            except AttributeError:
                continue
            

    def pos(self):
        for e in self.select(PosAnnotation):
            yield e
            
    def lemma(self):
        for e in self.select(LemmaAnnotation):
            yield e            

    def sense(self):
        for e in self.select(SenseAnnotation):
            yield e            

    def alternatives(self):
        for e in self.select(Alternative):
            yield e            

    def resolveword(self, id):
        if id == self.id:
            return self
        else:
            return None
            
    def correct(self, original, new, **kwargs):
        if not original in self:
            kwargs['original'] = original
            raise Exception("Original not found!")
        kwargs['new'] = new
        if not 'id' in kwargs:
            #TODO: calculate new ID
            pass
        self.remove(original)
        c = Correction(**kwargs)
        self.append( c )
        return c 
        


            

class AbstractTokenAnnotation(AbstractElement): pass
    
class AbstractSpanAnnotation(AbstractElement): 
    def xml(self, attribs = None,elements = None, skipchildren = False):  
        if not attribs: attribs = {}
        if Word in self.ACCEPTED_DATA:
            E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
            e = super(AbstractSpanAnnotation,self).__init__(attribs, elements, True)
            for child in self:
                if isinstance(child, Word):
                    #Include REFERENCES to word items instead of word items themselves
                    attribs['{http://www.w3.org/XML/1998/namespace}id'] = child.id
                    e.append( E.wref(**attribs) )
                else:
                    e.append( child.xml() )
            return e    
        else:
            return super(AbstractSpanAnnotation,self).__init__(attribs, elements, skipchildren)    

    def append(self, child):
        if isinstance(child, Word) and WordReference in self.ACCEPTED_DATA:
            #Accept Word instances instead of WordReference, references will be automagically used upon serialisation
            self.data.append(child)
            child.parent = self
        else:
            return super(AbstractSpanAnnotation,self).append(child)    


            

class AbstractAnnotationLayer(AbstractElement):
    OPTIONAL_ATTRIBS = (Attrib.CLASS,)
    def __init__(self, doc, *args, **kwargs):
        if 'set' in kwargs:
            self.set = kwargs['set']
            del kwargs['set']
        super(AbstractAnnotationLayer,self).__init__(doc, *args, **kwargs)

            
class Alternative(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (AbstractTokenAnnotation,)
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
        
class SyntacticUnit(AbstractSpanAnnotation):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.SYNTAX
    XMLTAG = 'su'
    
SyntacticUnit.ACCEPTED_DATA = (SyntacticUnit,WordReference)

class Chunk(AbstractSpanAnnotation):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ACCEPTED_DATA = (WordReference,)
    ANNOTATIONTYPE = AnnotationType.CHUNKING
    XMLTAG = 'chunk'

class Entity(AbstractSpanAnnotation):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
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


class PosFeature(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.CLASS)
    #TODO: Inherit set from parent
    
class PosAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.POS
    ACCEPTED_DATA = (PosFeature,)
    XMLTAG = 'pos'

class LemmaAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.LEMMA
    XMLTAG = 'lemma'


class DomainAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.DOMAIN
    XMLTAG = 'domain'


class SenseAnnotation(AbstractTokenAnnotation):
    REQUIRED_ATTRIBS = (Attrib.CLASS,)
    OPTIONAL_ATTRIBS = (Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.SENSE
    XMLTAG = 'sense'
    
class Correction(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    ANNOTATIONTYPE = AnnotationType.CORRECTION
    XMLTAG = 'correction'

    def __init__(self,  doc, *args, **kwargs):
        if 'new' in kwargs:
            self.new = kwargs['new']
            del kwargs['new'] 
        else:
            raise Exception("No new= argument specified!")
        if 'original' in kwargs:
            self.original = kwargs['original']
            del kwargs['original'] 
        else:
            raise Exception("No original= argument specified!") 
        if self.new.__class__ != self.original.__class__:
            raise Exception("New and Original are of different types!")             
        super(Correction,self).__init__(doc, *args, **kwargs)

    def xml(self, attribs = None, elements = None, skipchildren = False):
        if not attribs: attribs = {}
        if not elements: elements = []
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})

        if not isinstance(self.new, list) and not isinstance(self.original, list):
            elements.append( E.new( self.new.xml() ), E.original( self.original.xml() ) )
        elif isinstance(self.new, list):
            elements.append( E.new( *[ x.xml() for x in self.new ] ), E.original( self.original.xml() ) )
        elif isinstance(self.original, list):
            elements.append( E.new( self.new.xml() ), E.original( *[ x.xml() for x in self.original ] ) )
        elif (isinstance(self.original, str) or isinstance(self.original, unicode)) and (isinstance(self.original, str) or isinstance(self.original, unicode)):
            elements.append( E.new( E.t( self.original) ), E.original( E.t( self.new )) )

        return super(Correction,self).xml(attribs,elements, True)  


class Quote(AbstractStructureElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = ()    
    XMLTAG = 'quote'
    #ACCEPTED DATA defined later below
    
    def __init__(self,  doc, *args, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']
            del kwargs['text'] 
        else:
            self.text = None 
        super(Sentence,self).__init__(doc, *args, **kwargs)

    def __unicode__(self):
        s = u""
        for e in self.data:
            if instance(e, Word):
                s += unicode(e)
                if e.space:
                    s += ' '
            elif instance(e, Sentence):
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
    ACCEPTED_DATA = (Word, Quote, AbstractAnnotationLayer)
    XMLTAG = 's'
    
    def __init__(self,  doc, *args, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']
            del kwargs['text'] 
        else:
            self.text = None 
        super(Sentence,self).__init__(doc, *args, **kwargs)

    def __unicode__(self):
        s = u""
        for e in self.data:
            if isinstance(e, Word):
                s += unicode(e)
                if e.space:
                    s += ' '
        if not s and self.text:
            return self.text            
        return s
                
    def resolveword(self, id):
        for child in self:
            r =  child.resolveword(id)            
            if r:
                return r
        return None
        
    def splitword(self, originalword, newwords, **kwargs):
        if isinstance(originalword, str) or isinstance(originalword, unicode):
            originalword = self.doc[originalword]            
        if not originalword in self or not isinstance(originalword, Word):
            raise Exception("Original not found or not instance of Word!")
        else:
            kwargs['original'] = originalword
            
        if not isinstance(newwords, list) or not all( [ isinstance(w, Word) for w in newwords ] ):
            raise Exception("Second argument, new words, must be a list of Word instances!")
            
        kwargs['new'] = newwords
        if not 'id' in kwargs:
            #TODO: calculate new ID
            raise NotImplementerError()
        insertindex = self.data.index(originalword)        
        c = Correction(self.doc, **kwargs)
        self.insert( insertindex , c)
        self.remove(originalword)
        c.parent = self
        return c 
        
    def deleteword(self, word, **kwargs):
        if isinstance(word, str) or isinstance(word, unicode):
            word = self.doc[word]            
        if not word in self or not isinstance(originalword, Word):
            raise Exception("Original not found or not instance of Word!")
        else:
            kwargs['original'] = word
            
        kwargs['new'] = []
        if not 'id' in kwargs:
            #TODO: calculate new ID
            raise NotImplementerError()
        insertindex = self.data.index(originalword)        
        c = Correction(self.doc, **kwargs)
        self.insert( insertindex , c)
        self.remove(originalword)
        c.parent = self
        return c 
        
    def insertword(self, prevword, newword, **kwargs):
        if isinstance(prevword, str) or isinstance(prevword, unicode):
            prevword = self.doc[prevword]            
        if not prevword in self or not isinstance(prevword, Word):
            raise Exception("Previous word not found or not instance of Word!")
        if not newword in self or not isinstance(newword, Word):
            raise Exception("New word no instance of Word!")
        
        insertindex = self.data.index(prevword)
    
        kwargs['original'] = []
        kwargs['new'] = newword
        
        if not 'id' in kwargs:
            #TODO: calculate new ID
            raise NotImplementerError()
        c = Correction(self.doc, **kwargs)
        self.data.insert( insertindex, c )
        c.parent = self
        return c 
        
    def mergewords(self, originalwords, newword, **kwargs):
        #TODO!
        for w in originalwords:            
            if not isinstance(w, Word) or not w in self:
                raise Exception("Original word not found or not a Word instance!")    
        kwargs['original'] = originalwords                
        
        if not isinstance(newword, Word):        
            raise Exception("New word must be a Word instance")
        kwargs['new'] = newword
        if not 'id' in kwargs:
            #TODO: calculate new ID
            raise NotImplementerError()        
        
        
        insertindex = self.data.index(originalword)        
        c = Correction(self.doc, **kwargs)
        self.insert( insertindex, c )
        c.parent = self
        self.remove(original)        
        return c 
        

Quote.ACCEPTED_DATA = (Word, Sentence, Quote)        

class Paragraph(AbstractStructureElement):    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Sentence,)
    XMLTAG = 'p'
    ALLOWTEXT = True
    
     
        
    def __unicode__(self):
        p = u" ".join( ( unicode(x) for x in self.data if isinstance(x, Sentence) ) )
        if not p and self.text:
            return self.text            
        return p
                              
                
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
        else:
            raise Exception("No ID or filename specified")
                            
            
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
        f.write(str(self))
        f.close()
        
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


    def xmldeclarations(self):
        l = []
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        for annotationtype in self.annotations:
            label = None
            for key, value in vars(AnnotationType).items():
                if value == annotationtype:
                    label = key
                    break
            attribs = {}
            for key, value in self.annotationdefaults[annotationtype].items():                
                if value:
                    attribs['{http://ilk.uvt.nl/folia}' + key] = value
            if label:
                l.append( E._makeelement('{http://ilk.uvt.nl/folia}' + label.lower() + '-annotation', **attribs) )
            else:
                raise Exception("Invalid annotation type")            
        return l
        
    def xml(self):    
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        attribs = {}
        attribs['{http://www.w3.org/XML/1998/namespace}id'] = self.id
        e = E.FoLiA(
            E.metadata(
                E.annotations(
                    *self.xmldeclarations()
                ),
                self.xmlmetadata()
            )            
        , **attribs)
        for text in self.data:
            e.append(text.xml())
        return e
    
    def xmlmetadata(self):
        E = ElementMaker(namespace="http://ilk.uvt.nl/folia",nsmap={None: "http://ilk.uvt.nl/folia", 'xml' : "http://www.w3.org/XML/1998/namespace"})
        if self.metadatatype == MetaDataType.NATIVE:
            e = E.simple()
            if self.title(): e.append(E.meta(self.title(),id='title') )
            if self.date(): e.append(E.meta(self.date(),id='date') )
            if self.language(): e.append(E.meta(self.language(),id='language') )
            if self.license(): e.append(E.meta(self.license(),id='license') )    
            if self.publisher(): e.append(E.meta(self.publisher(),id='publisher') )
            return e
        else:
            return self.metadata
            
     
    def parsexmldeclarations(self, node):
        if self.debug >= 1: 
            print >>stderr, "[PyNLPl FoLiA DEBUG] Processing Annotation Declarations"
        for subnode in node:
            if subnode.tag[:25] == '{http://ilk.uvt.nl/folia}' and subnode.tag[-11:] == '-annotation':
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

    def parseimdi(self, node):
        ns = {'imdi': 'http://www.mpi.nl/IMDI/Schema/IMDI'}
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
            
    def parsecmdi(self, node):
        #TODO
        self.metadata = node            

    def parsexml(self, node):
        global XML2CLASS
        if not isinstance(node,ElementTree._Element):
            node = ElementTree.parse(StringIO(node)).getroot()         
        if node.tag == '{http://ilk.uvt.nl/folia}FoLiA':
            if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found FoLiA document"
            try:
                self.id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
            except KeyError:
                raise Exception("FoLiA Document has no ID!")
            for subnode in node:
                if subnode.tag == '{http://ilk.uvt.nl/folia}metadata':
                    if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found Metadata"
                    for subsubnode in subnode:
                        if subsubnode.tag == '{http://www.mpi.nl/IMDI/Schema/IMDI}METATRANSCRIPT':
                            self.metadatatype = MetaDataType.IMDI
                            self.parseimdi(subsubnode)
                        if subsubnode.tag == '{http://ilk.uvt.nl/folia}annotations':
                            self.parsexmldeclarations(subsubnode)
                elif subnode.tag == '{http://ilk.uvt.nl/folia}text' and self.loadall:
                    if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found Text"
                    self.data.append( self.parsexml(subnode) )
        elif node.tag[:25] == '{http://ilk.uvt.nl/folia}' and node.tag[25:] in XML2CLASS:
            #generic parsing
            if node.tag[25:] == 'wref':
                #special handling for word references
                id = node.attribs['{http://www.w3.org/XML/1998/namespace}id']
                try:
                    return self[id]
                except KeyError:
                    return WordReference(id=id)                
            else:
                #generic handling
                Class = XML2CLASS[node.tag[25:]]    
                args = []
                kwargs = {}
                text = None
                if node.tag == '{http://ilk.uvt.nl/folia}correction':
                    kwargs['original'] == {}
                    kwargs['new'] == {}
                for subnode in node:
                    if subnode.tag == '{http://ilk.uvt.nl/folia}t':
                        text = subnode.text
                    elif node.tag == '{http://ilk.uvt.nl/folia}correction' and subnode.tag == '{http://ilk.uvt.nl/folia}original':                        
                        if len(subnode) == 1:
                            if subnode[0].tag == '{http://ilk.uvt.nl/folia}t':
                                kwargs['original'] = subnode[0].text
                            else:
                                kwargs['original'] = self.parsexml(subnode[0])
                        else:
                            kwargs['original'] = [ self.parsexml(x) for x in subnode ] 
                    elif node.tag == '{http://ilk.uvt.nl/folia}correction' and subnode.tag == '{http://ilk.uvt.nl/folia}new':
                        if len(subnode) == 1:
                            if subnode[0].tag == '{http://ilk.uvt.nl/folia}t':
                                kwargs['new'] = subnode[0].text
                            else:
                                kwargs['new'] = self.parsexml(subnode[0])
                        else:
                            kwargs['new'] = [ self.parsexml(x) for x in subnode ] 
                    elif subnode.tag[:25] == '{http://ilk.uvt.nl/folia}':
                        if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found " + subnode.tag[25:]
                        args.append( self.parsexml(subnode) )
                
                id = None
                for key, value in node.attrib.items():
                    if key == '{http://www.w3.org/XML/1998/namespace}id':
                        id = value
                        key = 'id'
                    elif key[:25] == '{http://ilk.uvt.nl/folia}':
                        key = key[25:]
                    kwargs[key] = value
                                            
                if node.text and node.text.strip():
                    kwargs['value'] = node.text
                if text:
                    kwargs['text'] = text
                                        
                #if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found " + node.tag
                instance = Class(self, *args, **kwargs)
                if id:
                    self.index[value] = instance
                return instance
        else:
            raise Exception("Unknown FoLiA XML tag: " + node.tag)
        
        
    def paragraphs(self):
        for text in self.data:            
            for e in text.select(Paragraph):
                yield e
    
    def sentences(self):
        for text in self.data:            
            for e in text.select(Sentence):
                yield e
        
    def words(self):
        for text in self.data:            
            for e in text.select(Word):
                yield e
                
    
    def __str__(self):
        return ElementTree.tostring(self.xml(), pretty_print=True, encoding='utf-8')
        
    
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
        super(Division,self).__init__(doc, *args, **kwargs)
        
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
            self.head = kwargs['head']
            del kwargs['head']
        else:
            self.head = None
        self.data = []
        super(Division, self).__init__(doc, *args, **kwargs)
        
    def append(self, element):        
        if isinstance(element, Head):
            self.head = element #There can be only one
            element.parent = self
        else:
            super(Division,self).append(element)
            
    def paragraphs(self):            
        return self.select(Paragraph)
    
    def sentences(self):
        return self.select(Sentence)
        
    def words(self):
        return self.select(Word)            

Division.ACCEPTED_DATA = (Division, Paragraph, Sentence, List, Figure)

class Text(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Division, Paragraph, Sentence, List, Figure)
    XMLTAG = 'text' 
        
    def paragraphs(self):            
        return self.select(Paragraph)
    
    def sentences(self):
        return self.select(Sentence)
        
    def words(self):
        return self.select(Word)
        
            
def relaxng():
    grammar = E.grammar( E.start ( E.element( #FoLiA
                E.element( #metadata
                    E.element(name='annotations'),
                    #TODO: ADD IMDI
                    name='metadata'
                ),
                E.oneOrMore(
                    E.ref(name='text'),
                ),
                name='FoLiA'
            ) ) )
    
    for c in globals().values():
        if 'relaxng' in dir(c):
            if c.relaxng and c.XMLTAG:
                grammar.append( c.relaxng() )
        
    return grammar




def validate(filename):
    try:
        doc = ElementTree.parse(filename)
    except:
        raise Exception("Not well-formed XML!")
    grammar = ElementTree.RelaxNG(relaxng())
    grammar.assertValid(doc) #will raise exceptions


XML2CLASS = {}
for c in vars().values():
    try:
        if c.XMLTAG:
            XML2CLASS[c.XMLTAG] = c
    except: 
        continue

