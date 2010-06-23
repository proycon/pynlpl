#!/usr/bin/env python
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

from pynlpl.common import Enum

class InvalidTagException(Exception):
    pass

class AbstractPosType(object):
    def __init__(self, *args, **kwargs):
        for value in args:
            for prop in dir(self.__class__):
                if prop[0] != '_':
                    if value in getattr(self.__class__, prop):
                        setattr(self,prop,value)
        for key, value in kwargs.items():
            getattr(self,ntype) = value


class N(AbstractPosType):
    ntype = Enum('soort')
    getal = Enum('ev','mv')
    graad = Enum('basis','dim')
    genus = Enum('zijd','onz')
    naamval = Enum('stan','gen','dat')

class ADJ(AbstractPosType):
    positie = Enum('prenom','nom','posnom','vrij')
    graad = Enum('basis','comp','sup','dim')
    buiging = Enum('zonder','met-e','met-s')
    getal_n = Enum('zonder-v','mv-n')
    naamval = Enum('stan','bijz')

class WW(AbstractPosType):
    wvorm = Enum('pv','inf','vd','od')
    pvtijd = Enum('tgw','verl','conj')
    pvagr = Enum('ev','mv','met-t')
    positie = Enum('prenom','nom','posnom','vrij')
    buiging = Enum('zonder','met-e')
    getal_n = Enum('zonder-v','mv-n')

class TW(AbstractPosType):
    numtype = Enum('hoofd','rang')
    positie = Enum('prenom','posnom','vrij')
    getal_n = Enum('zonder-v','mv-n')
    graad = Enum('basis','dim')
    naamval = Enum('stan','bijz')

class VNW(AbstractPosType):
    vwtype = Enum('pers','refl','recip','bez','vb','betr','excl','aanw','onbep')
    pdtype = Enum('adv-pron','det') #TODO: pron, grad
    naamval = Enum('stan','nomin','obl','gen','dat')
    status = Enum('vol','red','nadr')
    persoon = Enum('1','2','2v','2b','3','3p','3m','3v','3o')
    getal = Enum('ev','mv')
    genus = Enum('masc','fem','onz')
    positie = Enum('prenom','nom','vrij')
    buiging = Enum('zonder','met-e')
    npagr = Enum('agr','evon','rest','evz','mv','agr3','evmo','rest3','evf')
    getal_n = Enum('zonder-v','mv-n')
    graad = Enum('basis','comp','sup','dim')
    
class LID(AbstractPosType):
    lwtype = Enum('bep','onbep')
    naamval = Enum('stan','gen','dat')
    npagr = Enum('agr','evon','rest','evz','mv','agr3','evmo','rest3','evf')

class VZ(AbstractPosType):
    vztype = Enum('init','versm','fin')
    
class VG(AbstractPosType):
    conjtype = Enum('neven','onder')

class BW(AbstractPosType):
    #no feature):
    pass

class LET(object):
    #no features
    pass

class SPEC(object):
    spectype = Enum('afgebr','afk','deeleigen','symb','vreemd')


def parse_cgn_postag(tag):
    """decodes PoS features like "N(soort,ev,basis,onz,stan)" into a data sructure 
    compiled by Matje van de Camp"""

    begin = tag.find('(')
    if tag[-1] == ')' and begin > 0:
        head = tag[0:begin]
        headcls = globals()[head]

        rawfeatures = tag[begin+1:-1]
        features = {}

        return headcls(rawfeatures)

    else:
        raise InvalidTagException("Not a valid CGN tag")




