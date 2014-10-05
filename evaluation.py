###############################################################
#  PyNLPl - Evaluation Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
# This is a Python library with classes and functions for evaluation
# and experiments .
#
###############################################################

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import u
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout
import io


from pynlpl.statistics import FrequencyList
from collections import defaultdict
import numpy as np
import subprocess
import itertools
import time
import random
import copy
import datetime
import os.path


def auc(x, y, reorder=False): #from sklearn, http://scikit-learn.org, licensed under BSD License
    """Compute Area Under the Curve (AUC) using the trapezoidal rule

    This is a general fuction, given points on a curve.  For computing the area
    under the ROC-curve, see :func:`auc_score`.

    Parameters
    ----------
    x : array, shape = [n]
        x coordinates.

    y : array, shape = [n]
        y coordinates.

    reorder : boolean, optional (default=False)
        If True, assume that the curve is ascending in the case of ties, as for
        an ROC curve. If the curve is non-ascending, the result will be wrong.

    Returns
    -------
    auc : float

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn import metrics
    >>> y = np.array([1, 1, 2, 2])
    >>> pred = np.array([0.1, 0.4, 0.35, 0.8])
    >>> fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=2)
    >>> metrics.auc(fpr, tpr)
    0.75

    See also
    --------
    auc_score : Computes the area under the ROC curve

    """
    # XXX: Consider using  ``scipy.integrate`` instead, or moving to
    # ``utils.extmath``
    if not isinstance(x, np.ndarray): x = np.array(x)
    if not isinstance(x, np.ndarray): y = np.array(y)
    if x.shape[0] < 2:
        raise ValueError('At least 2 points are needed to compute'
                         ' area under curve, but x.shape = %s' % x.shape)

    if reorder:
        # reorder the data points according to the x axis and using y to
        # break ties
        x, y = np.array(sorted(points for points in zip(x, y))).T
        h = np.diff(x)
    else:
        h = np.diff(x)
        if np.any(h < 0):
            h *= -1
            assert not np.any(h < 0), ("Reordering is not turned on, and "
                                       "The x array is not increasing: %s" % x)

    area = np.sum(h * (y[1:] + y[:-1])) / 2.0
    return area


class ProcessFailed(Exception):
    pass


class ConfusionMatrix(FrequencyList):
    """Confusion Matrix"""

    def __str__(self):
        """Print Confusion Matrix in table form"""
        o = "== Confusion Matrix == (hor: goals, vert: observations)\n\n"

        keys = sorted( set( ( x[1] for x in self._count.keys()) ) )

        linemask = "%20s"
        cells = ['']
        for keyH in keys:
                l = len(keyH)
                if l < 4:
                    l = 4
                elif l > 15:
                    l = 15

                linemask += " %" + str(l) + "s"
                cells.append(keyH)
        linemask += "\n"
        o += linemask % tuple(cells)

        for keyV in keys:
            linemask = "%20s"
            cells = [keyV]
            for keyH in keys:
                l = len(keyH)
                if l < 4:
                    l = 4
                elif l > 15:
                    l = 15
                linemask += " %" + str(l) + "d"
                try:
                    count = self._count[(keyH, keyV)]
                except:
                    count = 0
                cells.append(count)
            linemask += "\n"
            o += linemask % tuple(cells)

        return o




class ClassEvaluation(object):
    def __init__(self,  goals = [], observations = [], missing = {}, encoding ='utf-8'):
        assert len(observations) == len(goals)
        self.observations = copy.copy(observations)
        self.goals = copy.copy(goals)

        self.classes = set(self.observations + self.goals)

        self.tp = defaultdict(int)
        self.fp = defaultdict(int)
        self.tn = defaultdict(int)
        self.fn = defaultdict(int)
        self.missing = missing

        self.encoding = encoding

        self.computed = False

        if self.observations:
            self.compute()

    def append(self, goal, observation):
        self.goals.append(goal)
        self.observations.append(observation)
        self.classes.add(goal)
        self.classes.add(observation)
        self.computed = False

    def precision(self, cls=None, macro=False):
        if not self.computed: self.compute()
        if cls:
            if self.tp[cls] + self.fp[cls] > 0:
                return self.tp[cls] / (self.tp[cls] + self.fp[cls])
            else:
                #return float('nan')
                return 0
        else:
            if len(self.observations) > 0:
                if macro:
                    return sum( ( self.precision(x) for x in set(self.goals) ) ) / len(set(self.classes))
                else:
                    return sum( ( self.precision(x) for x in self.goals ) ) / len(self.goals)
            else:
                #return float('nan')
                return 0

    def recall(self, cls=None, macro=False):
        if not self.computed: self.compute()
        if cls:
            if self.tp[cls] + self.fn[cls] > 0:
                return self.tp[cls] / (self.tp[cls] + self.fn[cls])
            else:
                #return float('nan')
                return 0
        else:
            if len(self.observations) > 0:
                if macro:
                    return sum( ( self.recall(x) for x in set(self.goals) ) ) / len(set(self.classes))
                else:
                    return sum( ( self.recall(x) for x in self.goals ) ) / len(self.goals)
            else:
                #return float('nan')
                return 0

    def specificity(self, cls=None, macro=False):
        if not self.computed: self.compute()
        if cls:
            if self.tn[cls] + self.fp[cls] > 0:
                return self.tn[cls] / (self.tn[cls] + self.fp[cls])
            else:
                #return float('nan')
                return 0
        else:
            if len(self.observations) > 0:
                if macro:
                    return sum( ( self.specificity(x) for x in set(self.goals) ) ) / len(set(self.classes))
                else:
                    return sum( ( self.specificity(x) for x in self.goals ) ) / len(self.goals)
            else:
                #return float('nan')
                return 0

    def accuracy(self, cls=None):
        if not self.computed: self.compute()
        if cls:
            if self.tp[cls] + self.tn[cls] + self.fp[cls] + self.fn[cls] > 0:
                return (self.tp[cls]+self.tn[cls]) / (self.tp[cls] + self.tn[cls] + self.fp[cls] + self.fn[cls])
            else:
                #return float('nan')
                return 0
        else:
            if len(self.observations) > 0:
                return sum( ( self.tp[x] for x in self.tp ) ) / len(self.observations)
            else:
                #return float('nan')
                return 0

    def fscore(self, cls=None, beta=1, macro=False):
        if not self.computed: self.compute()
        if cls:
            prec = self.precision(cls)
            rec =  self.recall(cls)
            if prec * rec > 0:
                return (1 + beta*beta) * ((prec * rec) / (beta*beta * prec + rec))
            else:
                #return float('nan')
                return 0
        else:
            if len(self.observations) > 0:
                if macro:
                    return sum( ( self.fscore(x,beta) for x in set(self.goals) ) ) / len(set(self.classes))
                else:
                    return sum( ( self.fscore(x,beta) for x in self.goals ) ) / len(self.goals)
            else:
                #return float('nan')
                return 0

    def tp_rate(self, cls=None, macro=False):
        if not self.computed: self.compute()
        if cls:
            if self.tp[cls] > 0:
                return self.tp[cls] / (self.tp[cls] + self.fn[cls])
            else:
                return 0
        else:
            if len(self.observations) > 0:
                if macro:
                    return sum( ( self.tp_rate(x) for x in set(self.goals) ) ) / len(set(self.classes))
                else:
                    return sum( ( self.tp_rate(x) for x in self.goals ) ) / len(self.goals)
            else:
                #return float('nan')
                return 0

    def fp_rate(self, cls=None, macro=False):
        if not self.computed: self.compute()
        if cls:
            if self.fp[cls] > 0:
                return self.fp[cls] / (self.tn[cls] + self.fp[cls])
            else:
                return 0
        else:
            if len(self.observations) > 0:
                if macro:
                    return sum( ( self.fp_rate(x) for x in set(self.goals) ) ) / len(set(self.classes))
                else:
                    return sum( ( self.fp_rate(x) for x in self.goals ) ) / len(self.goals)
            else:
                #return float('nan')
                return 0

    def auc(self, cls=None, macro=False):
        if not self.computed: self.compute()
        if cls:
            tpr = self.tp_rate(cls)
            fpr =  self.fp_rate(cls)
            return auc([0,fpr,1], [0,tpr,1])
        else:
            if len(self.observations) > 0:
                if macro:
                    return sum( ( self.auc(x) for x in set(self.goals) ) ) / len(set(self.classes))
                else:
                    return sum( ( self.auc(x) for x in self.goals ) ) / len(self.goals)
            else:
                #return float('nan')
                return 0

    def __iter__(self):
        for g,o in zip(self.goals, self.observations):
             yield g,o

    def compute(self):
        self.tp = defaultdict(int)
        self.fp = defaultdict(int)
        self.tn = defaultdict(int)
        self.fn = defaultdict(int)
        for cls, count in self.missing.items():
            self.fn[cls] = count

        for goal, observation in self:
            if goal == observation:
                self.tp[observation] += 1
            elif goal != observation:
                self.fp[observation] += 1
                self.fn[goal] += 1


        l = len(self.goals) + sum(self.missing.values())
        for o in self.classes:
            self.tn[o] = l - self.tp[o] - self.fp[o] - self.fn[o]

        self.computed = True


    def confusionmatrix(self, casesensitive =True):
        return ConfusionMatrix(zip(self.goals, self.observations), casesensitive)

    def outputmetrics(self):
        o = "Accuracy:              " + str(self.accuracy()) + "\n"
        o += "Samples:               " + str(len(self.goals)) + "\n"
        o += "Correct:               " + str(sum(  ( self.tp[x] for x in set(self.goals)) ) ) + "\n"
        o += "Recall      (microav): "+ str(self.recall()) + "\n"
        o += "Recall      (macroav): "+ str(self.recall(None,True)) + "\n"
        o += "Precision   (microav): " + str(self.precision()) + "\n"
        o += "Precision   (macroav): "+ str(self.precision(None,True)) + "\n"
        o += "Specificity (microav): " + str(self.specificity()) + "\n"
        o += "Specificity (macroav): "+ str(self.specificity(None,True)) + "\n"
        o += "F-score1    (microav): " + str(self.fscore()) + "\n"
        o += "F-score1    (macroav): " + str(self.fscore(None,1,True)) + "\n"
        return o


    def __str__(self):
        if not self.computed: self.compute()
        o =  "%-15s TP\tFP\tTN\tFN\tAccuracy\tPrecision\tRecall(TPR)\tSpecificity(TNR)\tF-score\n" % ("")
        for cls in sorted(set(self.classes)):
            cls = u(cls)
            o += "%-15s %d\t%d\t%d\t%d\t%4f\t%4f\t%4f\t%4f\t%4f\n" % (cls, self.tp[cls], self.fp[cls], self.tn[cls], self.fn[cls], self.accuracy(cls), self.precision(cls), self.recall(cls),self.specificity(cls),  self.fscore(cls) )
        return o + "\n" + self.outputmetrics()

    def __unicode__(self): #Python 2.x
        return str(self)


class AbstractExperiment(object):

    def __init__(self, inputdata = None, **parameters):
        self.inputdata = inputdata
        self.parameters = self.defaultparameters()
        for parameter, value in parameters.items():
            self.parameters[parameter] = value
        self.process = None
        self.creationtime = datetime.datetime.now()
        self.begintime = self.endtime = 0

    def defaultparameters(self):
        return {}

    def duration(self):
        if self.endtime and self.begintime:
            return self.endtime - self.begintime
        else:
            return 0

    def start(self):
        """Start as a detached subprocess, immediately returning execution to caller."""
        raise Exception("Not implemented yet, make sure to overload the start() method in your Experiment class")

    def done(self, warn=True):
        """Is the subprocess done?"""
        if not self.process:
            raise Exception("Not implemented yet or process not started yet, make sure to overload the done() method in your Experiment class")
        self.process.poll()
        if self.process.returncode == None:
            return False
        elif self.process.returncode > 0:
            raise ProcessFailed()
        else:
            self.endtime = datetime.datetime.now()
            return True

    def run(self):
        if hasattr(self,'start'):
            self.start()
            self.wait()
        else:
            raise Exception("Not implemented yet, make sure to overload the run() method!")

    def startcommand(self, command, cwd, stdout, stderr, *arguments, **parameters):
        argdelimiter=' '
        printcommand = True

        cmd = command
        if arguments:
            cmd += ' ' + " ".join([ u(x) for x in arguments])
        if parameters:
            for key, value in parameters.items():
                if key == 'argdelimiter':
                    argdelimiter = value
                elif key == 'printcommand':
                    printcommand = value
                elif isinstance(value, bool) and value == True:
                    cmd += ' ' + key
                elif key[-1] != '=':
                    cmd += ' ' + key + argdelimiter + str(value)
                else:
                    cmd += ' ' + key + str(value)
        if printcommand:
            print("STARTING COMMAND: " + cmd, file=stderr)

        self.begintime = datetime.datetime.now()
        if not cwd:
            self.process = subprocess.Popen(cmd, shell=True,stdout=stdout,stderr=stderr)
        else:
            self.process = subprocess.Popen(cmd, shell=True,cwd=cwd,stdout=stdout,stderr=stderr)
        #pid = process.pid
        #os.waitpid(pid, 0) #wait for process to finish
        return self.process

    def wait(self):
        while not self.done():
           time.sleep(1)
           pass

    def score(self):
        raise Exception("Not implemented yet, make sure to overload the score() method")


    def delete(self):
        pass

    def sample(self, size):
        """Return a sample of the input data"""
        raise Exception("Not implemented yet, make sure to overload the sample() method")

class ExperimentPool(object):
    def __init__(self, size):
        self.size = size
        self.queue = []
        self.running = []

    def append(self, experiment):
        assert isinstance(experiment, AbstractExperiment)
        self.queue.append( experiment )

    def __len__(self):
        return len(self.queue)

    def __iter__(self):
        return iter(self.queue)

    def start(self, experiment):
        experiment.start()
        self.running.append( experiment )

    def poll(self, haltonerror=True):
        done = []
        for experiment in self.running:
            try:
                if experiment.done():
                    done.append( experiment )
            except ProcessFailed:
                print("ERROR: One experiment in the pool failed: " + repr(experiment.inputdata) + repr(experiment.parameters), file=stderr)
                if haltonerror:
                    raise
                else:
                    done.append( experiment )
        for experiment in done:
                self.running.remove( experiment )
        return done

    def run(self, haltonerror=True):
        while True:
            #check how many processes are done
            done = self.poll(haltonerror)

            for experiment in done:
                yield experiment
            #start new processes
            while self.queue and len(self.running) < self.size:
                self.start( self.queue.pop(0) )
            if not self.queue and not self.running:
                break



class WPSParamSearch(object):
    """ParamSearch with support for Wrapped Progressive Sampling"""

    def __init__(self, experimentclass, inputdata, size, parameterscope, poolsize=1, sizefunc=None, prunefunc=None, constraintfunc = None, delete=True): #parameterscope: {'parameter':[values]}
        self.ExperimentClass = experimentclass
        self.inputdata = inputdata
        self.poolsize = poolsize #0 or 1: sequential execution (uses experiment.run() ), >1: parallel execution using ExperimentPool (uses experiment.start() )
        self.maxsize = size
        self.delete = delete #delete intermediate experiments

        if self.maxsize == -1:
            self.sizefunc = lambda x,y: self.maxsize
        else:
            if sizefunc != None:
                self.sizefunc = sizefunc
            else:
                self.sizefunc = lambda i, maxsize: round((maxsize/100.0)*i*i)

        #prunefunc should return a number between 0 and 1, indicating how much is pruned. (for example: 0.75 prunes three/fourth of all combinations, retaining only 25%)
        if prunefunc != None:
            self.prunefunc = prunefunc
        else:
            self.prunefunc = lambda i: 0.5

        if constraintfunc != None:
            self.constraintfunc = constraintfunc
        else:
            self.constraintfunc = lambda x: True

        #compute all parameter combinations:
        if isinstance(parameterscope, dict):
            verboseparameterscope = [ self._combine(x,y) for x,y in parameterscope.items() ]
        else:
            verboseparameterscope = [ self._combine(x,y) for x,y in parameterscope ]
        self.parametercombinations = [ (x,0) for x in itertools.product(*verboseparameterscope) if self.constraintfunc(dict(x)) ] #generator

    def _combine(self,name, values): #TODO: can't we do this inline in a list comprehension?
        l = []
        for value in values:
            l.append( (name, value) )
        return l

    def searchbest(self):
        solution = None
        for s in iter(self):
            solution = s
        return solution[0]


    def test(self,i=None):
        #sample size elements from inputdata
        if i is None or self.maxsize == -1:
            data = self.inputdata
        else:
            size = int(self.sizefunc(i, self.maxsize))
            if size > self.maxsize:
                return []

            data = self.ExperimentClass.sample(self.inputdata, size)


        #run on ALL available parameter combinations and retrieve score
        newparametercombinations = []
        if self.poolsize <= 1:
            #Don't use experiment pool, sequential execution
            for parameters,score in self.parametercombinations:
                experiment = self.ExperimentClass(data, **dict(parameters))
                experiment.run()
                newparametercombinations.append( (parameters, experiment.score()) )
                if self.delete:
                    experiment.delete()
        else:
            #Use experiment pool, parallel execution
            pool = ExperimentPool(self.poolsize)
            for parameters,score in self.parametercombinations:
                pool.append( self.ExperimentClass(data, **dict(parameters)) )
            for experiment in pool.run(False):
                newparametercombinations.append( (experiment.parameters, experiment.score()) )
                if self.delete:
                    experiment.delete()

        return newparametercombinations


    def __iter__(self):
        i = 0
        while True:
            i += 1

            newparametercombinations = self.test(i)

            #prune the combinations, keeping only the best
            prune = int(round(self.prunefunc(i) * len(newparametercombinations)))
            self.parametercombinations = sorted(newparametercombinations, key=lambda v: v[1])[prune:]

            yield [ x[0] for x in self.parametercombinations ]
            if len(self.parametercombinations) <= 1:
                break

class ParamSearch(WPSParamSearch):
    """A simpler version of ParamSearch without Wrapped Progressive Sampling"""
    def __init__(self, experimentclass, inputdata, parameterscope, poolsize=1, constraintfunc = None, delete=True): #parameterscope: {'parameter':[values]}
        prunefunc = lambda x: 0
        super(ParamSearch, self).__init__(experimentclass, inputdata, -1, parameterscope, poolsize, None,prunefunc, constraintfunc, delete)

    def __iter__(self):
         for parametercombination, score in sorted(self.test(), key=lambda v: v[1]):
             yield parametercombination, score


def filesampler(files, testsetsize = 0.1, devsetsize = 0, trainsetsize = 0, outputdir = '', encoding='utf-8'):
        """Extract a training set, test set and optimally a development set from one file, or multiple *interdependent* files (such as a parallel corpus). It is assumed each line contains one instance (such as a word or sentence for example)."""

        if not isinstance(files, list):
            files = list(files)

        total = 0
        for filename in files:
            f = io.open(filename,'r', encoding=encoding)
            count = 0
            for line in f:
                count += 1
            f.close()
            if total == 0:
                total = count
            elif total != count:
                raise Exception("Size mismatch, when multiple files are specified they must contain the exact same amount of lines! (" +str(count)  + " vs " + str(total) +")")

        #support for relative values:
        if testsetsize < 1:
            testsetsize = int(total * testsetsize)
        if devsetsize < 1 and devsetsize > 0:
            devsetsize = int(total * devsetsize)


        if testsetsize >= total or devsetsize >= total or testsetsize + devsetsize >= total:
            raise Exception("Test set and/or development set too large! No samples left for training set!")


        trainset = {}
        testset = {}
        devset = {}
        for i in range(1,total+1):
            trainset[i] = True
        for i in random.sample(trainset.keys(), testsetsize):
            testset[i] = True
            del trainset[i]

        if devsetsize > 0:
            for i in random.sample(trainset.keys(), devsetsize):
                devset[i] = True
                del trainset[i]

        if trainsetsize > 0:
            newtrainset = {}
            for i in random.sample(trainset.keys(), trainsetsize):
                newtrainset[i] = True
            trainset = newtrainset

        for filename in files:
            if not outputdir:
                ftrain = io.open(filename + '.train','w',encoding=encoding)
            else:
                ftrain = io.open(outputdir + '/' +  os.path.basename(filename) + '.train','w',encoding=encoding)
            if not outputdir:
                ftest = io.open(filename + '.test','w',encoding=encoding)
            else:
                ftest = io.open(outputdir + '/' + os.path.basename(filename) + '.test','w',encoding=encoding)
            if devsetsize > 0:
                if not outputdir:
                    fdev = io.open(filename + '.dev','w',encoding=encoding)
                else:
                    fdev = io.open(outputdir + '/' +  os.path.basename(filename) + '.dev','w',encoding=encoding)

            f = io.open(filename,'r',encoding=encoding)
            for linenum, line in enumerate(f):
                if linenum+1 in trainset:
                    ftrain.write(line)
                elif linenum+1 in testset:
                    ftest.write(line)
                elif devsetsize > 0 and linenum+1 in devset:
                    fdev.write(line)
            f.close()

            ftrain.close()
            ftest.close()
            if devsetsize > 0: fdev.close()




