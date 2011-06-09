
FoLiA library - A short tutorial
***************************************

This short tutorial will introduce the FoLiA python library, part of PyNLPl. The FoLiA library provides an Application Programming Interface for the reading, creation and manipulation of FoLiA XML documents.



Reading FoLiA
===================

Loading a document
-------------------------------

Any script that uses FoLiA starts with the import::

    from pynlpl.formats import folia

Subsequently, a document can be read from file and into memory as follows::

    doc = folia.Document(file="/path/to/document.xml")

This returns an instance that holds the entire document.

Once you have loaded a document, all data is available for you to read and manipulate as you see fit. We will first illustrate some simple use cases:


Printing text
----------------------------------

You may want to simply print all (plain) text contained in the document, which is as easy as::

    print doc
    
Alternatively, you can obtain a string representation of all text:

    text_u = unicode(doc) #unicode instance
    text = str(doc) #UTF-8 encoded

For any subelement of the document, you can obtain its text in the same fashion.


Index
----------------------------------

A document instance has an index which you can use to grab any of its sub elements by ID. Querying using the index proceeds similar to using a python dictionary::

    word = doc['example.p.3.s.5.w.1']
    print word
    
    
Obtaining list of elements
------------------------------

Usually you do not know in advance the ID of the element you want, or you want multiple elements. There are some methods of iterating over certain elements using the FoLiA library.

For example, you can iterate over all words:

    for word in doc.words():
        print word
        
That however gives you one big iteration of words without boundaries. You may more likely seek word within sentences. So we first iterate over all sentences, then over the words therein:


    for sentence in doc.sentences():
        for word in sentence.words():
            print word
            
Or including paragraphs, assuming the document has them:

    for paragraph in doc.paragraphs():
        for sentence in paragraph.sentences():
            for word in sentence.words():
                print word
        
You can also use this method to obtain a specific word, by passing an index parameter:

        word = sentence.words(3) #retrieves the fourth word
                    
If you want to iterate over all of the child elements of a certain element, regardless of what class they are, you can simply do so as follows:

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
-----------------------


As you know, the FoLiA paradigm introduces 'sets', 'classes', `annotator' with `annotator types' and `confidence' values. These attributes are easily accessible on any element that has them:
    
    * ``element.id``        (string)
    * ``element.set``       (string)
    * ``element.cls``       (string) Since class is already a reserved keyword in python, the library consistently uses ``cls``
    * ``element.annotator`` (string)
    * ``element.annotatortype`` (set to folia.AnnotatorType.MANUAL or  folia.AnnotatorType.AUTO)
    * ``element.confidence`` (float)
    
Attributes that are not available for certain elements, or not set, default to None.


Annotations
--------------------

FoLiA is of course a format for linguistic annotation. So let's see at how to obtain annotations. This can be done using annotations() or annotation(), which is very similar to the select method, except that it will raise an exception when no such annotation is found. The difference between ``annotation()`` and ``annotations()`` is that the former will grab only one and raise an exception if there are more between which it can't disambiguate::

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

(to be written still)

Subtoken Annotation
+++++++++++++++++++++

(to be written still)

Saerching in a FoLiA document
================================

(Yet to be written)

Editing FoLiA
======================

Creating a new document
-------------------------

Creating a new FoliA document, rather than loading an existing one from file, can be done by explicitly providing an ID for the new document in the constructor::

    doc = folia.Document(id='example')
    

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

Adding annotations, or any elements for that matter, is done using the append method. Let's build on the previous example::

    #First we grab the fourth word, 'test', from the sentence
    word = sentence.words(3)
    
    #Add Part-of-Speech tag
    word.append(folia.PosAnnotation, set='brown-tagset',cls='n')
    
    #Add lemma
    lemma.append(folia.LemmaAnnotation, cls='test')


Note that in the above examples, the ``append()`` method takes a class as first argument, and subsequently takes keyword arguments that will be passed to the classes' constructor.

A second way of using ``append()`` is by simply passing a child element and constructing it itself. The following is equivalent to the above example:

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

 * id 
 * cls 
 * set 
 * annotator 
 * annotatortype
 * confidence
 
Instead of setting ``id``. you can also set the keyword argument ``generate_id_in`` and pass it another element, an ID will be automatically generated, based on the ID of the element passed. When you use the first method of appending, instatation with ``generate_id_in`` will take place automatically behind the screens when applicable.





