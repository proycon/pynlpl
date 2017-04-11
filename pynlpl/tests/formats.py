import sys
import os
import unittest

sys.path.append(sys.path[0] + '/../../')
os.environ['PYTHONPATH'] = sys.path[0] + '/../../'
from pynlpl.formats.timbl import TimblOutput
if sys.version < '3':
    from StringIO import StringIO
else:
    from io import StringIO

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


    def test2_db(self):
        """Timbl - Distribution output"""
        s = StringIO("a c ? c { c 1.00000, d 1.00000 }\na b ? c { c 1.00000 }\na d ? c { c 1.00000, e 1.00000 }")
        for i, (features, referenceclass, predictedclass, distribution, distance) in enumerate(TimblOutput(s)):
            if i == 0:
                self.assertEqual(features,['a','c'])
                self.assertEqual(referenceclass,'?')
                self.assertEqual(predictedclass,'c')
                self.assertEqual(distribution['c'], 0.5)
                self.assertEqual(distribution['d'], 0.5)
                self.assertEqual(distance,None)
            elif i == 1:
                self.assertEqual(features,['a','b'])
                self.assertEqual(referenceclass,'?')
                self.assertEqual(predictedclass,'c')
                self.assertEqual(distribution['c'], 1)
                self.assertEqual(distance,None)
            elif i == 2:
                self.assertEqual(features,['a','d'])
                self.assertEqual(referenceclass,'?')
                self.assertEqual(predictedclass,'c')
                self.assertEqual(distribution['c'], 0.5)
                self.assertEqual(distribution['e'], 0.5)
                self.assertEqual(distance,None)


    def test3_dbdi(self):
        """Timbl - Distribution + Distance output"""
        s = StringIO("a c ? c { c 1.00000, d 1.00000 }        1.0000000000000\na b ? c { c 1.00000 }        0.0000000000000\na d ? c { c 1.00000, e 1.00000 }        1.0000000000000")
        for i, (features, referenceclass, predictedclass, distribution, distance) in enumerate(TimblOutput(s)):
            if i == 0:
                self.assertEqual(features,['a','c'])
                self.assertEqual(referenceclass,'?')
                self.assertEqual(predictedclass,'c')
                self.assertEqual(distribution['c'], 0.5)
                self.assertEqual(distribution['d'], 0.5)
                self.assertEqual(distance,1.0)
            elif i == 1:
                self.assertEqual(features,['a','b'])
                self.assertEqual(referenceclass,'?')
                self.assertEqual(predictedclass,'c')
                self.assertEqual(distribution['c'], 1)
                self.assertEqual(distance,0.0)
            elif i == 2:
                self.assertEqual(features,['a','d'])
                self.assertEqual(referenceclass,'?')
                self.assertEqual(predictedclass,'c')
                self.assertEqual(distribution['c'], 0.5)
                self.assertEqual(distribution['e'], 0.5)
                self.assertEqual(distance,1.0)
