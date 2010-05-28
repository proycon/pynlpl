#---------------------------------------------------------------
# PyNLPl - Search Algorithms
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#
# This library contains various search algorithms.
#
#----------------------------------------------------------------

from pynlp.datatypes import FIFOQueue, PriorityQueue

class AbstractSearchState(object):
    def __init__(self,  parent = None, cost = 0):
        self.parent = parent        
        self.cost = cost



    def score(self):
        """Should return a heuristic value. """
        raise Exception("Classes derived from AbstractSearchState must define a score() method if used in informed search algorithms!")

    def expand(self):
        """Generates successor states, implement your custom operators in the derived method"""
        raise Exception("Classes derived from AbstractSearchState must define an expand() method!")

    def __eq__(self):
        """Implement an equality test in the derived method, based only on the state's content (not its path etc!)"""
        raise Exception("Classes derived from AbstractSearchState must define an __eq__() method!")

    def test(self):
        """Checks whether this state is a valid goal state, returns a boolean"""
        raise Exception("Classes derived from AbstractSearchState must define a test() method!")


    def depth(self):
        if not self.parent:
            return 0
        else:
            return self.parent.depth() + 1            


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
    def __init__(self, usememory = True, maxdepth = False, poll = lambda x: x.pop):
        """For graph-searches usememory must be on, otherwise the search may be infinite. For tree-searches, it can be be switched off for better performance"""
        self.poll = poll #poll function
        self.usememory = usememory
        self.visited = []
        self.maxdepth = maxdepth      
        self.incomplete = False            

    def memory(self):
        """Returns all visited states (only when usememory=True), note that this is not equal to the path, but to the entire traversal!"""
        return self.visited

    def __iter__(self):
        """Iterates over all valid goalstates it can find"""
        while len(self.fringe) != 0:
            state = self.popfunction(self.fringe)()
            if state.test():
                yield state
            """Expand the specified state and add to the fringe"""
            if not self.usememory or (self.usememory and not state in self.visited):
                if not self.maxdepth:
                     self.fringe += state.expand()
                     if self.usememory: 
                        self.visited.append(state)
                     self.prune()
                else:
                    for s in state.expand():
                        if s.depth() <= self.maxdepth:
                            self.fringe.append(s)
                            if self.usememory: 
                                self.visited.append(state)
                        else:
                            self.incomplete = True
                    self.prune()

    def prune(self):
        pass

class DepthFirstSearch(AbstractSearch):

    def __init__(self, state, usememory = True, maxdepth = False):
        assert issubclass(state, AbstractSearchState)
        self.fringe = [ state ]
        super(self, DepthFirstSearch).__init__(usememory, maxdepth)         



class BreadthFirstSearch(AbstractSearch):


    def __init__(self, state, usememory = True, maxdepth = False):
        assert issubclass(state, AbstractSearchState)
        self.fringe = FIFOQueue([state])
        super(self, BreadthFirstSearch).__init__(usememory, maxdepth)         


class IterativeDeepening(AbstractSearch):

    def __iter__(self):
        d = 0
        while not self.maxdepth or d <= self.maxdepth:
            dfs = DepthFirstSearch(self.state, self.usememory, d)
            for match in dfs:
                yield match
            if dfs.incomplete:
                d +=1 
            else:
                break


class BestFirstSearch(AbstractSearch):

    def __init__(self, state, usememory = True, maxdepth = False, minimize=False):
        assert issubclass(state, AbstractSearchState)
        self.fringe = PriorityQueue([state], lambda x: x.score, minimize)
        super(self, BestFirstSearch).__init__(state,usememory, maxdepth)            


class BeamSearch(AbstractSearch):
    
    def __init__(self, state, beamsize, usememory = True, maxdepth = False, minimize=False):
        assert issubclass(state, AbstractSearchState)
        self.fringe = PriorityQueue([state], lambda x: x.score, minimize)
        self.beamsize = beamsize
        super(self, BeamSearch).__init__(state,usememory, maxdepth, lambda x: x.pop(0))            

    def prune(self):
        self.fringe.prune(self.beamsize)


class HillClimbingSearch(BeamSearch):
    """BeamSearch with beam 1"""

    def __init__(self, state, usememory = True, maxdepth = False):
        super(self, HillClimbingSearch).__init__(state,1, usememory, maxdepth)            

