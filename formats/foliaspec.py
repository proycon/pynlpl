# -*- coding: utf-8 -*-
#----------------------------------------------------------------
# PyNLPl - FoLiA Format Specification 
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://proycon.github.com/folia
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#   Module for reading, editing and writing FoLiA XML
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

#pylint: disable=redefined-builtin,trailing-whitespace,superfluous-parens,bad-classmethod-argument

#foliaspec:version
version = '0.12.3'

#foliaspec:namespace
namespace = "http://ilk.uvt.nl/folia"

#foliaspec:attributes


def init(classes):
    """Initialisation, with dependency injection of all classes"""

    #dependency injection
    for Class in classes:
        globals()[Class] = Class

    #foliaspec:setelementproperties









