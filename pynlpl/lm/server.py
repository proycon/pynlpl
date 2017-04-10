#!/usr/bin/env python
#-*- coding:utf-8 -*-

#---------------------------------------------------------------
# PyNLPl - Language Models
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Generic Server for Language Models
#
#----------------------------------------------------------------

#No Python 3 support for twisted yet...

from twisted.internet import protocol, reactor
from twisted.protocols import basic

class LMSentenceProtocol(basic.LineReceiver):
    def lineReceived(self, sentence):
        try:
            score = self.factory.lm.scoresentence(sentence)
        except:
            score = 0.0
        self.sendLine(str(score))

class LMSentenceFactory(protocol.ServerFactory):
    protocol = LMSentenceProtocol

    def __init__(self, lm):
        self.lm = lm
        
class LMNGramProtocol(basic.LineReceiver):
    def lineReceived(self, ngram):
        ngram = ngram.split(" ")    
        try:
            score = self.factory.lm[ngram]
        except:
            score = 0.0
        self.sendLine(str(score))    
        
class LMNGramFactory(protocol.ServerFactory):
    protocol = LMNGramProtocol

    def __init__(self, lm):
        self.lm = lm        
        
        

class LMServer:
    """Language Model Server"""
    def __init__(self, lm, port=12346, n=0):
        """n indicates the n-gram size, if set to 0 (which is default), the server will expect to only receive whole sentence, if set to a particular value, it will only expect n-grams of that value"""
        if n == 0:
            reactor.listenTCP(port, LMSentenceFactory(lm))
        else:
            reactor.listenTCP(port, LMNGramFactory(lm))
        reactor.run()

