#!/usr/bin/env python
#-*- coding:utf-8 -*-

import socket

class LMClient(object):

    def __init__(self,host= "localhost",port=12346):
        self.BUFSIZE = 1024
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Create the socket
        self.socket.settimeout(120) 
        self.socket.connect((host, port)) #Connect to server

    def scoresentence(self, sentence):
        if isinstance(sentence,list) or isinstance(sentence,tuple):
            sentence = " ".join(sentence)
        self.socket.send(sentence+ "\r\n")
        return float(self.socket.recv(self.BUFSIZE).strip())


