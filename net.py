#-*- coding:utf-8 -*-

#---------------------------------------------------------------
# PyNLPl - Network utilities
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://www.github.com/proycon/pynlpl
#   proycon AT anaproy DOT nl
#
#   Generic Server for Language Models
#
#----------------------------------------------------------------

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import u,b
import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout
from twisted.internet import protocol, reactor # will fail on Python 3 for now
from twisted.protocols import basic
import shlex



class GWSNetProtocol(basic.LineReceiver):
    def connectionMade(self):
        print("Client connected", file=stderr)
        self.factory.connections += 1
        if self.factory.connections != 1:
            self.transport.loseConnection()
        else:
            self.sendLine(b("READY"))

    def lineReceived(self, line):
        try:
            print("Client in: " + line,file=stderr)
        except UnicodeDecodeError:
            print("Client in: (unicodeerror)",file=stderr)
        if sys.version < '3':
            if isinstance(line,unicode):
                self.factory.processprotocol.transport.write(line.encode('utf-8'))
            else:
                self.factory.processprotocol.transport.write(line)
            self.factory.processprotocol.transport.write(b('\n'))
        else:
            self.factory.processprotocol.transport.write(b(line + '\n'))
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
    def __init__(self, printstderr=True, sendstderr= False, filterout = None, filtererr = None):
        self.currentclient = None
        self.printstderr = printstderr
        self.sendstderr = sendstderr
        if not filterout:
            self.filterout = lambda x: x
        else:
            self.filterout = filterout
        if not filtererr:
            self.filtererr = lambda x: x
        else:
            self.filtererr = filtererr

    def connectionMade(self):
        pass

    def outReceived(self, data):
        try:
            print("Process out " + data,file=stderr)
        except UnicodeDecodeError:
            print("Process out (unicodeerror)",file=stderr)
        for line in b(data).strip().split(b('\n')):
            line = self.filterout(line.strip())
            if self.currentclient and line:
                self.currentclient.sendLine(line)

    def errReceived(self, data):
        try:
            print("Process err " + data,file=stderr)
        except UnicodeDecodeError:
            print("Process out (unicodeerror)",file=stderr)
        if self.printstderr and data:
            print(data.strip(),file=stderr)
        for line in b(data).strip().split(b('\n')):
            line = self.filtererr(line.strip())
            if self.sendstderr and self.currentclient and line:
                self.currentclient.sendLine(line)


    def processExited(self, reason):
        print("Process exited",file=stderr)


    def processEnded(self, reason):
        print("Process ended",file=stderr)
        if self.currentclient:
            self.currentclient.transport.loseConnection()
        reactor.stop()


class GenericWrapperServer:
    """Generic Server around a stdin/stdout based CLI tool. Only accepts one client at a time to prevent concurrency issues !!!!!"""
    def __init__(self, cmdline, port, printstderr= True, sendstderr= False, filterout = None, filtererr = None):
        gwsprocessprotocol = GWSProcessProtocol(printstderr, sendstderr, filterout, filtererr)
        cmdline = shlex.split(cmdline)
        reactor.spawnProcess(gwsprocessprotocol, cmdline[0], cmdline)

        gwsfactory = GWSFactory(gwsprocessprotocol)
        reactor.listenTCP(port, gwsfactory)
        reactor.run()
