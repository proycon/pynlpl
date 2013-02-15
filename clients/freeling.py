###############################################################
#  PyNLPl - FreeLing Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
# 
# This is a Python library for on-the-fly communication with
# a FreeLing server. Allowing on-the-fly lemmatisation and
# PoS-tagging. It is recommended to pass your data on a 
# sentence-by-sentence basis to FreeLingClient.process()
#
###############################################################


import socket

class FreeLingClient:
    def __init__(self, host, port, encoding='utf-8', timeout=120.0):
        """Initialise the client, set channel to the path and filename where the server's .in and .out pipes are (without extension)"""
        self.encoding = encoding
        self.BUFSIZE = 4096
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect( (host,int(port)) )
        self.encoding = encoding        

        
    def process(self, sourcewords):
        """Process a list of words, passing it to the server and realigning the output with the original words"""

        if isinstance( sourcewords, list ) or isinstance( sourcewords, tuple ):
            sourcewords_s = u" ".join(sourcewords)            
        else:
            sourcewords_s = sourcewords
            sourcewords = sourcewords.split(' ')
        
        self.socket.sendall(sourcewords_s.encode(self.encoding) +'\r\n')

        results = []
        done = False
        while not done:    
            data = ""
            while not data or data[-1] != '\n':
                moredata = self.socket.recv(self.BUFSIZE)
                if not moredata: break
                data += moredata
                data = unicode(data,self.encoding)


            for i, line in enumerate(data.strip(' \t\r\n').split('\n')):
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

