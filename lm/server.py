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

from twisted.internet import protocol, reactor
from twisted.protocols import basic

class LMProtocol(basic.LineReceiver):
    def lineReceived(self, sentence):
        try:
            score = self.factory.lm.scoresentence(sentence)
        except:
            score = 0.0
        self.sendLine(str(score))

class LMFactory(protocol.ServerFactory):
    protocol = LMProtocol

    def __init__(self, lm):
        self.lm = lm

class LMServer:
    def __init__(self, lm, port=12346):
        reactor.listenTCP(port, LMFactory(lm))
        reactor.run()

