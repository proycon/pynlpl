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
    def test_minimizeC1(self):
        """Beam Search needle-in-haystack problem (beam=2, minimize)"""
        #beamsize has been set to the minimum that yields the correct solution
        global informedinputstate, solution, goalstate
        search = BeamSearch(informedinputstate, beamsize=2, graph=True, minimize=True,debug=0, goal=goalstate)
        solution = search.searchbest()
        self.assertEqual( str(solution), str(goalstate) )
        self.assertEqual( search.solutions, 1 )
    
    
    def test_minimizeA1(self):
        """Beam Search optimisation problem A (beam=2, minimize)"""
        #beamsize has been set to the minimum that yields the correct solution
        global informedinputstate, solution, goalstate
        search = BeamSearch(informedinputstate, beamsize=2, graph=True, minimize=True,debug=0)
        solution = search.searchbest()
        self.assertEqual( str(solution), str(goalstate) )
        self.assertTrue( search.solutions > 1 ) #everything is a solution

        
    def test_minimizeA2(self):
        """Beam Search optimisation problem A (beam=100, minimize)"""
        #if a small beamsize works, a very large one should too
        global informedinputstate, solution, goalstate
        search = BeamSearch(informedinputstate, beamsize=100, graph=True, minimize=True,debug=0)
        solution = search.searchbest()
        self.assertEqual( str(solution), str(goalstate) )   
        self.assertTrue( search.solutions > 1 ) #everything is a solution
    
    #def test_minimizeA3(self):    
    #    """Beam Search optimisation problem A (eager mode, beam=2, minimize)"""
    #    #beamsize has been set to the minimum that yields the correct solution
    #    global informedinputstate, solution, goalstate
    #    search = BeamSearch(informedinputstate, beamsize=50, graph=True, minimize=True,eager=True,debug=2)
    #    solution = search.searchbest()
    #    self.assertEqual( str(solution), str(goalstate) )


    def test_minimizeB1(self):
        """Beam Search optimisation problem (longer) (beam=3, minimize)"""
        #beamsize has been set to the minimum that yields the correct solution
        goalstate = InformedReorderSearchState("This is supposed to be a very long sentence .".split(' '))
        informedinputstate = InformedReorderSearchState("a long very . sentence supposed to be This is".split(' '), goalstate)
        search = BeamSearch(informedinputstate, beamsize=3, graph=True, minimize=True,debug=False)
        solution = search.searchbest()
        self.assertEqual(str(solution),str(goalstate))
        
        

if __name__ == '__main__':
    unittest.main()



