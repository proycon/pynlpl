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
import re

OPERATORS = ('=','==','!=','>','<','<=','>=')
MASK_NORMAL = 0
MASK_LITERAL = 1
MASK_EXPRESSION = 2


def query(doc, q):
    q = Query.parse(UnparsedQuery(q))
    return q(doc)

class SyntaxError(Exception):
    pass

class UnparsedQuery(object):
    """This class takes care of handling grouped blocks in parentheses and handling quoted values"""
    def __init__(self, s, i):
        self.q = []
        self.mask = []
        l = len(s)
        begin = 0
        while i < l:
            c = s[i]
            if c == " ":
                #process previous word
                if begin < i:
                    self.q.append(s[begin:i])
                begin = i + 1
            elif i == l - 1:
                #process last word
                self.q.append(s[begin:])
                self.mask.append(MASK_NORMAL)

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
                    self.mask.append(MASK_EXPRESSION)
                    i = j
                    begin = i+1
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
                        self.mask.append(MASK_LITERAL)
                        i = j
                        begin = i+1
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
        except KeyError:
            return ""

    def kw(self, index, value):
        if isinstance(value, tuple):
            return self.q[index] in value and self.mask[index] == MASK_NORMAL
        else:
            return self.q[index] == value and self.mask[index] == MASK_NORMAL

    def __setitem__(self, index, value):
        self.q[index] = value






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
            if q.kw(i,"OF") and q[i+1]:
                set = q[i+1]
                i += 2
            elif q.kw(i,"ID") and q[i+1]:
                id = q[i+1]
                i += 2
            elif q.kw(i, "WHERE"):
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
            if q.kw(i, "NOT"):
                negation = True
            elif q[i+1] in OPERATORS and q[i] and q[i+2]:
                operator = q[i+1]
                if q[i] == "class":
                    v = lambda x,y='cls': getattr(x,y)
                elif q[i] == "text":
                    v = lambda x,y='text': getattr(x,'text')()
                else:
                    v = lambda x,y=q[i]: getattr(x,y)
                if operator == '=' or operator == '==':
                    self.filters.append( lambda x,y=q[i+2],v=v : v(x) == y )
                elif operator == '!=':
                    self.filters.append( lambda x,y=q[i+2],v=v : v(x) != y )
                elif operator == '>':
                    self.filters.append( lambda x,y=q[i+2],v=v : v(x) > y )
                elif operator == '<':
                    self.filters.append( lambda x,y=q[i+2],v=v : v(x) < y )
                elif operator == '>=':
                    self.filters.append( lambda x,y=q[i+2],v=v : v(x) >= y )
                elif operator == '<=':
                    self.filters.append( lambda x,y=q[i+2],v=v : v(x) <= y )
                elif operator == 'CONTAINS':
                    self.filters.append( lambda x,y=q[i+2],v=v : v(x).find( y ) != -1 )
                elif operator == 'MATCHES':
                    self.filters.append( lambda x,y=re.compile(q[i+2]),v=v : y.search(v(x)) is not None  )

                if q.kw(i+3,"AND") or q.kw(i+3,"OR"):
                    if logop and q[i+3] != logop:
                        raise SyntaxError("Mixed logical operators, use parentheses")
                    logop = q[i+3]
                else:
                    break #done
            elif isinstance(q, UnparsedQuery):
                filter, i = Filter.parse(q,i)
                filters.append(filter)
                if q.kw(i,"AND") or q.kw(i, "OR"):
                    if logop and q[i] != logop:
                        raise SyntaxError("Mixed logical operators, use parentheses")
                    logop = q[i]
                else:
                    break #done
            else:
                raise SyntaxError("Expected comparison operator, got " + q[i+1])
            i += 1

        return Filter(filters, negation, disjunction), i


class Target(object):
    pass #TODO

class Form(Object):  #AS... expression
    pass #TODO


class Action(object): #Action
    def __init__(self, action, actor, assignments={}):
        self.action = action
        self.actor = actor
        self.assignments = assignments
        self.form = None
        self.subactions = []
        self.nextaction = None
        self.respan = []


    @staticmethod
    def parse(q,i=0):
        if q.kw(i, ('SELECT','EDIT','DELETE','ADD','APPEND','PREPEND','MERGE','SPLIT')):
           action = q[i]
        else:
            raise SyntaxError("Expected action, got " + q[i])

        try:
            actor, i = Actor.parse(q,i)
        except ParseError as e:
            raise SyntaxError(e)

        if action == "ADD" and actor.filters:
            raise SyntaxError("Actor has WHERE statement but ADD action does not support this")

        assignments = {}
        if q.kw(i,"WITH"):
            if action in ("SELECT", "DELETE"):
                raise SyntaxError("Actor has WITH statement but " + action + " does not support this")
            i += 1
            l = len(q)
            while i < l:
                if q.kw(i, ('annotator','annotatortype','class','confidence','n','text')):
                    assignments[q[i]] = q[i+1]
                    i+=1
                else:
                    if not assignments:
                        raise SyntaxError("Expected assignments after WITH statement, but no valid attribute found")
                    break
            i+=1

        #we have enough to set up the action now
        action = Actions(action, actor, assignments)

        if action.action == "EDIT" and q.kw(i,"SPAN"):
            pass #TODO

        done = False
        while not done:
            if isinstance(q[i], UnparsedQuery):
                #we have a sub expression
                if q.kw(i, ('EDIT','DELETE','ADD')):
                    #It's a sub-action!
                    subaction, _ = Action.parse(q[i])
                    action.subactions.append( subaction )
                elif q.kw(i, 'AS'):
                    #It's an AS.. expression
                    pass #self.form = #TODO
            else:
                done = True
            i += 1

        if q.kw(i, ('SELECT','EDIT','DELETE','ADD','APPEND','PREPEND','MERGE','SPLIT')):
            #We have another action!
            action.nextaction, i = Action.parse(q,i)

        return action, i









class Context(object):
    def __init__(self):
        self.format = "python"
        self.returntype = "actor"
        self.request = "all"
        self.defaults = {}
        self.defaultsets = {}

class Query(object):
    def __init__(self, q, context):
        self.action = None
        self.targets = []
        self.format = context.format
        self.returntype = context.returntype
        self.request = copy(context.request)
        self.defaults = copy(context.defaults)
        self.defaultsets = copy(context.defaultsets)

    def parse(self, q, i=0):
        l = len(q)
        self.action,i = Action.parse(q,i)

        if q.kw(i,("FOR","IN")):
            self.targets,i = Target.parse(q,i)

        while i < l:
            if q.kw(i,"RETURN"):
                pass #TODO
            elif q.kw(i,"FORMAT"):
                pass #TODO
            elif q.kw(i,"REQUEST"):
                pass #TODO

        if i != l:
            raise SyntaxError("Expected end of query, got " + q[i])

    def __call__(self, doc):
        """Execute the query on the specified document"""
        pass #TODO










