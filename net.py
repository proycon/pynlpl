#-*- coding:utf-8 -*-

#---------------------------------------------------------------
# PyNLPl - Network utilities
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Generic Server for Language Models
#
#----------------------------------------------------------------

from twisted.internet import protocol, reactor
from twisted.protocols import basic
import shlex
import sys

class GWSNetProtocol(basic.LineReceiver):        
    def connectionMade(self):
        print >>sys.stderr, "Client connected"
        self.factory.connections += 1
        if self.factory.connections != 1:
            self.transport.loseConnection()            
        else:            
            self.sendLine("READY")
            
    def lineReceived(self, line):
        print >>sys.stderr, "Client in: " + line
        self.factory.processprotocol.transport.write(line +'\n')        
        self.factory.processprotocol.currentclient = self 
        
    def connectionLost(self, reason):
        self.factory.connections -= 1
        if self.factory.processprotocol.currentclient == self:
            self.factory.processprotocol.currentclient = None

class GWSFactory(protocol.ServerFactory):
    protocol = GWSNetProtocol

    def __init__(self, processprotocol):
        self.connections = 0
        self.processprotocol = processprotocol
        

class GWSProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, printstderr=True, sendstderr= False):
        self.currentclient = None        
        self.printstderr = printstderr
        self.sendstderr = sendstderr
        
    def connectionMade(self):
        pass
    
    def outReceived(self, data):
        print >>sys.stderr, "Process out " + data
        if self.currentclient:        
            self.currentclient.sendLine(data.strip())                
        
    def errReceived(self, data):
        print >>sys.stderr, "Process err " + data
        if self.sendstderr and self.currentclient:        
            self.currentclient.sendLine(data.strip())
        if self.printstderr:    
            print >>sys.stderr, data.strip()
            
    def processExited(self, reason):
        print >>sys.stderr, "Process died"
        raise Exception("Process ended")
    
    def processEnded(self, reason):
        print >>sys.stderr, "Process died"
        raise Exception("Process ended")
            
    
class GenericWrapperServer:
    """Generic Server around a stdin/stdout based CLI tool. Only accepts one client at a time to prevent concurrency issues !!!!!"""
    def __init__(self, cmdline, port, printstderr= True, sendstderr= False):
        gwsprocessprotocol = GWSProcessProtocol(printstderr, sendstderr)
        cmdline = shlex.split(cmdline)
        reactor.spawnProcess(gwsprocessprotocol, cmdline[0], cmdline)

        gwsfactory = GWSFactory(gwsprocessprotocol)
        reactor.listenTCP(port, gwsfactory)
        reactor.run()
