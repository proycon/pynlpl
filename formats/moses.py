###############################################################
#  PyNLPl - Moses formats
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
# This is a Python library classes and functions for 
# reading file-formats produced by Moses. Currently 
# contains only a class for reading a Moses PhraseTable.
# (migrated to pynlpl from pbmbmt)
#
###############################################################    

import sys
import bz2
import datetime
import socket
from twisted.internet import protocol, reactor
from twisted.protocols import basic

class PhraseTable:
    def __init__(self,filename, quiet=False, reverse=False, delimiter="|||", score_column = 5, align2_column = 4):
        """Load a phrase table from file into memory (memory intensive!)"""
        self.phrasetable = {}
        if filename.split(".")[-1] == "bz2":
            f = bz2.BZ2File(filename,'r')        
        else:
            f = open(filename,'r')
        linenum = 0
        while True:
            if not quiet:
                linenum += 1
                if (linenum % 100000) == 0:
                    print >> sys.stderr, "Loading phrase-table: @%d" % linenum, "\t(" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ")"
            line = f.readline()
            if not line: 
                break

             #split into (trimmed) segments
            segments = [ segment.strip() for segment in line.split(delimiter) ]

            #Do we have a score associated?
            if score_column > 0 and len(segments) >= score_column:
                nums = segments[score_column-1].strip().split(" ")
                Pst = float(nums[0]) #the 1st number is p(source|target)
                Pts = float(nums[2]) #3rd number is p(target|source)
            else:
                Pst = Pts = 0

            if align2_column > 0:
                try:
                    null_alignments = segments[align2_column].count("()")
                except:
                    null_alignments = 0
            else:
                null_alignments = 0

            if reverse:
                source = segments[1] #tuple(segments[1].split(" "))
                target = segments[0] #tuple(segments[0].split(" "))
            else:
                source = segments[0] #tuple(segments[0].split(" "))
                target = segments[1] #tuple(segments[1].split(" "))

            self.append(source, target,Pst,Pts,null_alignments)
                        
        f.close()        


    def append(self, source, target, Pst = 0, Pts = 0, null_alignments = 0):
        try:
            self.phrasetable[source].append((target, Pst, Pts, null_alignments))
        except:
            self.phrasetable[source] = [ (target, Pst, Pts, null_alignments) ]

        #d = self.phrasetable
        #for word in source:
        #    if not word in d:
        #        d[word] = {}
        #    d = d[word]

        #if "" in d:
        #    d[""].append( (target, Pst, Pts, null_alignments) )
        #else:
        #    d[""] = [ (target, Pst, Pts, null_alignments) ]

    def __contains__(self, phrase):
        """Query if a certain phrase exist in the phrase table"""
        return (phrase in self.phrasetable)
        #d = self.phrasetable
        #for word in phrase:
        #    if not word in d:
        #        return False
        #    d = d[word]
        #return ("" in d)

    def __getitem__(self, phrase): #same as translations
        """Return a list of (translation, Pst, Pts, null_alignment) tuples"""
        try:
            return self.phrasetable[phrase]
        except KeyError:
            raise


        #d = self.phrasetable
        #for word in phrase:
        #    if not word in d:
        #        raise KeyError
        #    d = d[word]

        #if "" in d:
        #    return d[""]
        #else:
        #    raise KeyError


class PTProtocol(basic.LineReceiver):
    def lineReceived(self, phrase):
        try:
            for target,Pst,Pts,null_alignments in self.factory.phrasetable[phrase]:
                self.sendLine(target+"\t"+str(Pst)+"\t"+str(Pts)+"\t"+str(null_alignments))
        except KeyError:
            self.sendLine("NOTFOUND")

class PTFactory(protocol.ServerFactory):
    protocol = PTProtocol
    def __init__(self, phrasetable):
        self.phrasetable = phrasetable

class PhraseTableServer:
    def __init__(self, phrasetable, port=65432):
        reactor.listenTCP(port, PTFactory(phrasetable))
        reactor.run()
        



class PhraseTableClient(object):

    def __init__(self,host= "localhost",port=65432):        
        self.BUFSIZE = 4048
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Create the socket
        self.socket.settimeout(120) 
        self.socket.connect((host, port)) #Connect to server
        self.lastresponse = ""
        self.lastquery = ""

    def __getitem__(self, phrase):
        solutions = []        
        if phrase != self.lastquery:
            self.socket.send(phrase+ "\r\n")
                    
        
            data = ""
            while not data or data[-1] != '\n':
                data += self.socket.recv(self.BUFSIZE)
        else:
            data = self.lastresponse

        for line in data.split('\n'):
            line = line.strip('\r\n')
            if line == "NOTFOUND":
                raise KeyError(phrase)
            elif line:
                fields = tuple(line.split("\t"))
                if len(fields) == 4:
                    solutions.append( fields )
                else:
                    print >>sys.stderr,"PHRASETABLECLIENT WARNING: Unable to parse response line"
                    
        self.lastresponse = data
        self.lastquery = phrase
                            
        return solutions
    
    def __contains__(self, phrase):
        self.socket.send(phrase+ "\r\n")\
        
        solutions = []
        
        data = ""
        while not data or data[-1] != '\n':
            data += self.socket.recv(self.BUFSIZE)

        for line in data.split('\n'):
            line = line.strip('\r\n')
            if line == "NOTFOUND":
                return False
                
        self.lastresponse = data
        self.lastquery = phrase
        
        return True
                
