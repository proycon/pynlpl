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


class AbstractExperiment(object):

    def __init__(self, inputdata = None, **parameters):
        self.inputdata = inputdata
        self.parameters = self.defaultparameters()
        for parameter, value in parameters.items():
            self.parameters[parameter] = value

    def defaultparameters(self):
        return {}

    def start(self):
        """Start as a detached subprocess, immediately returning execution to caller."""
        raise Exception("Not implemented yet, make sure to overload this method in your Experiment class")

    def done(self):
        """Is the subprocess done?"""
        self.process.poll()
        return (self.process.returncode != None)

    def run(self):
        raise Exception("Not implemented yet, make sure to overload this method")

    def runcommand(self, command, cwd, stdout, stderr, *arguments, **parameters):
        
        cmd = command
        if arguments:
            cmd += ' ' + " ".join(arguments)
        if parameters:
            for key, value in parameters.items():
              cmd += ' ' + key + ' ' + str(value)
        if not cwd:
            self.process = subprocess.Popen(cmd, shell=True,stdout=stdout,stderr=stderr)
        else:
            self.process = subprocess.Popen(cmd, shell=True,cwd=cwd,stdout=stdout,stderr=stderr)
        #pid = process.pid
        #os.waitpid(pid, 0) #wait for process to finish

    def wait(self):
        self.process.wait()

    def score(self):
        raise Exception("Not implemented yet, make sure to overload this method")

    def sample(self, size):
        """Return a sample of the input data"""
        raise Exception("Not implemented yet, make sure to overload this method")

class ExperimentPool:
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

    def poll(self):
        done = []
        for experiment in self.running:
            if experiment.done():
                done.append( experiment )
        for experiment in done:
                self.running.remove( experiment )
        return done

    def run(self):
        while True:
            #check how many processes are done
            done = self.poll()
            for experiment in done:
                yield experiment
            #start new processes
            while self.queue and len(self.running) < self.size:
                    self.start( self.queue.pop(0) )

            if not self.queue and not self.running:
                break



class WPSParamSearch:
    def __init__(self, experimentclass, inputdata, size, parameterscope, poolsize=1, sizefunc=None, prunefunc=None): #parameterscope: {'parameter':[values]}
        self.ExperimentClass = experimentclass
        self.inputdata = inputdata
        self.poolsize = poolsize #0 or 1: sequential execution (uses experiment.run() ), >1: parallel execution using ExperimentPool (uses experiment.start() )
        self.maxsize = size

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
            if self.poolsize <= 1:
                #Don't use experiment pool, sequential execution
                for parameters,score in self.parametercombinations:
                    experiment = self.ExperimentClass(data, **dict(parameters))
                    experiment.run()
                    newparametercombinations.append( (parameters, experiment.score()) )
            else:
                #Use experiment pool, parallel execution
                pool = ExperimentPool(self.poolsize)
                for parameters,score in self.parametercombinations:
                    pool.append( self.ExperimentClass(data, **dict(parameters)) )
                for experiment in pool.run():
                    newparametercombinations.append( (experiment.parameters, experiment.score()) )


            #prune the combinations, keeping only the best
            prune = int(round(self.prunefunc(i) * len(newparametercombinations)))
            self.parametercombinations = sorted(newparametercombinations, key=lambda v: v[1])[prune:]

            yield [ x[0] for x in self.parametercombinations ]
            if len(self.parametercombinations) <= 1:
                break

