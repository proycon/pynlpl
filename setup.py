#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function


import os
import sys
from setuptools import setup, find_packages

if os.path.dirname(__file__) != "":
    os.chdir(os.path.dirname(__file__))
if not os.path.exists('pynlpl'):
    print("Preparing build",file=sys.stderr)
    if os.path.exists('build'):
        os.system('rm -Rf build')
    os.mkdir('build')
    os.chdir('build')
    if not os.path.exists('pynlpl'): os.mkdir('pynlpl')
    os.system('cp -Rpf ../* pynlpl/ 2> /dev/null')
    os.system('mv -f pynlpl/setup.py pynlpl/setup.cfg .')
    os.system('cp -f pynlpl/README.rst .')

    #Do not include unfininished WIP modules:
    os.system('rm -f pynlpl/formats/colibri.py pynlpl/formats/alpino.py pynlpl/foliaprocessing.py pynlpl/grammar.py')

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

entry_points = {}
if sys.version > '3':
    entry_points = {    'console_scripts': [
            'pynlpl-classencoder = pynlpl.tools.classencoder:main',
            'pynlpl-classdecoder = pynlpl.tools.classdecoder:main',
            'pynlpl-computepmi = pynlpl.tools.computepmi:main',
            'pynlpl-sampler = pynlpl.tools.sampler:main',
            'pynlpl-makefreqlist = pynlpl.tools.freqlist:main',
        ]
    }


setup(
    name = "PyNLPl",
    version = "0.7.6.8", #edit version in __init__.py as well!
    author = "Maarten van Gompel",
    author_email = "proycon@anaproy.nl",
    description = ("PyNLPl, pronounced as 'pineapple', is a Python library for Natural Language Processing. It contains various modules useful for common, and less common, NLP tasks. PyNLPl can be used for example the computation of n-grams, frequency lists and distributions, language models. There are also more complex data types, such as Priority Queues, and search algorithms, such as Beam Search."),
    license = "GPL",
    keywords = "nlp computational_linguistics search ngrams language_models linguistics toolkit",
    url = "https://github.com/proycon/pynlpl",
    packages=['pynlpl','pynlpl.clients','pynlpl.lm','pynlpl.formats','pynlpl.mt','pynlpl.tools'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Text Processing :: Linguistic",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    zip_safe=False,
    #include_package_data=True,
    #package_data = {'': ['*.wsgi','*.js','*.xsl','*.gif','*.png','*.xml','*.html','*.jpg','*.svg','*.rng'] },
    install_requires=['lxml >= 2.2','httplib2 >= 0.6','numpy'],
    entry_points = entry_points
)
