
###############################################################9
# PyNLPl - Algorithms
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#       Licensed under GPLv3
#
###############################################################

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

def sum_to_n(n, size, limit=None): #from http://stackoverflow.com/questions/2065553/python-get-all-numbers-that-add-up-to-a-number
    """Produce all lists of `size` positive integers in decreasing order
    that add up to `n`."""
    if size == 1:
        yield [n]
        return
    if limit is None:
        limit = n
    start = (n + size - 1) // size
    stop = min(limit, n - size + 1) + 1
    for i in range(start, stop):
        for tail in sum_to_n(n - i, size - 1, i):
            yield [i] + tail


def consecutivegaps(n, leftmargin = 0, rightmargin = 0):
    """Compute all possible single consecutive gaps in any sequence of the specified length. Returns
    (beginindex, length) tuples. Runs in  O(n(n+1) / 2) time. Argument is the length of the sequence rather than the sequence itself"""
    begin = leftmargin
    while begin < n:
        length = (n - rightmargin) - begin
        while length > 0:
            yield (begin, length)
            length -= 1
        begin += 1


def bytesize(n):
    """Return the required size in bytes to encode the specified integer"""
    for i in range(1, 1000):
        if n < 2**(8*i):
            return i




