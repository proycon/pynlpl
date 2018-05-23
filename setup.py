#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function


import os
import sys
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

entry_points = {}
if sys.version > '3':
    entry_points = {    'console_scripts': [
            'pynlpl-computepmi = pynlpl.tools.computepmi:main',
            'pynlpl-sampler = pynlpl.tools.sampler:main',
            'pynlpl-makefreqlist = pynlpl.tools.freqlist:main',
        ]
    }


setup(
    name = "PyNLPl",
    version = "1.2.7", #edit version in __init__.py as well and ensure tests/folia.py FOLIARELEASE points to the right version and is not set to None!
    author = "Maarten van Gompel",
    author_email = "proycon@anaproy.nl",
    description = ("PyNLPl, pronounced as 'pineapple', is a Python library for Natural Language Processing. It contains various modules useful for common, and less common, NLP tasks. PyNLPl contains modules for basic tasks, clients for interfacting with server, and modules for parsing several file formats common in NLP, most notably FoLiA."),
    license = "GPL",
    keywords = "nlp computational_linguistics search ngrams language_models linguistics toolkit",
    url = "https://github.com/proycon/pynlpl",
    packages=['pynlpl','pynlpl.clients','pynlpl.lm','pynlpl.formats','pynlpl.mt','pynlpl.tools','pynlpl.tests'],
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
    include_package_data=True,
    package_data = {'pynlpl': ['tests/test.sh', 'tests/evaluation_timbl/*'] },
    install_requires=['lxml >= 2.2','httplib2 >= 0.6','rdflib'],
    entry_points = entry_points
)
