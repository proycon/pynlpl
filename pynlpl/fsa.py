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
from __future__ import print_function, unicode_literals, division, absolute_import
import sys


class State(object):
    def __init__(self, **kwargs):
        if 'epsilon' in kwargs:
            self.epsilon = kwargs['epsilon'] # epsilon-closure (lis of states)
        else:
            self.epsilon = [] # epsilon-closure
        if 'transitions' in kwargs:
            self.transitions = kwargs['transitions']
        else:
            self.transitions = [] #(matchitem, matchfunction(value), state)
        if 'final' in kwargs:
            self.final = bool(kwargs['final']) # ending state
        else:
            self.final = False
        self.transitioned = None #will be a tuple (state, matchitem) indicating how this state was reached



class NFA(object):
    """Non-deterministic finite state automaton. Can be used to model DFAs as well if your state transitions are not ambiguous and epsilon is empty."""

    def __init__(self, initialstate):
        self.initialstate = initialstate

    def run(self, sequence, mustmatchall=False,debug=False):
        def add(state, states):
            """add state and recursively add epsilon transitions"""
            assert isinstance(state, State)
            if state in states:
                return
            states.add(state)
            for eps in state.epsilon: #recurse into epsilon transitions
                add(eps, states)

        current_states = set()
        add(self.initialstate, current_states)
        if debug: print("Starting run, current states: ", repr(current_states),file=sys.stderr)

        for offset, value in enumerate(sequence):
            if not current_states: break
            if debug: print("Value: ", repr(value),file=sys.stderr)
            next_states = set()
            for state in current_states:
                for matchitem, matchfunction, trans_state in state.transitions:
                    if matchfunction(value):
                        trans_state.transitioned = (state, matchitem)
                        add(trans_state, next_states)

            current_states = next_states
            if debug: print("Current states: ", repr(current_states),file=sys.stderr)
            if not mustmatchall:
                for s in current_states:
                    if s.final:
                        if debug: print("Final state reached",file=sys.stderr)
                        yield offset+1

        if mustmatchall:
            for s in current_states:
                if s.final:
                    if debug: print("Final state reached",file=sys.stderr)
                    yield offset+1


    def match(self, sequence):
        try:
            return next(self.run(sequence,True)) == len(sequence)
        except StopIteration:
            return False

    def find(self, sequence, debug=False):
        l = len(sequence)
        for i in range(0,l):
            for length in self.run(sequence[i:], False, debug):
                yield sequence[i:i+length]

    def __iter__(self):
        return iter(self._states(self.initialstate))

    def _states(self, state, processedstates=[]): #pylint: disable=dangerous-default-value
        """Iterate over all states in no particular order"""
        processedstates.append(state)

        for nextstate in state.epsilon:
            if not nextstate in processedstates:
                self._states(nextstate, processedstates)

        for _, nextstate in state.transitions:
            if not nextstate in processedstates:
                self._states(nextstate, processedstates)

        return processedstates

    def __repr__(self):
        out = []
        for state in self:
            staterep = repr(state)
            if state is self.initialstate:
                staterep += " (INITIAL)"
            for nextstate in state.epsilon:
                nextstaterep = repr(nextstate)
                if nextstate.final:
                    nextstaterep += " (FINAL)"
                out.append( staterep + " -e-> " + nextstaterep )
            for item, _, nextstate in state.transitions:
                nextstaterep = repr(nextstate)
                if nextstate.final:
                    nextstaterep += " (FINAL)"
                out.append( staterep + " -(" + repr(item) + ")-> " + nextstaterep )

        return "\n".join(out)
