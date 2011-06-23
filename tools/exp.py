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

import expconf

HOST = os.uname()[1]
USER = os.getenv("USER")

if not os.path.isdir(expconf.PROCDIR):
    os.mkdir(expconf.PROCDIR)
if not os.path.isdir(expconf.EXPLOGDIR):
    os.mkdir(expconf.EXPLOGDIR)

def usage():
    print "Syntax: exp start    EXPERIMENT-ID [CWD] COMMAND"
    print "          - Start an experiment (in a specific working directory)"
    print "        exp stop     EXPERIMENT-ID"
    print "          - Stop an experiment (gently)"
    print "        exp kill     EXPERIMENT-ID"
    print "          - Stop an experiment (forcibly)"
    print "        exp ps       [HOST]"
    print "          - View process list (optionally for only the given host)"
    print "        exp history  [YEARMONTH/FILTERKEYWORD]"
    print "          - View experiment history (optionally with filter keyword of time filter (YYYYMM))"
    print "        exp log      EXPERIMENT-ID"
    print "          - View standard output of experiment"
    print "        exp errlog   EXPERIMENT-ID"
    print "          - View error output of experiment"
    print "        exp reslog   EXPERIMENT-ID"
    print "          - View resource usage log of experiment (periodic ps output)"
    print "        exp versionlog   EXPERIMENT-ID"
    print "          - View version log of experiment"    
    print "        exp audit    EXPERIMENT-ID"
    print "          - Follow all output of a running experiment live"
    print "        exp auditlog EXPERIMENT-ID"
    print "        exp auditerr EXPERIMENT-ID"
    print "        exp auditres EXPERIMENT-ID"
    print "        exp mailstat EXPERIMENT-ID"
    print "          - Force a report to be mailed about this experiment"
    #print "        exp initbatch BATCH-ID [MODE]"
    #print "          - initialise a (manual) batch experiment"
    #print "        exp add BATCH-ID EXPERIMENT-ID COMMAND"
    #print "          - Add an experiment to the batch's queue"
    #print "        exp startbatch BATCH-ID PROCESSES [COMMAND]"
    #print "          - start the batch. The batch must have been previously initialised and filled (with exp add). "
    #print "            Or command is specified that contains variables that will be auto-expanded"  
    #print "            Variable syntax:"
    #print "                {1,2,3}  expands to 1 on first run, 2 on second,  3 on third" 
    #print '                {"foo","bar"}  expands to "foo" on fist run, "bar" on second'
    #print "                {1-6}    range (1,2,3,4,5,6)"
    #print "                {2-6:2}  range with step size (2,4,6)"
    #print "                {{1}}    Expands to the same value as the first variable (1 can be any number)"

    

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
        pattern = expconf.PROCDIR + '/' + host + '/' + dir + '/*'
    else:
        pattern = expconf.PROCDIR + '/' + host + '/*'
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
    global USER, HOST
    try:
        os.mkdir(expconf.PROCDIR + '/' + HOST)
    except:
        pass

    HISTORYFILE = expconf.PROCDIR + '/' + datetime.datetime.now().strftime("%Y%m") + '.history'

    dir = os.path.dirname(id)
    base_id = os.path.basename(id)
    
    try:
        os.makedirs(expconf.PROCDIR + '/' + HOST + '/' + dir)
    except OSError:
        pass
    try:
        os.makedirs(expconf.EXPLOGDIR + '/' + dir)
    except OSError:
        pass
        
    if os.path.exists(expconf.EXPLOGDIR + '/' + id + '.failed'):
        os.unlink(expconf.EXPLOGDIR + '/' + id + '.failed')
        

    versionlog = expconf.EXPLOGDIR + '/' + dir + '/'+ base_id + '.versions'
    f = open(versionlog,'w')
    f.write("VERSION LOG\n-----------\n")
    f.close()
    
    for command in expconf.VERSION_AUDIT:
        os.system("echo \"$ " + command + "\" >> " + versionlog)
        os.system(command + ' >> ' + versionlog + ' 2>&1')                
        
    now = datetime.datetime.now()
    starttime =  now.strftime("%Y-%m-%d %a %H:%M:%S")
    log = open(expconf.EXPLOGDIR + '/' + dir + '/'+ base_id + '.log','w')
    log.write("#ID:  " + id + '\n')
    log.write("#COMMAND:  " + " ".join(cmdline) + '\n')
    log.write("#CWD:  " + os.getcwd() + '\n')
    log.write("#USER:     " + USER + '\n')
    log.write("#HOST:     " + HOST + '\n')
    log.write("#START:    " + starttime + '\n')
    head = open(expconf.EXPLOGDIR + '/' + dir + '/'+ base_id + '.head','w')
    head.write(HOST + "$ exp start " + id + ' ' + os.getcwd() + ' ' + " ".join(cmdline) + '\n')   
    head.write("*ID*       " + id + '\n')
    head.write("*COMMAND*  " + " ".join(cmdline) + '\n')
    head.write("*CWD*      " + os.getcwd() + '\n')
    head.write("*USER*     " + USER + '\n')
    head.write("*HOST*     " + HOST + '\n')
    head.write("*START*    " + starttime + '\n')   
    head.close() 
    errlog = open(expconf.EXPLOGDIR + '/' + dir + '/'+ base_id + '.err','w')
    errlog.write("#ID:  " + id + '\n')
    errlog.write("#COMMAND:  " + " ".join(cmdline) + '\n')
    errlog.write("#CWD:  " + os.getcwd() + '\n')
    errlog.write("#USER:     " + USER + '\n')
    errlog.write("#HOST:     " + HOST + '\n')
    errlog.write("#START:    " + starttime + '\n')
    reslog = open(expconf.EXPLOGDIR + '/' + dir + '/'+ base_id + '.res','w')
    reslog.write("#ID:  " + id + '\n')
    reslog.write("#COMMAND:  " + " ".join(cmdline) + '\n')
    reslog.write("#CWD:  " + os.getcwd() + '\n')
    reslog.write("#USER:     " + USER + '\n')
    reslog.write("#HOST:     " + HOST + '\n')
    reslog.write("#START:    " + starttime + '\n')
    reslog.close()



    process = subprocess.Popen(cmdline, shell=False,stdout=log,stderr=errlog)

    errlog.write("#PID:     " + str(process.pid) + '\n')

    os.system('echo -en "' + now.strftime("%Y-%m-%d %H:%M:%S %a ") + ' 0:00:00 " >> ' + expconf.EXPLOGDIR + '/' + dir + '/' + base_id + '.res')
    os.system("ps uh " + str(process.pid) + ' >> ' + expconf.EXPLOGDIR + '/' + dir + '/' + base_id + '.res')

    #write process file
    f = open(expconf.PROCDIR + '/' + HOST + '/' + dir + '/' + base_id ,'w')
    f.write(str(process.pid)+"\n")
    f.write(" ".join(cmdline)+"\n")
    f.close()

    #write history file
    f = open(HISTORYFILE,'a')
    f.write(now.strftime("%Y%m%d %a %H:%M:%S") + ' ' + ' ' + USER + '@' + HOST + ' ' + id + ' ' + os.getcwd() + '$ ' + " ".join(cmdline) + '\n')
    f.close()
    

    return process


def wait(id, process):
    global HOST, USER

    begintime = datetime.datetime.now()
    lastrestime = begintime
    lastmailtime = begintime
    
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
            time.sleep(expconf.POLLINTERVAL)
            now = datetime.datetime.now()
            duration = now - begintime
            if (now - lastrestime).seconds >= expconf.RESINTERVAL: 
                #write resource
                os.system('echo -en "' + now.strftime("%Y-%m-%d %H:%M:%S %a ") + ' ' + str(duration) + ' " >> ' + expconf.EXPLOGDIR + '/' + id + '.res')
                os.system("ps uh " + str(process.pid) + ' >> ' + expconf.EXPLOGDIR + '/' + id + '.res')
                lastrestime = now
            if (now - lastmailtime).seconds >= expconf.MAILINTERVAL:                
                headfile = expconf.EXPLOGDIR + '/' + id + '.head'
                errlogfile = expconf.EXPLOGDIR + '/' + id + '.err'
                logfile = expconf.EXPLOGDIR + '/' + id + '.log'
                reslogfile = expconf.EXPLOGDIR + '/' + id + '.res'
                lastmailtime = now                
                os.system('tail -n 25 ' + headfile + ' ' + errlogfile + " " + logfile + " " + reslogfile + " | mail -s \"Daily process report for " + id + " on " + HOST + " (" +str(duration.days) + "d)\" " + expconf.MAILTO)
        

    del process


    endtime = datetime.datetime.now()
    duration = endtime - begintime

    #delete process file
    try:
        os.unlink(expconf.PROCDIR + '/' + HOST + '/' + id )
    except:
        print >> sys.stderr,"ERROR REMOVING PROCESS FILE!"
        pass

    #mail = (duration > 60) #we won't mail if we finish in less than a minute
    headfile = expconf.EXPLOGDIR + '/' + id + '.head'
    logfile = expconf.EXPLOGDIR + '/' + id + '.log'
    errlogfile = expconf.EXPLOGDIR + '/' + id + '.err'    
    reslogfile = expconf.EXPLOGDIR + '/' + id + '.res'
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
        
        f = open(expconf.EXPLOGDIR + '/' + id + '.failed','w')
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
    os.system('tail -n 100 ' + headfile + ' ' +  errlogfile + " " + logfile + " " + reslogfile + " | mail -s \""+title+"\" " + expconf.MAILTO)



if len(sys.argv) < 2:
    usage()
else:
    command = sys.argv[1]
    if command == 'start':
        id = sys.argv[2] if len(sys.argv) >= 4 else usage()
        if id[0:2] == "./": usage()
    
        if os.path.isdir(sys.argv[3]):
            cwd = sys.argv[3]
            cmd = sys.argv[4]
            args = sys.argv[5:]
            os.chdir(cwd)
        else:
            cwd = None
            cmd = sys.argv[3]
            args = sys.argv[5:]
    
        ret = os.system('which ' + cmd)
        if ret != 0:
           print >>sys.stderr,"Command not found: ", cmd
        else:
           args = [cmd] + args
           pid = start(id, args)
           if pid:
              wait(id, pid)
    elif command in ['stop', 'kill']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        #find the process
        procfilename = expconf.PROCDIR + '/' + HOST + '/' + id
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
        logfile =  expconf.EXPLOGDIR + id + '.log'
        if os.path.exists(logfile):
            os.system("cat " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"

    elif command in ['stderr', 'err', 'errlog','errors']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  expconf.EXPLOGDIR + id + '.err'
        if os.path.exists(logfile):
            os.system("cat " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"
    elif command in ['versions', 'versionlog', 'vlog']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  expconf.EXPLOGDIR + id + '.versions'
        if os.path.exists(logfile):
            os.system("cat " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"            
    elif command in ['res', 'reslog','resources']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  expconf.EXPLOGDIR + id + '.res'
        if os.path.exists(logfile):
            os.system("cat " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"            
    elif command == 'auditlog':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  expconf.EXPLOGDIR + id + '.log'
        if os.path.exists(logfile):
            os.system("tail -f " + logfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"        
    elif command == 'auditerr':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        errfile =  expconf.EXPLOGDIR + id + '.err'
        if os.path.exists(errfile):
            os.system("tail -f " + errfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"
    elif command == 'auditres':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        resfile =  expconf.EXPLOGDIR + id + '.res'
        if os.path.exists(resfile):
            os.system("tail -f " + resfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"            
    elif command == 'audit':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        logfile =  expconf.EXPLOGDIR + id + '.log'
        errfile =  expconf.EXPLOGDIR + id + '.err'
        resfile =  expconf.EXPLOGDIR + id + '.res'
        if os.path.exists(logfile):
            os.system("tail -f " + resfile + ' ' + logfile + ' ' + errfile)
        else:
            print >>sys.stderr, "No such experiment on the current host"
    elif command in ['mailstat','mail','mailstatus']:
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        errlogfile =  expconf.EXPLOGDIR + '/' + id + '.err'
        logfile =  expconf.EXPLOGDIR + '/' + id + '.log'
        reslogfile =  expconf.EXPLOGDIR + '/' + id + '.res'        
        if os.path.exists(logfile):
            os.system('tail -n 100 ' + errlogfile + " " + logfile + " " + reslogfile + " | mail -s \"Requested process report for " + id + " on " + HOST + "\" " + expconf.MAILTO)        
        else:
            print "No such experiment running on " + host
    elif command == 'ps' or command == 'ls':
        if len(sys.argv) >= 3:
            host = sys.argv[2]
            if os.path.isdir(expconf.PROCDIR+'/'+host):
                found = ps(host)
                if not found:
                    print "No experiments running on " + host
            else:
                print "No experiments running on " + host
        else:
            for hostdir in glob.glob(expconf.PROCDIR+'/*'):
                if os.path.isdir(hostdir) and hostdir[0] != '.':
                    host = os.path.basename(hostdir)
                    ps(host)
    elif command == 'history':
        filters = []
        if len(sys.argv) >= 3:
            filters = sys.argv[2:]
                    
            
        for historyfile in sorted(glob.glob(expconf.PROCDIR+'/*.history')): 
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
                    
                    if len(prompt) > 1:
                        workdir = prompt[:-1]
                        prompt = prompt[-1]
                    else:
                        workdir = '/path/unknown'
                                            
                    
                    if os.path.exists(expconf.PROCDIR + '/' + userhost.split('@')[1] + '/' + id):
                        if userhost.split('@')[1] == HOST:
                            userhost = green(userhost)                        
                        else:
                            userhost = magenta(userhost)
                        prompt =  bold(yellow('RUNNING')) + ' ' + workdir + bold(yellow('$'))                                                    
                    elif userhost.split('@')[1] == HOST:
                        userhost = green(userhost)                        
                        if os.path.exists(expconf.EXPLOGDIR + id + '.failed'):
                            prompt =  bold(red('FAILED')) + ' ' + workdir + bold(red('$'))                                             
                        elif os.path.exists(expconf.EXPLOGDIR + id + '.log') and os.path.exists(expconf.EXPLOGDIR + id + '.err'):
                            #catch very common errors from err output (backward compatibility with old exp tools):                            
                            ferr = open(expconf.EXPLOGDIR + id + '.err','r')
                            firstline = ferr.read(15)
                            failed = (firstline[0:9] != "#COMMAND:") and (firstline[0:4] != "#ID:")                                           
                            if not failed:
                                lastline = tail(expconf.EXPLOGDIR + id + '.err', ferr)
                                failed = (lastline[:10] != "#DURATION:")
                            ferr.close()                            
                            if failed:
                                prompt =  bold(red('FAILED')) + ' ' + workdir + bold(red('$'))                                                                       
                            else:
                                prompt = bold(green('SUCCESS')) + ' ' + workdir + bold(green('$'))                            
                        else:
                            prompt = bold(red('MISSING')) + ' ' + workdir + bold(red('$'))
                    else:
                        userhost = magenta(userhost)
                        prompt = workdir + bold(magenta(prompt))    
                    
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



