###############################################################
#  PyNLPl - Evaluation Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
# This is a Python library classes and functions for evaluation
#
###############################################################    

import subprocess
import itertools
import os


class AbstractExperiment:

    def __init__(self, inputdata = None, **parameters):
        self.inputdata = inputdata
        self.parameters = AbstractExperiment.defaultparameters()
        for parameter, value in parameters.items():
            self.parameters[parameter] = value

    @staticmethod
    def defaultparameters():
        return {}

    def run(self):
        raise Exception("Not implemented yet, make sure to overload this method")

    def runcommand(self, command, *arguments, **parameters):
        cmd = command
        if arguments:
            cmd += ' ' + " ".join(arguments)
        if parameters:
            for key, value in parameters.items():
              cmd += ' ' + key + ' ' + str(value)
        process = subprocess.Popen(cmd, shell=True)
        process.communicate() #TODO: verify and catch stdout, stderr
        #pid = process.pid
        #os.waitpid(pid, 0) #wait for process to finish


    def score(self):
        raise Exception("Not implemented yet, make sure to overload this method")

    def stdout(self):
        #TODO: return standard output
        pass

    def stderr(self):
        #TODO: return error output
        pass

    @staticmethod
    def sample(inputdata, n):
        """Return a sample of the input data"""
        raise Exception("Not implemented yet, make sure to overload this method")


class WPSParamSearch:
    def __init__(self, experimentclass, inputdata, parameterscope, sizefunc=None, prunefunc=None): #parameterscope: {'parameter':[values]}
        self.ExperimentClass = experimentclass
        self.inputdata = inputdata

        self.maxsize = len(inputdata)

        if sizefunc != None:
            self.sizefunc = sizefunc
        else:
            self.sizefunc = lambda i, maxsize: round(i/10.0 * maxsize)

        #prunefunc should return a number between 0 and 1, indicating how much is pruned. (for example: 0.75 prunes three/fourth of all combinations, retaining only 25%)
        if prunefunc != None:    
            self.prunefunc = prunefunc
        else:
            self.prunefunc = lambda i: 0.5

        #compute all parameter combinations:
        verboseparameterscope = [ self._combine(x,y) for x,y in parameterscope ]
        self.parametercombinations = [ (x,0) for x in itertools.product(*verboseparameterscope) ] #generator
        #print list(iter(self.parametercombinations))

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

    def __iter__(self):
        i = 0
        while True:
            i += 1

            #sample size elements from inputdata
            size = int(self.sizefunc(i, self.maxsize))
            if size > self.maxsize:
                break

            #print "SAMPLING SIZE:",size
            data = self.ExperimentClass.sample(self.inputdata, size)

            #run on ALL available parameter combinations and retrieve score
            newparametercombinations = []
            for parameters,score in self.parametercombinations:
                    #print "PARAMS:",parameters
                    #print "SCORE:",score
                    #set up the experiment for this run
                    experiment = self.ExperimentClass(data, **dict(parameters))
                    experiment.run()
                    newparametercombinations.append( (parameters, experiment.score()) )

            #prune the combinations, keeping only the best
            prune = int(round(self.prunefunc(i) * len(newparametercombinations)))
            #print "PRUNE:",prune
            self.parametercombinations = sorted(newparametercombinations, key=lambda v: v[1])[prune:]

            yield [ x[0] for x in self.parametercombinations ]
            if len(self.parametercombinations) <= 1:
                break

