#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division, absolute_import

from pynlpl.formats import folia, fql, cql
import time
import sys
import os
import glob
try:
    from pympler import asizeof
except ImportError:
    print("An extra dependency called pympler is required: install using pip install pympler (or other means)",file=sys.stderr)
    raise

repetitions = 0

def timeit(f):
    def f_timer(*args, **kwargs):
        if 'filename' in kwargs:
            label = "on file " + kwargs['filename']
        elif 'dirname' in kwargs:
            label = "on directory " + kwargs['dirname']
        elif 'doc' in kwargs:
            label = "on document " + kwargs['doc'].id
        else:
            label = ""
        print(f.__name__ + " -- " + f.__doc__  + " -- " + label + " ...", end="")
        times = []
        for i in range(0, repetitions):
            start = time.time()
            try:
                result = f(*args, **kwargs)
            except Exception as e:
                print(" -- ERROR! -- ", e)
                return None
            times.append(time.time() - start)
        if times:
            d =  round(sum(times)  / len(times),4)
            print('took ' + str(d) + 's (averaged over ' + str(len(times)) + ' runs)')
        else:
            d = 0
        return result
    return f_timer


@timeit
def loadfile(**kwargs):
    """Loading file"""
    doc = folia.Document(file=kwargs['filename'],bypassleak=False)


@timeit
def savefile(**kwargs): #careful with SSDs
    """Saving file"""
    kwargs['doc'].save("/tmp/test.xml")

@timeit
def xml(**kwargs):
    """XML serialisation"""
    kwargs['doc'].xml()


@timeit
def json(**kwargs):
    """JSON serialisation"""
    kwargs['doc'].json()

@timeit
def text(**kwargs):
    """text serialisation"""
    kwargs['doc'].text()

@timeit
def countwords(**kwargs):
    """Counting words"""
    kwargs['doc'].count(folia.Word,None, True,[folia.AbstractAnnotationLayer])

@timeit
def selectwords(**kwargs):
    """Selecting words"""
    for word in kwargs['doc'].words():
        pass


@timeit
def selectwordsfql(**kwargs):
    """Selecting words using FQL"""
    query = fql.Query("SELECT w")
    for word in query(kwargs['doc']):
        pass

@timeit
def selectwordsfqlforp(**kwargs):
    """Selecting words in paragraphs using FQL"""
    query = fql.Query("SELECT w FOR p")
    for word in query(kwargs['doc']):
        pass

@timeit
def selectwordsfqlxml(**kwargs):
    """Selecting words using FQL (XML output)"""
    query = fql.Query("SELECT w FORMAT xml")
    for wordxml in query(kwargs['doc']):
        pass

@timeit
def selectwordsfqlwhere(**kwargs):
    """Selecting words using FQL (with WHERE clause)"""
    query = fql.Query("SELECT w WHERE text != \"blah\"")
    for word in query(kwargs['doc']):
        pass

@timeit
def editwordsfql(**kwargs):
    """Editing the text of  words using FQL (with WHERE clause)"""
    query = fql.Query("EDIT w WITH text \"blah\"")
    for word in query(kwargs['doc']):
        pass

@timeit
def nextwords(**kwargs):
    """Find neighbour of each word"""
    for word in kwargs['doc'].words():
        word.next()

@timeit
def addelement(**kwargs):
    """Adding a simple annotation (desc) to each word"""
    for word in kwargs['doc'].words():
        try:
            word.append(folia.Description, value="test")
        except folia.DuplicateAnnotationError:
            pass


@timeit
def ancestors(**kwargs):
    """Iterating over the ancestors of each word"""
    for word in kwargs['doc'].words():
        for ancestor in word.ancestors():
            pass

@timeit
def readerwords(**kwargs):
    """Iterating over words using Reader"""
    reader = folia.Reader(kwargs['filename'], folia.Word)
    for word in reader:
        pass

def main():
    global repetitions, target
    files = []
    try:
        begin = 1
        if os.path.exists(sys.argv[1]):
            begin = 1
            selectedtests = "all"
            repetitions = 1
        else:
            selectedtests = sys.argv[1].split(',')
            if os.path.exists(sys.argv[2]):
                repetitions = 1
                begin = 2
            else:
                repetitions = int(sys.argv[2])
                begin = 3
        filesordirs = sys.argv[begin:]
    except:
        print("Syntax: folia_benchmark [testfunctions [repetitions]] files-or-directories+",file=sys.stderr)
        print(" testfunctions is a comma separated list of function names, or the special keyword 'all'", file=sys.stderr)
        print(" directories are recursively searched for files with the extension folia.xml, +gz and +bz2 is supported too.", file=sys.stderr)
        sys.exit(2)


    for fd in filesordirs:
        if not os.path.exists(fd):
            raise Exception("No such file or directory" + fd)
        if os.path.isfile(fd):
            files.append(fd)
        elif os.path.isdir(fd):
            dirs = [fd]
            while dirs:
                dir = dirs.pop(0)
                for filename in glob.glob(dir + "/*"):
                    if os.path.isdir(filename):
                        dirs.append(filename)
                    elif filename.endswith('.folia.xml') or filename.endswith('.folia.xml.gz') or filename.endswith('.folia.xml.bz2'):
                        files.append(filename)


    for f in ('loadfile','loadfileleakbypass','readerwords'):
        if f in selectedtests or 'all' in selectedtests:
            for filename in files:
                globals()[f](filename=filename)


    for f in ('xml','text','json','countwords','selectwords','nextwords','ancestors','selectwordsfql','selectwordsfqlforp','selectwordsfqlxml','selectwordsfqlwhere','editwordsfql', 'addelement' ):
        if f in selectedtests or 'all' in selectedtests:
            for filename in files:
                doc = folia.Document(file=filename)
                globals()[f](doc=doc)

    for f in ('memtest',):
        if f in selectedtests or 'all' in selectedtests:
            for filename in files:
                doc = folia.Document(file=filename)
                print("memtest -- Memory test on document " + filename + " -- memory consumption estimated at " + str(round(asizeof.asizeof(doc) / 1024 / 1024,2)) + " MB" + " (filesize " + str(round(os.path.getsize(filename)/1024/1024,2)) + " MB)")



if __name__ == '__main__':
    main()
