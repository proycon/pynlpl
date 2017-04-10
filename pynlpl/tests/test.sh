#!/bin/bash

if [ ! -z "$1" ]; then
    PYTHON=$1
else
    PYTHON=python
fi

if [ ! -z "$2" ]; then
    TESTDIR="$2"
else
    TESTDIR=`dirname $0`
fi
cd $TESTDIR

GOOD=1

echo "Testing CGN">&2
$PYTHON cgn.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing datatypes">&2
$PYTHON datatypes.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi


echo "Testing evaluation">&2
$PYTHON evaluation.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi


echo "Testing search">&2
$PYTHON search.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing textprocessors">&2
$PYTHON textprocessors.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi


echo "Testing statistics">&2
$PYTHON statistics.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi


echo "Testing formats">&2
$PYTHON formats.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing folia">&2
$PYTHON folia.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing FQL">&2
$PYTHON fql.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing CQL">&2
$PYTHON cql.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

cd ..

if [ $GOOD -eq 1 ]; then
    echo "Done, all tests passed!" >&2
    exit 0
else
    echo "TESTS FAILED!!!!" >&2
    exit 1
fi



