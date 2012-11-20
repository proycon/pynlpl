Statistics and Information Theory
==================================

This module contains classes and functions for statistics and information theory. It is imported as follows:: 

	import pynlpl.statistics
	

Generic functions
-------------------------------------

Amongst others, the following generic statistical functions are available::

* ``mean(list)'' - Computes the mean of a given list of numbers

* ``median(list)'' - Computes the median of a given list of numbers

* ``stddev(list)'' - Computes the standard deviation of a given list of numbers  

* ``normalize(list)'' - Normalizes a list of numbers so that the sum is 1.0 .


Frequency Lists and Distributions
-------------------------------------

One of the most basic and widespread tasks in NLP is the creation of a frequency list. Counting is established by simply appending lists to the frequencylist::

	freqlist =  pynlpl.statistics.FrequencyList()
	freqlist.append(['to','be','or','not','to','be'])

Take care not to append lists rather than strings unless you mean to create a frequency list over its characters rather than words. You may want to use the ``pynlpl.textprocessors.crudetokeniser`` first::

	freqlist.append(pynlpl.textprocessors.crude_tokeniser("to be or not to be"))

The count can also be incremented explicitly explicitly for a single item:

	freqlist.count('shakespeare')
	
The FrequencyList offers dictionary-like access. For example, the following statement will be true for the frequency list just created::

	freqlist['be'] == 2

Normalised counts (pseudo-probabilities) can be obtained using the ``p()`` method::

	freqlist.p('be')
	
Normalised counts can also be obtained by instantiation a Distribution instance using the frequency list::

	dist = pynlpl.statistics.Distribution(freqlist)
	
This too offers a dictionary-like interface, where values are by definition normalised. The advantage of a Distribution class is that it offers information-theoretic methods such as ``entropy()``, ``maxentropy()``, ``perplexity()`` and ``poslog()``.

A frequency list can be saved to file using the ``save(filename)`` method, and loaded back from file using the ``load(filename)`` method. The ``output()`` method is a generator yielding strings for each line of output, in ranked order.



API Reference
===============


.. automodule:: pynlpl.statistics
    :members:
    :undoc-members:


