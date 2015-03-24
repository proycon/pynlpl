
FoLiA library 
*************

This tutorial will introduce the **FoLiA Python library**, part of PyNLPl. The
FoLiA library provides an Application Programming Interface for the reading,
creation and manipulation of FoLiA XML documents. The library works under
Python 2.7 as well as Python 3, which is the recommended version. The samples
in this documentation follow Python 3 conventions.

Prior to reading this document, it is  recommended to first read the
FoLiA documentation itself and familiarise yourself with the format and
underlying paradigm. The FoLiA documentation can be found on the `FoLiA website <
https://proycon.github.io/folia>`_. It is especially important to understand the
way FoLiA handles sets/classes, declarations, common attributes such as
annotator/annotatortype and the distinction between various kinds of annotation
categories such as token annotation and span annotation.

This Python library is also the foundation of the `FoLiA Tools
<https://pypi.python.org/pypi/FoLiA-tools>`_ collection, which consists of
various command line utilities to perform common tasks on FoLiA documents. If
you're merely interested in performing a certain common task, such as a single
query or conversion, you might want to check there if it contains is a tool that does
what you want already.


Reading FoLiA
===================

Loading a document
-------------------------------

Any script that uses FoLiA starts with the import::

    from pynlpl.formats import folia

Subsequently, a document can be read from file and follows::

    doc = folia.Document(file="/path/to/document.xml")

This returns an instance that holds the entire document in memory. Note that
for large FoLiA documents this may consume quite some memory! If you happened
to already have the document content in a string, you can load as follows::

    doc = folia.Document(string="<FoLiA ...")

Once you have loaded a document, all data is available for you to read and manipulate as you see fit. We will first illustrate some simple use cases:

To save a document back the file it was loaded from, we do::

    doc.save()

Or we can specify a specific filename::

    doc.save("/tmp/document.xml")

.. note:: Any content that is in a different XML namespace than the FoLiA namespaces or other supported namespaces (XML, Xlink), will be ignored upon loading and lost when saving.

Printing text
----------------------------------

You may want to simply print all (plain) text contained in the document, which is as easy as::

    print(doc)
    
Alternatively, you can obtain a string representation of all text::

    text = str(doc) 

For any subelement of the document, you can obtain its text in the same
fashion. 

.. note:: In Python 2, both ``str()`` as well as ``unicode()`` return a unicode instance. You may need to append ``.encode('utf-8')`` for proper output.

Index
----------------------------------

A document instance has an index which you can use to grab any of its sub
elements by ID. Querying using the index proceeds similar to using a python
dictionary::

    word = doc['example.p.3.s.5.w.1']
    print(word)

.. note:: Python 2 users will have to do ``print word.text().encode('utf-8')`` instead, to ensure non-ascii characters are printed properly.
    
    
Obtaining list of elements
------------------------------

Usually you do not know in advance the ID of the element you want, or you want
multiple elements. There are some methods of iterating over certain elements
using the FoLiA library.

For example, you can iterate over all words::

    for word in doc.words():
        print(word)
        
That however gives you one big iteration of words without boundaries. You may
more likely want to seek words within sentences. So we first iterate over all sentences,
then over the words therein::

    for sentence in doc.sentences():
        for word in sentence.words():
            print(word)
            
Or including paragraphs, assuming the document has them::

    for paragraph in doc.paragraphs():
        for sentence in paragraph.sentences():
            for word in sentence.words():
                print(word)
        
You can also use this method to obtain a specific word, by passing an index parameter::

        word = sentence.words(3) #retrieves the fourth word
                    
If you want to iterate over all of the child elements of a certain element,
regardless of what type they are, you can simply do so as follows::

    for subelement in element:
        if isinstance(subelement, folia.Sentence):
            print("this is a sentence")
        else: 
            print("this is something else")

If applied recursively this allows you to traverse the entire
element tree, there are however specialised methods available that do this for
you.

Select method
----------------------

There is a generic method available on all elements to select child elements of
any desired class. This method is by default applied recursively. Internally,
the ``paragraphs()``, ``words()`` and ``sentences()`` methods seen above are simply
shortcuts that make use of the select method::

    sentence = doc['example.p.3.s.5.w.1']
    words = sentence.select(folia.Word)
    for word in words:
        print(word)

The ``select()`` method has a sibling ``count()``, invoked with the same
arguments, which simply counts how many items it finds, without actually
returning them::

    word = sentence.count(folia.Word)

**Advanced Notes**:

The ``select()`` method and similar high-level methods derived from it, are
generators.  This implies that the results of the selection are returned one by
one in the iteration, as opposed to all stored in memory. This also implies
that you can only iterate over it once, we can not do another iteration over
the ``words`` variable in the above example, unless we reinvoke the
``select()`` method to get a new generator. Likewise, we can not do
``len(words)``, but have to use the ``count()`` method instead.

If you want to have all results in memory in a list, you can simply do the following::

    words = list(sentence.select(folia.Word))

The select method is by default recursive, set the third argument to False to
make it non-recursive. The second argument can be used for restricting matches
to a specific set, a tuple of classes. The recursion will not go into any
non-authoritative elements such as alternatives, originals of corrections. 

Navigating a document
--------------------------

The ``select()`` method is your main tool for descending downwards in the document
tree. There are occassions, however, when you want go upwards or sideways. The
``next()`` and ``previous()`` methods can be used for sideway navigation, they
return the next or previous element, respectively::

    nextelement = element.next()
    previouselement = element.previous()

You can explicitly filter by passing an element type::

    nextword = word.next(folia.Word)

By default, the search is constrained not to cross certain boundaries, such as
sentences and paragraphs. You can do so explicitly as well by passing a list of
constraints::

    nextword = word.next(folia.Word, [folia.Sentence])

If you do not want any constraints, pass ``None``::

    nextword = word.next(folia.Word)

These methods will return ``None`` if no next/previous element was found (of
the specified type).

Each element has a ``parent`` attributes that links it to its parent::

    sentence = word.parent

Only for the top-level element (Text), the parent is ``None``. There is also
the method ``ancestors()`` to iterate over all ancestors::

    for ancestor in element.ancestors():
        print(type(ancestor))

If you are looking for ancestors of a specific type, you can pass it as an
argument::

    for ancestor in element.ancestors(folia.Division):
        print(type(ancestor))

If only a single ancestor is desired, use the ``ancestor()`` method instead,
unlike the generator version ``ancestors()``, it will raise an exception if the
ancestor was not found::

    paragraph = word.ancestor(folia.Paragraph)


Structure Annotation Types
------------------------------

The FoLiA library discerns various Python classes for structure
annotation, the corresponding FoLiA XML tag is listed too. Sets and classes can
be associated with most of these elements to make them more specific, these are
never prescribed by FoLiA. The list of classes is as follows:

* ``folia.Cell`` - ``cell`` - A cell in a ``row`` in a ``table``
* ``folia.Division`` - ``div`` - Used for for example chapters, sections, subsections
* ``folia.Event`` - ``event`` -  Often in new-media data where a chat message, tweet or
  forum post is considered an event.
* ``folia.Figure`` - ``figure`` - A graphic/image
* ``folia.Gap`` - ``gap`` - A gap containing raw un-annotated textual content
* ``folia.Head`` - ``head`` - The head/title of a division (``div``), used for chapter/section/subsection titles etc..
* ``folia.Linebreak`` - ``br`` - An explicit linebreak/newline
* ``folia.List`` - ``list`` - A list, bulleted or enumerated
* ``folia.ListItem`` - ``listitem`` - An item in a ``list``
* ``folia.Note`` - ``note`` - A note, such as a footnote or bibliography reference for instance 
* ``folia.Paragraph`` - ``p``
* ``folia.Part`` - ``part`` - An abstract part of a larger structure
* ``folia.Quote`` - ``quote`` - Cited text
* ``folia.Reference`` - ``ref`` - A reference to another structural element,
  used to refer to footnotes (``note``) for example.
* ``folia.Sentence`` - ``s``
* ``folia.Table`` - ``table`` - A table
* ``folia.TableHead`` - ``tablehead`` - The head of a table, containing cells (``cell``) with column labels
* ``folia.Row`` - ``row`` - A row in a ``table``
* ``folia.Text`` - ``text`` - The root of the document's content
* ``folia.Whitespace`` - ``whitespace`` - Explicit vertical whitespace
* ``folia.Word``- ``w``

The FoLiA documentation explain all of these in detail.  

FoLiA and this library enforce explicit rules about what elements are allowed
in what others. Exceptions will be raised when this is about to be violated.

Common attributes
-----------------------

The FoLiA paradigm features *sets* and *classes* as primary means to represent
the actual value (class) of an annotation. A set often corresponds to a tagset,
such as a set of part-of-speech tags, and a class is one selected value in such a set.

The paradigm furthermore introduces other comomn attributes to set on
annotation elements, such as an identifier,  information on the annotator, and
more. A full list is provided below:
    
* ``element.id``        (string) - The unique identifier of the element
* ``element.set``       (string) - The set the element pertains to.
* ``element.cls``       (string) - The assigned class, of the set above.
    Classes correspond with tagsets in this case of many annotation types.
    Note that since class is already a reserved keyword in python, the library consistently uses ``cls``
* ``element.annotator`` (string) - The name or ID of the annotator who added/modified this element
* ``element.annotatortype`` - The type of annotator, can be either ``folia.AnnotatorType.MANUAL`` or ``folia.AnnotatorType.AUTO``
* ``element.confidence`` (float) - A confidence value expressing
* ``element.datetime``  (datetime.datetime) - The date and time when the element was added/modified.
* ``element.n``         (string) - An ordinal label, used for instance in enumerated list contexts, numbered sections, etc..

The following attributes are specific to a speech context:

* ``element.src``       (string) - A URL or filename referring the an audio or video file containing the speech. Access this attribute using the ``element.speaker_src()`` method, as it is inheritable from ancestors.
* ``element.speaker``   (string) -  The name of ID of the speaker. Access this attribute using the ``element.speech_speaker()`` method, as it is inheritable from ancestors.
* ``element.begintime`` (4-tuple) - The time in the above source fragment when the phonetic content of this element starts, this is a (hours, minutes,seconds,milliseconds) tuple.
* ``element.endtime``   (4-tuple) - The time in the above source fragment when the phonetic content of this element ends, this is a (hours, minutes,seconds,milliseconds) tuple.
 
Attributes that are not available for certain elements, or not set, default to ``None``.

Annotations
--------------------

FoLiA is of course a format for linguistic annotation. Accessing annotation is
therefore one of the primary functions of this library. This can be done using
``annotations()`` or ``annotation()``, which is similar to the ``select()``
method, except that it will raise an exception when no such annotation is
found. The difference between ``annotation()`` and ``annotations()`` is that
the former will grab only one and raise an exception if there are more between
which it can't disambiguate, whereas the second is a generator, but will still
raise an exception if none is found::

    for word in doc.words():
        try:
            pos = word.annotation(folia.PosAnnotation, 'CGN')
            lemma = word.annotation(folia.LemmaAnnotation)
            print("Word: ", word)
            print("ID: ", word.id)
            print("PoS-tag: " , pos.cls)
            print("PoS Annotator: ", pos.annotator)
            print("Lemma-tag: " , lemma.cls)
        except folia.NoSuchAnnotation:
            print("No PoS or Lemma annotation")

Note that the second argument of ``annotation()``, ``annotations()`` or
``select()`` can be used to restrict your selection to a certain set. In the
above example we restrict ourselves to Part-of-Speech tags in the CGN set.

Token Annotation Types
+++++++++++++++++++++++++

The following token annotation elements are available in FoLiA, they are
embedded under a structural element. 

* ``folia.DomainAnnotation`` - ``domain`` - Domain/genre annotation
* ``folia.PosAnnotation`` - ``pos`` - Part of Speech Annotation
* ``folia.LangAnnotation`` - ``lang`` - Language identification
* ``folia.LemmaAnnotation`` - ``lemma``
* ``folia.SenseAnnotation`` - ``sense`` - Lexical semantic sense annotation
* ``folia.SubjectivityAnnotation`` - ``subjectivity`` - Sentiment analysis / subjectivity annotation

The following annotation types are somewhat special, as they are the only
elements for which FoLiA assumes a default set and a default class:

* ``folia.TextContent`` - ``t`` - Text content, this carries the actual text
  for the structural element in which is it embedded
* ``folia.PhonContent`` - ``ph`` - Phonetic content, this carries a phonetic
  representation 


Span Annotation
+++++++++++++++++++

FoLiA distinguishes token annotation and span annotation, token annotation is
embedded in-line within a structural element, and the annotation therefore
pertains to that structural element, whereas span annotation is stored
in a stand-off annotation layer outside the element and refers back to it. Span
annotation elements typically *span* over multiple structural elements.

We will discuss three ways of accessing span annotation. As stated, span annotation is
contained within an annotation layer of a certain structure element, often a
sentence. In the first way of accessing span annotation, we do everything explicitly. We
first obtain the layer, then iterate over the span annotation elements within that layer,
and finally iterate over the words to which the span applies. Assume we have a
``sentence`` and we want to print all the named entities in it::


    for layer in sentence.select(folia.EntitiesLayer):
        for entity in layer.select(folia.Entity):
            print(" Entity class=", entity.cls, " words=")
            for word in entity.wrefs():
                print(word, end="")  #print without newline
            print()   #print newline

The ``wrefs()`` method, available on all span annotation elements, will return
a list of all words (as well as morphemes and phonemes) over which a span
annotation element spans.

This first way is rather verbose. The second way of accessing span annotation
takes another approach, using the ``findspans()`` method on Word instances.
Here we start from a word and seek span annotations in which that word occurs.
Assume we have a ``word`` and want to find chunks it occurs in::

    for chunk in word.findspans(folia.Chunk):
        print(" Chunk class=", chunk.cls, " words=")
        for word2 in chunk.wrefs(): #print all words in the chunk (of which the word is a part)
            print(word2, end="")
        print()

The ``findspans()`` method can be called with either the class of a Span
Annotation Element, such as ``folia.Chunk``, or which the class of the layer,
such as ``folia.ChunkingLayer``.

The third way allows us to look for span elements given an annotation layer and
words. In other words, it checks if one or more words form a span. This is an
exact match and not a sub-part match as in the previously described method. To
do this, we use use the ``findspan()`` method on annotation layers::

    for span in annotationlayer.findspan(word1,word2):
        print(span.cls)

Span Annotation Types
++++++++++++++++++++++++

This section lists the available Span annotation elements, the layer that contains
them is explicitly mentioned as well.

Some of the span annotation elements are complex and take span role elements as
children, these are normal span annotation elements that occur on a within
another span annotation (of a particular type) and can not be used standalone.

* ``folia.Chunk`` in ``folia.ChunkingLayer`` - ``chunk`` in ``chunks`` - Shallow parsing.  Not nested .
* ``folia.CoreferenceChain`` in ``folia.CoreferenceLayer`` - ``coreferencechain`` in ``coreferences`` - Co-references

 * Requires the roles ``folia.CoreferenceLink`` (``coreferencelink``) pointing to each coreferenced structure in the chain

* ``folia.Dependency`` in ``folia.DependencyLayer`` - ``dependency`` in ``dependencies`` - Dependency Relations

 * Requires the roles ``folia.HeadSpan`` (``hd``) and ``folia.DependencyDependent`` (``dep``)

* ``folia.Entity`` in ``folia.EntitiesLayer`` - ``entity`` in ``entities`` - Named entities
* ``folia.SyntacticUnit`` in ``folia.SyntaxLayer`` - ``su`` in ``syntax`` - Syntax.  These elements are generally nested to form syntax trees.

* ``folia.SemanticRole`` in ``folia.SemanticRolesLayer`` - ``semrole`` in ``semroles`` - Semantic Roles


The span role ``folia.HeadSpan`` (``hd``)  may actually be used by
most span annotation elements, indicating it's head-part.


Editing FoLiA
======================

Creating a new document
-------------------------

Creating a new FoliA document, rather than loading an existing one from file,
is done by explicitly providing the ID for the new document in the
constructor::

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

Any additional sets for Part-of-Speech would have to be explicitly declared as
well. To check if a particular annotation type and set is declared, use the
``declared(Class, set)`` method.

Adding structure
-------------------------

Assuming we begin with an empty document, we should first add a Text element.
Then we can add paragraphs, sentences, or other structural elements. The
``add()`` adds new children to an element::
    
    text = doc.add(folia.Text)
    paragraph = text.add(folia.Paragraph)
    sentence = paragraph.add(folia.Sentence)
    sentence.add(folia.Word, 'This')
    sentence.add(folia.Word, 'is')
    sentence.add(folia.Word, 'a')
    sentence.add(folia.Word, 'test')
    sentence.add(folia.Word, '.')


.. note:: The ``add()`` method is actually a wrapper around ``append()``, which takes the
    exact same arguments. It performs extra checks and works for both span
    annotation as well as token annotation. Using ``append()`` will be faster.

Adding annotations
-------------------------

Adding annotations, or any elements for that matter, is done using the
``add()`` method on the intended parent element. We assume that the annotations
we add have already been properly declared, otherwise an exception will be
raised as soon as ``add()`` is called. Let's build on the previous example::

    #First we grab the fourth word, 'test', from the sentence
    word = sentence.words(3)
    
    #Add Part-of-Speech tag
    word.add(folia.PosAnnotation, set='brown-tagset',cls='n')
    
    #Add lemma
    lemma.add(folia.LemmaAnnotation, cls='test')


Note that in the above examples, the ``add()`` method takes a class as first
argument, and subsequently takes keyword arguments that will be passed to the
classes' constructor.

A second way of using ``add()`` is by simply passing a fully instantiated child
element, thus constructing it prior to adding. The following is equivalent to the
above example, as the previous method is merely a shortcut for convenience::

    #First we grab the fourth word, 'test', from the sentence
    word = sentence.words(3)
    
    #Add Part-of-Speech tag
    word.add( folia.PosAnnotation(doc, set='brown-tagset',cls='n') )
    
    #Add lemma
    lemma.add( folia.LemmaAnnotation(doc , cls='test') )   

The ``add()`` method always returns that which was added, allowing it to be chained.

In the above example we first explicitly instantiate a ``folia.PosAnnotation``
and a ``folia.LemmaAnnotation``. Instantiation of any FoLiA element (always
Python class subclassed off ``folia.AbstractElement``) follows the following
pattern::

    Class(document, *children, **kwargs)

Note that the document has to be passed explicitly as first argument to the constructor.

The common attributes are set using equally named keyword arguments:

 * ``id=`` 
 * ``cls=``
 * ``set=`` 
 * ``annotator=`` 
 * ``annotatortype=``
 * ``confidence=``
 * ``src=``
 * ``speaker=``
 * ``begintime=``
 * ``endtime=``

Not all attributes are allowed for all elements, and certain attributes are
required for certain elements. ``ValueError`` exceptions will be raised when these
constraints are not met.
 
Instead of setting ``id``. you can also set the keyword argument
``generate_id_in`` and pass it another element, an ID will be automatically
generated, based on the ID of the element passed. When you use the first method
of adding elements, instantiation with ``generate_id_in`` will take place automatically
behind the scenes when applicable and when ``id`` is not explicitly set.

Any extra non-keyword arguments should be FoLiA elements and will be appended
as the contents of the element, i.e. the children or subelements. Instead of
using non-keyword arguments, you can also use the keyword argument ``content``
and pass a list. This is a shortcut made merely for convenience, as Python
obliges all non-keyword arguments to come before the keyword-arguments, which
if often aesthetically unpleasing for our purposes. Example of this use case
will be shown in the next section.


Adding span annotation
---------------------------

Adding span annotation is easy with the FoLiA library. As you know, span
annotation uses a stand-off annotation embedded in annotation layers. These
layers are in turn embedded in structural elements such as sentences. However,
the ``add()`` method abstracts over this. Consider the following example of a named entity::

    doc.declare(folia.Entity, "https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/namedentities.foliaset.xml")
    
    sentence = text.add(folia.Sentence)
    sentence.add(folia.Word, 'I',id='example.s.1.w.1')
    sentence.add(folia.Word, 'saw',id='example.s.1.w.2')
    sentence.add(folia.Word, 'the',id='example.s.1.w.3')
    word = sentence.add(folia.Word, 'Dalai',id='example.s.1.w.4')
    word2 =sentence.add(folia.Word, 'Lama',id='example.s.1.w.5')
    sentence.add(folia.Word, '.', id='example.s.1.w.6')

    word.add(folia.Entity, word, word2, cls="per")

To make references to the words, we simply pass the word instances and use the
document's index to obtain them.  Note also that passing a list using the
keyword argument ``contents`` is wholly equivalent to passing the non-keyword
arguments separately::

    word.add(folia.Entity, cls="per", contents=[word,word2])

In the next example we do things more explicitly. We first create a sentence
and then add a syntax parse, consisting of nested elements::

    doc.declare(folia.SyntaxLayer, 'some-syntax-set')
    
    sentence = text.add(folia.Sentence)
    sentence.add(folia.Word, 'The',id='example.s.1.w.1')
    sentence.add(folia.Word, 'boy',id='example.s.1.w.2')
    sentence.add(folia.Word, 'pets',id='example.s.1.w.3')
    sentence.add(folia.Word, 'the',id='example.s.1.w.4')
    sentence.add(folia.Word, 'cat',id='example.s.1.w.5')
    sentence.add(folia.Word, '.', id='example.s.1.w.6')
    
    #Adding Syntax Layer
    layer = sentence.add(folia.SyntaxLayer)
    
    #Adding Syntactic Units
    layer.add( 
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
    

.. note:: The lower-level ``append()`` method would have had the same effect in the above syntax tree sample.

Deleting annotation
----------------------

Any element can be deleted by calling the ``remove()`` method of its parent. Suppose we want to delete ``word``::

    word.parent.remove(word)

Copying annotations
----------------------

A *deep copy* can be made of any element by calling its ``copy()`` method:: 

    word2 = word.copy()

The copy will be without parent and document. If you intend to associate a copy with a new document, then copy as follows instead::

    word2 = word.copy(newdoc)

If you intend to attach the copy somewhere in the same document, you may want to add a suffix for any identifiers in its scope, since duplicate identifiers are not allowed and would raise an exception. This can be specified as the second argument::

    word2 = word.copy(doc, ".copy")

Searching in a FoLiA document
================================

If you have loaded a FoLiA document into memory, you may want to search for a
particular annotations. You can of course loop over all structural and
annotation elements using ``select()``, ``annotation()`` and ``annotations()``.
Additionally, ``Word.findspans()`` and ``AbstractAnnotationLayer.findspan()``
are useful methods of finding span annotations covering particular words,
whereas ``AbstractSpanAnnotation.wrefs()`` does the reverse and finds the words
for a given span annotation element. In addition to these main methods of
navigation and selection, there is higher-level function available for
searching, this uses the **FoLiA Query Language** (FQL) or the **Corpus Query
Language** (CQL).

These two languages are part of separate libraries that need to be imported::

    from pynlpl.formats import fql, cql


Corpus Query Language (CQL)
-----------------------------

CQL is the easier-language of the two and most suitable for corpus searching.
It is, however, less flexible than FQL, which is designed specifically for
FoLiA and can not just query, but also manipulate FoLiA documents in great
detail.

CQL was developed for the `IMS Corpus Workbench
<http://www.ims.uni-stuttgart.de/forschung/projekte/CorpusWorkbench.html>`_,
at Stuttgart Univeristy, and is implemented in Sketch Engine, who provide good
`CQL documentation
<http://www.sketchengine.co.uk/documentation/wiki/SkE/CorpusQuerying>`_.


CQL has to be converted to FQL first, which is then executed on the given document. This is a simple example querying for the word "house"::

    doc = folia.Document(file="/path/to/some/document.folia.xml")
    query = fql.Query(cql.cql2fql('"house"'))
    for word in query(doc):
        print(word) #these will be folia.Word instances (all matching house)

Multiple words can be queried::

    query = fql.Query(cql.cql2fql('"the" "big" "house"'))
    for word1,word2,word3 in query(doc):
        print(word1, word2,word3) 

Queries may contain wildcard expressions to match multiple text patterns. Gaps can be specified using []. The following will match any three word combination starting with the and ending with something that starts with house. It will thus match things like "the big house" or "the small household"::

    query = fql.Query(cql.cql2fql('"the" [] "house.*"'))
    for word1,word2,word3 in query(doc):
        ...

We can make the gap optional with a question mark, it can be lenghtened with + or * , like regular expressions::

    query = fql.Query(cql.cql2fql('"the" []? "house.*"'))
    for match in query(doc):
        print("We matched ", len(match), " words")

Querying is not limited to text, but all of FoLiA's annotations can be used. To force our gap consist of one or more adjectives, we do::

    query = fql.Query(cql.cql2fql('"the" [ pos = "a" ]+ "house.*"'))
    for match in query(doc):
        ...

The original CQL attribute here is ``tag`` rather than ``pos``, this can be used too. In addition, all FoLiA element types can be used!  Just use their FoLiA tagname.

Consult the CQL documentation for more. Do note that CQL is very word/token centered, for searching other types of elements, use FQL instead.

    
FoLiA Query Language (FQL)
-------------------------------

 
FQL is documented `here
<https://github.com/proycon/foliadocserve/blob/master/README.rst>`__, a full
overview is beyond the scope of this documentation. We will just introduce some
basic selection queries so you can develop an initial impression of the language's abilities.

Selecting a word with a particular text is done as follows::

    query = fql.Query('SELECT w WHERE text = "house"')
    for word in query(doc):
        print(word)  #this will be an instance of folia.Word

Regular expression matching can be done using the ``MATCHES`` operator::

    query = fql.Query('SELECT w WHERE text MATCHES "^house.*$"')
    for word in query(doc):
        print(word)  

The classes of other annotation types can be easily queried as follows::

    query = fql.Query('SELECT w WHERE :pos = "v"' AND :lemma = "be"')
    for word in query(doc):
        print(word) 

You can constrain your queries to a particular target selection using the ``FOR`` keyword::

    query = fql.Query('SELECT w WHERE text MATCHES "^house.*$" FOR s WHERE text CONTAINS "sell"')
    for word in query(doc):
        print(word)

This construction also allows you to select the actual annotations. To select all people (a named entity) for words that are not John::

    query = fql.Query('SELECT entity WHERE class = "person" FOR w WHERE text != "John"')
    for entity in query(doc):
        print(entity) #this will be an instance of folia.Entity

**FOR** statement may be chained, and Explicit IDs can be passed using the ``ID`` keyword::

    query = fql.Query('SELECT entity WHERE class = "person" FOR w WHERE text != "John" FOR div ID "section.21"')
    for entity in query(doc):
        print(entity) 
    
Sets are specified using the **OF** keyword, it can be omitted if there is only one for the annotation type, but will be required otherwise::

    query = fql.Query('SELECT su OF "http://some/syntax/set" WHERE class = "np"')
    for su in query(doc):
        print(su) #this will be an instance of folia.SyntacticUnit


We have just covered the **SELECT** keyword, FQL has other keywords for manipulating documents, such as **EDIT**, **ADD**, **APPEND** and **PREPEND**.

.. note:: Consult the FQL documentation at https://github.com/proycon/foliadocserve/blob/master/README.rst for further documentation on the language.

Streaming Reader
-------------------

Throughout this tutorial you have seen the ``folia.Document`` class as a means
of reading FoLiA documents. This class always loads the entire document in
memory, which can be a considerable resource demand. The ``folia.Reader`` class
provides an alternative to loading FoLiA documents. It does not load the entire
document in memory but merely returns the elements you are interested in. This
results in far less memory usage and also provides a speed-up.

A reader is constructed as follows, the second argument is the class of the element you
want::

    reader = folia.Reader("my.folia.xml", folia.Word)
    for word in reader:
        print(word.id)


Higher-Order Annotations
===========================


Text Markup
--------------

FoLiA has a number of text markup elements, these appear within the
``folia.TextContent`` (``t``) element, iterating over the element of a
``folia.TextContent`` element will first and foremost produce strings, but also
uncover these markup elements when present. The following markup types exists:

* ``folia.TextMarkupGap`` (``t-gap``) - For marking gaps in the text
* ``folia.TextMarkupString`` (``t-str``) - For marking arbitrary substring
* ``folia.TextMarkupStyle`` (``t-style``) - For marking style (such as bold, italics, as dictated by the set used)
* ``folia.TextMarkupCorrection`` (``t-correction``) - Simple in-line corrections
* ``folia.TextMarkupError`` (``t-error``) -  For marking errors


Features
-------------

Features allow a second-order annotation by adding the abilities to assign
properties and values to any of the existing annotation elements. They follow
the set/class paradigm by adding the notion of a subset and class relative to
this subset. The ``feat()`` method provides a shortcut that can be used on any
annotation element to obtain the class of the feature, given a subset. To
illustrate the concept, take a look at part of speech annotation with some
features::

    pos = word.annotation(folia.PosAnnotation)
    if pos.cls = "n":
        if pos.feat('number') == 'plural':
            print("We have a plural noun!")
        elif pos.feat('number') == 'plural':
            print("We have a singular noun!")

The ``feat()`` method will return an exception when the feature does not exist.
Note that the actual subset and class values are defined by the set and not
FoLiA itself! They are therefore fictitious in the above example. 

The Python class for features is ``folia.Feature``, in the following example we
add a feature::

    pos.add(folia.Feature, subset="gender", class="f")

Although FoLiA does not define any sets nor subsets. Some annotation types do
come with some associated subsets, their use is never mandatory. The advantage
is that these associated subsets can be directly used as an XML attribute in
the FoLiA document. The FoLiA library provides extra classes, iall subclassed
off ``folia.Feature`` for these:

* ``folia.SynsetFeature``, for use with ``folia.SenseAnnotation`` 
* ``folia.ActorFeature``, for use with ``folia.Event`` 
* ``folia.BegindatetimeFeature``, for use with ``folia.Event`` 
* ``folia.EnddatetimeFeature``, for use with ``folia.Event`` 

Alternatives
------------------

A key feature of FoLiA is its ability to make explicit alternative annotations,
for token annotations, the ``folia.Alternative`` (``alt``) class is used to
this end. Alternative annotations are embedded in this structure. This implies
the annotation is not authoritative, but is merely an alternative to the actual
annotation (if any). Alternatives may typically occur in larger numbers,
representing a distribution each with a confidence value (not mandatory). Each
alternative is wrapped in its own ``folia.Alternative`` element, as multiple
elements inside a single alternative are considered dependent and part of the
same alternative. Combining multiple annotation in one alternative makes sense
for mixed annotation types, where for instance a pos tag alternative is tied to
a particular lemma::

    alt = word.add(folia.Alternative)
    alt.add(folia.PosAnnotation, set='brown-tagset',cls='n',confidence=0.5)
    alt = word.add(folia.Alternative)   #note that we reassign the variable!
    alt.add(folia.PosAnnotation, set='brown-tagset',cls='a',confidence=0.3)
    alt = word.add(folia.Alternative)
    alt.add(folia.PosAnnotation, set='brown-tagset',cls='v',confidence=0.2)

Span annotation elements have a different mechanism for alternatives, for those
the entire annotation layer is embedded in a ``folia.AlternativeLayers``
element. This element should be repeated for every type, unless the layers it
describeds are dependent on it eachother::

    alt = sentence.add(folia.AlternativeLayers)
    layer = alt.add(folia.Entities)
    entity = layer.add(folia.Entity, word1,word2,cls="person", confidence=0.3)


Because the alternative annotations are **non-authoritative**, normal selection
methods such as ``select()`` and ``annotations()`` will never yield them,
unless explicitly told to do so. For this reason, there is an
``alternatives()`` method on structure elements, for the first category of alternatives.

Corrections
------------------

Corrections are one of the most complex annotation types in FoLiA. Corrections
can be applied not just over text, but over any type of structure annotation,
token annotation or span annotation. Corrections explicitly preserve the
original, and recursively so if corrections are done over other corrections.

Despite their complexity, the library treats correction transparently. Whenever
you query for a particular element, and it is part of a correction, you get the
corrected version rather than the original. The original is always *non-authoritative*
and normal selection methods will ignore it.

If you want to deal with correction, you have to explicitly get a
``folia.Correction`` element. If an element is part of a correction, its
``incorrection()`` method will give the correction element, if not, it will
return ``None``::

    pos = word.annotation(folia.PosAnnotation)
    correction = pos.incorrection()
    if correction: 
        if correction.hasoriginal():
            originalpos = correction.original(0) #assuming it's the only element as is customary
            #originalpos will be an instance of folia.PosAnnotation
            print("The original pos was", originalpos.cls)

Corrections themselves carry a class too, indicating the type of correction (defined by the set used and not by FoLiA).

Besides ``original()``, corrections distinguish three other types, ``new()`` (the corrected version), ``current()`` (the current uncorrected version) and ``suggestions(i)`` (a suggestion for correction), the former two and latter two usually form pairs, ``current()`` and ``new()`` can never be used together. Of ``suggestions(i)`` there may be multiple, hence the index argument. These return, respectively, instances of ``folia.Original``, ``folia.New``, ``folia.Current`` and ``folia.Suggestion``.

Adding a correction can be done explicitly::

    wrongpos = word.annotation(folia.PosAnnotation)
    word.add(folia.Correction, folia.New(doc, folia.PosAnnotation(doc, cls="n")) , folia.Original(doc, wrongpos), cls="misclassified")   

Let's settle for a suggestion rather than an actual correction::

    wrongpos = word.annotation(folia.PosAnnotation)
    word.add(folia.Correction, folia.Suggestion(doc, folia.PosAnnotation(doc, cls="n")), cls="misclassified")   


In some instances, when correcting text or structural elements, ``folia.New()`` may be
empty, which would correspond to an *deletion*. Similarly, ``folia.Original()`` may be
empty, corresponding to an *insertion*. 

The use of ``folia.Current()`` is reserved for use with structure elements, such as words, in combination with suggestions. The structure elements then have to be embedded in ``folia.Current()``. This situation arises for instance when making suggestions for a merge or split.



API Reference
==============================

.. automodule:: pynlpl.formats.folia
     :members:
     :undoc-members:
 
