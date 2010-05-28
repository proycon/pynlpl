#---------------------------------------------------------------
# PyNLPl - Search Algorithms
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#
# This library contains search algorithms
#
#----------------------------------------------------------------

class AbstractSearchState(object):
    def score(self):
        return 0 

    def expand(self):
        return []

    def test(self):
        return False



class DepthFirstSearch(object):
    
    def __init__(self, state, usememory = True):    
        assert isinstance(state, AbstractSearchState)
        self.fringe = [ state ]
        self.usememory = usememory
        self.visited = []

    def __iter__(self):
        while len(self.fringe) != 0:
            state = self.fringe.pop()
            if state.test():
                yield state
            if not self.usememory or (self.usememory and not state in self.visited):
                self.fringe += state.expand()
                if self.usememory: 
                    self.visited.append(state)

    def memory(self):
        return self.visited


class BreadthFirstSearch(object):
    def __init__(self, state, usememory = True):    
        assert isinstance(state, AbstractSearchState)
        self.fringe = [ state ]
        self.usememory = usememory
        self.visited = []

    def __iter__(self):
        while len(self.fringe) != 0:
            state = self.fringe.pop(0)
            if state.test():
                yield state
            if not self.usememory or (self.usememory and not state in self.visited):
                self.fringe += state.expand()
                if self.usememory: 
                    self.visited.append(state)

    def memory(self):
        return self.visited


