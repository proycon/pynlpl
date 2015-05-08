#---------------------------------------------------------------
# PyNLPl - Finite State Automata
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://proycon.github.com/folia
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
# Partially based/inspired on code by Xiayun Sun (https://github.com/xysun/regex)
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------


class State(object):
    def __init__(self):
        self.epsilon = [] # epsilon-closure
        self.transitions = [] # (matchfunction(value), state)   (values must be hashable)
        self.final = True # ending state

class NFA(object):
    """Non-deterministic finite state automaton. Can be used to model DFAs as well if your state transitions are not ambiguous and epsilon is empty."""

    def __init__(self, initialstate):
        self.initialstate = initialstate

    def run(self, sequence, mustmatchall=False):
        def add(self, state, states):
            """add state and recursively add epsilon transitions"""
            assert isinstance(state, State)
            if state in states:
                return
            states.add(state)
            for eps in state.epsilon: #recurse into epsilon transitions
                add(eps, states)

        current_states = set()
        add(self.initialstate, current_states)

        for offset, value in enumerate(sequence):
            next_states = set()
            for state in current_states:
                for matchfunction, trans_state in state.transitions:
                    if matchfunction(value):
                        add(trans_state, next_states)

            current_states = next_states
            if not mustmatchall:
                for s in current_states:
                    if s.final:
                        yield offset+1

        if mustmatchall:
            for s in current_states:
                if s.final:
                    yield offset+1


    def match(self, sequence):
        try:
            return (next(self.run(sequence,True)) == len(sequence))
        except StopIteration:
            return False

    def find(self, sequence):
        l = len(sequence)
        for i in range(0,l):
            for length in self.run(sequence):
                yield sequence[i:i+length]

