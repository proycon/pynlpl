#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os
import subprocess
import getopt


class MTWrapper(object):
    

    def __init__(self):        
        self.CORPUSNAME = ""
        self.WORKDIR = "./" 

        self.TRAINSOURCECORPUS = ""
        self.TRAINTARGETCORPUS = ""

        self.SOURCELANG = "" #language code
        self.TARGETLANG = "" #language code

        self.TOKENIZE_SOURCECORPUS = False #Set to true if the corpus is not tokenised yet
        self.TOKENIZE_TARGETCORPUS = False #Set to true if the corpus is not tokenised yet
        self.BUILD_SRILM_SOURCEMODEL = False
        self.BUILD_SRILM_TARGETMODEL = False
        self.BUILD_GIZA_WORDALIGNMENT = False
        self.BUILD_MOSES_PHRASETABLE = False
        
        #defaults
        self.PATH_UCTO = self.findpath('ucto')      
        self.PATH_TIMBL = self.findpath('timbl')
        self.PATH_MKCLS = self.findpath('mkcls')
        self.PATH_GIZA = self.findpath('GIZA++')
        self.PATH_PLAIN2SNT = self.findpath('plain2snt.out')                
        self.PATH_MOSES = self.findpath('moses')



    def findpath(self, name):
        for path in os.environ['PATH'].split(':'):
            if os.path.exists(path + '/' + name) and not os.path.isdir(path + '/' + name):
                print >>sys.stderr, green("Found " + name + " in " + path)
                return path + '/' + name
        return ""

    def check_common(self):
        sane = True
        if self.WORKDIR[-1] != '/':     
            self.WORKDIR += '/'
            if not os.path.isdir(self.WORKDIR):
                print >>sys.stderr,yellow("Work directory does not exist, creating " + self.WORKDIR)
                try:
                    os.mkdir(self.WORKDIR)
                except:
                    print >>sys.stderr, red("Configuration error: Unable to create work directory " + self.WORKDIR)
                    sane = False
        
        sane = True
        if not self.CORPUSNAME:
            print >>sys.stderr,red("Configuration error: CORPUSNAME not specified!")
            sane = False
        if not self.SOURCELANG:
            print >>sys.stderr,red("Configuration error: SOURCELANG not specified!")
            sane = False
        if not self.TARGETLANG:
            print >>sys.stderr,red("Configuration error: TARGETLANG not specified!")
            sane = False
        return sane

    def check_train(self):
        sane = True                            
        if not self.TRAINSOURCECORPUS:
            print >>sys.stderr,red("Configuration error: TRAINSOURCECORPUS not specified!")
            sane = False
        if not self.TRAINTARGETCORPUS:
            print >>sys.stderr,red("Configuration error: TRAINTARGETCORPUS not specified!")
            sane = False
            
            
        if self.BUILD_MOSES_PHRASETABLE:            
            print >>sys.stderr,red("Configuration update: BUILD_GIZA_WORDALIGNMENT automatically enabled because BUILD_MOSES_PHRASETABLE is too")
            self.BUILD_GIZA_WORDALIGNMENT = True
            if not self.PATH_MOSES or not os.path.isfile(self.PATH_MOSES):
                sane = False
                print >>sys.stderr,red("Dependency error: Moses not found (PATH_MOSES=" + self.PATH_MOSES + ")")
        if self.BUILD_GIZA_WORDALIGNMENT and (not self.PATH_GIZA or not os.path.isfile(self.PATH_GIZA)): 
            print >>sys.stderr,red("Dependency error: GIZA++ not found (PATH_GIZA=" + self.PATH_GIZA + ")")
        if self.BUILD_GIZA_WORDALIGNMENT and (not self.PATH_PLAIN2SNT or not os.path.isfile(self.PATH_PLAIN2SNT)): 
            print >>sys.stderr,red("Dependency error: plain2snt.out (provided by GIZA++) not found (PATH_PLAIN2SNT=" + self.PATH_PLAIN2SNT + ")")            
            sane = False
        if self.BUILD_GIZA_WORDALIGNMENT and (not self.PATH_MKCLS or not os.path.isfile(self.PATH_MKCLS)): 
            print >>sys.stderr,red("Dependency error: mkcls (provided by GIZA++) not found (PATH_MKCLS=" + self.PATH_MKCLS + ")")            
            sane = False                            
        
        return sane
    
    

    def getsourcefilename(self, extension):
        return self.WORKDIR + self.CORPUSNAME + '-' + self.SOURCELANG + '.' + extension

    def gettargetfilename(self, extension):
        return self.WORKDIR + self.CORPUSNAME + '-' + self.SOURCELANG + '.' + extension
    
    def getsntfilename(self):
        return self.WORKDIR + self.CORPUSNAME + '-' + self.SOURCELANG + '_' + self.CORPUSNAME + '-' + self.TARGETLANG + '.snt'
    
    def getgizafilename(self, extension = ''):
        s = self.WORKDIR + self.CORPUSNAME + '-' + self.SOURCELANG + '-' + self.TARGETLANG 
        if extension: s +=  '.' + extension
        return s    


    def usage(self):
        print >>sys.stderr,"Usage: " + os.path.basename(sys.argv[0]) + ' [command]'
        print >>sys.stderr,"Commands:"
        print >>sys.stderr,"\ttrain                  Train the MT system"


    def start(self):        
        try:
            cmd = sys.argv[1]
        except:
            self.usage()
            sys.exit(2)
        if cmd == 'train':
            self.starttrain()
        elif cmd == 'help' or cmd == '-h':
            self.usage()
        else:
            print >>sys.stderr,"Error, no such command: " + cmd
            self.usage()
            sys.exit(2)
            
    def starttrain(self):                
        self.init()
        if not self.check_common(): return False
        if not self.check_train(): return False
        
        if self.BUILD_GIZA_WORDALIGNMENT:
            if not self.build_giza_wordalignment():
                print >>sys.stderr, "Building GIZA++ Wordalignment failed. Aborting"    
                return False
        
    def runcmd(self, cmd, name):
        print >>sys.stderr, "----------------------------------------------------"
        print >>sys.stderr, bold(white("Calling " + name)) + ": " + cmd        
        r = subprocess.call(cmd, shell=True)
        if r != 0:
            print >>sys.stderr, bold(red("Runtime error from " + name))
            return False
        else:
            print >>sys.stderr, bold(green("Finished " + name))
            print >>sys.stderr, "----------------------------------------------------"
        return True
        
    def init(self):
        if not os.path.exists(self.getsourcefilename('txt')):
            os.symlink(self.TRAINSOURCECORPUS, self.getsourcefilename('txt') )
        if not os.path.exists(self.gettargetfilename('txt')):
            os.symlink(self.TRAINTARGETCORPUS, self.gettargetfilename('txt') )
        return True        
        
    def build_giza_wordalignment(self):
        if not self.runcmd(self.PATH_PLAIN2SNT + ' ' + self.getsourcefilename('txt') + ' ' + self.gettargetfilename('txt'),'giza-plain2snt'): return False
        if not self.runcmd(self.PATH_MKCLS + ' -m2 -p' + self.getsourcefilename('txt') + ' -c50 -V' + self.getsourcefilename('vcb.classes') + ' opt','giza-mkcls-source'): return False
        if not self.runcmd(self.PATH_MKCLS + ' -m2 -p' + self.gettargetfilename('txt') + ' -c50 -V' + self.gettargetfilename('vcb.classes') + ' opt','giza-mkcls-target'): return False       
        if not self.runcmd(self.PATH_GIZA + ' -S ' + self.gettargetfilename('vcb') + ' -T ' + self.gettargetfilename('vcb') + ' -C ' + self.getsntfilename() + ' -p0 0.98 -o ' + self.getgizafilename(),'giza'): return False
        return True
        #GIZA++ -S ${sourcelang}.vcb -T ${targetlang}.vcb -C "${sourcelang}_${targetlang}.snt" -p0 0.98 -o "${sourcelang}-${targetlang}"

    def build_moses_phrasetable(self):
        pass            
    
def usage():
    print >>sys.stderr,"wrapper.py -- MT wrapper - Outputs a MT wrapper script (python)"
    print >>sys.stderr,"Mandatory Input:"
    print >>sys.stderr,"\t-n <name>         Name of the corpus [MANDATORY!]"
    print >>sys.stderr,"\t-s <file>         Corpus in source language"
    print >>sys.stderr,"\t-t <file>         Corpus in target language"
    print >>sys.stderr,"\t-S <code>         Source language (iso-639-1 or 3)"
    print >>sys.stderr,"\t-T <code>         Target language (iso-639-1 or 3)"
    print >>sys.stderr,"\t-w <dir>          Work directory (by default: current dir)"
    
    
if __name__ == "__main__":        
    
    workdir = os.getcwd()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:S:T:n:w:")
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    sourcecorpusfile = targetcorpusfile = sourcelang = targetlang = corpusname = workdir = ""


    for o, a in opts:
        if o == '-s':
            sourcecorpusfile = a
        elif o == '-t':
            targetcorpusfile = a
        elif o == '-S':
            sourcelang = a        
        elif o == '-T':
            targetlang = a        
        elif o == '-n':
            corpusname = a
        elif o == '-w':
            workdir = a
        else:
            usage()
            sys.exit(0)
    
    if not corpusname:
        usage()
        sys.exit(2)
        
        
    print """#! /usr/bin/env python
# -*- coding: utf8 -*-#     
    
from pynlpl.mt.wrapper import MTWrapper

mtwrapper = MTWrapper()
    
mtwrapper.CORPUSNAME = "%s"
mtwrapper.WORKDIR = "%s"

mtwrapper.TRAINSOURCECORPUS = "%s"
mtwrapper.TRAINTARGETCORPUS = "%s"

mtwrapper.SOURCELANG = "%s" #language code
mtwrapper.TARGETLANG = "%s" #language code

mtwrapper.TOKENIZE_SOURCECORPUS = False #Set to true if the corpus is not tokenised yet
mtwrapper.TOKENIZE_TARGETCORPUS = False #Set to true if the corpus is not tokenised yet
mtwrapper.BUILD_SRILM_SOURCEMODEL = False
mtwrapper.BUILD_SRILM_TARGETMODEL = True
mtwrapper.BUILD_GIZA_WORDALIGNMENT = True
mtwrapper.BUILD_MOSES_PHRASETABLE = True

#defaults
#mtwrapper.PATH_UCTO = ""      
#mtwrapper.PATH_TIMBL = ""
#mtwrapper.PATH_MKCLS = ""
#mtwrapper.PATH_GIZA = ""
#mtwrapper.PATH_PLAIN2SNT = ""                
#mtwrapper.PATH_MOSES = ""

mtwrapper.start()
    """ % (corpusname, workdir, sourcecorpusfile, targetcorpusfile, sourcelang, targetlang)




def bold(s):
   CSI="\x1B["
   return CSI+"1m" + s + CSI + "0m"
   
def white(s):
   CSI="\x1B["
   return CSI+"37m" + s + CSI + "0m"   


def red(s):
   CSI="\x1B["
   return CSI+"31m" + s + CSI + "0m"
   
def green(s):
   CSI="\x1B["
   return CSI+"32m" + s + CSI + "0m"   


def yellow(s):
   CSI="\x1B["
   return CSI+"33m" + s + CSI + "0m"   

   
def blue(s):
   CSI="\x1B["
   return CSI+"34m" + s + CSI + "0m"   
   

def magenta(s):
   CSI="\x1B["
   return CSI+"35m" + s + CSI + "0m"   

