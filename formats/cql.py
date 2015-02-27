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

OPERATORS = ('=','!=','>','>=','<','<=')
MAXINTERVAL = 99

class SyntaxError(Exception):
    pass

class ValueExpression(object):
    def __init__(self, values):
        self.values = values #disjunction

    @staticmethod
    def parse(s,i):
        assert s[i] == '"'
        i += 1
        while s[i] != '"' and s[i-1] != "\\":
            values += s[i]
            i += 1

        values = values.split("|")
        return ValueExpression(values), i

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
            if operator not in operators:
                raise SyntaxError("Expected operator, got " + operator)
        if s[i] != '"':
            raise SyntaxError("Expected start of value expression (doublequote) in position " + str(i) + ", got " + s[i])
        valueexpr, i = ValueExpression.parse(s,i)
        return AttributeExpression(attrigbute,operator, valueexpr), i

class TokenExpression(object):
    def __init__(self, attribexprs=[], interval=None):
        self.attribexprs = attribexprs
        self.interval = interval

    @staticmethod
    def parse(s,i):
        attribexprs = []
        interval = None
        while s[i] == " ":
            i +=1
        if s[i] == "[":
            i += 1
            while True:
                while s[i] == " ":
                    i +=1
                if s[i] == "&":
                    attribexpr,i = AttributeExpression(s,i+1)
                    attribexprs.append(attribexpr)
                elif s[i] == "]":
                    break
                elif not attribexprs:
                    attribexpr,i = AttributeExpression(s,i)
                    attribexprs.append(attribexpr)

            if s[i] == "{":
                #interval expression, find end:
                for j in range(i+1, len(s)):
                    if s[j] == "}":
                        interval = s[i+1:j]
                if ',' in interval:
                    interval = tuple(interval.split(","))
                    if len(interval) != 2:
                        raise SyntaxError("Invalid interval: " + interval)
                elif '-' in interval: #alternative
                    interval = tuple(interval.split("-"))
                    if len(interval) != 2:
                        raise SyntaxError("Invalid interval: " + interval)
                else:
                    try:
                        interval = (int(interval),int(interval))
                    except:
                        raise SyntaxError("Invalid interval: " + interval)
            elif s[i] == "?":
                interval = (0,1)
            elif s[i] == "+":
                interval = (1,MAXINTERVAL)
            elif s[i] == "*":
                interval = (0,MAXINTERVAL)

        return TokenExpression(attribexprs,interval),i




class Query(object):
    def __init__(self, s):
        self.tokenexprs = []
        i = 0
        while True:
            while s[i] == " ":
                i +=1
            tokenexpr,i = TokenExpression(s,i)
            self.tokens.append(tokenexpr)



