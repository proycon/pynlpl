#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import u

import os
import sys
import unittest


from pynlpl.datatypes import PriorityQueue

values = [3,6,6,1,8,2]
mintomax = sorted(values)
maxtomin = list(reversed(mintomax))


class PriorityQueueTest(unittest.TestCase):
    def test_append_minimized(self):
        """Minimized PriorityQueue"""
        global values
        pq = PriorityQueue(values, lambda x: x, True,0,False,False)
        result = list(iter(pq))
        self.assertEqual(result, mintomax)

    def test_append_maximized(self):
        """Maximized PriorityQueue"""
        global values
        pq = PriorityQueue(values, lambda x: x, False,0,False,False)
        result = list(iter(pq))
        self.assertEqual(result, maxtomin)

    def test_append_maximized_blockworse(self):
        """Maximized PriorityQueue (with blockworse)"""
        global values
        pq = PriorityQueue(values, lambda x: x, False,0,True,False)
        result = list(iter(pq))
        self.assertEqual(result, [8,6,6,3])

    def test_append_maximized_blockworse_blockequal(self):
        """Maximized PriorityQueue (with blockworse + blockequal)"""
        global values
        pq = PriorityQueue(values, lambda x: x, False,0,True,True)
        result = list(iter(pq))
        self.assertEqual(result, [8,6,3])

    def test_append_minimized_blockworse(self):
        """Minimized PriorityQueue (with blockworse)"""
        global values
        pq = PriorityQueue(values, lambda x: x, True,0,True,False)
        result = list(iter(pq))
        self.assertEqual(result, [1,3])
        

    def test_append_minimized_fixedlength(self):
        """Fixed-length priority queue (min)"""
        global values
        pq = PriorityQueue(values, lambda x: x, True,4, False,False)
        result = list(iter(pq))
        self.assertEqual(result, mintomax[:4])        

    def test_append_maximized_fixedlength(self):
        """Fixed-length priority queue (max)"""
        global values
        pq = PriorityQueue(values, lambda x: x, False,4,False,False)
        result = list(iter(pq))
        self.assertEqual(result, maxtomin[:4])                


if __name__ == '__main__':
    unittest.main()
