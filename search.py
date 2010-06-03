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

from pynlpl.datatypes import FIFOQueue, PriorityQueue

class AbstractSearchState(object):
    def __init__(self,  parent = None, cost = 0):
        self.parent = parent        
        self.cost = cost



    def test(self):
        """Checks whether this state is a valid goal state, returns a boolean. For optimisation problems, you often want to always return True here."""
        raise Exception("Classes derived from AbstractSearchState must define a test() method!")

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
        for key, value in kwargs.items():
            if key == 'graph':
                self.usememory = value #search space is a graph? memory required to keep visited states
            elif key == 'tree':
                self.usememory = not value;  #search space is a tree? memory not required
            elif key == 'poll':
                self.poll = value
            elif key == 'maxdepth':
                self.maxdepth = value
            elif key == 'minimize':
                self.minimize = value
            elif key == 'maximize':
                self.minimize = not value
            elif key == 'keeptraversal': #remember entire traversal?
                self.keeptraversal = value
        self.visited = {}
        self.traversal = []
        self.incomplete = False            


    def traversal(self):
        """Returns all visited states (only when keeptraversal=True), note that this is not equal to the path, but contains all states that were checked!"""
        if self.keeptraversal:
            return self.traversal
        else:
            raise Exception("No traversal available, algorithm not started with keeptraversal=True!")

    def visited(self, state):
        if self.usememory:
            return (state in self.visited)
        else:
            raise Exception("No memory kept, algorithm not started with graph=True!")
        
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
                else:
                    for s in state.expand():
                        if s.depth() <= self.maxdepth:
                            self.fringe.append(s)
                        else:
                            self.incomplete = True
                if self.keeptraversal: self.keeptraversal.append(state)
                if self.usememory: self.visited[state] = True
                self.prune() #calls prune method

    def prune(self):
        #pruning nothing by default
        pass

class DepthFirstSearch(AbstractSearch):

    def __init__(self, state, **kwargs):
        assert issubclass(state, AbstractSearchState)
        self.fringe = [ state ]
        super(self, DepthFirstSearch).__init__(**kwargs)         



class BreadthFirstSearch(AbstractSearch):


    def __init__(self, state, **kwargs):
        assert issubclass(state, AbstractSearchState)
        self.fringe = FIFOQueue([state])
        super(self, BreadthFirstSearch).__init__(**kwargs)         


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

    def __init__(self, state, **kwargs):
        super(self, BestFirstSearch).__init__(**kwargs)            
        assert issubclass(state, AbstractSearchState)
        self.fringe = PriorityQueue([state], lambda x: x.score, self.minimize)


class BeamSearch(AbstractSearch):
    
    def __init__(self, state, beamsize, **kwargs):
        assert issubclass(state, AbstractSearchState)
        self.beamsize = beamsize
        super(self, BeamSearch).__init__(beamsize, **kwargs)            
        self.fringe = PriorityQueue([state], lambda x: x.score, self.minimize)

    def prune(self):
        self.fringe.prune(self.beamsize)


class HillClimbingSearch(BeamSearch):
    """BeamSearch with beam 1"""

    def __init__(self, state, **kwargs):
        super(self, HillClimbingSearch).__init__(state,1, **kwargs)            

