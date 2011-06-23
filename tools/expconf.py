import os
#Configuration is specific to ILK servers

HOST = os.uname()[1]
USER = os.getenv("USER")

MAILTO='proycon@anaproy.nl'
HOMEDIR = os.getenv("HOME")
PROCDIR = HOMEDIR + '/.expproc'
EXPLOGDIR = '/exp/' + USER + '/explogs/'
POLLINTERVAL = 30 #poll every 30 seconds
RESINTERVAL = 600 #every 10 minutes (update resource logs)
MAILINTERVAL = 6 * 3600 #every 6 hours


VERSION_AUDIT = ['frog -v','timbl -v','ucto -v', 'svn info /exp/mvgompel/local/pynlpl', 'svn info /exp/mvgompel/local/pbmbmt'] 
