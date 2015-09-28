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


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from pynlpl.formats import folia
from copy import copy
import json
import re
import sys
import random
import datetime

OPERATORS = ('=','==','!=','>','<','<=','>=','CONTAINS','NOTCONTAINS','MATCHES','NOTMATCHES')
MASK_NORMAL = 0
MASK_LITERAL = 1
MASK_EXPRESSION = 2
MAXEXPANSION = 99

FOLIAVERSION = '0.12.1'
FQLVERSION = '0.2.4'

class SyntaxError(Exception):
    pass

class QueryError(Exception):
    pass


def getrandomid(query,prefix=""):
    randomid = ""
    while not randomid or randomid in query.doc.index:
        randomid =  prefix + "%08x" % random.getrandbits(32) #generate a random ID
    return randomid

class UnparsedQuery(object):
    """This class takes care of handling grouped blocks in parentheses and handling quoted values"""
    def __init__(self, s, i=0):
        self.q = []
        self.mask = []
        l = len(s)
        begin = 0
        while i < l:
            c = s[i]
            if c == " ":
                #process previous word
                if begin < i:
                    w = s[begin:i]
                    self.q.append(w)
                    self.mask.append(MASK_NORMAL)
                begin = i + 1
            elif i == l - 1:
                #process last word
                w = s[begin:]
                self.q.append(w)
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
                        self.q.append(s2.replace('\\"','"')) #undo escaped quotes
                        self.mask.append(MASK_LITERAL)
                        i = j
                        begin = i+1
                    else:
                        raise SyntaxError("Unterminated string literal at char " + str(i))

            i += 1

        remove = []
        #process shortcut notation
        for i, (w,m) in enumerate(zip(self.q,self.mask)):
            if m == MASK_NORMAL and w[0] == ':':
                #we have shortcut notation for a HAS statement, rewrite:
                self.q[i] = UnparsedQuery(w[1:] + " HAS class " + self.q[i+1] + " \"" + self.q[i+2] + "\"")
                self.mask[i] = MASK_EXPRESSION
                remove += [i+1,i+2]

        if remove:
            for index in reversed(remove):
                del self.q[index]
                del self.mask[index]




    def __iter__(self):
        for w in self.q:
            yield w

    def __len__(self):
        return len(self.q)

    def __getitem__(self, index):
        try:
            return self.q[index]
        except:
            return ""

    def kw(self, index, value):
        try:
            if isinstance(value, tuple):
                return self.q[index] in value and self.mask[index] == MASK_NORMAL
            else:
                return self.q[index] == value and self.mask[index] == MASK_NORMAL
        except:
            return False


    def __exists__(self, keyword):
        for k,m in zip(self.q,self.mask):
            if keyword == k and m == MASK_NORMAL:
                return True
        return False

    def __setitem__(self, index, value):
        self.q[index] = value


    def __str__(self):
        s = []
        for w,m in zip(self.q,self.mask):
            if m == MASK_NORMAL:
                s.append(w)
            elif m == MASK_LITERAL:
                s.append('"' + w.replace('"','\\"') + '"')
            elif m == MASK_EXPRESSION:
                s.append('(' + str(w) + ')')
        return " ".join(s)






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
                i += 1
            elif isinstance(q[i], UnparsedQuery):
                filter,_  = Filter.parse(q[i])
                filters.append(filter)
                i += 1
                if q.kw(i,"AND") or q.kw(i, "OR"):
                    if logop and q[i] != logop:
                        raise SyntaxError("Mixed logical operators, use parentheses: " + str(q))
                    logop = q[i]
                    i += 1
                else:
                    break #done
            elif i == 0 and (q[i].startswith("PREVIOUS") or q[i].startswith("NEXT") or q.kw(i, ("LEFTCONTEXT","RIGHTCONTEXT","CONTEXT","PARENT","ANCESTOR","CHILD") )):
                #we have a context expression, always occuring in its own subquery
                modifier = q[i]
                i += 1
                selector,i =  Selector.parse(q,i)
                filters.append( (modifier, selector,None) )
                break
            elif q[i+1] in OPERATORS and q[i] and q[i+2]:
                operator = q[i+1]
                if q[i] == "class":
                    v = lambda x,y='cls': getattr(x,y)
                elif q[i] == "text":
                    v = lambda x,y='text': getattr(x,'text')()
                else:
                    v = lambda x,y=q[i]: getattr(x,y)
                if operator == '=' or operator == '==':
                    filters.append( lambda x,y=q[i+2],v=v : v(x) == y )
                elif operator == '!=':
                    filters.append( lambda x,y=q[i+2],v=v : v(x) != y )
                elif operator == '>':
                    filters.append( lambda x,y=q[i+2],v=v : v(x) > y )
                elif operator == '<':
                    filters.append( lambda x,y=q[i+2],v=v : v(x) < y )
                elif operator == '>=':
                    filters.append( lambda x,y=q[i+2],v=v : v(x) >= y )
                elif operator == '<=':
                    filters.append( lambda x,y=q[i+2],v=v : v(x) <= y )
                elif operator == 'CONTAINS':
                    filters.append( lambda x,y=q[i+2],v=v : v(x).find( y ) != -1 )
                elif operator == 'NOTCONTAINS':
                    filters.append( lambda x,y=q[i+2],v=v : v(x).find( y ) == -1 )
                elif operator == 'MATCHES':
                    filters.append( lambda x,y=re.compile(q[i+2]),v=v : y.search(v(x)) is not None  )
                elif operator == 'NOTMATCHES':
                    filters.append( lambda x,y=re.compile(q[i+2]),v=v : y.search(v(x)) is None  )

                if q.kw(i+3,("AND","OR")):
                    if logop and q[i+3] != logop:
                        raise SyntaxError("Mixed logical operators, use parentheses: " + str(q))
                    logop = q[i+3]
                    i += 4
                else:
                    i += 3
                    break #done
            elif 'HAS' in q[i:]:
                #has statement (spans full UnparsedQuery by definition)
                selector,i =  Selector.parse(q,i)
                if not q.kw(i,"HAS"):
                    raise SyntaxError("Expected HAS, got " + str(q[i]) + " at position " + str(i) + " in: " + str(q))
                i += 1
                subfilter,i = Filter.parse(q,i)
                filters.append( ("CHILD",selector,subfilter) )
            else:
                raise SyntaxError("Expected comparison operator, got " + str(q[i+1]) + " in: " + str(q))

        if negation and len(filters) > 1:
            raise SyntaxError("Expecting parentheses when NOT is used with multiple conditions")

        return Filter(filters, negation, logop == "OR"), i

    def __call__(self, query, element, debug=False):
        """Tests the filter on the specified element, returns a boolean"""
        match = True
        if debug: print("[FQL EVALUATION DEBUG] Filter - Testing filter [" + str(self) + "] for ", repr(element),file=sys.stderr)
        for filter in self.filters:
            if isinstance(filter,tuple):
                modifier, selector, subfilter = filter
                if debug: print("[FQL EVALUATION DEBUG] Filter - Filter is a subfilter of type " + modifier + ", descending...",file=sys.stderr)
                #we have a subfilter, i.e. a HAS statement on a subelement
                match = False
                if modifier == "CHILD":
                    for subelement,_ in selector(query, [element], True, debug): #if there are multiple subelements, they are always treated disjunctly
                        if not subfilter:
                            match = True
                        else:
                            match = subfilter(query, subelement, debug)
                        if match: break #only one subelement has to match by definition, then the HAS statement is matched
                elif modifier == "PARENT":
                    match = selector.match(query, element.parent,debug)
                elif modifier == "NEXT":
                    neighbour = element.next()
                    if neighbour:
                        match = selector.match(query, neighbour,debug)
                elif modifier == "PREVIOUS":
                    neighbour = element.previous()
                    if neighbour:
                        match = selector.match(query, neighbour,debug)
                else:
                    raise NotImplementedError("Context keyword " + modifier + " not implemented yet")
            elif isinstance(filter, Filter):
                #we have a nested filter (parentheses)
                match = filter(query, element, debug)
            else:
                #we have a condition function we can evaluate
                match = filter(element)

            if self.negation:
                match = not match
            if match:
                if self.disjunction:
                    if debug: print("[FQL EVALUATION DEBUG] Filter returns True",file=sys.stderr)
                    return True
            else:
                if not self.disjunction: #implies conjunction
                    if debug: print("[FQL EVALUATION DEBUG] Filter returns False",file=sys.stderr)
                    return False

        if debug: print("[FQL EVALUATION DEBUG] Filter returns ", str(match),file=sys.stderr)
        return match

    def __str__(self):
        q = ""
        if self.negation:
            q += "NOT "
        for i, filter in enumerate(self.filters):
            if i > 0:
                if self.disjunction:
                    q += "OR "
                else:
                    q += "AND "
            if isinstance(filter, Filter):
                q += "(" + str(filter) + ") "
            elif isinstance(filter, tuple):
                modifier,selector,subfilter = filter
                q += "(" + modifier + " " + str(selector) + " HAS " + str(subfilter) + ") "
            else:
                #original filter can't be reconstructed, place dummy:
                q += "...\"" + str(filter.__defaults__[0]) +"\""
        return q.strip()




class SpanSet(list):
    def select(self,*args):
        raise QueryError("Got a span set for a non-span element")

    def partof(self, collection):
        for e in collection:
            if isinstance(e, SpanSet):
                if len(e) != len(self):
                    return False
                for c1,c2 in zip(e,self):
                    if c1 is not c2:
                        return False
        return False



class Selector(object):
    def __init__(self, Class, set=None,id=None, filter=None, nextselector=None, expansion = None):
        self.Class = Class
        self.set = set
        self.id = id
        self.filter = filter
        self.nextselector =  nextselector #selectors can be chained
        self.expansion = expansion #{min,max} occurrence interval, allowed only in Span and evaluated there instead of here


    def chain(self, targets):
        assert targets[0] is self
        selector = self
        selector.nextselector = None
        for target in targets[1:]:
            selector.nextselector = target
            selector = target

    @staticmethod
    def parse(q, i=0, allowexpansion=False):
        l = len(q)
        set = None
        id = None
        filter = None
        expansion = None

        if q[i] == "ID" and q[i+1]:
            id = q[i+1]
            Class = None
            i += 2
        else:
            if q[i] == "ALL":
                Class = "ALL"
            else:
                try:
                    Class = folia.XML2CLASS[q[i]]
                except:
                    raise SyntaxError("Expected element type, got " + str(q[i]) + " in: " + str(q))
            i += 1

        if q[i] and q[i][0] == "{" and q[i][-1] == "}":
            if not allowexpansion:
                raise SyntaxError("Expansion expressions not allowed at this point, got one at position " + str(i) + " in: " + str(q))
            expansion = q[i][1:-1]
            expansion = expansion.split(',')
            i += 1
            try:
                if len(expansion) == 1:
                    expansion = (int(expansion), int(expansion))
                elif len(expansion) == 2 and expansion[0] == "":
                    expansion = (0,int(expansion[1]))
                elif len(expansion) == 2 and expansion[1] == "":
                    expansion = (int(expansion[0]),MAXEXPANSION)
                elif len(expansion) == 2:
                    expansion = tuple(int(x) for x in expansion if x)
                else:
                    raise SyntaxError("Invalid expansion expression: " + ",".join(expansion))
            except ValueError:
                raise SyntaxError("Invalid expansion expression: " + ",".join(expansion))

        while i < l:
            if q.kw(i,"OF") and q[i+1]:
                set = q[i+1]
                i += 2
            elif q.kw(i,"ID") and q[i+1]:
                id = q[i+1]
                i += 2
            elif q.kw(i, "WHERE"):
                #ok, big filter coming up!
                filter, i = Filter.parse(q,i+1)
                break
            else:
                #something we don't handle
                break

        return Selector(Class,set,id,filter, None, expansion), i

    def __call__(self, query, contextselector, recurse=True, debug=False): #generator, lazy evaluation!
        if isinstance(contextselector,tuple) and len(contextselector) == 2:
            selection = contextselector[0](*contextselector[1])
        else:
            selection = contextselector

        count = 0

        for e in selection:
            selector = self
            while True: #will loop through the chain of selectors, only the first one is called explicitly
                if debug: print("[FQL EVALUATION DEBUG] Select - Running selector [", str(self), "] on ", repr(e),file=sys.stderr)

                if selector.id:
                    if debug: print("[FQL EVALUATION DEBUG] Select - Selecting ID " + selector.id,file=sys.stderr)
                    try:
                        candidate = query.doc[selector.id]
                        selector.Class = candidate.__class__
                        if not selector.filter or  selector.filter(query,candidate, debug):
                            if debug: print("[FQL EVALUATION DEBUG] Select - Yielding (by ID) ", repr(candidate),file=sys.stderr)
                            yield candidate, None
                    except KeyError:
                        pass #silently ignore ID mismatches
                elif selector.Class == "ALL":
                    for candidate in e:
                        if isinstance(candidate, folia.AbstractElement):
                            yield candidate, e
                elif selector.Class:
                    if debug: print("[FQL EVALUATION DEBUG] Select - Selecting Class " + selector.Class.XMLTAG + " with set " + str(selector.set),file=sys.stderr)
                    if selector.Class.XMLTAG in query.defaultsets:
                        selector.set = query.defaultsets[selector.Class.XMLTAG]
                    isspan = issubclass(selector.Class, folia.AbstractSpanAnnotation)
                    if isinstance(e, tuple): e = e[0]
                    if isspan and (isinstance(e, folia.Word) or isinstance(e, folia.Morpheme)):
                        for candidate in e.findspans(selector.Class, selector.set):
                            if not selector.filter or  selector.filter(query,candidate, debug):
                                if debug: print("[FQL EVALUATION DEBUG] Select - Yielding span, single reference: ", repr(candidate),file=sys.stderr)
                                yield candidate, e
                    elif isspan and isinstance(e, SpanSet):
                        #we take the first item of the span to find the candidates
                        for candidate in e[0].findspans(selector.Class, selector.set):
                            if not selector.filter or  selector.filter(query,candidate, debug):
                                #test if all the other elements in the span are in this candidate
                                matched = True
                                spanelements = list(candidate.wrefs())
                                for e2 in e[1:]:
                                    if e2 not in spanelements:
                                        matched = False
                                        break
                                if matched:
                                    if debug: print("[FQL EVALUATION DEBUG] Select - Yielding span, multiple references: ", repr(candidate),file=sys.stderr)
                                    yield candidate, e
                    elif isinstance(e, SpanSet):
                        yield e, e
                    else:
                        #print("DEBUG: doing select " + selector.Class.__name__ + " (recurse=" + str(recurse)+") on " + repr(e))
                        for candidate  in e.select(selector.Class, selector.set, recurse):
                            try:
                                if candidate.changedbyquery is query:
                                    #this candidate has been added/modified by the query, don't select it again
                                    continue
                            except AttributeError:
                                pass
                            if not selector.filter or  selector.filter(query,candidate, debug):
                                if debug: print("[FQL EVALUATION DEBUG] Select - Yielding ", repr(candidate), " in ", repr(e),file=sys.stderr)
                                yield candidate, e

                if selector.nextselector is None:
                    if debug: print("[FQL EVALUATION DEBUG] Select - End of chain",file=sys.stderr)
                    break # end of chain
                else:
                    if debug: print("[FQL EVALUATION DEBUG] Select - Selecting next in chain",file=sys.stderr)
                    selector = selector.nextselector


    def match(self, query, candidate, debug = False):
        if debug: print("[FQL EVALUATION DEBUG] Select - Matching selector [", str(self), "] on ", repr(candidate),file=sys.stderr)
        if self.id:
            if candidate.id != self.id:
                return False
        elif self.Class:
            if not isinstance(candidate,self.Class):
                return False
        if self.filter and not self.filter(query,candidate, debug):
            return False
        if debug: print("[FQL EVALUATION DEBUG] Select - Selector matches! ", repr(candidate),file=sys.stderr)
        return True

    def autodeclare(self,doc):
        if self.Class and self.set:
            if not doc.declared(self.Class, self.set):
                doc.declare(self.Class, self.set)
            if self.nextselector:
                self.nextselector.autodeclare()

    def __str__(self):
        s = ""
        if self.Class:
            s += self.Class.XMLTAG + " "
        if self.set:
            s += "OF " + self.set + " "
        if self.id:
            s += "ID " + self.id + " "
        if self.filter:
            s += "WHERE " + str(self.filter)

        if self.nextselector:
            s += str(self.nextselector)
        return s.strip()


class Span(object):
    def __init__(self, targets, intervals = []):
        self.targets = targets #Selector instances making up the span

    @staticmethod
    def parse(q, i=0):
        targets = []
        l = len(q)
        while i < l:
            if q.kw(i,"ID") or q[i] in folia.XML2CLASS:
                target,i = Selector.parse(q,i, True)
                targets.append(target)
            elif q.kw(i,"&"):
                #we're gonna have more targets
                i += 1
            else:
                break

        if not targets:
            raise SyntaxError("Expected one or more span targets, got " + str(q[i]) + " in: " + str(q))

        return Span(targets), i

    def __call__(self, query, contextselector, recurse=True,debug=False): #returns a list of element in a span
        if debug: print("[FQL EVALUATION DEBUG] Span  - Building span from target selectors (" + str(len(self.targets)) + ")",file=sys.stderr)

        backtrack = []
        l = len(self.targets)

        #find the first non-optional element, it will be our pivot:
        pivotindex = None
        for i, target in enumerate(self.targets):
            if self.targets[i].id or not self.targets[i].expansion or self.targets[i].expansion[0] > 0:
                pivotindex = i
                break
        if pivotindex is None:
            raise QueryError("All parts in the SPAN expression are optional, at least one non-optional component is required")


        #get first target
        for element, target in self.targets[pivotindex](query, contextselector, recurse,debug):
            if debug: print("[FQL EVALUATION DEBUG] Span  - First item of span found  (pivotindex=" + str(pivotindex) + ",l=" + str(l) + "," + str(repr(element)) + ")",file=sys.stderr)
            spanset = SpanSet() #elemnent is added later

            match = True #we attempt to disprove this


            #now see if consecutive elements match up


            #--- matching prior to pivot -------

            #match optional elements before pivotindex
            i = pivotindex
            currentelement = element
            while i > 0:
                i -= 1
                if i < 0: break
                selector = self.targets[i]
                minmatches = selector.expansion[0]
                assert minmatches == 0 #everything before pivot has to have minmatches 0
                maxmatches = selector.expansion[1]
                done = False

                matches = 0
                while True:
                    prevelement = element
                    element = element.previous(selector.Class, None)
                    if not element or (target and target not in element.ancestors()):
                        if debug: print("[FQL EVALUATION DEBUG] Span  - Prior element not found or out of scope",file=sys.stderr)
                        done = True #no more elements left
                        break
                    elif element and not selector.match(query, element,debug):
                        if debug: print("[FQL EVALUATION DEBUG] Span  - Prior element does not match filter",file=sys.stderr)
                        element = prevelement #reset
                        break

                    if debug: print("[FQL EVALUATION DEBUG] Span  - Prior element matches",file=sys.stderr)
                    #we have a match
                    matches += 1
                    spanset.insert(0,element)
                    if matches >= maxmatches:
                        if debug: print("[FQL EVALUATION DEBUG] Span  - Maximum threshold reached for span selector " + str(i) + ", breaking", file=sys.stderr)
                        break

                if done:
                    break

            #--- matching pivot and selectors after pivot  -------

            done = False #are we done with this selector?
            element = currentelement
            i = pivotindex - 1 #loop does +1 at the start of each iteration, we want to start with the pivotindex
            while i < l:
                i += 1
                if i == l:
                    if debug: print("[FQL EVALUATION DEBUG] Span  - No more selectors to try",i,l, file=sys.stderr)
                    break
                selector = self.targets[i]
                if selector.id: #selection by ID, don't care about consecutiveness
                    try:
                        element = query.doc[selector.id]
                        if debug: print("[FQL EVALUATION DEBUG] Span  - Obtained subsequent span item from ID: ", repr(element), file=sys.stderr)
                    except KeyError:
                        if debug: print("[FQL EVALUATION DEBUG] Span  - Obtained subsequent with specified ID does not exist ", file=sys.stderr)
                        match = False
                        break
                    if element and not selector.match(query, element,debug):
                        if debug: print("[FQL EVALUATION DEBUG] Span  - Subsequent element does not match filter",file=sys.stderr)
                    else:
                        spanset.append(element)

                else: #element must be consecutive
                    if selector.expansion:
                        minmatches = selector.expansion[0]
                        maxmatches = selector.expansion[1]
                    else:
                        minmatches = maxmatches = 1

                    if debug: print("[FQL EVALUATION DEBUG] Span  - Preparing to match selector " + str(i) + " of span, expansion={" + str(minmatches) + "," + str(maxmatches) + "}", file=sys.stderr)
                    matches = 0

                    while True:
                        submatch = True #does the element currenty under consideration match? (the match variable is reserved for the entire match)
                        done = False #are we done with this span selector?
                        holdelement = False #do not go to next element

                        if debug: print("[FQL EVALUATION DEBUG] Span  - Processing element with span selector " + str(i) + ": ", repr(element), file=sys.stderr)

                        if not element or (target and target not in element.ancestors()):
                            if debug:
                                if not element:
                                    print("[FQL EVALUATION DEBUG] Span  - Element not found",file=sys.stderr)
                                elif target and not target in element.ancestors():
                                    print("[FQL EVALUATION DEBUG] Span  - Element out of scope",file=sys.stderr)
                            submatch = False
                        elif element and not selector.match(query, element,debug):
                            if debug: print("[FQL EVALUATION DEBUG] Span  - Element does not match filter",file=sys.stderr)
                            submatch = False

                        if submatch:
                            matches += 1
                            if debug: print("[FQL EVALUATION DEBUG] Span  - Element is a match, got " + str(matches) + " match(es) now", file=sys.stderr)

                            if matches > minmatches:
                                #check if the next selector(s) match too, then we have a point where we might branch two ways
                                #j = 1
                                #while i+j < len(self.targets):
                                #    nextselector = self.targets[i+j]
                                #    if nextselector.match(query, element,debug):
                                #        #save this point for backtracking, when we get stuck, we'll roll back to this point
                                #       backtrack.append( (i+j, prevelement, copy(spanset) ) ) #using prevelement, nextelement will be recomputed after backtracking,   using different selector
                                #   if not nextselector.expansion or nextselector.expansion[0] > 0:
                                #        break
                                #    j += 1
                                #TODO: implement
                                pass
                            elif matches < minmatches:
                                if debug: print("[FQL EVALUATION DEBUG] Span  - Minimum threshold not reached yet for span selector " + str(i), file=sys.stderr)

                            spanset.append(element)
                            if matches >= maxmatches:
                                if debug: print("[FQL EVALUATION DEBUG] Span  - Maximum threshold reached for span selector " + str(i) + ", breaking", file=sys.stderr)
                                done = True #done with this selector
                        else:
                            if matches < minmatches:
                                #can we backtrack?
                                if backtrack: #(not reached currently)
                                    if debug: print("[FQL EVALUATION DEBUG] Span  - Backtracking",file=sys.stderr)
                                    index, element, spanset = backtrack.pop()
                                    i = index - 1 #next iteration will do +1 again
                                    match = True #default
                                    continue
                                else:
                                    #nope, all is lost, we have no match
                                    if debug: print("[FQL EVALUATION DEBUG] Span  - Minimum threshold could not be attained for span selector " + str(i), file=sys.stderr)
                                    match = False
                                    break
                            else:
                                if debug: print("[FQL EVALUATION DEBUG] Span  - No match for span selector " + str(i) + ", but no problem since matching threshold was already reached", file=sys.stderr)
                                holdelement = True
                                done = True
                                break

                        if not holdelement:
                            prevelement = element
                            #get next element
                            element = element.next(selector.Class, None)
                            if debug: print("[FQL EVALUATION DEBUG] Span  - Selecting next element for next round", repr(element), file=sys.stderr)

                        if done or not match:
                            if debug: print("[FQL EVALUATION DEBUG] Span  - Done with span selector " + str(i), repr(element), file=sys.stderr)
                            break

                    if not match: break

            if match:
                if debug: print("[FQL EVALUATION DEBUG] Span  - Span found, returning spanset (" + repr(spanset) + ")",file=sys.stderr)
                yield spanset
            else:
                if debug: print("[FQL EVALUATION DEBUG] Span  - Span not found",file=sys.stderr)




class Target(object): #FOR/IN... expression
    def __init__(self, targets, strict=False,nested = None, start=None, end=None,endinclusive=True,repeat=False):
        self.targets = targets #Selector instances
        self.strict = strict #True for IN
        self.nested = nested #in a nested another target
        self.start = start
        self.end = end
        self.endinclusive = endinclusive
        self.repeat = repeat


    @staticmethod
    def parse(q, i=0):
        if q.kw(i,'FOR'):
            strict = False
        elif q.kw(i,'IN'):
            strict = True
        else:
            raise SyntaxError("Expected target expression, got " + str(q[i]) + " in: " + str(q))
        i += 1

        targets = []
        nested = None
        start = end = None
        endinclusive = True
        repeat = False
        l = len(q)
        while i < l:
            if q.kw(i,'SPAN'):
                target,i = Span.parse(q,i+1)
                targets.append(target)
            elif q.kw(i,"ID") or q[i] in folia.XML2CLASS or q[i] == "ALL":
                target,i = Selector.parse(q,i)
                targets.append(target)
            elif q.kw(i,","):
                #we're gonna have more targets
                i += 1
            elif q.kw(i, ('FOR','IN')):
                nested,i = Selector.parse(q,i+1)
            elif q.kw(i,"START"):
                start,i = Selector.parse(q,i+1)
            elif q.kw(i,("END","ENDAFTER")): #inclusive
                end,i = Selector.parse(q,i+1)
                endinclusive = True
            elif q.kw(i,"ENDBEFORE"): #exclusive
                end,i = Selector.parse(q,i+1)
                endinclusive = False
            elif q.kw(i,"REPEAT"):
                repeat = True
                i += 1
            else:
                break

        if not targets:
            raise SyntaxError("Expected one or more targets, got " + str(q[i]) + " in: " + str(q))

        return Target(targets,strict,nested,start,end,endinclusive, repeat), i


    def __call__(self, query, contextselector, recurse, debug=False): #generator, lazy evaluation!
        if self.nested:
            if debug: print("[FQL EVALUATION DEBUG] Target - Deferring to nested target first",file=sys.stderr)
            contextselector = (self.nested, (query, contextselector, not self.strict))

        if debug: print("[FQL EVALUATION DEBUG] Target - Chaining and calling target selectors (" + str(len(self.targets)) + ")",file=sys.stderr)

        if self.targets:
            if isinstance(self.targets[0], Span):
                for span in self.targets:
                    if not isinstance(span, Span): raise QueryError("SPAN statement may not be mixed with non-span statements in a single selection")
                    if debug: print("[FQL EVALUATION DEBUG] Target - Evaluation span ",file=sys.stderr)
                    for spanset in span(query, contextselector, recurse, debug):
                        if debug: print("[FQL EVALUATION DEBUG] Target - Yielding spanset ",file=sys.stderr)
                        yield spanset
            else:
                selector = self.targets[0]
                selector.chain(self.targets)

                started = (self.start is None)
                dobreak = False

                for e,_ in selector(query, contextselector, recurse, debug):
                    if not started:
                        if self.start.match(query, e):
                            if debug: print("[FQL EVALUATION DEBUG] Target - Matched start! Starting from here...",e, file=sys.stderr)
                            started = True
                    if started:
                        if self.end:
                            if self.end.match(query, e):
                                if not self.endinclusive:
                                    if debug: print("[FQL EVALUATION DEBUG] Target - Matched end! Breaking before yielding...",e, file=sys.stderr)
                                    started = False
                                    if self.repeat:
                                        continue
                                    else:
                                        break
                                else:
                                    if debug: print("[FQL EVALUATION DEBUG] Target - Matched end! Breaking after yielding...",e, file=sys.stderr)
                                    started = False
                                    dobreak = True
                        if debug: print("[FQL EVALUATION DEBUG] Target - Yielding  ",e, file=sys.stderr)
                        yield e
                        if dobreak and not self.repeat:
                            break






class Alternative(object):  #AS ALTERNATIVE ... expression
    def __init__(self, subassignments={},assignments={},filter=None, nextalternative=None):
        self.subassignments = subassignments
        self.assignments = assignments
        self.filter = filter
        self.nextalternative = nextalternative

    @staticmethod
    def parse(q,i=0):
        if q.kw(i,'AS') and q[i+1] == "ALTERNATIVE":
            i += 1

        subassignments = {}
        assignments = {}
        filter = None

        if q.kw(i,'ALTERNATIVE'):
            i += 1
            if not q.kw(i,'WITH'):
                i = getassignments(q, i, subassignments)
            if q.kw(i,'WITH'):
                i = getassignments(q, i+1,  assignments)
            if q.kw(i,'WHERE'):
                filter, i = Filter.parse(q, i+1)
        else:
            raise SyntaxError("Expected ALTERNATIVE, got " + str(q[i]) + " in: " + str(q))

        if q.kw(i,'ALTERNATIVE'):
            #we have another!
            nextalternative,i  = Alternative.parse(q,i)
        else:
            nextalternative = None

        return Alternative(subassignments, assignments, filter, nextalternative), i

    def __call__(self, query, action, focus, target,debug=False):
        """Action delegates to this function"""
        isspan = isinstance(action.focus.Class, folia.AbstractSpanAnnotation)

        subassignments = {} #make a copy
        for key, value in action.assignments.items():
            subassignments[key] = value
        for key, value in self.subassignments.items():
            subassignments[key] = value

        if action.action == "SELECT":
            if not focus: raise QueryError("SELECT requires a focus element")
            if not isspan:
                for alternative in focus.alternatives(action.focus.Class, focus.set):
                    if not self.filter or (self.filter and self.filter.match(query, alternative, debug)):
                        yield alternative
            else:
                raise NotImplementedError("Selecting alternative span not implemented yet")
        elif action.action == "EDIT" or action.action == "ADD":
            if not isspan:
                if focus:
                    parent = focus.ancestor(folia.AbstractStructureElement)
                    alternative = folia.Alternative( query.doc, action.focus.Class( query.doc , **subassignments), **self.assignments)
                    parent.append(alternative)
                    yield alternative
                else:
                    alternative = folia.Alternative( query.doc, action.focus.Class( query.doc , **subassignments), **self.assignments)
                    target.append(alternative)
                    yield alternative
            else:
                raise NotImplementedError("Editing alternative span not implemented yet")
        else:
            raise QueryError("Alternative does not handle action " + action.action)


    def autodeclare(self, doc):
        pass #nothing to declare

    def substitute(self, *args):
        raise QueryError("SUBSTITUTE not supported with AS ALTERNATIVE")

class Correction(object): #AS CORRECTION/SUGGESTION expression...
    def __init__(self, set,actionassignments={}, assignments={},filter=None,suggestions=[], bare=False):
        self.set = set
        self.actionassignments = actionassignments #the assignments in the action
        self.assignments = assignments #the assignments for the correction
        self.filter = filter
        self.suggestions = suggestions # [ (subassignments, suggestionassignments) ]
        self.bare = bare

    @staticmethod
    def parse(q,i, focus):
        if q.kw(i,'AS') and q.kw(i+1,'CORRECTION'):
            i += 1
            bare = False
        if q.kw(i,'AS') and q.kw(i+1,'BARE') and q.kw(i+2,'CORRECTION'):
            bare = True
            i += 2

        set = None
        actionassignments = {}
        assignments = {}
        filter = None
        suggestions = []

        if q.kw(i,'CORRECTION'):
            i += 1
            if q.kw(i,'OF') and q[i+1]:
                set = q[i+1]
                i += 2
            if not q.kw(i,'WITH'):
                i = getassignments(q, i, actionassignments, focus)
            if q.kw(i,'WHERE'):
                filter, i = Filter.parse(q, i+1)
            if q.kw(i,'WITH'):
                i = getassignments(q, i+1,  assignments)
        else:
            raise SyntaxError("Expected CORRECTION, got " + str(q[i]) + " in: " + str(q))

        l = len(q)
        while i < l:
            if q.kw(i,'SUGGESTION'):
                i+= 1
                suggestion = ( {}, {} )
                if isinstance(q[i], UnparsedQuery):
                    if not q[i].kw(0,'SUBSTITUTE') and not q[i].kw(0,'ADD'):
                        raise SyntaxError("Subexpression after SUGGESTION, expected ADD or SUBSTITUTE, got " + str(q[i]))
                    Correction.parsesubstitute(q[i],suggestion)
                    i += 1
                elif q.kw(i,'MERGE'):
                    suggestion[0]['merge'] = True
                    i+= 1
                elif q.kw(i,'SPLIT'):
                    suggestion[0]['split'] = True
                    i+= 1
                elif q.kw(i,'DELETION'):
                    #No need to do anything, DELETION is just to make things more explicit in the syntax, it will result in an empty suggestion
                    i+= 1
                elif not q.kw(i,'WITH'):
                    i = getassignments(q, i, suggestion[0], focus) #subassignments (the actual element in the suggestion)
                if q.kw(i,'WITH'):
                    i = getassignments(q, i+1, suggestion[1]) #assignments for the suggestion
                suggestions.append(suggestion)
            else:
                raise SyntaxError("Expected SUGGESTION or end of AS clause, got " + str(q[i]) + " in: " + str(q))

        return Correction(set, actionassignments, assignments, filter, suggestions, bare), i

    @staticmethod
    def parsesubstitute(q,suggestion):
        suggestion[0]['substitute'],_ = Action.parse(q)

    def __call__(self, query, action, focus, target,debug=False):
        """Action delegates to this function"""
        if debug: print("[FQL EVALUATION DEBUG] Correction - Processing ", repr(focus),file=sys.stderr)

        isspan = isinstance(action.focus.Class, folia.AbstractSpanAnnotation)


        actionassignments = {} #make a copy
        for key, value in action.assignments.items():
            if key == 'class': key = 'cls'
            actionassignments[key] = value
        for key, value in self.actionassignments.items():
            if key == 'class': key = 'cls'
            actionassignments[key] = value

        if actionassignments:
            if (not 'set' in actionassignments or actionassignments['set'] is None) and action.focus.Class:
                try:
                    actionassignments['set'] = query.defaultsets[action.focus.Class.XMLTAG]
                except KeyError:
                    actionassignments['set'] = query.doc.defaultset(action.focus.Class)
            if folia.Attrib.ID in action.focus.Class.REQUIRED_ATTRIBS:
                actionassignments['id'] = getrandomid(query, "corrected." + action.focus.Class.XMLTAG + ".")

        kwargs = {}
        if self.set:
            kwargs['set'] = self.set

        for key, value in self.assignments.items():
            if key == 'class': key = 'cls'
            kwargs[key] = value

        if action.action == "SELECT":
            if not focus: raise QueryError("SELECT requires a focus element")
            correction = focus.incorrection()
            if correction:
                if not self.filter or (self.filter and self.filter.match(query, correction, debug)):
                    yield correction
        elif action.action in ("EDIT","ADD","PREPEND","APPEND"):
            if focus:
                correction = focus.incorrection()
            else:
                correction = False

            inheritchildren = []
            if focus and not self.bare: #copy all data within
                inheritchildren = list(focus.copychildren(query.doc, True))
                if action.action == "EDIT" and 'respan' in action.extra:
                    #delete all word references from the copy first, we will add new ones
                    inheritchildren = [ c  for c in inheritchildren if not isinstance(c, folia.WordReference) ]
                    if not isinstance(focus, folia.AbstractSpanAnnotation): raise QueryError("Can only perform RESPAN on span annotation elements!")
                    contextselector = target if target else query.doc
                    spanset = next(action.extra['respan'](query, contextselector, True, debug)) #there can be only one
                    for w in spanset:
                        inheritchildren.append(w)

            if actionassignments:
                kwargs['new'] = action.focus.Class(query.doc,*inheritchildren, **actionassignments)
                if focus and action.action not in ('PREPEND','APPEND'):
                    kwargs['original'] = focus
                #TODO: if not bare, fix all span annotation references to this element
            elif focus and action.action not in ('PREPEND','APPEND'):
                if isinstance(focus, folia.AbstractStructureElement):
                    kwargs['current'] = focus #current only needed for structure annotation
                if correction and (not 'set' in kwargs or correction.set == kwargs['set']) and (not 'cls' in kwargs or correction.cls == kwargs['cls']): #reuse the existing correction element
                    print("Reusing " + correction.id,file=sys.stderr)
                    kwargs['reuse'] = correction

            if action.action in ('PREPEND','APPEND'):
                #get parent relative to target
                parent = target.ancestor( (folia.AbstractStructureElement, folia.AbstractSpanAnnotation, folia.AbstractAnnotationLayer) )
            elif focus:
                if 'reuse' in kwargs and kwargs['reuse']:
                    parent = focus.ancestor( (folia.AbstractStructureElement, folia.AbstractSpanAnnotation, folia.AbstractAnnotationLayer) )
                else:
                    parent = focus.ancestor( (folia.AbstractStructureElement, folia.AbstractSpanAnnotation, folia.AbstractAnnotationLayer, folia.Correction) )
            else:
                parent = target

            if 'id' not in kwargs and 'reuse' not in kwargs:
                kwargs['id'] = parent.generate_id(folia.Correction)

            kwargs['suggestions'] = []
            for subassignments, suggestionassignments in self.suggestions:
                subassignments = copy(subassignments) #assignment for the element in the suggestion
                for key, value in action.assignments.items():
                    if not key in subassignments:
                        if key == 'class': key = 'cls'
                        subassignments[key] = value
                if (not 'set' in subassignments or subassignments['set'] is None) and action.focus.Class:
                    try:
                        subassignments['set'] = query.defaultsets[action.focus.Class.XMLTAG]
                    except KeyError:
                        subassignments['set'] = query.doc.defaultset(action.focus.Class)
                if focus and not self.bare: #copy all data within (we have to do this again for each suggestion as it will generate different ID suffixes)
                    inheritchildren = list(focus.copychildren(query.doc, True))
                if folia.Attrib.ID in action.focus.Class.REQUIRED_ATTRIBS:
                    subassignments['id'] = getrandomid(query, "suggestion.")
                kwargs['suggestions'].append( folia.Suggestion(query.doc, action.focus.Class(query.doc, *inheritchildren,**subassignments), **suggestionassignments )   )

            if action.action == 'PREPEND':
                index = parent.getindex(target,True) #recursive
                if index == -1:
                    raise QueryError("Insertion point for PREPEND action not found")
                kwargs['insertindex'] = index
                kwargs['nooriginal'] = True
            elif action.action == 'APPEND':
                index = parent.getindex(target,True) #recursive
                if index == -1:
                    raise QueryError("Insertion point for APPEND action not found")
                kwargs['insertindex'] = index+1
                kwargs['insertindex_offset'] = 1 #used by correct if it needs to recompute the index
                kwargs['nooriginal'] = True

            yield parent.correct(**kwargs) #generator
        elif action.action == "DELETE":
            if debug: print("[FQL EVALUATION DEBUG] Correction - Deleting ", repr(focus), " (in " + repr(focus.parent) + ")",file=sys.stderr)
            if not focus: raise QueryError("DELETE AS CORRECTION did not find a focus to operate on")
            kwargs['original'] = focus
            kwargs['new'] = [] #empty new
            c = focus.parent.correct(**kwargs) #generator
            yield c
        else:
            raise QueryError("Correction does not handle action " + action.action)


    def autodeclare(self,doc):
        if self.set:
            if not doc.declared(folia.Correction, self.set):
                doc.declare(folia.Correction, self.set)

    def prepend(self, query, content, contextselector, debug):
        return self.insert(query, content, contextselector, 0, debug)

    def append(self, query, content, contextselector, debug):
        return self.insert(query, content, contextselector, 1, debug)

    def insert(self,  query, content, contextselector, offset, debug):
        kwargs = {}
        if self.set:
            kwargs['set'] = self.set
        for key, value in self.assignments.items():
            if key == 'class': key = 'cls'
            kwargs[key] = value
        self.autodeclare(query.doc)

        if not content:
            #suggestions only, no subtitution obtained from main action yet, we have to process it still
            if debug: print("[FQL EVALUATION DEBUG] Correction.insert - Initialising for suggestions only",file=sys.stderr)
            if isinstance(contextselector,tuple) and len(contextselector) == 2:
                contextselector = contextselector[0](*contextselector[1])
            target = list(contextselector)[0] #not a spanset


            insertindex = 0
            #find insertion index:
            for i, e in enumerate(target.parent):
                if e is target[0]:
                    insertindex = i
                    break

            content = {'parent': target.parent,'new':[]}
            kwargs['insertindex'] = insertindex + offset
        else:
            kwargs['insertindex'] = content['index'] + offset
            if debug: print("[FQL EVALUATION DEBUG] Correction.insert - Initialising correction",file=sys.stderr)
            kwargs['new'] = [] #stuff will be appended

        kwargs['nooriginal'] = True #this is an insertion, there is no original
        kwargs = self.assemblesuggestions(query,content,debug,kwargs)

    def substitute(self, query, substitution, contextselector, debug):
        kwargs = {}
        if self.set:
            kwargs['set'] = self.set
        for key, value in self.assignments.items():
            if key == 'class': key = 'cls'
            kwargs[key] = value
        self.autodeclare(query.doc)


        if not substitution:
            #suggestions only, no subtitution obtained from main action yet, we have to process it still
            if debug: print("[FQL EVALUATION DEBUG] Correction.substitute - Initialising for suggestions only",file=sys.stderr)
            if isinstance(contextselector,tuple) and len(contextselector) == 2:
                contextselector = contextselector[0](*contextselector[1])
            target = list(contextselector)[0]
            if not isinstance(target, SpanSet):
                raise QueryError("SUBSTITUTE expects target SPAN")

            prev = target[0].parent
            for e in target[1:]:
                if e.parent != prev:
                    raise QueryError("SUBSTITUTE can only be performed when the target items share the same parent. First parent is " + repr(prev) + ", parent of " + repr(e) + " is " + repr(e.parent))

            insertindex = 0
            #find insertion index:
            for i, e in enumerate(target[0].parent):
                if e is target[0]:
                    insertindex = i
                    break

            substitution = {'parent': target[0].parent,'new':[]}
            kwargs['insertindex'] = insertindex
            kwargs['current'] = target
        else:
            kwargs['insertindex'] = substitution['index']
            kwargs['original'] =  substitution['span']
            if debug: print("[FQL EVALUATION DEBUG] Correction.substitute - Initialising correction",file=sys.stderr)
            kwargs['new'] = [] #stuff will be appended

        kwargs = self.assemblesuggestions(query,substitution,debug,kwargs)

        if debug: print("[FQL EVALUATION DEBUG] Correction.substitute - Returning correction",file=sys.stderr)
        return substitution['parent'].correct(**kwargs)


    def assemblesuggestions(self, query, substitution, debug, kwargs):
        if self.suggestions:
            kwargs['suggestions'] = [] #stuff will be appended

        for i, (Class, actionassignments, subactions) in enumerate(substitution['new']):
            if actionassignments:
                if (not 'set' in actionassignments or actionassignments['set'] is None):
                    try:
                        actionassignments['set'] = query.defaultsets[Class.XMLTAG]
                    except KeyError:
                        actionassignments['set'] = query.doc.defaultset(Class)
            actionassignments['id'] = "corrected.%08x" % random.getrandbits(32) #generate a random ID
            e = Class(query.doc, **actionassignments)
            if debug: print("[FQL EVALUATION DEBUG] Correction.substitute - Adding to new",file=sys.stderr)
            kwargs['new'].append(e)
            for subaction in subactions:
                subaction.focus.autodeclare(query.doc)
                if debug: print("[FQL EVALUATION DEBUG] Correction.substitute - Invoking subaction", subaction.action,file=sys.stderr)
                subaction(query, [e], debug ) #note: results of subactions will be silently discarded

        for subassignments, suggestionassignments in self.suggestions:
            suggestionchildren = []
            if 'substitute' in subassignments:
                #SUBTITUTE (or synonym ADD)
                action = subassignments['substitute']
                del subassignments['substitute']
            else:
                #we have a suggested deletion
                action = None
            if debug: print("[FQL EVALUATION DEBUG] Correction.assemblesuggestions - Adding suggestion",file=sys.stderr)
            while action:
                subassignments = copy(subassignments) #assignment for the element in the suggestion
                if isinstance(action.focus, tuple) and len(action.focus) == 2:
                    action.focus = action.focus[0]
                for key, value in action.assignments.items():
                    if key == 'class': key = 'cls'
                    subassignments[key] = value
                if (not 'set' in subassignments or subassignments['set'] is None) and action.focus.Class:
                    try:
                        subassignments['set'] = query.defaultsets[action.focus.Class.XMLTAG]
                    except KeyError:
                        subassignments['set'] = query.doc.defaultset(action.focus.Class)
                focus = action.focus
                focus.autodeclare(query.doc)
                if folia.Attrib.ID in focus.Class.REQUIRED_ATTRIBS:
                    subassignments['id'] = getrandomid(query, "suggestion.")
                suggestionchildren.append( focus.Class(query.doc, **subassignments))
                action = action.nextaction

            if 'split' in suggestionassignments and suggestionassignments['split']:
                suggestionassignments['split'] = focus.ancestor(folia.StructureElement).id
            if 'merge' in suggestionassignments and suggestionassignments['merge']:
                suggestionassignments['merge'] = focus.ancestor(folia.StructureElement).id
            kwargs['suggestions'].append( folia.Suggestion(query.doc,*suggestionchildren, **suggestionassignments )   )

        return kwargs


def getassignments(q, i, assignments,  focus=None):
    l = len(q)
    while i < l:
        if q.kw(i, ('id','set','annotator','class','n')):
            assignments[q[i]] = q[i+1]
            i+=2
        elif q.kw(i,'confidence'):
            try:
                assignments[q[i]] = float(q[i+1])
            except:
                raise SyntaxError("Invalid value for confidence: " + str(q[i+1]))
            i+=2
        elif q.kw(i,'annotatortype'):
            if q[i+1] == "auto":
                assignments[q[i]] = folia.AnnotatorType.AUTO
            elif q[i+1] == "manual":
                assignments[q[i]] = folia.AnnotatorType.MANUAL
            else:
                raise SyntaxError("Invalid value for annotatortype: " + str(q[i+1]))
            i+=2
        elif q.kw(i,'text'):
            if not focus is None and focus.Class is folia.TextContent:
                key = 'value'
            else:
                key = 'text'
            assignments[key] = q[i+1]
            i+=2
        elif q.kw(i, 'datetime'):
            if q[i+1] == "now":
                assignments[q[i]] = datetime.datetime.now()
            elif q[i+1].isdigit():
                try:
                    assignments[q[i]] = datetime.datetime.fromtimestamp(q[i+1])
                except:
                    raise SyntaxError("Unable to parse datetime: " + str(q[i+1]))
            else:
                try:
                    assignments[q[i]] = datetime.strptime("%Y-%m-%dT%H:%M:%S")
                except:
                    raise SyntaxError("Unable to parse datetime: " + str(q[i+1]))
            i += 2
        else:
            if not assignments:
                raise SyntaxError("Expected assignments after WITH statement, but no valid attribute found, got  " + str(q[i]) + " at position " + str(i) + " in: " +  str(q))
            break
    return i

class Action(object): #Action expression
    def __init__(self, action, focus, assignments={}):
        self.action = action
        self.focus = focus #Selector
        self.assignments = assignments
        self.form = None
        self.subactions = []
        self.nextaction = None
        self.respan = []
        self.extra = {}


    @staticmethod
    def parse(q,i=0):
        if q.kw(i, ('SELECT','EDIT','DELETE','ADD','APPEND','PREPEND','SUBSTITUTE')):
            action = q[i]
        else:
            raise SyntaxError("Expected action, got " + str(q[i]) + " in: " + str(q))

        assignments = {}

        i += 1
        if (action in ('SUBSTITUTE','APPEND','PREPEND')) and (isinstance(q[i],UnparsedQuery)):
            focus = None   #We have a SUBSTITUTE/APPEND/PREPEND (AS CORRECTION) expression
        elif (action == 'SELECT') and q.kw(i,('FOR','IN')): #select statement  without focus, pure target
            focus = None
        else:
            focus, i = Selector.parse(q,i)

            if action == "ADD" and focus.filter:
                raise SyntaxError("Focus has WHERE statement but ADD action does not support this")

            if q.kw(i,"WITH"):
                if action in ("SELECT", "DELETE"):
                    raise SyntaxError("Focus has WITH statement but " + action + " does not support this: " +str(q))
                i += 1
                i = getassignments(q,i ,assignments, focus)

        #we have enough to set up the action now
        action = Action(action, focus, assignments)

        if action.action == "EDIT" and q.kw(i,"RESPAN"):
            action.extra['respan'], i = Span.parse(q,i+1)

        done = False
        while not done:
            if isinstance(q[i], UnparsedQuery):
                #we have a sub expression
                if q[i].kw(0, ('EDIT','DELETE','ADD')):
                    #It's a sub-action!
                    if action.action in ("DELETE"):
                        raise SyntaxError("Subactions are not allowed for action " + action.action + ", in: " + str(q))
                    subaction, _ = Action.parse(q[i])
                    action.subactions.append( subaction )
                elif q[i].kw(0, 'AS'):
                    if q[i].kw(1, "ALTERNATIVE"):
                        action.form,_ = Alternative.parse(q[i])
                    elif q[i].kw(1, "CORRECTION") or (q[i].kw(1,"BARE") and q[i].kw(2, "CORRECTION")):
                        action.form,_ = Correction.parse(q[i],0,action.focus)
                    else:
                        raise SyntaxError("Invalid keyword after AS: " + str(q[i][1]))
                i+=1
            else:
                done = True


        if q.kw(i, ('SELECT','EDIT','DELETE','ADD','APPEND','PREPEND','SUBSTITUTE')):
            #We have another action!
            action.nextaction, i = Action.parse(q,i)

        return action, i


    def __call__(self, query, contextselector, debug=False):
        """Returns a list focusselection after having performed the desired action on each element therein"""

        #contextselector is a two-tuple function recipe (f,args), so we can reobtain the generator which it returns

        #select all focuss, not lazy because we are going return them all by definition anyway


        if debug: print("[FQL EVALUATION DEBUG] Action - Preparing to evaluate action chain starting with ", self.action,file=sys.stderr)

        #handles all actions further in the chain, not just this one!!! This actual method is only called once
        actions = [self]
        a = self
        while a.nextaction:
            actions.append(a.nextaction)
            a = a.nextaction

        if len(actions) > 1:
            #multiple actions to perform, apply contextselector once and load in memory    (will be quicker at higher memory cost, proportionate to the target selection size)
            if isinstance(contextselector, tuple) and len(contextselector) == 2:
                contextselector = list(contextselector[0](*contextselector[1]))
            focusselection_all = []
            constrainedtargetselection_all = []

        for action in actions:
            if action.action != "SELECT" and action.focus:
                #check if set is declared, if not, auto-declare
                if debug: print("[FQL EVALUATION DEBUG] Action - Auto-declaring ",action.focus.Class.__name__, " of ", str(action.focus.set),file=sys.stderr)
                action.focus.autodeclare(query.doc)

            if action.form and isinstance(action.form, Correction) and action.focus:
                if debug: print("[FQL EVALUATION DEBUG] Action - Auto-declaring ",action.focus.Class.__name__, " of ", str(action.focus.set),file=sys.stderr)
                action.form.autodeclare(query.doc)


        substitution = {}
        if self.action == 'SUBSTITUTE' and not self.focus and self.form:
            #we have a SUBSTITUTE (AS CORRECTION) statement with no correction but only suggestions
            #defer substitute to form
            result = self.form.substitute(query, None, contextselector, debug)
            focusselection = [result]
            constrainedtargetselection = []
            #(no further chaining possible in this setup)
        elif self.action == 'PREPEND' and not self.focus and self.form:
            #we have a PREPEND (AS CORRECTION) statement with no correction but only suggestions
            #defer substitute to form
            result = self.form.prepend(query, None, contextselector, debug)
            focusselection = [result]
            constrainedtargetselection = []
            #(no further chaining possible in this setup)
        elif self.action == 'APPEND' and not self.focus and self.form:
            #we have a APPEND (AS CORRECTION) statement with no correction but only suggestions
            #defer substitute to form
            result = self.form.append(query, None, contextselector, debug)
            focusselection = [result]
            constrainedtargetselection = []
            #(no further chaining possible in this setup)
        else:

            for action in actions:
                if debug: print("[FQL EVALUATION DEBUG] Action - Evaluating action ", action.action,file=sys.stderr)
                focusselection = []
                constrainedtargetselection = [] #selecting focus elements constrains the target selection
                processed_form = []

                if substitution and action.action != "SUBSTITUTE":
                    raise QueryError("SUBSTITUTE can not be chained with " + action.action)

                if action.action == "SELECT" and not action.focus: #SELECT without focus, pure target-select
                    if isinstance(contextselector, tuple) and len(contextselector) == 2:
                        for e in contextselector[0](*contextselector[1]):
                            constrainedtargetselection.append(e)
                            focusselection.append(e)
                    else:
                        for e in contextselector:
                            constrainedtargetselection.append(e)
                            focusselection.append(e)

                elif action.action not in ("ADD","APPEND","PREPEND"): #only for actions that operate on an existing focus
                    if contextselector is query.doc and action.focus.Class in ('ALL',folia.Text):
                        focusselector = ( (x,x) for x in query.doc )  #Patch to make root-level SELECT ALL work as intended
                    else:
                        strict = query.targets and query.targets.strict
                        focusselector = action.focus(query,contextselector, not strict, debug)
                    if debug: print("[FQL EVALUATION DEBUG] Action - Obtaining focus...",file=sys.stderr)
                    for focus, target in focusselector:
                        if target and action.action != "SUBSTITUTE":
                            if isinstance(target, SpanSet):
                                if not target.partof(constrainedtargetselection):
                                    if debug: print("[FQL EVALUATION DEBUG] Action - Got target result (spanset), adding ", repr(target),file=sys.stderr)
                                    constrainedtargetselection.append(target)
                            elif not any(x is target for x in constrainedtargetselection):
                                if debug: print("[FQL EVALUATION DEBUG] Action - Got target result, adding ", repr(target),file=sys.stderr)
                                constrainedtargetselection.append(target)


                        if action.form and action.action != "SUBSTITUTE":
                            #Delegate action to form (= correction or alternative)
                            if not any(x is focus for x in  processed_form):
                                if debug: print("[FQL EVALUATION DEBUG] Action - Got focus result, processing using form ", repr(focus),file=sys.stderr)
                                processed_form.append(focus)
                                focusselection += list(action.form(query, action,focus,target,debug))
                            else:
                                if debug: print("[FQL EVALUATION DEBUG] Action - Focus result already obtained, skipping... ", repr(focus),file=sys.stderr)
                                continue
                        else:
                            if isinstance(focus,SpanSet):
                                if not focus.partof(focusselection):
                                    if debug: print("[FQL EVALUATION DEBUG] Action - Got focus result (spanset), adding ", repr(target),file=sys.stderr)
                                    focusselection.append(target)
                                else:
                                    if debug: print("[FQL EVALUATION DEBUG] Action - Focus result (spanset) already obtained, skipping... ", repr(target),file=sys.stderr)
                                    continue
                            elif not any(x is focus for x in  focusselection):
                                if debug: print("[FQL EVALUATION DEBUG] Action - Got focus result, adding ", repr(focus),file=sys.stderr)
                                focusselection.append(focus)
                            else:
                                if debug: print("[FQL EVALUATION DEBUG] Action - Focus result already obtained, skipping... ", repr(focus),file=sys.stderr)
                                continue

                            if action.action == "EDIT":
                                if debug: print("[FQL EVALUATION DEBUG] Action - Applying EDIT to focus ", repr(focus),file=sys.stderr)
                                for attr, value in action.assignments.items():
                                    if attr in ("text","value"):
                                        if debug: print("[FQL EVALUATION DEBUG] Action - settext("+ value+ ") on focus ", repr(focus),file=sys.stderr)
                                        focus.settext(value)
                                    elif attr == "class":
                                        if debug: print("[FQL EVALUATION DEBUG] Action - " + attr +  " = " + value + " on focus ", repr(focus),file=sys.stderr)
                                        focus.cls = value
                                    else:
                                        if debug: print("[FQL EVALUATION DEBUG] Action - " + attr +  " = " + value + " on focus ", repr(focus),file=sys.stderr)
                                        setattr(focus, attr, value)
                                if 'respan' in action.extra:
                                    if not isinstance(focus, folia.AbstractSpanAnnotation): raise QueryError("Can only perform RESPAN on span annotation elements!")
                                    spanset = next(action.extra['respan'](query, contextselector, True, debug)) #there can be only one
                                    focus.setspan(*spanset)

                                query._touch(focus)
                            elif action.action == "DELETE":
                                if debug: print("[FQL EVALUATION DEBUG] Action - Applying DELETE to focus ", repr(focus),file=sys.stderr)
                                p = focus.parent
                                p.remove(focus)
                                #we set the parent back on the element we return, so return types like ancestor-focus work
                                focus.parent = p
                            elif action.action == "SUBSTITUTE":
                                if debug: print("[FQL EVALUATION DEBUG] Action - Applying SUBSTITUTE to target ", repr(focus),file=sys.stderr)
                                if not isinstance(target,SpanSet) or not target: raise QueryError("SUBSTITUTE requires a target SPAN")
                                focusselection.remove(focus)

                                if not substitution:
                                    #this is the first SUBSTITUTE in a chain
                                    prev = target[0].parent
                                    for e in target[1:]:
                                        if e.parent != prev:
                                            raise QueryError("SUBSTITUTE can only be performed when the target items share the same parent")

                                    substitution['parent'] = target[0].parent
                                    substitution['index'] = 0
                                    substitution['span'] = target
                                    substitution['new'] = []

                                    #find insertion index:
                                    for i, e in enumerate(target[0].parent):
                                        if e is target[0]:
                                            substitution['index'] = i
                                            break

                                substitution['new'].append( (action.focus.Class, action.assignments, action.subactions)  )



                if action.action in ("ADD","APPEND","PREPEND") or (action.action == "EDIT" and not focusselection):
                    if debug: print("[FQL EVALUATION DEBUG] Action - Applying " + action.action + " to targets",file=sys.stderr)
                    if not action.focus.Class:
                        raise QueryError("Focus of action has no class!")

                    isspan = issubclass(action.focus.Class, folia.AbstractSpanAnnotation)

                    if not 'set' in action.assignments:
                        if action.focus.set and action.focus.set != "undefined":
                            action.assignments['set'] = action.focus.set
                        elif action.focus.Class.XMLTAG in query.defaultsets:
                            action.assignments['set'] = action.focus.set = query.defaultsets[action.focus.Class.XMLTAG]
                        else:
                            action.assignments['set'] = action.focus.set = query.doc.defaultset(action.focus.Class)

                    if isinstance(contextselector, tuple) and len(contextselector) == 2:
                        targetselection = contextselector[0](*contextselector[1])
                    else:
                        targetselection = contextselector

                    for target in targetselection:
                        if action.form:
                            #Delegate action to form (= correction or alternative)
                            focusselection += list( action.form(query, action,None,target,debug) )
                        else:
                            if isinstance(target, SpanSet):
                                if action.action == "ADD" or action.action == "EDIT":
                                    if debug: print("[FQL EVALUATION DEBUG] Action - Applying " + action.action + " of " + action.focus.Class.__name__ + " to target spanset " + repr(target),file=sys.stderr)
                                    focusselection.append( target[0].add(action.focus.Class, *target, **action.assignments) ) #handles span annotation too
                                    query._touch(focusselection[-1])
                            else:
                                if action.action == "ADD" or action.action == "EDIT":
                                    if debug: print("[FQL EVALUATION DEBUG] Action - Applying " + action.action + " of " + action.focus.Class.__name__ + " to target " + repr(target),file=sys.stderr)
                                    focusselection.append( target.add(action.focus.Class, **action.assignments) ) #handles span annotation too
                                    query._touch(focusselection[-1])
                                elif action.action == "APPEND":
                                    if debug: print("[FQL EVALUATION DEBUG] Action - Applying " + action.action + " of " + action.focus.Class.__name__ +" to target " + repr(target),file=sys.stderr)
                                    index = target.parent.getindex(target)
                                    if index == -1:
                                        raise QueryError("Insertion point for APPEND action not found")
                                    focusselection.append( target.parent.insert(index+1, action.focus.Class, **action.assignments) )
                                    query._touch(focusselection[-1])
                                elif action.action == "PREPEND":
                                    if debug: print("[FQL EVALUATION DEBUG] Action - Applying " + action.action + " of " + action.focus.Class.__name__ +" to target " + repr(target),file=sys.stderr)
                                    index = target.parent.getindex(target)
                                    if index == -1:
                                        raise QueryError("Insertion point for PREPEND action not found")
                                    focusselection.append( target.parent.insert(index, action.focus.Class, **action.assignments) )
                                    query._touch(focusselection[-1])

                        if isinstance(target, SpanSet):
                            if not target.partof(constrainedtargetselection):
                                constrainedtargetselection.append(target)
                        elif not any(x is target for x in constrainedtargetselection):
                            constrainedtargetselection.append(target)

                if focusselection and action.subactions and not substitution:
                    for subaction in action.subactions:
                        #check if set is declared, if not, auto-declare
                        if debug: print("[FQL EVALUATION DEBUG] Action - Auto-declaring ",action.focus.Class.__name__, " of ", str(action.focus.set),file=sys.stderr)
                        subaction.focus.autodeclare(query.doc)
                        if debug: print("[FQL EVALUATION DEBUG] Action - Invoking subaction ", subaction.action,file=sys.stderr)
                        subaction(query, focusselection, debug ) #note: results of subactions will be silently discarded, they can never select anything

                if len(actions) > 1:
                    #consolidate results:
                    focusselection_all = []
                    for e in focusselection:
                        if isinstance(e, SpanSet):
                            if not e.partof(focusselection_all):
                                focusselection_all.append(e)
                        elif not any(x is e for x in focusselection_all):
                            focusselection_all.append(e)
                    constrainedtargetselection_all = []
                    for e in constrainedtargetselection:
                        if isinstance(e, SpanSet):
                            if not e.partof(constrainedtargetselection_all):
                                constrainedtargetselection_all.append(e)
                        elif not any(x is e for x in constrainedtargetselection_all):
                            constrainedtargetselection_all.append(e)

            if substitution:
                constrainedtargetselection_all = []
                constrainedtargetselection = []
                if action.form:
                    result = action.form.substitute(query, substitution, None, debug)
                    if len(actions) > 1:
                        focusselection_all.append(result)
                    else:
                        focusselection.append(result)
                else:
                    if debug: print("[FQL EVALUATION DEBUG] Action - Substitution - Removing target",file=sys.stderr)
                    for e in substitution['span']:
                        substitution['parent'].remove(e)

                    for i, (Class, assignments, subactions) in enumerate(substitution['new']):
                        if debug: print("[FQL EVALUATION DEBUG] Action - Substitution - Inserting substitution",file=sys.stderr)
                        e =  substitution['parent'].insert(substitution['index']+i, Class, **assignments)
                        for subaction in subactions:
                            subaction.focus.autodeclare(query.doc)
                            if debug: print("[FQL EVALUATION DEBUG] Action - Invoking subaction (in substitution) ", subaction.action,file=sys.stderr)
                            subaction(query, [e], debug ) #note: results of subactions will be silently discarded, they can never select anything

                        if len(actions) > 1:
                            focusselection_all.append(e)
                        else:
                            focusselection.append(e)

        if len(actions) > 1:
            return focusselection_all, constrainedtargetselection_all
        else:
            return focusselection, constrainedtargetselection



class Context(object):
    def __init__(self):
        self.format = "python"
        self.returntype = "focus"
        self.request = "all"
        self.defaults = {}
        self.defaultsets = {}

class Query(object):
    def __init__(self, q, context=Context()):
        self.action = None
        self.targets = None
        self.declarations = []
        self.format = context.format
        self.returntype = context.returntype
        self.request = copy(context.request)
        self.defaults = copy(context.defaults)
        self.defaultsets = copy(context.defaultsets)
        self.parse(q)

    def parse(self, q, i=0):
        if not isinstance(q,UnparsedQuery):
            q = UnparsedQuery(q)

        l = len(q)
        if q.kw(i,"DECLARE"):
            try:
                Class = folia.XML2CLASS[q[i+1]]
            except:
                raise SyntaxError("DECLARE statement expects a FoLiA element, got: " + str(q[i+1]))

            if not Class.ANNOTATIONTYPE:
                raise SyntaxError("DECLARE statement for undeclarable element type: " + str(q[i+1]))

            i += 2

            defaults = {}
            if q.kw(i,"OF") and q[i+1]:
                i += 1
                decset = q[i]
                i += 1
                if q.kw(i,"WITH"):
                    i = getassignments(q,i+1,defaults)

            self.declarations.append( (Class, decset, defaults)  )

        if i < l:
            self.action,i = Action.parse(q,i)

            if q.kw(i,("FOR","IN")):
                self.targets, i = Target.parse(q,i)

            while i < l:
                if q.kw(i,"RETURN"):
                    self.returntype = q[i+1]
                    i+=2
                elif q.kw(i,"FORMAT"):
                    self.format = q[i+1]
                    i+=2
                elif q.kw(i,"REQUEST"):
                    self.request = q[i+1].split(",")
                    i+=2
                else:
                    raise SyntaxError("Unexpected " + str(q[i]) + " at position " + str(i) + " in: " + str(q))


        if i != l:
            raise SyntaxError("Expected end of query, got " + str(q[i]) + " in: " + str(q))

    def __call__(self, doc, wrap=True,debug=False):
        """Execute the query on the specified document"""

        self.doc = doc

        if debug: print("[FQL EVALUATION DEBUG] Query  - Starting on document ", doc.id,file=sys.stderr)

        if self.declarations:
            for Class, decset, defaults in self.declarations:
                if debug: print("[FQL EVALUATION DEBUG] Processing declaration for ", Class.__name__, "of",str(decset),file=sys.stderr)
                doc.declare(Class,decset,**defaults)

        if self.action:
            targetselector = doc
            if self.targets and not (isinstance(self.targets.targets[0], Selector) and self.targets.targets[0].Class in ("ALL", folia.Text)):
                targetselector = (self.targets, (self, targetselector, True, debug)) #function recipe to get the generator for the targets, (f, *args) (first is always recursive)

            focusselection, targetselection = self.action(self, targetselector, debug) #selecting focus elements further constrains the target selection (if any), return values will be lists

            if self.returntype == "nothing":
                return ""
            elif self.returntype == "focus":
                responseselection = focusselection
            elif self.returntype == "target" or self.returntype == "inner-target":
                responseselection = []
                for e in targetselection:
                    if not any(x is e for x in responseselection): #filter out duplicates
                        responseselection.append(e)
            elif self.returntype == "outer-target":
                raise NotImplementedError
            elif self.returntype == "ancestor" or self.returntype == "ancestor-focus":
                responseselection = []
                try:
                    responseselection.append( next(folia.commonancestors(folia.AbstractStructureElement,*focusselection)) )
                except StopIteration:
                    raise QueryError("No ancestors found for focus: " + str(repr(focusselection)))
            elif self.returntype == "ancestor-target":
                elems = []
                for e in targetselection:
                    if isinstance(e, SpanSet):
                        elems += e
                    else:
                        elems.append(e)
                responseselection = []
                try:
                    responseselection.append( next(folia.commonancestors(folia.AbstractStructureElement,*elems)) )
                except StopIteration:
                    raise QueryError("No ancestors found for targets: " + str(repr(targetselection)))
            else:
                raise QueryError("Invalid return type: " + self.returntype)

        else:
            responseselection = []

        if self.returntype == "nothing": #we're done
            return ""

        #convert response selection to proper format and return
        if self.format.startswith('single'):
            if len(responseselection) > 1:
                raise QueryError("A single response was expected, but multiple are returned")
            if self.format == "single-xml":
                if debug: print("[FQL EVALUATION DEBUG] Query  - Returning single-xml",file=sys.stderr)
                if not responseselection:
                    return ""
                else:
                    if isinstance(responseselection[0], SpanSet):
                            r = "<result>\n"
                            for e in responseselection[0]:
                                r += e.xmlstring(True)
                            r += "</result>\n"
                            return r
                    else:
                        return responseselection[0].xmlstring(True)
            elif self.format == "single-json":
                if debug: print("[FQL EVALUATION DEBUG] Query  - Returning single-json",file=sys.stderr)
                if not responseselection:
                    return "null"
                else:
                    return json.dumps(responseselection[0].json())
            elif self.format == "single-python":
                if debug: print("[FQL EVALUATION DEBUG] Query  - Returning single-python",file=sys.stderr)
                if not responseselection:
                    return None
                else:
                    return responseselection[0]
        else:
            if self.format == "xml":
                if debug: print("[FQL EVALUATION DEBUG] Query  - Returning xml",file=sys.stderr)
                if not responseselection:
                    if wrap:
                        return "<results></results>"
                    else:
                        return ""
                else:
                    if wrap:
                        r = "<results>\n"
                    else:
                        r = ""
                    for e in responseselection:
                        if isinstance(e, SpanSet):
                            r += "<result>\n"
                            for e2 in e:
                                r += "" + e2.xmlstring(True) + "\n"
                            r += "</result>\n"
                        else:
                            r += "<result>\n" + e.xmlstring(True) + "</result>\n"
                    if wrap:
                        r += "</results>\n"
                    return r
            elif self.format == "json":
                if debug: print("[FQL EVALUATION DEBUG] Query  - Returning json",file=sys.stderr)
                if not responseselection:
                    if wrap:
                        return "[]"
                    else:
                        return ""
                else:
                    if wrap:
                        s = "[ "
                    else:
                        s = ""
                    for e in responseselection:
                        if isinstance(e, SpanSet):
                            s += json.dumps([ e2.json() for e2 in e ] ) + ", "
                        else:
                            s += json.dumps(e.json()) + ", "
                    s = s.strip(", ")
                    if wrap:
                        s += "]"
                    return s
            else: #python and undefined formats
                if debug: print("[FQL EVALUATION DEBUG] Query  - Returning python",file=sys.stderr)
                return responseselection

        return QueryError("Invalid format: " + self.format)

    def _touch(self, *args):
        for e in args:
            if isinstance(e, folia.AbstractElement):
                e.changedbyquery = self
                self._touch(*e.data)




