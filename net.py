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
import subprocess
import shlex
import time
import sys

class GWSProtocol(basic.LineReceiver):
    def lineReceived(self, line):
        #post line as input to process
        while self.factory.busy: 
            time.sleep(0.1)
        #send output to client
        self.factory.process.stdin.write(line+"\n")
        output = self.factory.process.stdout.readline().strip()
        self.sendLine(output)
        
class GWSFactory(protocol.ServerFactory):
    protocol = GWSProtocol

    def __init__(self, cmd, shell=True, sendstderr=False):
        if isinstance(cmd, str) or isinstance(cmd,unicode):
            self.cmd = shlex.split(cmd)
        else: 
            self.cmd = cmd
            
        self.sendstderr = False
        self.busy = False
        print >>sys.stderr, "Launching background process"
        print >>sys.stderr, self.cmd        
        self.process = subprocess.Popen(self.cmd, shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def __delete__(self):
        self.process.close()
    
class GenericWrapperServer:
    """Generic Server around a stdin/stdout based CLI tool"""
    def __init__(self, cmdline, port, shell=True,sendstderr= False, close_fds=True):
        reactor.listenTCP(port, GWSFactory(cmdline, shell, sendstderr))
        reactor.run()

