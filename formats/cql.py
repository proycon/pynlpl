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

    def __call__(self, **tokens):
        """Execute the CQL expression, pass a list of tokens/annotations using keyword arguments: text, pos, lemma, etc"""
        if not tokens:
            raise Exception("Pass a list of tokens/annotation using keyword arguments! (text,pos,lemma, or others)")

        for v in tokens.values():
            l = len(v)

        if not all( (len(v) == l for k,v in tokens.items() ) ):
            raise Exception("All lists passed as keyword arguments must represent the same tokens and thus have the same length!")

        raise NotImplementedError #TODO



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
