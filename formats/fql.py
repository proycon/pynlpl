#---------------------------------------------------------------
# PyNLPl - FoLiA Query Language
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://proycon.github.com/folia
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#   Module for reading, editing and writing FoLiA XML using
#   the FoLiA Query Language
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

from pynlpl.formats import folia

OPERATORS = ('=','==','!=','>','<','<=','>=')

def query(doc, query):


class SyntaxError(Exception):
    pass



class UnparsedQuery(object):
    """This class takes care of handling grouped blocks in parentheses and handling quoted values"""
    def __init__(self, s, i):
        self.q = []
        l = len(s)
        while i < l:
            c = s[i]
            if c == '(': #groups
                #find end quote and process block
                level = 0
                quoted = False
                s2 = ""
                for j in range(i+1,l):
                    c2 = s[j]
                    if c2 == '"':
                        if s[j-1] != "\\": #check it isn't escaped
                            quoted = not quoted
                    if not quoted:
                        if c2 == '(':
                            level += 1
                        elif c2 == ')':
                            if level == 0:
                                s2 = s[i+1:j]
                                break
                            else:
                                level -= 1
                if s2:
                    self.q.append(UnparsedQuery(s2))
                    i = j
                else:
                    raise SyntaxError("Unmatched parenthesis at char " + str(i))
            elif c == '"': #literals
                if i == 0 or (i > 0 and s[i-1] != "\\"): #check it isn't escaped
                    #find end quote and process block
                    s2 = None
                    for j in range(i+1,l):
                        c2 = s[j]
                        if c2 == '"':
                            if s[j-1] != "\\": #check it isn't escaped
                                s2 = s[i+1:j]
                                break
                    if not s2 is None:
                        self.q.append(s2)
                        i = j
                    else:
                        raise SyntaxError("Unterminated string literal at char " + str(i))
            i += 1


    def __iter__(self):
        for w in self.q:
            yield w

    def __len__(self):
        return len(self.q)

    def __getitem__(self, index):
        try:
            return self.q[index]
        raise KeyError:
            return ""




class Query(object):
    def __init__(self, s):
        action =
        action = Action(s)


    def __add__(self, other):
        if isinstance(other, Query):

        else:


class DocumentSelector(object):
    def __init__(self):


class Actor(object):
    def __init__(self, actor, set=None,id=None, filter=None):
        try:
            self.Class = folia.XML2CLASS[actor]
        except:
            raise SyntaxError("No such actor: " + actor)
        self.set = set
        self.id = id
        self.filter = filter

    @staticmethod
    def parse(q, i=0):
        if q[i] not in folia.XML2CLASS:
            raise SyntaxError("Expected actor, got " + q[i])
        actor = q[i]

        l = len(q)
        set = None
        id = None
        filter = None
        while i < l:
            if q[i] == "OF" and q[i+1]:
                set = q[i+1]
                i += 2
            elif q[i] == "ID" and q[i+1]:
                id = q[i+1]
                i += 2
            elif q[i] == "WHERE":
                #ok, big filter coming up!
                filter, i = Filter.parse(Filter.parse(),i)
                break
            else:
                #something we don't handle
                return None, i

        return Actor(actor,set,id,filter), i

class Filter(object): #WHERE ....
    def __init__(self, filters, negation=False,disjunction=False):
        self.filters = filters
        self.negation = negation
        self.disjunction = disjunction

    @staticmethod
    def parse(q, i=0):
        filters = []
        negation = False
        logop = ""

        l = len(q)
        while i < l:
            if q[i] == "NOT"
                negation = True
            elif q[i+1] in OPERATORS and q[i] and q[i+2]:
                operator = q[i+1]
                if operator == '=' or operator == '==':
                    self.filters.append( lambda x: getattr(x, q[i]) == q[i+2] )
                elif operator == '!=':
                    self.filters.append( lambda x: getattr(x, q[i]) != q[i+2] )
                elif operator == '>':
                    self.filters.append( lambda x: getattr(x, q[i]) > q[i+2] )
                elif operator == '<':
                    self.filters.append( lambda x: getattr(x, q[i]) < q[i+2] )
                elif operator == '>=':
                    self.filters.append( lambda x: getattr(x, q[i]) >= q[i+2] )
                elif operator == '<=':
                    self.filters.append( lambda x: getattr(x, q[i]) <= q[i+2] )

                if q[i+3] == "AND" or q[i+3] == "OR":
                    if logop and q[i+3] != logop:
                        raise SyntaxError("Mixed logical operators, use parentheses")
                    logop = q[i+3]
                else:
                    break
            elif isinstance(q, UnparsedQuery):
                filter, i = Filter.parse(q,i)
                filters.append(filter)
                if q[i] == "AND" or q[i] == "OR":
                    if logop and q[i] != logop:
                        raise SyntaxError("Mixed logical operators, use parentheses")
                    logop = q[i]
                else:
                    break
            else:
                raise SyntaxError("Expected comparison operator, got " + q[i+1])
            i += 1

        return Filter(filters, negation, disjunction), i









class Assignment(object):
    def __init__(self, assignment):
        self.assignment = assignment











class Action(object):
    def __init__(self, action, actor, assignments = None, targets = None):
        if action in ('SELECT','EDIT','DELETE','ADD'):
            self.action = action
        else:
            raise SyntaxError("Excepted action: " + actor)

        self.actor = actor

        if self.action in ( 'SELECT','DELETE') and assignments:
            raise SyntaxError("No WITH statement expected for " + self.action + " action")

        if self.action == 'ADD' and self.actor.filters:
            raise SyntaxError("No WHERE statement expected for " + self.action + " action")

        if self.action == 'SELECT' and assignments:
            raise SyntaxError("No WITH statement expected for SELECT action")

        self.assignments = assignments
        self.targets = targets


    @staticmethod
    def parse(q,i=0):
        try:
            s = Actor.parse(s)
        except ParseError as e:
            raise SyntaxError(e)




class TargetExpression(object): #FOR .....
    def __init__(self, ):



class AssignmentExpression(object): #WITH .....
    def __init__(self, assignments):
        self.assignments = assignments






