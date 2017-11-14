#!/bin/bash

echo "START ARGUMENTS"
./runArguments_providedTriggers.sh 1 $1
echo "Start REALIS"
./runRealis_providedTriggers.sh 1 $1
