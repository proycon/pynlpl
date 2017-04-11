#---------------------------------------------------------------
# PyNLPl - Corpus Query Language (CQL)
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://proycon.github.com/folia
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
# Parser and interpreter for a basic subset of the Corpus Query Language
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

from __future__ import print_function, unicode_literals, division, absolute_import

from pynlpl.fsa import State, NFA
import re
import sys

OPERATORS = ('=','!=')
MAXINTERVAL = 99

class SyntaxError(Exception):
    pass

class ValueExpression(object):
    def __init__(self, values):
        self.values = values #disjunction

    @staticmethod
    def parse(s,i):
        values = ""
        assert s[i] == '"'
        i += 1
        while not (s[i] == '"' and s[i-1] != "\\"):
            values += s[i]
            i += 1
        values = values.split("|")
        return ValueExpression(values), i+1

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        for x in self.values:
            yield x

    def __getitem__(self,index):
        return self.values[index]

class AttributeExpression(object):
    def __init__(self, attribute, operator, valueexpression):
        self.attribute = attribute
        self.operator = operator
        self.valueexpr = valueexpression

    @staticmethod
    def parse(s,i):
        while s[i] == " ":
            i +=1
        if s[i] == '"':
            #no attribute and no operator, use defaults:
            attribute = "word"
            operator = "="
        else:
            attribute = ""
            while s[i] not in (' ','!','>','<','='):
                attribute += s[i]
                i += 1
            if not attribute:
                raise SyntaxError("Expected attribute name, none found")
            operator = ""
            while s[i] in (' ','!','>','<','='):
                if s[i] != ' ':
                    operator += s[i]
                i += 1
            if operator not in OPERATORS:
                raise SyntaxError("Expected operator, got '" + operator + "'")
        if s[i] != '"':
            raise SyntaxError("Expected start of value expression (doublequote) in position " + str(i) + ", got " + s[i])
        valueexpr, i = ValueExpression.parse(s,i)
        return AttributeExpression(attribute,operator, valueexpr), i

class TokenExpression(object):
    def __init__(self, attribexprs=[], interval=None):
        self.attribexprs = attribexprs
        self.interval = interval

    @staticmethod
    def parse(s,i):
        attribexprs = []
        while s[i] == " ":
            i +=1
        if s[i] == '"':
            attribexpr,i = AttributeExpression.parse(s,i)
            attribexprs.append(attribexpr)
        elif s[i] == "[":
            i += 1
            while True:
                while s[i] == " ":
                    i +=1
                if s[i] == "&":
                    attribexpr,i = AttributeExpression.parse(s,i+1)
                    attribexprs.append(attribexpr)
                elif s[i] == "]":
                    i += 1
                    break
                elif not attribexprs:
                    attribexpr,i = AttributeExpression.parse(s,i)
                    attribexprs.append(attribexpr)
                else:
                    raise SyntaxError("Unexpected char whilst parsing token expression,  position " + str(i) + ": " + s[i])
        else:
            raise SyntaxError("Expected token expression starting with either \" or [, got: " + s[i])

        if i == len(s):
            interval = None #end of query!
        elif s[i] == "{":
            #interval expression, find end:
            interval = None
            for j in range(i+1, len(s)):
                if s[j] == "}":
                    interval = s[i+1:j]

            if interval is None:
                raise SyntaxError("Interval expression started but no end-brace found")

            i += len(interval) + 2

            try:
                if ',' in interval:
                    interval = tuple(int(x) for x in interval.split(","))
                    if len(interval) != 2:
                        raise SyntaxError("Invalid interval: " + interval)
                elif '-' in interval: #alternative
                    interval = tuple(int(x) for x in interval.split("-"))
                    if len(interval) != 2:
                        raise SyntaxError("Invalid interval: " + interval)
                else:
                    interval = (int(interval),int(interval))
            except ValueError:
                raise SyntaxError("Invalid interval: " + interval)
        elif s[i] == "?":
            interval = (0,1)
            i += 1
        elif s[i] == "+":
            interval = (1,MAXINTERVAL)
            i += 1
        elif s[i] == "*":
            interval = (0,MAXINTERVAL)
            i += 1
        else:
            interval = None

        return TokenExpression(attribexprs,interval),i


    def __len__(self):
        return len(self.attribexprs)

    def __iter__(self):
        for x in self.attribexprs:
            yield x

    def __getitem__(self,index):
        return self.attribexprs[index]

    def nfa(self, nextstate):
        """Returns an initial state for an NFA"""
        if self.interval:
            mininterval, maxinterval = self.interval #pylint: disable=unpacking-non-sequence
            nextstate2 = nextstate
            for i in range(maxinterval):
                state = State(transitions=[(self,self.match, nextstate2)])
                if i+1> mininterval:
                    if nextstate is not nextstate2: state.transitions.append((self,self.match, nextstate))
                    if maxinterval == MAXINTERVAL:
                        state.epsilon.append(state)
                        break
                nextstate2 = state
            return state
        else:
            state = State(transitions=[(self,self.match, nextstate)])
            return state


    def match(self, value):
        match = False
        for _, attribexpr in enumerate(self):
            annottype = attribexpr.attribute
            if annottype == 'text': annottype = 'word'
            if attribexpr.operator == "!=":
                negate = True
            elif attribexpr.operator == "=":
                negate = False
            else:
                raise Exception("Unexpected operator " + attribexpr.operator)

            if len(attribexpr.valueexpr) > 1:
                expr = re.compile("^(" + "|".join(attribexpr.valueexpr) + ")$")
            else:
                expr = re.compile("^" + attribexpr.valueexpr[0] + '$')
            match = (expr.match(value[annottype]) is not None)
            if negate:
                match = not match
            if not match:
                return False
        return True



class Query(object):
    def __init__(self, s):
        self.tokenexprs = []
        i = 0
        l = len(s)
        while i < l:
            if s[i] == " ":
                i += 1
            else:
                tokenexpr,i = TokenExpression.parse(s,i)
                self.tokenexprs.append(tokenexpr)

    def __len__(self):
        return len(self.tokenexprs)

    def __iter__(self):
        for x in self.tokenexprs:
            yield x

    def __getitem__(self,index):
        return self.tokenexprs[index]

    def nfa(self):
        """convert the expression into an NFA"""
        finalstate = State(final=True)
        nextstate = finalstate
        for tokenexpr in reversed(self):
            state = tokenexpr.nfa(nextstate)
            nextstate = state
        return NFA(state)


    def __call__(self, tokens, debug=False):
        """Execute the CQL expression, pass a list of tokens/annotations using keyword arguments: word, pos, lemma, etc"""

        if not tokens:
            raise Exception("Pass a list of tokens/annotation using keyword arguments! (word,pos,lemma, or others)")

        #convert the expression into an NFA
        nfa = self.nfa()
        if debug:
            print(repr(nfa), file=sys.stderr)

        return list(nfa.find(tokens,debug))







def cql2fql(cq):
    fq = "SELECT FOR SPAN "
    if not isinstance(cq, Query):
        cq = Query(cq)

    for i, token in enumerate(cq):
        if i > 0: fq += " & "
        fq += "w"
        if token.interval:
            fq += " {" + str(token.interval[0]) + "," + str(token.interval[1])+ "} "
        else:
            fq += " "
        if token.attribexprs:
            fq += "WHERE "
            for j, attribexpr in enumerate(token):
                if j > 0:
                    fq += " AND "
                fq += "("
                if attribexpr.operator == "!=":
                    operator = "NOTMATCHES"
                elif attribexpr.operator == "=":
                    operator = "MATCHES"
                else:
                    raise Exception("Invalid operator: " + attribexpr.operator)
                if attribexpr.attribute in ("word","text"):
                    if len(attribexpr.valueexpr) > 1:
                        fq += "text " + operator + " \"^(" + "|".join(attribexpr.valueexpr) + ")$\" "
                    else:
                        fq += "text " + operator + " \"^" + attribexpr.valueexpr[0] + "$\" "
                else:
                    annottype = attribexpr.attribute
                    if annottype == "tag":
                        annottype = "pos"
                    elif annottype == "lempos":
                        raise Exception("lempos not supported in CQL to FQL conversion, use pos and lemma separately")
                    fq += annottype + " HAS class "
                    if len(attribexpr.valueexpr) > 1:
                        fq += operator + " \"^(" + "|".join(attribexpr.valueexpr) + ")$\" "
                    else:
                        fq += operator + " \"^" + attribexpr.valueexpr[0] + "$\" "
                fq += ")"

    return fq
