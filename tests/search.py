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

from pynlpl.search import AbstractSearchState, DepthFirstSearch, BreadthFirstSearch, IterativeDeepening, HillClimbingSearch, BeamSearch
from pynlpl.lm.lm import SimpleLanguageModel

class ReorderSearchState(AbstractSearchState):
    def __init__(self, tokens, parent = None):
        self.tokens = tokens
        super(ReorderSearchState, self).__init__(parent)

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

class InformedReorderSearchState(ReorderSearchState):
    def __init__(self, tokens, goal = None, lm=None, parent = None):
        self.tokens = tokens
        self.goal = goal
        self.lm = lm
        super(ReorderSearchState, self).__init__(parent)

    def score(self):
        """Run through language model"""
        try:
            self.lm.scoresentence(self.tokens)
        except KeyError:
            return 0


    def expand(self):
        #Operator: Swap two consecutive pairs
        l = len(self.tokens)
        for i in range(0,l - 1):
            newtokens = self.tokens[:i]
            newtokens.append(self.tokens[i + 1])
            newtokens.append(self.tokens[i])
            if i+2 < l:
                newtokens += self.tokens[i+2:]
            yield InformedReorderSearchState(newtokens, self.goal, self.lm, self)


inputstate = ReorderSearchState("a This test . sentence is".split(' '))
goalstate = ReorderSearchState("This is a test sentence .".split(' '))

class DepthFirstSearchTest(unittest.TestCase):
    def test_solution(self):
        global inputstate, goalstate
        search = DepthFirstSearch(inputstate ,graph=True, goal=goalstate)
        solution = search.searchfirst()
        #print "DFS:", search.traversalsize(), "nodes visited |",
        self.assertEqual(solution, goalstate)




class BreadthFirstSearchTest(unittest.TestCase):
    def test_solution(self):
        global inputstate, goalstate
        search = BreadthFirstSearch(inputstate ,graph=True, goal=goalstate)
        solution = search.searchfirst()
        #print "BFS:", search.traversalsize(), "nodes visited |",
        self.assertEqual(solution, goalstate)


class IterativeDeepeningTest(unittest.TestCase):
    def test_solution(self):
        global inputstate, goalstate
        search = IterativeDeepening(inputstate ,graph=True, goal=goalstate)
        solution = search.searchfirst()
        #print "It.Deep:", search.traversalsize(), "nodes visited |",
        self.assertEqual(solution, goalstate)



lm = SimpleLanguageModel(2,False)
lm.append("This is a test sentence .")
informedinputstate = InformedReorderSearchState("a This test . sentence is".split(' '), lm)
#making a simple language model

class HillClimbingTest(unittest.TestCase):
    def test_solution(self):
        global informedinputstate
        search = HillClimbingSearch(informedinputstate, graph=True, minimize=True)
        for solution in search:
            print str(solution), solution.score()
        self.assertTrue(solution)


if __name__ == '__main__':
    unittest.main()



