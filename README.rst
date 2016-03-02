PyNLPl - Python Natural Language Processing Library
=====================================================

.. image:: https://travis-ci.org/proycon/pynlpl.svg?branch=master
    :target: https://travis-ci.org/proycon/pynlpl

.. image:: http://applejack.science.ru.nl/lamabadge.php/pynlpl
   :target: http://applejack.science.ru.nl/languagemachines/

PyNLPl, pronounced as 'pineapple', is a Python library for Natural Language
Processing. It contains various modules useful for common, and less common, NLP
tasks. PyNLPl can be used for basic tasks such as the extraction of n-grams and
frequency lists, and to build simple language model. There are also more
complex data types and algorithms. Moreover, there are parsers for file formats
common in NLP (e.g. FoLiA/Giza/Moses/ARPA/Timbl/CQL). There are also clients to
interface with various NLP specific servers. PyNLPl most notably features a
very extensive library for working with FoLiA XML (Format for Linguistic
Annotatation).

The library is a divided into several packages and modules. It works on Python
2.7, as well as Python 3.

The following modules are available:

- ``pynlpl.datatypes`` - Extra datatypes (priority queues, patterns, tries)
- ``pynlpl.evaluation`` - Evaluation & experiment classes (parameter search, wrapped
  progressive sampling, class evaluation (precision/recall/f-score/auc), sampler, confusion matrix, multithreaded experiment pool)
- ``pynlpl.formats.cgn`` - Module for parsing CGN (Corpus Gesproken Nederlands) part-of-speech tags
- ``pynlpl.formats.folia`` - Extensive library for reading and manipulating the
  documents in `FoLiA <http://proycon.github.io/folia>`_ format (Format for Linguistic Annotation).
- ``pynlpl.formats.fql`` - Extensive library for the FoLiA Query Language (FQL),
  built on top of ``pynlpl.formats.folia``. FQL is currently documented `here
  <https://github.com/proycon/foliadocserve>`__. 
- ``pynlpl.formats.cql`` - Parser for the Corpus Query Language (CQL), as also used by
  Corpus Workbench and Sketch Engine. Contains a convertor to FQL.
- ``pynlpl.formats.giza`` - Module for reading GIZA++ word alignment data
- ``pynlpl.formats.moses`` - Module for reading Moses phrase-translation tables.
- ``pynlpl.formats.sonar`` - Largely obsolete module for pre-releases of the
  SoNaR corpus, use ``pynlpl.formats.folia`` instead.
- ``pynlpl.formats.timbl`` - Module for reading Timbl output (consider using
  `python-timbl <https://github.com/proycon/python-timbl>`_ instead though)
- ``pynlpl.lm.lm`` - Module for simple language model and reader for ARPA
  language model data as well (used by SRILM).
- ``pynlpl.search`` - Various search algorithms (Breadth-first, depth-first,
  beam-search, hill climbing, A star, various variants of each)
- ``pynlpl.statistics`` - Frequency lists, Levenshtein, common statistics and
  information theory functions
- ``pynlpl.textprocessors`` - Simple tokeniser, n-gram extraction 


API Documentation can be found `here <http://pythonhosted.org/PyNLPl/>`__.


