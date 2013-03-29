#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import    

import socket

class LMClient(object):

    def __init__(self,host= "localhost",port=12346,n = 0):        
        self.BUFSIZE = 1024
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Create the socket
        self.socket.settimeout(120)
        assert isinstance(port,int) 
        self.socket.connect((host, port)) #Connect to server
        assert isinstance(n,int)
        self.n = n

    def scoresentence(self, sentence):
        if self.n > 0:
            raise Exception("This client instance has been set to send only " + str(self.n) +  "-grams")
        if isinstance(sentence,list) or isinstance(sentence,tuple):
            sentence = " ".join(sentence)
        self.socket.send(sentence+ "\r\n")
        return float(self.socket.recv(self.BUFSIZE).strip())

    def __getitem__(self, ngram):
        if self.n == 0:
            raise Exception("This client  has been set to send only full sentence, not n-grams")
        if isinstance(ngram,str) or isinstance(ngram,unicode):
            ngram = ngram.split(" ")
        if len(ngram) != self.n:
            raise Exception("This client instance has been set to send only " + str(self.n) +  "-grams.")
        ngram = " ".join(ngram)
        if (sys.version < '3' and isinstance(ngram,unicode)) or( sys.version == '3' and isinstance(ngram,str)):
            ngram = ngram.encode('utf-8')        
        self.socket.send(ngram + b"\r\n")
        return float(self.socket.recv(self.BUFSIZE).strip())
        
        
        
        
