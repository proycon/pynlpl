
FoLiA library 
*************

This tutorial will introduce the FoLiA Python library, part of PyNLPl. The FoLiA library provides an Application Programming Interface for the reading, creation and manipulation of FoLiA XML documents. The library works under Python 2.6, 2.7, as well as Python 3. The samples in this documentation follow Python 2.x conventions.

Prior to reading this document, it is highly recommended to first read the FoLiA documentation itself and familiarise yourself with the format and underlying paradigm. The FoLiA documentation can be found through http://proycon.github.com/folia . It is especially important to understand the way FoLiA handles sets/classes, declarations, common attributes such as annotator/annotatortype and the distinction between various kinds of annotation categories such as token annotation and span annotation.


Reading FoLiA
===================

Loading a document
-------------------------------

Any script that uses FoLiA starts with the import::

    from pynlpl.formats import folia

Subsequently, a document can be read from file and follows::

    doc = folia.Document(file="/path/to/document.xml")

This returns an instance that holds the entire document in memory. Note that for large
FoLiA documents this may consume quite some memory!

Once you have loaded a document, all data is available for you to read and manipulate as you see fit. We will first illustrate some simple use cases:


Printing text
----------------------------------

You may want to simply print all (plain) text contained in the document, which is as easy as::

    print doc
    
Alternatively, you can obtain a string representation of all text::

    text_u = unicode(doc) #unicode instance
    text = str(doc) #UTF-8 encoded string

For any subelement of the document, you can obtain its text in the same fashion. In Python 3, ``str()`` returns a ``str``, which by definition is a unicode instance,  the ``unicode()`` method is not available there.

Index
----------------------------------

A document instance has an index which you can use to grab any of its sub elements by ID. Querying using the index proceeds similar to using a python dictionary::

    word = doc['example.p.3.s.5.w.1']
    print word
    
    
Obtaining list of elements
------------------------------

Usually you do not know in advance the ID of the element you want, or you want multiple elements. There are some methods of iterating over certain elements using the FoLiA library.

For example, you can iterate over all words::

    for word in doc.words():
        print word
        
That however gives you one big iteration of words without boundaries. You may more likely seek word within sentences. So we first iterate over all sentences, then over the words therein::


    for sentence in doc.sentences():
        for word in sentence.words():
            print word
            
Or including paragraphs, assuming the document has them::

    for paragraph in doc.paragraphs():
        for sentence in paragraph.sentences():
            for word in sentence.words():
                print word
        
You can also use this method to obtain a specific word, by passing an index parameter::

        word = sentence.words(3) #retrieves the fourth word
                    
If you want to iterate over all of the child elements of a certain element, regardless of what type they are, you can simply do so as follows::

    for element in doc:
        if isinstance(element, folia.Sentence):
            print "this is a sentence"
        else: 
            print "this is something else"

If applied recursively this allows you in principle to traverse the entire element tree.

Select method
----------------------

There is a generic method available on all elements to select child elements of any desired class. This method is by default applied recursively. Internally, the paragraphs(), words() and sentences() methods seen above are simply shortcuts that make use of the select method::

    sentence = doc['example.p.3.s.5.w.1']
    words = sentence.select(folia.Word)
    for word in words:
        print word
        
Note that the select method is by default recursive, set the third argument to False to make it non-recursive. The second argument can be used for restricting matches to a specific set.

Common attributes
3-----------------------


As you know, the FoLiA paradigm introduces *sets*, *classes*, *annotator* with *annotator types* and *confidence* values. These attributes are easily accessible on any element that has them:
    
    * ``element.id``        (string)
    * ``element.set``       (string)
    * ``element.cls``       (string) Since class is already a reserved keyword in python, the library consistently uses ``cls``
    * ``element.annotator`` (string)
    * ``element.annotatortype`` (set to folia.AnnotatorType.MANUAL or  folia.AnnotatorType.AUTO)
    * ``element.confidence`` (float)
    
Attributes that are not available for certain elements, or not set, default to None.


Annotations
--------------------

FoLiA is of course a format for linguistic annotation. So let's see at how to obtain annotations. This can be done using ``annotations()`` or ``annotation()``, which is very similar to the ``select()`` method, except that it will raise an exception when no such annotation is found. The difference between ``annotation()`` and ``annotations()`` is that the former will grab only one and raise an exception if there are more between which it can't disambiguate::

    for word in doc.words():
        try:
            pos = word.annotation(folia.PosAnnotation, 'CGN')
            lemma = word.annotation(folia.LemmaAnnotation)
            print "Word: ", word
            print "ID: ", word.id
            print "PoS-tag: " , pos.cls
            print "PoS Annotator: ", pos.annotator
            print "Lemma-tag: " , lemma.cls
        except folia.NoSuchAnnotation:
            print "No PoS or Lemma annotation"

Note that the second argument of ``annotation()``, ``annotations()`` or ``select()`` can be used to restrict your selection to a certain set. In the above example we restrict ourselves to Part-of-Speech tags in the CGN set.

Span Annotation
+++++++++++++++++++

We will discuss three ways of accessing span annotation. Span annotation is contained within an annotation layer of a certain structure element, often a sentence. In the first way of accessing span annotation, we will first obtain the layer, then iterate over the span annotation elements within that layer, and finally iterate over the words to which the span applies. Assume we have a ``sentence`` and we want to print all the named entities in it::


    for layer in sentence.select(folia.EntitiesLayer):
        for entity in layer.select(folia.Entity):
            print " Entity class=", entity.cls, " words="
            for word in entity.wrefs():
                print word,  #print without newline
            print   #print newline

The ``wrefs()`` method, available on all span annotation elements, will return a list of all words (as well as morphemes and phonemes) over which a span annotation element spans.

The second way of accessing span annotation takes another approach, using the ``findspans()`` method on Word instances. Here we start from a word and seek span annotations in which the word occurs. Assume we have a ``word`` and want to find chunks it occurs in::

    for chunk in word.findspans(folia.ChunkingLayer):
        print " Chunk class=", chunk.cls, " words="
        for word2 in chunk.wrefs(): #print all words in the chunk (of which the word is a part)
            print word2,
        print

The third way allows us to look for span elements given an annotation layer and words. In other words, it checks if one or more words form a span. This is an exact match and not a sub-part match as in the previously described method. To do this, we use use the ``findspan()`` method on annotation layers::

    for span in annotationlayer.findspan(word1,word2):
        print span.cls


Editing FoLiA
======================

Creating a new document
-------------------------

Creating a new FoliA document, rather than loading an existing one from file, can be done by explicitly providing an ID for the new document in the constructor::

    doc = folia.Document(id='example')
    

Declarations
---------------------

Whenever you add a new type of annotation, or a different set, to a FoLiA document, you have to
first declare it. This is done using the ``declare()`` method. It takes as
arguments the annotation type, the set, and you can optionally pass keyword
arguments to ``annotator=`` and ``annotatortype=`` to set defaults.

An example for Part-of-Speech annotation::

    doc.declare(folia.PosAnnotation, 'brown-tag-set')

An example with a default annotator::
    
    doc.declare(folia.PosAnnotation, 'brown-tag-set', annotator='proycon', annotatortype=folia.AnnotatorType.MANUAL)

Any additional sets for Part-of-Speech would have to be explicitly declared as well.

Adding structure
-------------------------

Assuming we begin with an empty document, we should first add a Text element. Then we can append paragraphs, sentences, or other structural elements. The ``append()`` is always used to append new children to an element::
    
    text = doc.append(folia.Text)
    paragraph = text.append(folia.Paragraph)
    sentence = paragraph.append(folia.Sentence)
    sentence.append(folia.Word, 'This')
    sentence.append(folia.Word, 'is')
    sentence.append(folia.Word, 'a')
    sentence.append(folia.Word, 'test')
    sentence.append(folia.Word, '.')

Adding annotations
-------------------------

Adding annotations, or any elements for that matter, is done using the append method. We assume that the annotations we add have already been properly declared, otherwise an exception will be raised as soon as ``append()`` is called. Let's build on the previous example::

    #First we grab the fourth word, 'test', from the sentence
    word = sentence.words(3)
    
    #Add Part-of-Speech tag
    word.append(folia.PosAnnotation, set='brown-tagset',cls='n')
    
    #Add lemma
    lemma.append(folia.LemmaAnnotation, cls='test')


Note that in the above examples, the ``append()`` method takes a class as first argument, and subsequently takes keyword arguments that will be passed to the classes' constructor.

A second way of using ``append()`` is by simply passing a child element and constructing it prior to appending. The following is equivalent to the above example::

    #First we grab the fourth word, 'test', from the sentence
    word = sentence.words(3)
    
    #Add Part-of-Speech tag
    word.append( folia.PosAnnotation(doc, set='brown-tagset',cls='n') )
    
    #Add lemma
    lemma.append( folia.LemmaAnnotation(doc , cls='test') )   

The append method always returns that which was appended. 

In the above example we first instantiate a PosAnnotatation and a LemmaAnnotation. Instantiation of any element follows the following pattern::

    Class(document, *children, **kwargs)

The common attributes are set using equally named keyword arguments:

 * ``id=`` 
 * ``cls=``
 * ``set=`` 
 * ``annotator=`` 
 * ``annotatortype=``
 * ``confidence=``
 
Not all attributes are allowed for all elements, and certain attributes are required for certain elements. ValueError exceptions will be raised when these constraints are not met.
 
Instead of setting ``id``. you can also set the keyword argument ``generate_id_in`` and pass it another element, an ID will be automatically generated, based on the ID of the element passed. When you use the first method of appending, instatation with ``generate_id_in`` will take place automatically behind the screens when applicable and when ``id`` is not explicitly set.

Any extra non-keyword arguments should be FoLiA elements and will be appended as the contents of the element, i.e. the children or subelements. Instead of using non-keyword arguments, you can also use the keyword argument ``content`` and pass a list. This is a shortcut made merely for convenience, as Python obliges all non-keyword arguments to come before the keyword-arguments, which if often aesthetically unpleasing for our purposes. Example of this use case will be shown in the next section.


Adding span annotation
---------------------------

Adding span annotation is easy with the FoLiA library, not withstanding the fact that there's more to it than adding token annotation.

As you know, span annotation uses a stand-off annotation embedded in annotation layers. These layers are in turn embedded in structural elements such as sentences. In the following example we first create a sentence and then add a syntax parse::

    doc.declare(folia.SyntaxLayer, 'some-syntax-set')
    
    sentence = text.append(folia.Sentence)
    sentence.append(folia.Word, 'The',id='example.s.1.w.1')
    sentence.append(folia.Word, 'boy',id='example.s.1.w.2')
    sentence.append(folia.Word, 'pets',id='example.s.1.w.3')
    sentence.append(folia.Word, 'the',id='example.s.1.w.4')
    sentence.append(folia.Word, 'cat',id='example.s.1.w.5')
    sentence.append(folia.Word, '.', id='example.s.1.w.6')
    
    #Adding Syntax Layer
    layer = sentence.append(folia.SyntaxLayer)
    
    #Adding Syntactic Units
    layer.append( 
        folia.SyntacticUnit(self.doc, cls='s', contents=[
            folia.SyntacticUnit(self.doc, cls='np', contents=[
                folia.SyntacticUnit(self.doc, self.doc['example.s.1.w.1'], cls='det'),
                folia.SyntacticUnit(self.doc, self.doc['example.s.1.w.2'], cls='n'),
            ]),
            folia.SyntacticUnit(self.doc, cls='vp', contents=[
                folia.SyntacticUnit(self.doc, self.doc['example.s.1.w.3'], cls='v')
                    folia.SyntacticUnit(self.doc, cls='np', contents=[
                        folia.SyntacticUnit(self.doc, self.doc['example.s.1.w.4'], cls='det'),
                        folia.SyntacticUnit(self.doc, self.doc['example.s.1.w.5'], cls='n'),            
                    ]),
                ]),
            folia.SyntacticUnit(self.doc, self.doc['example.s.1.w.6'], cls='fin')        
        ])
    )
    
To make references to the words, we simply pass the word instances and use the document's index to obtain them.  Note also that passing a list using the keyword argument ``contents`` is wholly equivalent to passing the non-keyword arguments separately.


Searching in a FoLiA document
================================

If you have loaded a FoLiA document into memory, there are several ways to search in it. Iteration over any FoLiA element will iterate over all its children. As already discussed, you can of course loop over any annotation element using ``select()``, ``annotation()`` and ``annotations()``. Additionally, ``Word.findspans()`` and ``AbstractAnnotationLayer.findspan()`` are useful methods of finding span annotations covering particular words, whereas ``AbstractSpanAnnotation.wrefs()`` does the reverse and finds the words for a given span annotation element. In addition to these main methods of navigation and selection, there are several more high-level functions available for searching.

For this we introduce the ``folia.Pattern`` class. This class describes a pattern over words to be searched for. The ``Document.findwords()`` method can subsequently be called with this pattern, and it will return all the words that match. An example will best illustrate this, first a trivial example of searching for one word::

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



API Reference
==============================

.. automodule:: pynlpl.formats.folia
     :members:
     :undoc-members:
 
