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

import itertools

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

    def score(self):
        raise Exception("Not implemented yet, make sure to overload this method")

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
        
        if prunefunc != None:    
            self.prunefunc = prunefunc
        else:
            self.prunefunc = lambda i: 0.5

        #compute all parameter combinations:
        verboseparameterscope = [ self._combine(x) for x in self.parameterscope ]
        self.parametercombinations = list(itertools.product(*verboseparameterscope))

    def _combine(self,name, values):
        l = []
        for value in values:
            l.append( (name, value) )
        return l


    def __iter__(self):
        i = 0
        while True:
            i += 1

            #sample size elements from inputdata
            size = self.sizefunc(i, self.maxsize)

            data = self.ExperimentClass.sample(self.inputdata, size)

            #run on ALL available parameter combinations and retrieve score
            newparametercombinations = []
            for parameters, score in self.parametercombinations:
                experiment = self.ExperimentClass(data, **parameters)
                self.experiment.run()
                newparametercombinations.append( (parameters, self.experiment.score()) )

            #prune the combinations, keeping only the best
            prune = round(self.prunefunc(i) * len(newparametercombinations))
            parametercombinations = sorted(newparametercombinations, key=lambda v: v[1])[prune:]

