Text Processors
==================================

This module contains classes and functions for text processing. It is imported as follows:: 

	import pynlpl.textprocessors

Tokenisation
------------------

A very crude tokeniser is available in the form of the function ``pynlpl.textprocessors.crude_tokeniser(string)''. This will split punctuation characters from words and returns a list of tokens. It however has no regard for abbreviations and end-of-sentence detection, which is functionality a more sophisticated tokeniser can provide::

	tokens = pynlpl.textprocessors.crude_tokeniser("to be, or not to be.")
	
This will result in:

	tokens == ['to','be',',','or','not','to','be','.']

  
N-gram extraction
------------------

The extraction of n-grams is an elemental operation in Natural Language Processing. PyNLPl offers the ``Windower`` class to accomplish this task::

	tokens = pynlpl.textprocessors.crude_tokeniser("to be or not to be")
	for trigram in Windower(tokens,3):
		print trigram
		
The input to the Windower should be a list of words and a value for n. In addition, the windower can output extra symbols at the beginning of the input sequence and at the end of it. By default, this behaviour is enabled and the input symbol is ``<begin>``, whereas the output symbol is ``<end>``. If this behaviour is unwanted you can suppress it by instantiating the Windower as follows::

	Windower(tokens,3, None, None)

The Windower is implemented as a Python generator and at each iteration yields a tuple of length n.


.. automodule:: pynlpl.textprocessors
    :members:
    :undoc-members:
