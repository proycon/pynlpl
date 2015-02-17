#!/bin/bash


TESTDIR=`dirname $0`
cd $TESTDIR

GOOD=1

echo "Testing CGN">&2
python cgn.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing datatypes">&2
python datatypes.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi


echo "Testing evaluation">&2
python evaluation.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi


echo "Testing search">&2
python search.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing textprocessors">&2
python textprocessors.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi


echo "Testing statistics">&2
python statistics.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi


echo "Testing formats">&2
python formats.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing folia">&2
python folia.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

echo "Testing FQL">&2
python fql.py
if [ $? -ne 0 ]; then
    echo "Test failed!!!" >&2
    GOOD=0
fi

if [ $GOOD -eq 1 ]; then
    echo "Done, all tests passed!" >&2
    exit 0
else
    echo "TESTS FAILED!!!!" >&2
    exit 1
fi


