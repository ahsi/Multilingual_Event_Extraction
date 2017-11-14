#!/bin/bash

echo "Start TRIGGERS"
./runTriggers.sh 1 $1
echo "START ARGUMENTS"
./runArguments.sh 1 $1
echo "Start REALIS"
./runRealis.sh 1 $1
