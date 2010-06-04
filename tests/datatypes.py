#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import unittest

sys.path.append(sys.path[0] + '/../../')
os.environ['PYTHONPATH'] = sys.path[0] + '/../../'

from pynlpl.datatypes import PriorityQueue

values = [3,6,6,1,8,2]
mintomax = sorted(values)
maxtomin = list(reversed(mintomax))

class PriorityQueueTest(unittest.TestCase):
    def test_append_minimized(self):
        """Minimized PriorityQueue"""
        global values
        pq = PriorityQueue(values, lambda x: x, True,False,False)
        result = list(iter(pq))
        self.assertEqual(result, mintomax)

    def test_append_maximized(self):
        """Maximized PriorityQueue"""
        global values
        pq = PriorityQueue(values, lambda x: x, False,False,False)
        result = list(iter(pq))
        self.assertEqual(result, maxtomin)

    def test_append_maximized_blockworse(self):
        """Maximized PriorityQueue (with blockworse)"""
        global values
        pq = PriorityQueue(values, lambda x: x, False,True,False)
        result = list(iter(pq))
        self.assertEqual(result, [8,6,6,3])

    def test_append_maximized_blockworse_blockequal(self):
        """Maximized PriorityQueue (with blockworse + blockequal)"""
        global values
        pq = PriorityQueue(values, lambda x: x, False,True,True)
        result = list(iter(pq))
        self.assertEqual(result, [8,6,3])

    def test_append_minimized_blockworse(self):
        """Minimized PriorityQueue (with blockworse)"""
        global values
        pq = PriorityQueue(values, lambda x: x, True,True,False)
        result = list(iter(pq))
        self.assertEqual(result, [1,3])


if __name__ == '__main__':
    unittest.main()
