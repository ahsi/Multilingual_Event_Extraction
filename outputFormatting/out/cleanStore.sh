#!/bin/bash

# move to store and clean again
cd store
for file in arguments/*; do rm "$file" ; done
for file in linking/*; do rm "$file" ; done
for file in nuggets/*; do rm "$file" ; done
rm corpusLinking/*

# return to original directory
cd ../
