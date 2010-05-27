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


import codecs
import os.path
#import os.subprocess

class FreeLingClient:
    def __init__(self, channel, encoding='iso-8859-15'):
        """Initialise the client, set channel to the path and filename where the server's .in and .out pipes are (without extension)"""
        if not os.path.exists(channel+".in"):
            raise Exception("Channel does not exist. Is the FreeLing server started in the specified directory?")
        self.channel = channel
        self.encoding = encoding


    def sendrecv(self, sourcewords):       
        """Send data to server and return received result""" 
        fin = codecs.open(self.channel+".in",'w', self.encoding, 'ignore')
        if isinstance( sourcewords, list ):
            fin.write(" ".join(sourcewords)+ "\n")
        else:
            fin.write(sourcewords + "\n")
        fin.close()

        fout = codecs.open(self.channel+".out",'r',self.encoding, 'ignore')
        output = []
        while True:
            line = fout.readline()
            if not line:
                   break #EOF
            else:
                if line.strip():
                    output.append(line.strip())
        fout.close()
        return output
        
    def process(self, sourcewords):
        """Process a list of words, passing it to the server and realigning the output with the original words"""
        targetwords = []
        for i, outputline in enumerate(self.sendrecv(sourcewords)):
            cols = outputline.split(" ")
            subwords = cols[0].lower().split("_")
            if len(cols) > 2: #this seems a bit odd?
                for word in subwords: #split multiword expressions
                    targetwords.append( (word, cols[1], cols[2], i, len(subwords) > 1 ) ) #word, lemma, pos, index, multiword?


        sourcewords = [ w.lower() for w in sourcewords ]          

        alignment = []
        for i, sourceword in enumerate(sourcewords):
            found = False
            best = 0  
            distance = 999999          
            for j, (targetword, lemma, pos, index, multiword) in enumerate(targetwords):
                if sourceword == targetword and abs(i-j) < distance:
                    found = True
                    best = j
                    distance = abs(i-j)

            if found:
                alignment.append(targetwords[best])
            else:                
                alignment.append((None,None,None,None,False)) #no alignment found
        return alignment

