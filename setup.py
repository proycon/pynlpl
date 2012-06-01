#! /usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
from setuptools import setup, find_packages

os.chdir(os.path.dirname(sys.argv[0]))
if not os.path.exists('pynlpl') and not os.path.exists('.readysetup'):
    print >>sys.stderr, "Running setup for first time, preparing source tree"
    os.mkdir('pynlpl')
    os.system('mv * pynlpl/ 2> /dev/null')
    os.system('ln -s pynlpl/README; ln -s pynlpl/docs')
    open('.readysetup','w')
elif not os.path.exists('.readysetup'):
    print >>sys.stderr, "Not ready for setup. Please obtain sources anew."
    sys.exit(2)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "PyNLPl",
    version = "0.5",
    author = "Maarten van Gompel",
    author_email = "proycon@anaproy.nl",
    description = ("PyNLPl, pronounced as 'pineapple', is a Python library for Natural Language Processing. It contains various modules useful for common, and less common, NLP tasks. PyNLPl can be used for example the computation of n-grams, frequency lists and distributions, language models. There are also more complex data types, such as Priority Queues, and search algorithms, such as Beam Search."),
    license = "GPL",
    keywords = "nlp computational_linguistics search ngrams language_models linguistics toolkit",
    url = "https://github.com/proycon/pynlpl",
    packages=find_packages('pynlpl'),
    long_description=read('README'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Text Processing :: Linguistic",
        "Programming Language :: Python :: 2.6",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    #include_package_data=True,
    #package_data = {'': ['*.wsgi','*.js','*.xsl','*.gif','*.png','*.xml','*.html','*.jpg','*.svg','*.rng'] },
    install_requires=['lxml >= 2.2']
)
