###############################################################
#  PyNLPl - Frog Client - Version 1.4.1
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Derived from code by Rogier Kraf
#
#       Licensed under GPLv3
#
# This is a Python library for on-the-fly communication with
# a Frog/Tadpole Server. Allowing on-the-fly lemmatisation and
# PoS-tagging. It is recommended to pass your data on a
# sentence-by-sentence basis to FrogClient.process()
#
###############################################################

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from pynlpl.common import u

import socket

class FrogClient:
    def __init__(self,host="localhost",port=12345, server_encoding="utf-8", returnall=False, timeout=120.0, ner=False):
        """Create a client connecting to a Frog or Tadpole server."""
        self.BUFSIZE = 4096
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect( (host,int(port)) )
        self.server_encoding = server_encoding
        self.returnall = returnall




    def process(self,input_data, source_encoding="utf-8", return_unicode = True, oldfrog=False):
        """Receives input_data in the form of a str or unicode object, passes this to the server, with proper consideration for the encodings, and returns the Frog output as a list of tuples: (word,pos,lemma,morphology), each of these is a proper unicode object unless return_unicode is set to False, in which case raw strings will be returned. Return_unicode is no longer optional, it is fixed to True, parameter is still there only for backwards-compatibility."""
        if isinstance(input_data, list) or isinstance(input_data, tuple):
            input_data = " ".join(input_data)



        input_data = u(input_data, source_encoding) #decode (or preferably do this in an earlier stage)
        input_data = input_data.strip(' \t\n')

        s = input_data.encode(self.server_encoding) +b'\r\n'
        if not oldfrog: s += b'EOT\r\n'
        self.socket.sendall(s) #send to socket in desired encoding
        output = []

        done = False
        while not done:
            data = b""
            while not data.endswith(b'\n'):
                moredata = self.socket.recv(self.BUFSIZE)
                if not moredata: break
                data += moredata


            data = u(data,self.server_encoding)


            for line in data.strip(' \t\r\n').split('\n'):
                if line == "READY":
                    done = True
                    break
                elif line:
                    line = line.split('\t') #split on tab
                    if len(line) > 4 and line[0].isdigit(): #first column is token number
                        if line[0] == '1' and output:
                            if self.returnall:
                                output.append( (None,None,None,None, None,None,None, None) )
                            else:
                                output.append( (None,None,None,None) )
                        fields = line[1:]
                        parse1=parse2=ner=chunk=""
                        word,lemma,morph,pos = fields[0:4]
                        if len(fields) > 5:
                            ner = fields[5]
                        if len(fields) > 6:
                            chunk = fields[6]

                        if len(fields) < 5:
                            raise Exception("Can't process response line from Frog: ", repr(line), " got unexpected number of fields ", str(len(fields) + 1))

                        if self.returnall:
                            output.append( (word,lemma,morph,pos,ner,chunk,parse1,parse2) )
                        else:
                            output.append( (word,lemma,morph,pos) )

        return output

    def process_aligned(self,input_data, source_encoding="utf-8", return_unicode = True):
        output = self.process(input_data, source_encoding, return_unicode)
        outputwords = [ x[0] for x in output ]
        inputwords = input_data.strip(' \t\n').split(' ')
        alignment = self.align(inputwords, outputwords)
        for i, _ in enumerate(inputwords):
            targetindex = alignment[i]
            if targetindex == None:
                if self.returnall:
                    yield (None,None,None,None,None,None,None,None)
                else:
                    yield (None,None,None,None)
            else:
                yield output[targetindex]

    def align(self,inputwords, outputwords):
        """For each inputword, provides the index of the outputword"""
        alignment = []
        cursor = 0
        for inputword in inputwords:
            if len(outputwords) > cursor and outputwords[cursor] == inputword:
                alignment.append(cursor)
                cursor += 1
            elif len(outputwords) > cursor+1 and outputwords[cursor+1] == inputword:
                alignment.append(cursor+1)
                cursor += 2
            else:
                alignment.append(None)
                cursor += 1
        return alignment


    def __del__(self):
        self.socket.close()

