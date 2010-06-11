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

import socket

class LMServer:
    def __init__(self,lm,host="",port=12346):
        self.lm = lm
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host,port))
        self.socket.listen(5)


        while True:
            client_socket, address = self.socket.accept()
            while True:
                data = client_socket.recv(4084)
                if not data: break
                client_socket.send(str(lm.scoresentence(data)))

