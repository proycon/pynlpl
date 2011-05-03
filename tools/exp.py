#!/usr/bin/env python
#-*- coding:utf-8 -*-

##############################
# EXPERIMENT FRAMEWORK
##############################


import datetime
import subprocess
import sys
import os
import glob
import time

#Configuration is specific to ILK servers (TODO: make external configuration file)
MAILTO='proycon@anaproy.nl'
HOST = os.uname()[1]
USER = os.getenv("USER")
HOMEDIR = os.getenv("HOME")
PROCDIR = HOMEDIR + '/.expproc'
EXPLOGDIR = '/exp/' + USER + '/explogs/'
DAILYMAILHOUR = 6
POLLINTERVAL = 30 #poll every 30 seconds
RESINTERVAL = 600 #every 10 minutes (update resource logs)

if not os.path.isdir(PROCDIR):
    os.mkdir(PROCDIR)
if not os.path.isdir(EXPLOGDIR):
    os.mkdir(EXPLOGDIR)

def usage():
    print "Syntax: exp start    EXPERIMENT-ID COMMAND"
    print "        exp stop     EXPERIMENT-ID"
    print "        exp kill     EXPERIMENT-ID"
    print "        exp ps       [HOST]"
    print "        exp history  [YEARMONTH/FILTERKEYWORD]"
    print "        exp log      EXPERIMENT-ID"
    print "        exp errlog   EXPERIMENT-ID"
    print "        exp reslog   EXPERIMENT-ID"
    print "        exp audit    EXPERIMENT-ID"
    print "        exp auditlog EXPERIMENT-ID"
    print "        exp auditerr EXPERIMENT-ID"
    print "        exp auditres EXPERIMENT-ID"
    print "        exp mailstat EXPERIMENT-ID"
    sys.exit(2)

def bold(s):
   CSI="\x1B["
   reset=CSI+"m"
   return CSI+"1m" + s + CSI + "0m"


def red(s):
   CSI="\x1B["
   reset=CSI+"m"
   return CSI+"31m" + s + CSI + "0m"
   
def green(s):
   CSI="\x1B["
   reset=CSI+"m"
   return CSI+"32m" + s + CSI + "0m"   


def yellow(s):
   CSI="\x1B["
   reset=CSI+"m"
   return CSI+"33m" + s + CSI + "0m"   

   
def blue(s):
   CSI="\x1B["
   reset=CSI+"m"
   return CSI+"34m" + s + CSI + "0m"   
   

def magenta(s):
   CSI="\x1B["
   reset=CSI+"m"
   return CSI+"35m" + s + CSI + "0m"   
   
   
def tail(filepath, f, read_size=1024): #source: Manu Garg, http://www.manugarg.com/2007/04/tailing-in-python.html
  """
  This function returns the last line of a file.
  Args:
    filepath: path to file
    read_size:  data is read in chunks of this size (optional, default=1024)
  Raises:
    IOError if file cannot be processed.
  """
  #f = open(filepath, 'rU')    # U is to open it with Universal newline support
  offset = read_size
  f.seek(0, 2)
  file_size = f.tell()
  while 1:
    if file_size < offset:
      offset = file_size
    f.seek(-1*offset, 2)
    read_str = f.read(offset)
    # Remove newline at the end
    if read_str[offset - 1] == '\n':
      read_str = read_str[0:-1]
    lines = read_str.split('\n')
    if len(lines) > 1:  # Got a line
      return lines[len(lines) - 1]
    if offset == file_size:   # Reached the beginning
      return read_str
    offset += read_size
  #f.close()

def ps(host, dir = ""):
    global HOST
    found = False
    pids = None
    out = ""
    if dir:
        pattern = PROCDIR + '/' + host + '/' + dir + '/*'
    else:
        pattern = PROCDIR + '/' + host + '/*'
    for filename in glob.glob(pattern):
        if os.path.isdir(filename):
            if dir:
                found = ps(host, dir + '/' + os.path.basename(filename)) or found
            else:
                found = ps(host, os.path.basename(filename)) or found
        elif filename[-8:8] != '.history':
            found = True
            expid = os.path.basename(filename)
            if dir:
                expid = dir + '/' + expid
            pids = []
            f = open(filename,'r')
            try:
                pid = int(f.readline())
            except:
                continue
            cmdline = f.readline()
            f.close()
            if HOST == host:
                pids.append( pid )
                pidstring = green(str(pid))
                #sanity check, check if pid really still exists:
                if not os.path.exists('/proc/' + str(pid)):
                   os.unlink(filename)
                   continue
            else:
                pidstring = magenta(str(pid))
            out +=  "%-33s %-22s %-6s\n  --> %s\n" % (bold(expid), host,pidstring, blue(cmdline.strip()))
    
    if HOST == host and found and pids:
        print "---"
        print "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"
        os.system("ps uh " + " ".join([ str(p) for p in pids ]))
        print "---"

    if out: print out
    return found

def start(id, cmdline):
    global PROCDIR, USER, HOST, EXPLOGDIR
    try:
        os.mkdir(PROCDIR + '/' + HOST)
    except:
        pass

    HISTORYFILE = PROCDIR + '/' + datetime.datetime.now().strftime("%Y%m") + '.history'

    dir = os.path.dirname(id)
    base_id = os.path.basename(id)


    
    
    
    
    try:
        os.makedirs(PROCDIR + '/' + HOST + '/' + dir)
    except OSError:
        pass
    try:
        os.makedirs(EXPLOGDIR + '/' + dir)
    except OSError:
        pass
        
    if os.path.exists(EXPLOGDIR + '/' + id + '.failed'):
        os.unlink(EXPLOGDIR + '/' + id + '.failed')
        
    now = datetime.datetime.now()
    starttime =  now.strftime("%Y-%m-%d %a %H:%M:%S")
    log = open(EXPLOGDIR + '/' + dir + '/'+ base_id + '.log','w')
    log.write("#COMMAND:  " + cmdline + '\n')
    log.write("#CWD:  " + os.getcwd() + '\n')
    log.write("#USER:     " + USER + '\n')
    log.write("#HOST:     " + HOST + '\n')
    log.write("#START:    " + starttime + '\n')
    errlog = open(EXPLOGDIR + '/' + dir + '/'+ base_id + '.err','w')
    errlog.write("#COMMAND:  " + cmdline + '\n')
    errlog.write("#CWD:  " + os.getcwd() + '\n')
    errlog.write("#USER:     " + USER + '\n')
    errlog.write("#HOST:     " + HOST + '\n')
    errlog.write("#START:    " + starttime + '\n')
    reslog = open(EXPLOGDIR + '/' + dir + '/'+ base_id + '.res','w')
    reslog.write("#COMMAND:  " + cmdline + '\n')
    reslog.write("#CWD:  " + os.getcwd() + '\n')
    reslog.write("#USER:     " + USER + '\n')
    reslog.write("#HOST:     " + HOST + '\n')
    reslog.write("#START:    " + starttime + '\n')
    reslog.close()



    process = subprocess.Popen(cmdline, shell=True,stdout=log,stderr=errlog)

    errlog.write("#PID:     " + str(process.pid) + '\n')

    os.system('echo -en "' + now.strftime("%Y-%m-%d %H:%M:%S %a ") + ' 0:00:00 " >> ' + EXPLOGDIR + '/' + dir + '/' + base_id + '.res')
    os.system("ps uh " + str(process.pid) + ' >> ' + EXPLOGDIR + '/' + dir + '/' + base_id + '.res')

    #write process file
    f = open(PROCDIR + '/' + HOST + '/' + dir + '/' + base_id ,'w')
    f.write(str(process.pid)+"\n")
    f.write(cmdline+"\n")
    f.close()

    #write history file
    f = open(HISTORYFILE,'a')
    f.write(now.strftime("%Y%m%d %a %H:%M:%S") + ' ' + ' ' + USER + '@' + HOST + ' ' + id + ' $ ' + cmdline + '\n')
    f.close()
    

    return process


def wait(id, process):
    global MAILTO, HOST, DAILYMAILHOUR, POLLINTERVAL, RESINTERVAL

    begintime = datetime.datetime.now()

    #Now wait till process is done
    while True:
            process.poll()
            if process.returncode == 0:
                errors = False
                break
            elif process.returncode > 0:
                errorcode = process.returncode
                errors = True                
                break
            time.sleep(POLLINTERVAL)
            now = datetime.datetime.now()
            duration = now - begintime
            if duration.seconds % RESINTERVAL == 0: #every ten minutes
                #write resource
                os.system('echo -en "' + now.strftime("%Y-%m-%d %H:%M:%S %a ") + ' ' + str(duration) + ' " >> ' + EXPLOGDIR + '/' + id + '.res')
                os.system("ps uh " + str(process.pid) + ' >> ' + EXPLOGDIR + '/' + id + '.res')
            if now.hour == DAILYMAILHOUR and not mailed:                
                mailed = True
                errlogfile =  EXPLOGDIR + '/' + id + '.err'
                logfile =  EXPLOGDIR + '/' + id + '.log'
                reslogfile =  EXPLOGDIR + '/' + id + '.res'
                os.system('tail -n 25 ' + errlogfile + " " + logfile + " " + reslogfile + " | mail -s \"Daily process report for " + id + " on " + HOST + " (" +str(duration.days) + "d)\"" + MAILTO)
            elif now.hour < DAILYMAILHOUR:
                mailed = False                        

    del process


    endtime = datetime.datetime.now()
    duration = endtime - begintime
    mail = True

    #delete process file
    try:
        os.unlink(PROCDIR + '/' + HOST + '/' + id )
    except:
        print >> sys.stderr,"ERROR REMOVING PROCESS FILE!"
        pass

    #mail = (duration > 60) #we won't mail if we finish in less than a minute
    logfile = EXPLOGDIR + '/' + id + '.log'
    errlogfile = EXPLOGDIR + '/' + id + '.err'    
    reslogfile = EXPLOGDIR + '/' + id + '.res'
    f = open(logfile,'a')
    f.write("#END:      " + endtime.strftime("%a %Y-%m-%d %H:%M:%S") + '\n')
    f.write("#DURATION: " + str(duration) + '\n')
    f.close()
    f = open(errlogfile,'a')
    f.write("#END:      " + endtime.strftime("%a %Y-%m-%d %H:%M:%S") + '\n')
    if errors:
        f.write("#ERRORCODE: " + str(errorcode) + "\n")
    f.write("#DURATION: " + str(duration) + '\n')
    f.close()
    

    if errors:
        printfile = errlogfile
        title = "Experiment " + id + " on " + HOST + " finished with errors (in " + str(duration).split('.')[0] + ')'
        
        f = open(EXPLOGDIR + '/' + id + '.failed','w')
        f.write(str(errorcode))
        f.close()
    else:
        printfile = logfile
        title = "Experiment " + id + " on " + HOST + " finished succesfully (in " + str(duration).split('.')[0] + ')'

    print title
    print "--------------------------------------------------------------"
    print "Start:      " + begintime.strftime("%a %Y-%m%-d %H:%M:%S")
    print "End:        " + endtime.strftime("%a %Y-%m-%d %H:%M:%S")
    print "Duration:   " + str(duration)
    print
    os.system('cat ' + printfile) #to stdout
    if mail:
        os.system('tail -n 100 ' + errlogfile + " " + logfile + " " + reslogfile + " | mail -s \""+title+"\" " + MAILTO)



if len(sys.argv) < 2:
    usage()
else:
    command = sys.argv[1]
    if command == 'start':
        id = sys.argv[2] if len(sys.argv) >= 4 else usage()
	if id[0:2] == "./": usage()
        ret = os.system('which ' + sys.argv[3])
        if ret != 0:
           print >>sys.stderr,"Command not found: ", sys.argv[3]
        else:
           pid = start(id, " ".join(sys.argv[3:]))
           if pid:
              wait(id, pid)
    elif command in ['stop', 'kill']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        #find the process
        procfilename = PROCDIR + '/' + HOST + '/' + id
        if os.path.exists(procfilename):            
            f = open(procfilename,'r')
            pid = int(f.readline())
            f.close()
            #kill the process
            if command == 'kill':
                ret = os.system('kill -s 11 ' + str(pid))
            else:
                ret = os.system('kill ' + str(pid))
            #delete process file
            if ret == 0:
                try:
                    os.unlink(procfilename)
                except:
                    print >> sys.stderr,"ERROR REMOVING PROCESS FILE!"
                    pass
        else:
            print >>sys.stderr, "No such experiment on the current host"
    elif command in ['stdout','log','out']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  EXPLOGDIR + id + '.log'
        if os.path.exists(logfile):
            os.system("cat " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"

    elif command in ['stderr', 'err', 'errlog','errors']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  EXPLOGDIR + id + '.err'
        if os.path.exists(logfile):
            os.system("cat " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"
    elif command in ['res', 'reslog','resources']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  EXPLOGDIR + id + '.res'
        if os.path.exists(logfile):
            os.system("cat " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"            
    elif command == 'auditlog':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  EXPLOGDIR + id + '.log'
        if os.path.exists(logfile):
            os.system("tail -f " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"        
    elif command == 'auditerr':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        errfile =  EXPLOGDIR + id + '.err'
        if os.path.exists(errfile):
            os.system("tail -f " + errfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"
    elif command == 'auditres':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        resfile =  EXPLOGDIR + id + '.res'
        if os.path.exists(resfile):
            os.system("tail -f " + resfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"            
    elif command == 'audit':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  EXPLOGDIR + id + '.log'
        errfile =  EXPLOGDIR + id + '.err'
        resfile =  EXPLOGDIR + id + '.res'
        if os.path.exists(logfile):
            os.system("tail -f " + resfile + ' ' + logfile + ' ' + errfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"
    elif command in ['mailstat','mail','mailstatus']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        if os.path.exists(logfile):
            errlogfile =  EXPLOGDIR + '/' + id + '.err'
            logfile =  EXPLOGDIR + '/' + id + '.log'
            reslogfile =  EXPLOGDIR + '/' + id + '.res'
            days = round(duration / float(3600*24))
            os.system('tail -n 100 ' + errlogfile + " " + logfile + " " + reslogfile + " | mail -s \"Requested process report for " + id + " on " + HOST + " (" + str(days) + "d)\"" + MAILTO)        
        else:
            print "No such experiment running on " + host
    elif command == 'ps' or command == 'ls':
        if len(sys.argv) >= 3:
            host = sys.argv[2]
            if os.path.isdir(PROCDIR+'/'+host):
                found = ps(host)
                if not found:
                    print "No experiments running on " + host
            else:
                print "No experiments running on " + host
        else:
            for hostdir in glob.glob(PROCDIR+'/*'):
                if os.path.isdir(hostdir) and hostdir[0] != '.':
                    host = os.path.basename(hostdir)
                    ps(host)
    elif command == 'history':
        filters = []
        if len(sys.argv) >= 3:
            filters = sys.argv[2:]
                    
            
        for historyfile in sorted(glob.glob(PROCDIR+'/*.history')): 
            match = True
            for filter in filters:
                if len(filter) == 6 and filter.isdigit():
                    if historyfile[-8:8] != filter:
                        match = False
                        break
            if not match:
                continue
                        
            output = []
            prevcmdline = ""
            f = open(historyfile)
            for line in f:
                if not filters:
                    match = True
                else:
                    match = False
                    for filter in filters:
                        if not (len(filter) == 6 and filter.isdigit()):
                            if line.find(filter) != -1:
                                match = True
                                break
                if match:
                    fields = line.split(' ',7)
                    date,weekday, time,empty, userhost, id,prompt, cmdline = fields
                    
                    if os.path.exists(PROCDIR + '/' + userhost.split('@')[1] + '/' + id):
                        if userhost.split('@')[1] == HOST:
                            userhost = green(userhost)                        
                        else:
                            userhost = magenta(userhost)
                        prompt =  bold(yellow('RUNNING $'))                                                    
                    elif userhost.split('@')[1] == HOST:
                        userhost = green(userhost)                        
                        if os.path.exists(EXPLOGDIR + id + '.failed'):
                            prompt =  bold(red('FAILED $'))                                             
                        elif os.path.exists(EXPLOGDIR + id + '.log') and os.path.exists(EXPLOGDIR + id + '.err'):
                            #catch very common errors from err output (backward compatibility with old exp tools):                            
                            ferr = open(EXPLOGDIR + id + '.err','r')
                            firstline = ferr.read(15)
                            failed = (firstline[0:9] != "#COMMAND:")                                            
                            if not failed:
                                lastline = tail(EXPLOGDIR + id + '.err', ferr)
                                failed = (lastline[:10] != "#DURATION:")
                            ferr.close()                            
                            if failed:
                                prompt =  bold(red('FAILED $'))                                                                       
                            else:
                                prompt = bold(green('SUCCESS $'))                            
                        else:
                            prompt = bold(red('MISSING $'))
                    else:
                        userhost = magenta(userhost)
                        prompt = bold(magenta(prompt))    
                    
                    out = yellow(date[0:4] + '-' + date[4:6] + '-' + date[6:8] + ' ' + weekday + ' ' + time) + ' ' + userhost +' ' +bold(id) + ' ' + prompt +' ' +cmdline
                    if cmdline == prevcmdline:
                        #duplicate, replace:
                        output[-1] = out
                    else:
                        output.append(out)
                        prevcmdline = cmdline	   
            f.close()
            print "\n".join(output)                        
    else:
        print >>sys.stderr,"Unknown command: " + command
        usage()



