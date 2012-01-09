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

import sys
import os
import unittest
import random

sys.path.append(sys.path[0] + '/../../')
os.environ['PYTHONPATH'] = sys.path[0] + '/../../'

from pynlpl.evaluation import AbstractExperiment, WPSParamSearch, ExperimentPool, ClassEvaluation

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
        self.runcommand('sleep',None,None,None,str(self.parameters['duration']))
        print "STARTING: sleep " + str(self.parameters['duration'])


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
            pool.append( PoolExperiment(None, duration=random.randint(1,60)) )
        for experiment in pool.run():
            print "DONE: sleep " + str(experiment.parameters['duration'])
        self.assertEqual(1, False) 
        
#class ClassEvaluationTest(unittest.TestCase):
#    def setUp(self):
#        self.goals = ['sun','sun','rain','cloudy','sun','rain']
#        self.observations = ['cloudy','cloudy','cloudy','rain','sun','sun']
#    
#        
#    def test001(self):
#        e = ClassEvaluation(self.goals, self.observations)
#        print
#        print e
#        print e.confusionmatrix()
    
    
class ClassEvaluationTest(unittest.TestCase):
    def setUp(self):
        self.goals =        ['cat','cat','cat','cat','cat','cat','cat','cat',    'dog',  'dog','dog','dog','dog','dog'      ,'rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit']
        self.observations = ['cat','cat','cat','cat','cat','dog','dog','dog',  'cat','cat','rabbit','dog','dog','dog'   ,'rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','rabbit','dog','dog']
    
        
    def test001(self):
        e = ClassEvaluation(self.goals, self.observations)
        print
        print e
        print e.confusionmatrix()
    

if __name__ == '__main__':
    unittest.main()


