PyNLPl - Python Natural Language Processing Library
=====================================================

.. image:: https://travis-ci.org/proycon/pynlpl.svg?branch=master
    :target: https://travis-ci.org/proycon/pynlpl

PyNLPl, pronounced as "pineapple", is a Python library for Natural Language
Processing. It contains various modules useful for common, and less common, NLP
tasks. PyNLPl can be used for example the computation of n-grams, frequency
lists and distributions, language models. There are also more complex data
types, such as Priority Queues, and search algorithms, such as Beam Search.

The library is divided into several packages and modules. It works on Python
2.7, as well as Python 3.

The following modules are available:

- ``pynlpl.datatypes`` - Extra datatypes (priority queues, patterns, tries)
- ``pynlpl.evaluation`` - Evaluation & experiment classes (parameter search, wrapped
  progressive sampling, class evaluation (precision/recall/f-score/auc), sampler, confusion matrix, multithreaded experiment pool)
- ``pynlpl.formats.cgn`` - Module for parsing CGN (Corpus Gesproken Nederlands) part-of-speech tags
- ``pynlpl.formats.folia`` - **Extensive library for reading and manipulating the
  documents in `FoLiA <http://proycon.github.io/folia>`_ format (Format for Linguistic Annotation).**
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


API Documentation can be found `here <http://pythonhosted.org/PyNLPl/>`_.


