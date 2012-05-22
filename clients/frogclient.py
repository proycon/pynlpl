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

from socket import *

class FrogClient:
    def __init__(self,host="localhost",port=12345, tadpole_encoding="utf-8", parser=False, timeout=120.0):
        """Create a client connecting to a Frog or Tadpole server."""
        self.BUFSIZE = 4096
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect( (host,int(port)) )
        self.tadpole_encoding = tadpole_encoding
        self.parser = parser
        

    def process(self,input_data, source_encoding="utf-8", return_unicode = True):
        """Receives input_data in the form of a str or unicode object, passes this to the server, with proper consideration for the encodings, and returns the Tadpole output as a list of tuples: (word,pos,lemma,morphology), each of these is a proper unicode object unless return_unicode is set to False, in which case raw strings in the tadpole encoding will be returned."""
        if isinstance(input_data, list):
            input_data = " ".join(input_data)

        input_data = input_data.strip(' \t\n')

        #buffer = ""

        #print "SEND: ",input_data #DEBUG
        if not isinstance(input_data, unicode):
            input_data = unicode(input_data, source_encoding) #decode (or preferably do this in an earlier stage)
        self.socket.sendall(input_data.encode(self.tadpole_encoding) +'\r\n') #send to socket in desired encoding

        tp_output = []

        done = False
        while not done:    
            data = data = ""
            while not data or data[-1] != '\n':
                moredata = self.socket.recv(self.BUFSIZE)
                if not moredata: break
                data += moredata
            if return_unicode:
                data = unicode(data,self.tadpole_encoding)


            for line in data.strip(' \t\r\n').split('\n'):
                if line == "READY":
                    done = True
                    break
                elif line:
                    line = line.split('\t') #split on tab
                    if len(line) > 4 and line[0].isdigit(): #first column is token number
                        if line[0] == '1' and tp_output:
                            if self.parser:
                                tp_output.append( (None,None,None,None, None, None) )
                            else:
                                tp_output.append( (None,None,None,None) )  
                        fields = line[1:]
                        parse1=parse2=""
                        if len(fields) == 7:
                             word,lemma,morph,pos,posprob, parse1,parse2 = line[1:]
                        elif len(fields) == 6:
                            word,lemma,morph,pos, parse1,parse2 = line[1:]
                        elif len(fields) == 5:
                            word,lemma,morph,pos, posprob = line[1:]
                        elif len(fields) == 4:
                            word,lemma,morph,pos = line[1:]
                        elif len(fields) == 8:
                            word,lemma,morph,pos, posprob,parse1,parse2,chunker1 = line[1:]                            
                        elif len(fields) == 9:
                            word,lemma,morph,pos, posprob,parse1,parse2,chunker1,chunker2 = line[1:]
                        elif len(fields) == 11:
                            word,lemma,morph,pos, posprob,parse1,parse2,chunker1,chunker2,ner1,ner2 = line[1:]
                        elif len(fields) == 10:
                            word,lemma,morph,pos, posprob,parse1,parse2,ner,chunker1,chunker2 = line[1:]
                        else:
                            raise Exception("Can't process response line from Frog: ", repr(line), " got unexpected number of fields ", str(len(fields) + 1))

                        if self.parser:
                            tp_output.append( (word,lemma,morph,pos,parse1,parse2) )
                        else:
                            tp_output.append( (word,lemma,morph,pos) )
                        
        return tp_output
    
    def process_aligned(self,input_data, source_encoding="utf-8", return_unicode = True):
        output = self.process(input_data, source_encoding, return_unicode)
        outputwords = [ x[0] for x in output ]
        inputwords = input_data.strip(' \t\n').split(' ')
        alignment = self.align(inputwords, outputwords)
        for i, _ in enumerate(inputwords):
            targetindex = alignment[i]
            if targetindex == None:
                if self.parser:
                    yield (None,None,None,None,None,None)
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

