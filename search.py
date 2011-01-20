#---------------------------------------------------------------
# PyNLPl - Search Algorithms
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

"""This module contains various search algorithms."""

from sys import stderr
from pynlpl.datatypes import FIFOQueue, PriorityQueue
from collections import deque

class AbstractSearchState(object):
    def __init__(self,  parent = None, cost = 0):
        self.parent = parent        
        self.cost = cost

    def test(self, goalstates = None):
        """Checks whether this state is a valid goal state, returns a boolean. If not goalstate is defined, then all states will test positively, this is what you usually want for optimisation problems."""
        if goalstates:
            return (self in goalstates)
        else:
            return True
            #raise Exception("Classes derived from AbstractSearchState must define a test() method!")

    def score(self):
        """Should return a heuristic value. This needs to be set if you plan to used an informed search algorithm."""
        raise Exception("Classes derived from AbstractSearchState must define a score() method if used in informed search algorithms!")

    def expand(self):
        """Generates successor states, implement your custom operators in the derived method."""
        raise Exception("Classes derived from AbstractSearchState must define an expand() method!")

    def __eq__(self):
        """Implement an equality test in the derived method, based only on the state's content (not its path etc!)"""
        raise Exception("Classes derived from AbstractSearchState must define an __eq__() method!")

    
    def __hash__(self):
        """Return a unique hash for this state, based on its ID"""
        raise Exception("Classes derived from AbstractSearchState must define a __hash__() method if the search space is a graph and visited nodes to be are stored in memory!")        


    def depth(self):
        if not self.parent:
            return 0
        else:
            return self.parent.depth() + 1            

    #def __len__(self):
    #    return len(self.path())

    def path(self):
        if not self.parent:
            return [self]
        else: 
            return self.parent.path() + [self]

    def pathcost(self):
        if not self.parent:
            return self.cost
        else: 
            return self.parent.pathcost() + self.cost


        

    #def __cmp__(self, other):
    #    if self.score < other.score:
    #        return -1
    #    elif self.score > other.score:
    #        return 1
    #    else:
    #        return 0

class AbstractSearch(object): #not a real search, just a base class for DFS and BFS
    def __init__(self, **kwargs):
        """For graph-searches usememory=True is required (default), otherwise the search may loop forever. For tree-searches, it can be be switched off for better performance"""
        self.usememory = True
        self.poll = lambda x: x.pop
        self.maxdepth = False #unlimited
        self.minimize = False #minimize rather than maximize the score function? default: no
        self.keeptraversal = False
        self.goalstates = None
        self.debug = False
        for key, value in kwargs.items():
            if key == 'graph':
                self.usememory = value #search space is a graph? memory required to keep visited states
            elif key == 'tree':
                self.usememory = not value;  #search space is a tree? memory not required
            elif key == 'poll':
                self.poll = value #function
            elif key == 'maxdepth':
                self.maxdepth = value
            elif key == 'minimize':
                self.minimize = value
            elif key == 'maximize':
                self.minimize = not value
            elif key == 'keeptraversal': #remember entire traversal?
                self.keeptraversal = value
            elif key == 'goal' or key == 'goals': #remember entire traversal?
                if isinstance(value, list) or isinstance(value, tuple):
                    self.goalstates = value
                else:
                    self.goalstates = [value]
            elif key == 'debug':
                self.debug = value
        self.visited = {}
        self.traversal = []
        self.incomplete = False
        self.traversed = 0

    def traversal(self):
        """Returns all visited states (only when keeptraversal=True), note that this is not equal to the path, but contains all states that were checked!"""
        if self.keeptraversal:
            return self.traversal
        else:
            raise Exception("No traversal available, algorithm not started with keeptraversal=True!")
    
    def traversalsize(self):
        """Returns the number of nodes visited  (also when keeptravel=False). Note that this is not equal to the path, but contains all states that were checked!"""
        return self.traversed
        

    def visited(self, state):
        if self.usememory:
            return (state in self.visited)
        else:
            raise Exception("No memory kept, algorithm not started with graph=True!")
        
    def __iter__(self):
        """Iterates over all valid goalstates it can find"""
        self.traversed = 0
        while len(self.fringe) > 0:
            if self.debug: print >>stderr,"\t[pynlpl debug] FRINGE: ", self.fringe
            state = self.poll(self.fringe)()
            if self.debug:
                print >>stderr,"\t[pynlpl debug] CURRENT STATE: " + str(state),
                try:
                    print >>stderr,state.score()
                except:
                    pass
            self.traversed += 1
            if state.test(self.goalstates):
                if self.debug: print >>stderr,"\t[pynlpl debug] *YIELDING TARGET!*"
                yield state
            elif self.debug:
                print >>stderr,"\t[pynlpl debug] (no target, not yielding)"

            if self.debug: print >>stderr,"\t[pynlpl debug] \tEXPANDING:"

            #Expand the specified state and add to the fringe
            if not self.usememory or (self.usememory and not hash(state) in self.visited):
                for i, s in enumerate(state.expand()):
                    if self.debug:
                        print >>stderr,"\t[pynlpl debug] Expanded state #" + str(i+1) + ", adding to fringe: " + str(s),
                        try:
                            print >>stderr,s.score()
                        except:
                            pass
                    if not self.maxdepth or s.depth() <= self.maxdepth:
                        self.fringe.append(s)
                    else:
                        if self.debug: print >>stderr,"\t[pynlpl debug] Not adding to fringe, maxdepth exceeded"
                        self.incomplete = True
                if self.keeptraversal: self.keeptraversal.append(state)
                if self.usememory: self.visited[hash(state)] = True
                self.prune(state) #calls prune method

    def searchfirst(self):
        for solution in self:
            return solution

    def searchall(self):
        return list(iter(self))

    def searchbest(self):
        finalsolution = None
        for solution in self:
            finalsolution = solution
        return finalsolution

    def searchtop(self,n=10):
        solutions = deque([], n)
        for solution in self:
            solutions.append(solution)
        return solutions


    def prune(self, state):
        #pruning nothing by default
        pass

class DepthFirstSearch(AbstractSearch):

    def __init__(self, state, **kwargs):
        assert isinstance(state, AbstractSearchState)
        self.fringe = [ state ]
        super(DepthFirstSearch,self).__init__(**kwargs)         



class BreadthFirstSearch(AbstractSearch):


    def __init__(self, state, **kwargs):
        assert isinstance(state, AbstractSearchState)
        self.fringe = FIFOQueue([state])
        super(BreadthFirstSearch,self).__init__(**kwargs)         


class IterativeDeepening(AbstractSearch):

    def __init__(self, state, **kwargs):
        assert isinstance(state, AbstractSearchState)
        self.state = state
        self.kwargs = kwargs
        self.traversed = 0

    def __iter__(self):
        self.traversed = 0
        d = 0
        while not 'maxdepth' in self.kwargs or d <= self.kwargs['maxdepth']:
            dfs = DepthFirstSearch(self.state, **self.kwargs)
            self.traversed += dfs.traversalsize()
            for match in dfs:
                yield match
            if dfs.incomplete:
                d +=1 
            else:
                break

    def traversal(self):
        #TODO: add
        raise Exception("not implemented yet")

    def traversalsize(self):
        return self.traversed


class BestFirstSearch(AbstractSearch):

    def __init__(self, state, **kwargs):
        super(BestFirstSearch,self).__init__(**kwargs)
        assert isinstance(state, AbstractSearchState)
        self.fringe = PriorityQueue([state], lambda x: x.score, self.minimize, blockworse=False, blockequal=False,duplicates=False)

class BeamSearch(AbstractSearch):

    def __init__(self, state, beamsize, **kwargs):
        assert isinstance(state, AbstractSearchState)
        self.beamsize = beamsize
        super(BeamSearch,self).__init__(**kwargs)
        self.fringe = PriorityQueue([state], lambda x: x.score, self.minimize, blockworse=False, blockequal=False,duplicates= kwargs['duplicates'] if 'duplicates' in kwargs else False)

    def prune(self, state):
        if self.debug: 
            l = len(self.fringe)
            print >>stderr,"\t[pynlpl debug] pruning with beamsize " + str(self.beamsize) + "...",
        self.fringe.prunebyscore(state.score(), retainequalscore=True)
        self.fringe.prune(self.beamsize)
        if self.debug: print >>stderr," (" + str(l) + " to " + str(len(self.fringe)) + " items)"

class HillClimbingSearch(AbstractSearch):
    """(identical to beamsearch with beam 1, but implemented differently)"""

    def __init__(self, state, **kwargs):
        assert isinstance(state, AbstractSearchState)
        super(HillClimbingSearch,self).__init__(**kwargs)
        self.fringe = PriorityQueue([state], lambda x: x.score, self.minimize, blockworse=True, blockequal=False,duplicates=False)
