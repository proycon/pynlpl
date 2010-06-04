#!/usr/bin/env python
#-*- coding:utf-8 -*-


#---------------------------------------------------------------
# PyNLPl - Test Units for Search Algorithms
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

import sys
import os
import unittest


sys.path.append(sys.path[0] + '/../../')
os.environ['PYTHONPATH'] = sys.path[0] + '/../../'

from pynlpl.search import AbstractSearchState, DepthFirstSearch, BreadthFirstSearch, IterativeDeepening

class ReorderSearchState(AbstractSearchState):
    def __init__(self, tokens, parent = None, goalstates = None):
        self.tokens = tokens
        super(ReorderSearchState, self).__init__(parent, goalstates)

    def expand(self):
        #Operator: Swap two consecutive pairs
        l = len(self.tokens)
        for i in range(0,l - 1):
            newtokens = self.tokens[:i]
            newtokens.append(self.tokens[i + 1])
            newtokens.append(self.tokens[i])
            if i+2 < l:
                newtokens += self.tokens[i+2:]
            yield ReorderSearchState(newtokens, self)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        return " ".join(self.tokens)


inputstate = ReorderSearchState("a This test . sentence is".split(' '))
goalstate = ReorderSearchState("This is a test sentence .".split(' '))

class DepthFirstSearchTest(unittest.TestCase):
    def test_solution(self):
        global inputstate, goalstate
        search = DepthFirstSearch(inputstate ,graph=True, goal=goalstate)
        solution = search.searchone()
        self.assertEqual(solution, goalstate)


class BreadthFirstSearchTest(unittest.TestCase):
    def test_solution(self):
        global inputstate, goalstate
        search = BreadthFirstSearch(inputstate ,graph=True, goal=goalstate)
        solution = search.searchone()
        self.assertEqual(solution, goalstate)

class IterativeDeepeningTest(unittest.TestCase):
    def test_solution(self):
        global inputstate, goalstate
        search = IterativeDeepening(inputstate ,graph=True, goal=goalstate)
        solution = search.searchone()
        self.assertEqual(solution, goalstate)

if __name__ == '__main__':
    unittest.main()



