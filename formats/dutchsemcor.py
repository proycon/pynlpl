#-*- coding:utf-8 -*-

###############################################################
#  Modified by Ruben Izquierdo
#  We need also to store the TIMBL distance to the nearest neighboor  
#
# PyNLPl - DutchSemCor
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
# 
# Collection of formats for the DutchSemCor project
#
###############################################################


from pynlpl.formats.timbl import TimblOutput
from pynlpl.statistics import Distribution
import codecs
from sys import stderr

class WSDSystemOutput(object):
    def __init__(self, filename = None):
        self.data = {}
        self.distances={}
        self.maxDistance=1
        if filename:
            self.load(filename)

    def append(self, word_id, senses,distance=0):
       # Commented by Ruben, there are some ID's that are repeated in all sonar test files...            
       #assert (not word_id in self.data)
       if isinstance(senses, Distribution):
            self.data[word_id] = ( (x,y) for x,y in senses ) #PATCH UNDONE (#TODO: this is a patch, something's not right in Distribution?)
            self.distances[word_id]=distance
            if distance > self.maxDistance:
              self.maxDistance=distance
            return
       else:
           assert isinstance(senses, list) and len(senses) >= 1

       self.distances[word_id]=distance
       if distance > self.maxDistance:
        self.maxDistance=distance
                             
       
       if len(senses[0]) == 1:
            #not a (sense_id, confidence) tuple! compute equal confidence for all elements automatically:
            confidence = 1 / float(len(senses))
            self.data[word_id]  = [ (x,confidence) for x in senses ]
       else: 
          fulldistr = True
          for sense, confidence in senses:
            if confidence == None:
                fulldistr = False
                break

          if fulldistr:
               self.data[word_id] = Distribution(senses)
          else:
               self.data[word_id] = senses
        

    def getMaxDistance(self):
        return self.maxDistance
    
    def __iter__(self):
        for word_id, senses in  self.data.items():
            yield word_id, senses,self.distances[word_id]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, word_id):
        """Returns the sense distribution for the given word_id"""
        return self.data[word_id]

    def load(self, filename):
        f = codecs.open(filename,'r','utf-8')
        for line in f:
            fields = line.strip().split(" ")
            word_id = fields[0]
            if len(fields[1:]) == 1:
                #only one sense, no confidence expressed:
                self.append(word_id, [(fields[1],None)])
            else:
                senses = []
                distance=-1
                for i in range(1,len(fields),2):
                    if i+1==len(fields):
                        #The last field is the distance
                        if fields[i][:4]=='+vdi': #Support for previous format of wsdout
                            distance=float(fields[i][4:])
                        else:
                            distance=float(fields[i])
                    else:
                        if fields[i+1] == '?': fields[i+1] = None
                        senses.append( (fields[i], fields[i+1]) )
                self.append(word_id, senses,distance)
                
        f.close()

    def save(self, filename):
        f = codecs.open(filename,'w','utf-8')
        for word_id, senses,distance in self:
            f.write(word_id)
            for sense, confidence in senses:
                if confidence == None: confidence = "?"
                f.write(" " + str(sense) + " " + str(confidence))
            if word_id in self.distances.keys():
                f.write(' '+str(self.distances[word_id]))
            f.write("\n")
        f.close()

    def out(self, filename):
        for word_id, senses,distance in self:
            print word_id,distance,
            for sense, confidence in senses:
                if confidence == None: confidence = "?"
                print " " + sense + " " + str(confidence),
            print

    def senses(self, bestonly=False):
        """Returns a list of all predicted senses"""
        l = []
        for word_id, senses,distance in self:
            for sense, confidence in senses:
                if not sense in l: l.append(sense)
                if bestonly:
                    break
        return l


    def loadfromtimbl(self, filename):
        timbloutput = TimblOutput(codecs.open(filename,'r','utf-8'))
        for i, (features, referenceclass, predictedclass, distribution, distance) in enumerate(timbloutput):
            if distance != None:
                #distance='+vdi'+str(distance)
                distance=float(distance)
            if len(features) == 0:
                print >>stderr, "WARNING: Empty feature vector in " + filename + " (line " + str(i+1) + ") skipping!!"
                continue
            word_id = features[0] #note: this is an assumption that must be adhered to!
            if distribution:
                self.append(word_id, distribution,distance)

    def fromTimblToWsdout(self,fileTimbl,fileWsdout):
        timbloutput = TimblOutput(codecs.open(fileTimbl,'r','utf-8'))
        wsdoutfile = codecs.open(fileWsdout,'w','utf-8')
        for i, (features, referenceclass, predictedclass, distribution, distance) in enumerate(timbloutput):
            if len(features) == 0:
                print >>stderr, "WARNING: Empty feature vector in " + fileTimbl + " (line " + str(i+1) + ") skipping!!"
                continue
            word_id = features[0] #note: this is an assumption that must be adhered to!
            if distribution:
                wsdoutfile.write(word_id+' ')
                for sense, confidence in distribution:
                    if confidence== None: confidence='?'
                    wsdoutfile.write(sense+' '+str(confidence)+' ')
                wsdoutfile.write(str(distance)+'\n')
        wsdoutfile.close()
                                                    


class DataSet(object): #for testsets/trainingsets
    def __init__(self, filename):
        self.sense = {} #word_id => (sense_id, lemma,pos)
        self.targetwords = {} #(lemma,pos) => [sense_id]
        f = codecs.open(filename,'r','utf-8')
        for line in f:
            if len(line) > 0 and line[0] != '#':
                fields = line.strip('\n').split('\t')
                word_id = fields[0]
                sense_id = fields[1]
                lemma = fields[2]
                pos = fields[3]
                self.sense[word_id] = (sense_id, lemma, pos)
                if not (lemma,pos) in self.targetwords:
                    self.targetwords[(lemma,pos)] = []
                if not sense_id in self.targetwords[(lemma,pos)]:
                    self.targetwords[(lemma,pos)].append(sense_id)
        f.close()

    def __getitem__(self, word_id):
        return self.sense[self._sanitize(word_id)]

    def getsense(self, word_id):
        return self.sense[self._sanitize(word_id)][0]

    def getlemma(self, word_id):
        return self.sense[self._sanitize(word_id)][1]

    def getpos(self, word_id):
        return self.sense[self._sanitize(word_id)][2]

    def _sanitize(self, word_id):
        if isinstance(word_id, unicode):
            return word_id
        else:
            return unicode(word_id,'utf-8')

    def __contains__(self, word_id):
        return (self._sanitize(word_id) in self.sense)


    def __iter__(self):
        for word_id, (sense, lemma, pos) in self.sense.items():
            yield (word_id, sense, lemma, pos)

    def senses(self, lemma, pos):
        return self.targetwords[(lemma,pos)]
