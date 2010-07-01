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
    def __init__(self, tokens, goal = None, parent = None):
        self.tokens = tokens
        self.goal = goal
        super(ReorderSearchState, self).__init__(parent)

    def score(self):
        """Compute distortion"""
        totaldistortion = 0
        for i, token in enumerate(self.goal.tokens):
            tokendistortion = 9999999
            for j, token2 in enumerate(self.tokens):
                if token == token2 and abs(i - j) < tokendistortion:
                    tokendistortion = abs(i - j)
            totaldistortion += tokendistortion
        return totaldistortion


    def expand(self):
        #Operator: Swap two consecutive pairs
        l = len(self.tokens)
        for i in range(0,l - 1):
            newtokens = self.tokens[:i]
            newtokens.append(self.tokens[i + 1])
            newtokens.append(self.tokens[i])
            if i+2 < l:
                newtokens += self.tokens[i+2:]
            yield InformedReorderSearchState(newtokens, self.goal, self)

inputstate = ReorderSearchState("a This test . sentence is".split(' '))
goalstate = ReorderSearchState("This is a test sentence .".split(' '))

class DepthFirstSearchTest(unittest.TestCase):
    def test_solution(self):
        """Depth First Search"""
        global inputstate, goalstate
        search = DepthFirstSearch(inputstate ,graph=True, goal=goalstate)
        solution = search.searchfirst()
        #print "DFS:", search.traversalsize(), "nodes visited |",
        self.assertEqual(solution, goalstate)




class BreadthFirstSearchTest(unittest.TestCase):
    def test_solution(self):
        """Breadth First Search"""
        global inputstate, goalstate
        search = BreadthFirstSearch(inputstate ,graph=True, goal=goalstate)
        solution = search.searchfirst()
        #print "BFS:", search.traversalsize(), "nodes visited |",
        self.assertEqual(solution, goalstate)


class IterativeDeepeningTest(unittest.TestCase):
    def test_solution(self):
        """Iterative Deepening DFS"""
        global inputstate, goalstate
        search = IterativeDeepening(inputstate ,graph=True, goal=goalstate)
        solution = search.searchfirst()
        #print "It.Deep:", search.traversalsize(), "nodes visited |",
        self.assertEqual(solution, goalstate)



informedinputstate = InformedReorderSearchState("a This test . sentence is".split(' '), goalstate)
#making a simple language model

class HillClimbingTest(unittest.TestCase):
    def test_solution(self):
        """Hill Climbing"""
        global informedinputstate
        search = HillClimbingSearch(informedinputstate, graph=True, minimize=True,debug=False)
        solution = search.searchbest()
        self.assertTrue(solution) #TODO: this is not a test!

class BeamSearchTest(unittest.TestCase):
    def test_minimize5(self):
        """Beam Search (size=5, minimize)"""
        global informedinputstate, solution, goalstate
        search = BeamSearch(informedinputstate, beamsize=5, graph=True, minimize=True,debug=False)
        solution = search.searchbest()
        self.assertEqual( str(solution), str(goalstate) )


    def test_minimize3(self):
        """Beam Search (beam=3, minimize)"""
        informedinputstate = InformedReorderSearchState("a long very . sentence supposed to be This is".split(' '), goalstate)
        search = BeamSearch(informedinputstate, beamsize=5, graph=True, minimize=False,debug=True)
        solution = search.searchbest()
        self.assertTrue(solution)

if __name__ == '__main__':
    unittest.main()



