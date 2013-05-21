#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################9
# PyNLPl - Common functions
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#       Licensed under GPLv3
#
# This contains very common functions and language extensions
#
###############################################################

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import datetime
from sys import stderr, version

## From http://code.activestate.com/recipes/413486/ (r7)
def Enum(*names):
   ##assert names, "Empty enums are not supported" # <- Don't like empty enums? Uncomment!

   class EnumClass(object):
      __slots__ = names
      def __iter__(self):        return iter(constants)
      def __len__(self):         return len(constants)
      def __getitem__(self, i):  return constants[i]
      def __repr__(self):        return 'Enum' + str(names)
      def __str__(self):         return 'enum ' + str(constants)

   class EnumValue(object):
      __slots__ = ('__value')
      def __init__(self, value): self.__value = value
      Value = property(lambda self: self.__value)
      EnumType = property(lambda self: EnumType)
      def __hash__(self):        return hash(self.__value)
      def __cmp__(self, other):
         # C fans might want to remove the following assertion
         # to make all enums comparable by ordinal value {;))
         assert self.EnumType is other.EnumType, "Only values from the same enum are comparable"
         return cmp(self.__value, other.__value)
      def __invert__(self):      return constants[maximum - self.__value]
      def __bool__(self):     return bool(self.__value)
      def __nonzero__(self):     return bool(self.__value) #Python 2.x
      def __repr__(self):        return str(names[self.__value])

   maximum = len(names) - 1
   constants = [None] * len(names)
   for i, each in enumerate(names):
      val = EnumValue(i)
      setattr(EnumClass, each, val)
      constants[i] = val
   constants = tuple(constants)
   EnumType = EnumClass()
   return EnumType


def u(s, encoding = 'utf-8', errors='strict'):
    #ensure s is properly unicode.. wrapper for python 2.6/2.7,
    if version < '3':
        #ensure the object is unicode
        if isinstance(s, unicode):
            return s
        else:
            return unicode(s, encoding,errors=errors)
    else:
        #will work on byte arrays
        if isinstance(s, str):
            return s
        else:
            return str(s,encoding,errors=errors)

def b(s):
    #ensure s is bytestring
    if version < '3':
        #ensure the object is unicode
        if isinstance(s, str):
            return s
        else:
            return s.encode('utf-8')
    else:
        #will work on byte arrays
        if isinstance(s, bytes):
            return s
        else:
            return s.encode('utf-8')

def isstring(s): #Is this a proper string?
    return isinstance(s, str) or (version < '3' and isinstance(s, unicode))

def log(msg, **kwargs):
    """Generic log method. Will prepend timestamp.

    Keyword arguments:
      system   - Name of the system/module
      indent   - Integer denoting the desired level of indentation
      streams  - List of streams to output to
      stream   - Stream to output to (singleton version of streams)
    """
    if 'debug' in kwargs:
        if 'currentdebug' in kwargs:
            if kwargs['currentdebug'] < kwargs['debug']:
                return False
        else:
            return False #no currentdebug passed, assuming no debug mode and thus skipping message

    s = "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
    if 'system' in kwargs:
        s += "[" + system + "] "


    if 'indent' in kwargs:
        s += ("\t" * int(kwargs['indent']))

    s += u(msg)

    if s[-1] != '\n':
        s += '\n'

    if 'streams' in kwargs:
        streams = kwargs['streams']
    elif 'stream' in kwargs:
        streams = [kwargs['stream']]
    else:
        streams = [stderr]

    for stream in streams:
        stream.write(s)
    return s
