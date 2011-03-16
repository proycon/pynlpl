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
from sys import stderr

class AnnotatorType:
    AUTO = 0
    MANUAL = 1
    

class Attrib:
    ID, CLASS, ANNOTATOR, CONFIDENCE, N = (0,1,2,3,4)

class AnnotationType:
    TOKEN, DIVISION, POS, LEMMA, DOMAIN, SENSE, SYNTAX, CHUNKING, ENTITY = range(9)
     


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
    
    return kwargs
    
        




        
class AbstractElement(object):
    REQUIRED_ATTRIBS = ()
    OPTIONAL_ATTRIBS = ()
    ACCEPTED_DATA = ()
    ANNOTATIONTYPE = None
    
    def __init__(self, doc, *args, **kwargs):
        if not isinstance(doc, Document):
            raise Exception("Expected first parameter to be instance of Document, got " + str(type(doc)))
        self.doc = doc
        self.parent = None
        self.data = []
        
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
            
    def append(self, child):
        if child.__class__ in self.ACCEPTED_DATA:
            self.data.append(child)
            child.parent = self
        else:
            raise ValueError("Unable to append object of type " + child.__class__.__name__)

    def xml(self):        
        return node


class Word(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.CLASS,Attrib.ANNOTATOR,Attrib.CONFIDENCE)
    XMLTAG = 'w'
    ANNOTATIONTYPE = AnnotationType.TOKEN
    
    def __init__(self, doc, *args, **kwargs):
        self.space = True
        if 'text' in kwargs:
            if isinstance(kwargs['text'], unicode):
                self.text = kwargs['text']
            else:
                self.text = unicode(kwargs['text'],'utf-8') #assume utf-8
            del kwargs['text']                        
        elif 'space' in kwargs:            
            self.space = kwargs['space']
            del kwargs['space']
        else:
            self.text = None 
        super(Word,self).__init__(doc, *args, **kwargs)
        
    
    def append(self, child):
        if isinstance(child, AbstractTokenAnnotation) or isinstance(child, Alternative):
            self.data.append(child)
            child.parent = self
        else:
            raise TypeError("Invalid type")
            
    def __unicode__(self):
        return self.text
    


class AbstractTokenAnnotation(AbstractElement): pass
    
class AbstractSpanAnnotation(AbstractElement): pass

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
    XMLTAG = 'alt'

class AlternativeLayers(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    ACCEPTED_DATA = (AbstractAnnotationLayer,)    
    XMLTAG = 'altlayers'
    

class WordReference(object):
    def __init__(self, id):
        self.id = id
        self.parent = None
        self.resolved = None

    def __call__():
        if self.resolved:
            return self.resolved
        else:
            #backtrack to sentence element
            s = self.parent
            while s != None and not isinstance(p, Sentence):
                s = s.parent
            if s:
                #forward-track to find word element
                for w in s:
                    if isinstance(w, Word):
                        if w.id == self.id:
                            self.resolved = w
                            return self.resolved                        
                raise Exception("Unable to resolve word reference, no such word found")
            else:
                raise Exception("Unable to resolve word reference, parent sentence not found")
                
                


        
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
    

class Quote(AbstractElement):
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
        
        
class Sentence(AbstractElement):
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
            if instance(e, Word):
                s += unicode(e)
                if e.space:
                    s += ' '
        if not s and self.text:
            return self.text            
        return s
                

Quote.ACCEPTED_DATA = (Word, Sentence, Quote)        

class Paragraph(AbstractElement):    
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Sentence,)
    XMLTAG = 'p'
    
    def __init__(self, doc, *args, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']
            del kwargs['text']
        else:
            self.text = None 
        super(Paragraph,self).__init__(doc, *args, **kwargs)    
        
    def __unicode__(self):
        p = u" ".join( ( unicode(x) for x in self.data if isinstance(x, Sentence) ) )
        if not p and self.text:
            return self.text            
        return p
                
                
class Head(AbstractElement):
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
    
    def __init__(self, *args, **kwargs):
        self.data = [] #will hold all texts (usually only one)
        
        self.annotationdefaults = {}
        self.annotations = [] #Ordered list of incorporated annotations ['token','pos', etc..]
    
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            self.debug = False
    
        if 'id' in kwargs:
            self.id = kwargs['id']
        elif 'file' in kwargs:
            self.filename = kwargs['file']
            self.load(self.filename)              
        else:
            raise Exception("No ID or filename specified")
                
            
    def load(self, filename):
        f = open(filename,'r')
        self.parsexml(ElementTree.XML(f.read()))
        f.close()        
        
        
    def save(self, filename):
        raise NotImplementedError  #TODO

    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        for text in self.data:
            yield text   
        
            
    def xml(self):    
        raise NotImplementedError #TODO
        
     
    def parsexmldeclarations(self, node):
        if self.debug >= 1: 
            print >>stderr, "[PyNLPl FoLiA DEBUG] Processing Annotation Declarations"
        for subnode in node:
            if subnode.tag[-11:] == '-annotation':
                prefix = subnode.tag[:-11]
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
            

    def parsexml(self, node):
        global XML2CLASS
        if not isinstance(node,ElementTree._Element):
            node = ElementTree.parse(StringIO(node)).getroot()         
        if node.tag == 'FoLiA':
            if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found FoLiA document"
            try:
                self.id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
            except KeyError:
                raise Exception("FoLiA Document has no ID!")
            for subnode in node:
                if subnode.tag == 'metadata':
                    if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found Metadata"
                    for subsubnode in subnode:
                        if subsubnode.tag == 'annotations':
                            self.parsexmldeclarations(subsubnode)
                elif subnode.tag == 'text':
                    if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found Text"
                    self.data.append( self.parsexml(subnode) )
        elif node.tag in XML2CLASS:
            #generic parsing
            Class = XML2CLASS[node.tag]    
            args = []
            text = None
            for subnode in node:
                if subnode.tag == 't':
                    text = subnode.text
                else:
                    if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found " + subnode.tag
                    args.append( self.parsexml(subnode) )
            kwargs = {}
            for key, value in node.attrib.items():
                if key == '{http://www.w3.org/XML/1998/namespace}id':
                    key = 'id'
                kwargs[key] = value
                                        
            if node.text and node.text.strip():
                kwargs['value'] = node.text
            if text:
                kwargs['text'] = text
            #if self.debug >= 1: print >>stderr, "[PyNLPl FoLiA DEBUG] Found " + node.tag
            return Class(self, *args, **kwargs)
        else:
            raise Exception("Unknown FoLiA XML tag: " + node.tag)
        
        
            
    

    
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
        raise NotImplementedError #on purpose!
        
    def _len__(self):
        raise NotImplementedError #on purpose!

        
   


        


            

    
class ListItem(AbstractElement):
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    #ACCEPTED_DATA = (List, Sentence) #Defined below
    XMLTAG = 'listitem'
    
    def __init__(self, doc, *args, **kwargs):
        self.data = []
        super( ListItem, self).__init__(doc, *args, **kwargs)
    
class List(AbstractElement):    
    OPTIONAL_ATTRIBS = (Attrib.ID,Attrib.N)
    ACCEPTED_DATA = (ListItem,)
    XMLTAG = 'list'
    
    def __init__(self, doc, *args, **kwargs):
        self.data = []
        super( List, self).__init__(doc, *args, **kwargs)

ListItem.ACCEPTED_DATA = (List, Sentence)


class Figure(AbstractElement):    
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
        

class Division(AbstractElement):    
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

Division.ACCEPTED_DATA = (Division, Paragraph, Sentence, List, Figure)

class Text(AbstractElement):
    REQUIRED_ATTRIBS = (Attrib.ID,)
    OPTIONAL_ATTRIBS = (Attrib.N,)
    ACCEPTED_DATA = (Division, Paragraph, Sentence, List, Figure)
    XMLTAG = 'text' 



XML2CLASS = {}
for c in vars().values():
    try:
        XML2CLASS[c.XMLTAG] = c
    except AttributeError: 
        continue
