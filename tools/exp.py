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

#Configuration is specific to ILK servers (TODO: make external configuration file)
MAILTO='proycon@anaproy.nl'
HOST = os.uname()[1]
USER = os.getenv("USER")
HOMEDIR = os.getenv("HOME")
PROCDIR = HOMEDIR + '/.expproc'
EXPLOGDIR = '/exp/' + USER + '/explogs/'

if not os.path.isdir(PROCDIR):
    os.mkdir(PROCDIR)
if not os.path.isdir(EXPLOGDIR):
    os.mkdir(EXPLOGDIR)

def usage():
    print "Syntax: exp start   EXPERIMENT-ID COMMAND"
    print "        exp stop    EXPERIMENT-ID"
    print "        exp stat    EXPERIMENT-ID"
    print "        exp log     EXPERIMENT-ID"
    print "        exp errlog  EXPERIMENT-ID"
    print "        exp history [YEARMONTH/FILTER]"
    print "        exp ps      [HOST]"
    sys.exit(2)


def ps(host, dir = ""):
    global HOST
    found = False
    if dir:
        pattern = PROCDIR + '/' + host + '/' + dir + '/*'
    else:
        pattern = PROCDIR + '/' + host + '/*'
    for filename in glob.glob(pattern):
        if os.path.isdir(filename):
            if dir:
                found = ps(host, dir + '/' + filename) or found
            else:
                found = ps(host, filename) or found
        else:
            found = True
            expid = os.path.basename(filename)
            if dir:
                expid = dir + '/' + expid
            pids = []
            f = open(filename,'r')
            pid = int(f.readline())
            pids.append(pid)
            cmdline = int(f.readline())
            f.close()
            print expid+"\t" + host + "\t" + str(pid) + "\t" + cmdline
     
    if HOST == host:
        os.system("ps u " + " ".join([ str(p) for p in pids ]))

    return found

def start(id, cmdline, dir = ""):
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

    starttime =  datetime.datetime.now().strftime("%Y%m%d %a %H:%M:%S")
    log = open(EXPLOGDIR + '/' + dir + '/'+ base_id + '.log','w')
    log.write("#COMMAND: " + cmdline + '\n')
    log.write("#USER:    " + USER + '\n')
    log.write("#HOST:    " + HOST + '\n')
    log.write("#START:   " + starttime + '\n')
    errlog = open(EXPLOGDIR + '/' + dir + '/'+ base_id + '.err','w')
    errlog.write("#COMMAND: " + cmdline + '\n')
    errlog.write("#USER:    " + USER + '\n')
    errlog.write("#HOST:    " + HOST + '\n')
    errlog.write("#START:   " + starttime + '\n')


    process = subprocess.Popen(cmdline, shell=True,stdout=log,stderr=errlog)

    errlog.write("#PID:     " + str(process.pid) + '\n')

    #write process file
    f = open(PROCDIR + '/' + HOST + '/' + dir + '/' + base_id ,'w')
    f.write(str(process.pid)+"\n")
    f.write(cmdline+"\n")
    f.close()

    #write history file
    f = open(HISTORYFILE,'a')
    f.write(datetime.datetime.now().strftime("%Y%m%d %a %H:%M:%S") + ' ' + id  + ' ' + USER + '@' + HOST + ' $ ' + cmdline + '\n')
    f.close()

    return process


def wait(id, process):
    global MAILTO, HOST

    begintime = datetime.datetime.now()

    #Now wait till process is done
    while True:
            process.poll()
            if process.returncode == None:
                errors = False
                break
            elif process.returncode > 0:
                errors = True

    del process
    endtime = datetime.datetime.now()
    duration = endtime - begintime
    mail = (duration > 60) #we won't mail if we finish in less than a minute
    logfile = EXPLOGDIR + '/' + id + '.log'
    errlogfile = EXPLOGDIR + '/' + id + '.err'
    f = open(logfile,'a')
    f.write("#END:      " + endtime.strftime("%a %Y%m%d %H:%M:%S") + '\n')
    f.write("#DURATION: " + str(duration) + '\n')
    f.close()
    f = open(errlogfile,'a')
    f.write("#END:      " + endtime.strftime("%a %Y%m%d %H:%M:%S") + '\n')
    f.write("#DURATION: " + str(duration) + '\n')
    f.close()

    if errors:
        printfile = errlogfile
        title = "Experiment " + id + " on " + HOST + " finished with errors (in " + str(duration).split('.')[0] + ')'
    else:
        printfile = logfile
        title = "Experiment " + id + " on " + HOST + " finished succesfully (in " + str(duration).split('.')[0] + ')'

    print title
    print "Start: "      + begintime.strftime("%a %Y%m%d %H:%M:%S")
    print "End: "        + endtime.strftime("%a %Y%m%d %H:%M:%S")
    print "Duration: "   + str(duration)
    print
    os.system('tail -n 25 ' + printfile) #to stdout
    if mail:
        os.system('tail -n 25 ' + printfile + " | mail -s \""+title+"\" " + MAILTO)



if len(sys.argv) < 2:
    usage()
else:
    command = sys.argv[1]
    if command == 'start':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        wait(start(sys.argv[3:]))
    elif command == 'stop':
        id = sys.argv[2] if len(sys.argv) >= 3 else usage()
        #find the process
        procfilename = PROCDIR + '/' + HOST + '/' + id
        if os.path.exists(procfilename):            
            f = open(procfilename,'r')
            pid = int(f.readline())
            f.close()
            #kill the process
            os.kill(pid,11)
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
    elif command == 'ps' or command == 'ls':
        if len(sys.argv >= 3):
            host = sys.argv[2]
            if os.path.isdir(PROCDIR+'/'+host):
                found = ps(host)
                if not found:
                    print "No experiments running on " + host
            else:
                print "No experiments running on " + host
        else:
            for hostdir in glob.glob(PROCDIR+'/'):
                if os.path.isdir(hostdir):
                    host = os.path.basename(hostdir)
                    ps(host)
    elif command == 'history':
        filter = ''
        date = datetime.datetime.now().strftime("%Y%m")
        if len(sys.argv >= 3):
            filter = sys.argv[2]
            if len(filter) == 6 and filter.isdigit():
                date = filter
                filter = ''
        historyfile = PROCDIR + '/' + date + '.history'
        if os.path.exists(historyfile):
            if filter == '*':
                os.system("cat " + PROCDIR + '/*.history')
            elif filter:
                os.system("cat " + historyfile + " | grep " + filter)
            else:
                os.system("cat " + historyfile)
        else:
            print "No history evailable"
    else:
        print >>sys.stderr,"Unknown command: " + command
        usage()

    id = sys.argv[2]
    cmdline = sys.argv[2:]


