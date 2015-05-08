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
        self.transitions = {} # value --> state   (values must be hashable)
        self.final = True # ending state

class NFA(object):
    def __init__(self, initialstate):
        self.initialstate = initialstate

    def match(self, sequence):
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

        for value in sequence:
            next_states = set()
            for state in current_states:
                if value in state.transitions.keys():
                    trans_state = state.transitions[c]
                    add(trans_state, next_states)

            current_states = next_states

        for s in current_states:
            if s.final:
                return True
        return False





