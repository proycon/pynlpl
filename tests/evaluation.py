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

from pynlpl.evaluation import AbstractExperiment, WPSParamSearch

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

class WPSTest(unittest.TestCase):
    def test_wps(self):
        inputdata = [ 1,2,3,4,5,6 ]
        parameterscope = [ ('a',[2,4]), ('b',[2,5,8]),  ('c',[3,6,9]) ]
        search = WPSParamSearch(ParamExperiment, inputdata, parameterscope)
        solution = search.searchbest()
        self.assertEqual(solution,  (('a', 4), ('b', 8), ('c', 3)) ) 



if __name__ == '__main__':
    unittest.main()


