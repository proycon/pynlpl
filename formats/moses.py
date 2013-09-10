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


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from pynlpl.common import u

import sys
import bz2
import gzip
import datetime
import socket
import io

try:
    from twisted.internet import protocol, reactor #No Python 3 support yet :(
    from twisted.protocols import basic
    twistedimported = True
except:
    print("WARNING: Twisted could not be imported",file=sys.stderr)
    twistedimported = False


class PhraseTable(object):
    def __init__(self,filename, quiet=False, reverse=False, delimiter="|||", score_column = 3, max_sourcen = 0,sourceencoder=None, targetencoder=None, scorefilter=None):
        """Load a phrase table from file into memory (memory intensive!)"""
        self.phrasetable = {}
        self.sourceencoder = sourceencoder
        self.targetencoder = targetencoder


        if filename.split(".")[-1] == "bz2":
            f = bz2.BZ2File(filename,'r')
        elif filename.split(".")[-1] == "gz":
            f = gzip.GzipFile(filename,'r')
        else:
            f = io.open(filename,'r',encoding='utf-8')
        linenum = 0
        prevsource = None
        targets = []

        while True:
            if not quiet:
                linenum += 1
                if (linenum % 100000) == 0:
                    print("Loading phrase-table: @%d" % linenum, "\t(" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ")",file=sys.stderr)
            line = u(f.readline())
            if not line:
                break

            #split into (trimmed) segments
            segments = [ segment.strip() for segment in line.split(delimiter) ]

            if len(segments) < 3:
                print("Invalid line: ", line, file=sys.stderr)
                continue

            #Do we have a score associated?
            if score_column > 0 and len(segments) >= score_column:
                scores = tuple( ( float(x) for x in segments[score_column-1].strip().split() ) )
            else:
                scores = tuple()

            #if align2_column > 0:
            #    try:
            #        null_alignments = segments[align2_column].count("()")
            #    except:
            #        null_alignments = 0
            #else:
            #    null_alignments = 0

            if scorefilter:
                if not scorefilter(scores): continue

            if reverse:
                if max_sourcen > 0 and segments[1].count(' ') + 1 > max_sourcen:
                    continue

                if self.sourceencoder:
                    source = self.sourceencoder(segments[1]) #tuple(segments[1].split(" "))
                else:
                    source = segments[1]
                if self.targetencoder:
                    target = self.targetencoder(segments[0]) #tuple(segments[0].split(" "))
                else:
                    target = segments[0]
            else:
                if max_sourcen > 0 and segments[0].count(' ') + 1 > max_sourcen:
                    continue

                if self.sourceencoder:
                    source = self.sourceencoder(segments[0]) #tuple(segments[0].split(" "))
                else:
                    source = segments[0]
                if self.targetencoder:
                    target = self.targetencoder(segments[1]) #tuple(segments[1].split(" "))
                else:
                    target = segments[1]


            if prevsource and source != prevsource and targets:
                self.phrasetable[prevsource] = tuple(targets)
                targets = []

            targets.append( (target,scores) )
            prevsource = source

        #don't forget last one:
        if prevsource and targets:
            self.phrasetable[prevsource] = tuple(targets)

        f.close()


    def __contains__(self, phrase):
        """Query if a certain phrase exist in the phrase table"""
        if self.sourceencoder: phrase = self.sourceencoder(phrase)
        return (phrase in self.phrasetable)
        #d = self.phrasetable
        #for word in phrase:
        #    if not word in d:
        #        return False
        #    d = d[word
        #return ("" in d)

    def __iter__(self):
        for phrase, targets in self.phrasetable.items():
            yield phrase, targets

    def __len__(self):
        return len(self.phrasetable)

    def __bool__(self):
        return bool(self.phrasetable)

    def __getitem__(self, phrase): #same as translations
        """Return a list of (translation, scores) tuples"""
        if self.sourceencoder: phrase = self.sourceencoder(phrase)
        return self.phrasetable[phrase]


        #d = self.phrasetable
        #for word in phrase:
        #    if not word in d:
        #        raise KeyError
        #    d = d[word]

        #if "" in d:
        #    return d[""]
        #else:
        #    raise KeyError

if twistedimported:
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

    class PhraseTableServer(object):
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

            data = b""
            while not data or data[-1] != '\n':
                data += self.socket.recv(self.BUFSIZE)
        else:
            data = self.lastresponse

        data = u(data)

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
        self.socket.send(phrase.encode('utf-8')+ b"\r\n")\


        data = b""
        while not data or data[-1] != '\n':
            data += self.socket.recv(self.BUFSIZE)

        data = u(data)

        for line in data.split('\n'):
            line = line.strip('\r\n')
            if line == "NOTFOUND":
                return False

        self.lastresponse = data
        self.lastquery = phrase

        return True

