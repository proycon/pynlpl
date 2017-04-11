#!/usr/bin/env python
#-*- coding:utf-8 -*-

#---------------------------------------------------------------
# PyNLPl - Test Units for Evaluation
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#-------------------------------------------------------------

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import u

import sys
import os
import unittest
import random

from pynlpl.evaluation import AbstractExperiment, WPSParamSearch, ExperimentPool, ClassEvaluation, OrdinalEvaluation

class ParamExperiment(AbstractExperiment):
    def defaultparameters(self):
        return {'a':1,'b':1,'c':1}

    def run(self):
        self.result = 0
        for line in self.inputdata:
            self.result += int(line) * self.parameters['a'] * self.parameters['b'] - self.parameters['c']

    def score(self):
        return self.result

    @staticmethod
    def sample(inputdata,n):
        n = int(n)
        if n > len(inputdata):
            return inputdata
        else:
            return random.sample(inputdata,int(n))

class PoolExperiment(AbstractExperiment):
    def start(self):
        self.startcommand('sleep',None,None,None,str(self.parameters['duration']))
        print("STARTING: sleep " + str(self.parameters['duration']))


class WPSTest(unittest.TestCase):
    def test_wps(self):
        inputdata = [ 1,2,3,4,5,6 ]
        parameterscope = [ ('a',[2,4]), ('b',[2,5,8]),  ('c',[3,6,9]) ]
        search = WPSParamSearch(ParamExperiment, inputdata, len(inputdata), parameterscope)
        solution = search.searchbest()
        self.assertEqual(solution,  (('a', 4), ('b', 8), ('c', 3)) )



class ExperimentPoolTest(unittest.TestCase):
    def test_pool(self):
        pool = ExperimentPool(4)
        for i in range(0,15):
            pool.append( PoolExperiment(None, duration=random.randint(1,6)) )
        for experiment in pool.run():
            print("DONE: sleep " + str(experiment.parameters['duration']))
        
        self.assertTrue(True) #if we got here, no exceptions were raised and it's okay 
        
class ClassEvaluationTest2(unittest.TestCase):
    def setUp(self):
        self.goals = ['sun','sun','rain','cloudy','sun','rain']
        self.observations = ['cloudy','cloudy','cloudy','rain','sun','sun']
    
       
    def test001(self):
        e = ClassEvaluation(self.goals, self.observations)
        print()
        print(e)
        print(e.confusionmatrix())

class OrdinalEvaluationTest(unittest.TestCase):
    def setUp(self):
        self.goals = [1,2,3,4,3,2]
        self.observations = [4,1,3,4,2,2]

    def test001(self):
        oe = OrdinalEvaluation(self.goals,self.observations)
        print(oe.mae())
        print(oe.mae(2))
        print(oe.rmse())
        print(oe.rmse(4))
    
class ClassEvaluationTest(unittest.TestCase):
    def setUp(self):
        self.goals =        ['cat','cat','cat','cat','cat','cat','cat','cat',    'dog',  'dog','dog','dog','dog','dog'      ,'rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit']
        self.observations = ['cat','cat','cat','cat','cat','dog','dog','dog',  'cat','cat','rabbit','dog','dog','dog'   ,'rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','dog','dog']
    
        
    def test001(self):
        """Class evaluation test -- (See also http://en.wikipedia.org/wiki/Confusion_matrix , using same data)"""
        e = ClassEvaluation(self.goals, self.observations)
        
        print
        print(e)
        print(e.confusionmatrix())
    
                
        self.assertEqual(e.tp['cat'], 5)
        self.assertEqual(e.fp['cat'], 2)
        self.assertEqual(e.tn['cat'], 17)
        self.assertEqual(e.fn['cat'], 3)
        
        self.assertEqual(e.tp['rabbit'], 11)
        self.assertEqual(e.fp['rabbit'], 1)
        self.assertEqual(e.tn['rabbit'], 13)
        self.assertEqual(e.fn['rabbit'], 2)
        
        self.assertEqual(e.tp['dog'], 3)
        self.assertEqual(e.fp['dog'], 5)
        self.assertEqual(e.tn['dog'], 16)
        self.assertEqual(e.fn['dog'], 3)
        
        self.assertEqual( round(e.precision('cat'),6), 0.714286)
        self.assertEqual( round(e.precision('rabbit'),6), 0.916667)
        self.assertEqual( round(e.precision('dog'),6), 0.375000)

        self.assertEqual( round(e.recall('cat'),6), 0.625000)
        self.assertEqual( round(e.recall('rabbit'),6), 0.846154)
        self.assertEqual( round(e.recall('dog'),6),0.500000)

        self.assertEqual( round(e.fscore('cat'),6), 0.666667)
        self.assertEqual( round(e.fscore('rabbit'),6), 0.880000)
        self.assertEqual( round(e.fscore('dog'),6),0.428571)

        self.assertEqual( round(e.accuracy(),6), 0.703704)
        
        

if __name__ == '__main__':
    unittest.main()


