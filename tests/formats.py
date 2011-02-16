import sys
import os
import unittest

sys.path.append(sys.path[0] + '/../../')
os.environ['PYTHONPATH'] = sys.path[0] + '/../../'
from pynlpl.formats.timbl import TimblOutput
from StringIO import StringIO

class TimblTest(unittest.TestCase):
    
    def test1_simple(self):
        """Timbl - simple output"""
        s = StringIO("a b ? c\nc d ? e\n")
        for i, (features, referenceclass, predictedclass, distribution, distance) in enumerate(TimblOutput(s)):
            if i == 0:
                self.assertEqual(features,['a','b'])
                self.assertEqual(referenceclass,'?')
                self.assertEqual(predictedclass,'c')
                self.assertEqual(distribution,None)
                self.assertEqual(distance,None)
            elif i == 1:
                self.assertEqual(features,['c','d'])
                self.assertEqual(referenceclass,'?')
                self.assertEqual(predictedclass,'e')
                self.assertEqual(distribution,None)
                self.assertEqual(distance,None)            
                        

            
        
