###############################################################
#  PyNLPl - FreeLing Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Radboud University Nijmegen
#       
#       Licensed under GPLv3
# 
# This is a Python library for on-the-fly communication with
# a FreeLing server. Allowing on-the-fly lemmatisation and
# PoS-tagging. It is recommended to pass your data on a 
# sentence-by-sentence basis to FreeLingClient.process()
#
# Make sure to start Freeling (analyzer)  with the --server 
# and --flush flags !!!!!
#
###############################################################

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import    
from pynlpl.common import u
    
import socket
import sys

class FreeLingClient(object):
    def __init__(self, host, port, encoding='utf-8', timeout=120.0):
        """Initialise the client, set channel to the path and filename where the server's .in and .out pipes are (without extension)"""
        self.encoding = encoding
        self.BUFSIZE = 10240
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect( (host,int(port)) )
        self.encoding = encoding
        self.socket.sendall('RESET_STATS\0')
        r = self.socket.recv(self.BUFSIZE)
        if not r.strip('\0') == 'FL-SERVER-READY':
            raise Exception("Server not ready")

        
    def process(self, sourcewords, debug=False):
        """Process a list of words, passing it to the server and realigning the output with the original words"""

        if isinstance( sourcewords, list ) or isinstance( sourcewords, tuple ):
            sourcewords_s = " ".join(sourcewords)            
        else:
            sourcewords_s = sourcewords
            sourcewords = sourcewords.split(' ')
        
        self.socket.sendall(sourcewords_s.encode(self.encoding) +'\n\0')
        if debug: print("Sent:",sourcewords_s.encode(self.encoding),file=sys.stderr)
        
        results = []
        done = False
        while not done:    
            data = b""
            while not data:
                buffer = self.socket.recv(self.BUFSIZE)
                if debug: print("Buffer: ["+repr(buffer)+"]",file=sys.stderr)
                if buffer[-1] == '\0':
                    data += buffer[:-1]
                    done = True
                    break
                else:
                    data += buffer

            
            data = u(data,self.encoding)
            if debug: print("Received:",data,file=sys.stderr) 

            for i, line in enumerate(data.strip(' \t\0\r\n').split('\n')):
                if not line.strip():
                    done = True
                    break
                else:
                    cols = line.split(" ")
                    subwords = cols[0].lower().split("_")
                    if len(cols) > 2: #this seems a bit odd?
                        for word in subwords: #split multiword expressions
                            results.append( (word, cols[1], cols[2], i, len(subwords) > 1 ) ) #word, lemma, pos, index, multiword?

        sourcewords = [ w.lower() for w in sourcewords ]          

        alignment = []
        for i, sourceword in enumerate(sourcewords):
            found = False
            best = 0  
            distance = 999999          
            for j, (targetword, lemma, pos, index, multiword) in enumerate(results):
                if sourceword == targetword and abs(i-j) < distance:
                    found = True
                    best = j
                    distance = abs(i-j)

            if found:
                alignment.append(results[best])
            else:                
                alignment.append((None,None,None,None,False)) #no alignment found
        return alignment

