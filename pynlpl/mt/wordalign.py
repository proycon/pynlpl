from pynlpl.statistics import FrequencyList, Distribution


class WordAlignment(object):

    def __init__(self, casesensitive = False):
        self.casesensitive = casesensitive

    def train(self, sourcefile, targetfile):
        sourcefile = open(sourcefile)
        targetfile = open(targetfile)

        self.sourcefreqlist = FrequencyList(None, self.casesensitive)
        self.targetfreqlist = FrequencyList(None, self.casesensitive)

        #frequency lists
        self.source2target = {}
        self.target2source = {}

        for sourceline, targetline in zip(sourcefile, targetfile):
            sourcetokens = sourceline.split()
            targettokens = targetline.split()

            self.sourcefreqlist.append(sourcetokens)
            self.targetfreqlist.append(targettokens)

            for sourcetoken in sourcetokens:
                if not sourcetoken in self.source2target:
                    self.source2target[sourcetoken] = FrequencyList(targettokens,self.casesensitive)
                else:
                    self.source2target[sourcetoken].append(targettokens)

            for targettoken in targettokens:
                if not targettoken in self.target2source:
                    self.target2source[targettoken] = FrequencyList(sourcetokens,self.casesensitive)
                else:
                    self.target2source[targettoken].append(sourcetokens)

        sourcefile.close()
        targetfile.close()

    def test(self, sourcefile, targetfile):
        sourcefile = open(sourcefile)
        targetfile = open(targetfile)


        #stage 2
        for sourceline, targetline in zip(sourcefile, targetfile):
            sourcetokens = sourceline.split()
            targettokens = targetline.split()

            S2Talignment = []
            T2Salignment = []

            for sourcetoken in sourcetokens:
                #which of the target-tokens is most frequent?
                besttoken = None
                bestscore = -1
                for i, targettoken in enumerate(targettokens):
                    if targettoken in self.source2target[sourcetoken]:
                        score = self.source2target[sourcetoken][targettoken] / float(self.targetfreqlist[targettoken])
                        if score > bestscore:
                            bestscore = self.source2target[sourcetoken][targettoken]
                            besttoken = i
                S2Talignment.append(besttoken) #TODO: multi-alignment?

            for targettoken in targettokens:
                besttoken = None
                bestscore = -1
                for i, sourcetoken in enumerate(sourcetokens):
                    if sourcetoken in self.target2source[targettoken]:
                        score = self.target2source[targettoken][sourcetoken] / float(self.sourcefreqlist[sourcetoken])
                        if score > bestscore:
                            bestscore = self.target2source[targettoken][sourcetoken]
                            besttoken = i
                T2Salignment.append(besttoken) #TODO: multi-alignment?

            yield sourcetokens, targettokens, S2Talignment, T2Salignment

        sourcefile.close()
        targetfile.close()

