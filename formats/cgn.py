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

from pynlpl.formats import folia
from pynlpl.common import Enum

class InvalidTagException(Exception):
    pass

subsets = {
    'ntype': ['soort'],
    'getal': ['ev','mv'],
    'genus': ['zijd','onz','masc','fem'],
    'naamval': ['stan','gen','dat','nomin','obl','bijz'],
    'spectype': ['afgebr','afk','deeleigen','symb','vreemd','enof','meta'],
    'conjtype': ['neven','onder'],
    'vztype': ['init','versm','fin'],
    'npagr': ['agr','evon','rest','evz','mv','agr3','evmo','rest3','evf'],
    'lwtype': ['bep','onbep'],
    'vwtype': ['pers','pr','refl','recip','bez','vb','betr','excl','aanw','onbep'], #pr == pers?
    'pdtype':  ['adv-pron','pron','det','grad'], #pron == adv-pron?, grad == det?
    'status': ['vol','red','nadr'],
    'persoon': ['1','2','2v','2b','3','3p','3m','3v','3o'],
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

def parse_cgn_postag(rawtag):
    global subsets
    """decodes PoS features like "N(soort,ev,basis,onz,stan)" into a PosAnnotation data structure 
    based on CGN tag overview compiled by Matje van de Camp"""
    
    
    begin = rawtag.find('(')
    if rawtag[-1] == ')' and begin > 0:
        tag = folia.PosAnnotation(None, cls='rawtag',set='http://ilk.uvt.nl/folia/sets/cgn')

        
        head = rawtag[0:begin]
        tag.append( folia.Feature, subset='head',cls=head)

        rawfeatures = rawtag[begin+1:-1].split(',')
        for rawfeature in rawfeatures:            
            if rawfeature:
                found = False
                for subset, classes in subsets.items():
                    if rawfeature in classes:
                        found = True
                        tag.append( folia.Feature, subset=subset,cls=rawfeature)
                        break
                if not found:
                    raise InvalidTagException("Unknown feature value: " + rawfeature)            
        return tag
    else:
        raise InvalidTagException("Not a valid CGN tag")





