#-*- coding:utf-8 -*-

###############################################################
#  PyNLPl - Corpus Gesproken Nederlands
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
# 
# Classes for reading CGN (still to be added). Most notably, contains a function for decoding
# PoS features like "N(soort,ev,basis,onz,stan)" into a data structure.
#
###############################################################

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import  
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout
    
from pynlpl.formats import folia
from pynlpl.common import Enum


class InvalidTagException(Exception):
    pass
    
class InvalidFeatureException(Exception):
    pass

subsets = {
    'ntype': ['soort','eigen'],
    'getal': ['ev','mv','getal',],
    'genus': ['zijd','onz','masc','fem','genus'],
    'naamval': ['stan','gen','dat','nomin','obl','bijz'],
    'spectype': ['afgebr','afk','deeleigen','symb','vreemd','enof','meta','achter','comment','onverst'],
    'conjtype': ['neven','onder'],
    'vztype': ['init','versm','fin'],
    'npagr': ['agr','evon','rest','evz','mv','agr3','evmo','rest3','evf'],
    'lwtype': ['bep','onbep'],
    'vwtype': ['pers','pr','refl','recip','bez','vb','vrag','betr','excl','aanw','onbep'], 
    'pdtype':  ['adv-pron','pron','det','grad'],
    'status': ['vol','red','nadr'],
    'persoon': ['1','2','2v','2b','3','3p','3m','3v','3o','persoon'],
    'positie': ['prenom','postnom', 'nom','vrij'],
    'buiging': ['zonder','met-e','met-s'],
    'getal-n' : ['zonder-v','mv-n','zonder-n'],
    'graad' : ['basis','comp','sup','dim'],
    'wvorm': ['pv','inf','vd','od'],
    'pvtijd': ['tgw','verl','conj'],
    'pvagr':  ['ev','mv','met-t'],
    'numtype': ['hoofd','rang'],
    'dial': ['dial'],
}
constraints = {
    'getal':['N','VNW'],
    'npagr':['VNW','LID'],
    'pvagr':['WW'],    
}

def parse_cgn_postag(rawtag, raisefeatureexceptions = False):
    global subsets, constraints
    """decodes PoS features like "N(soort,ev,basis,onz,stan)" into a PosAnnotation data structure 
    based on CGN tag overview compiled by Matje van de Camp"""
    
    
    begin = rawtag.find('(')
    if rawtag[-1] == ')' and begin > 0:
        tag = folia.PosAnnotation(None, cls=rawtag,set='http://ilk.uvt.nl/folia/sets/cgn')

        
        head = rawtag[0:begin]
        tag.append( folia.Feature, subset='head',cls=head)

        rawfeatures = rawtag[begin+1:-1].split(',')
        for rawfeature in rawfeatures:            
            if rawfeature:
                found = False
                for subset, classes in subsets.items():
                    if rawfeature in classes:
                        if subset in constraints:
                            if not head in constraints[subset]:
                                continue #constraint not met!
                        found = True
                        tag.append( folia.Feature, subset=subset,cls=rawfeature)
                        break
                if not found:
                    print("\t\tUnknown feature value: " + rawfeature + " in " + rawtag, file=stderr)
                    if raisefeatureexceptions:
                        raise InvalidFeatureException("Unknown feature value: " + rawfeature + " in " + rawtag)
                    else:    
                        continue
        return tag
    else:
        raise InvalidTagException("Not a valid CGN tag")





