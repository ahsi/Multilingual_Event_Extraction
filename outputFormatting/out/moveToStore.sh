#!/bin/bash
./cleanStore.sh

cp linked_arguments/* arguments/.

cd store

cp -r ../arguments/ .
cp -r ../linking/ .
cp -r ../corpusLinking/ .
cp -r ../nuggets/ .

cd ../
for file in arguments/*; do rm "$file" ; done
for file in linking/*; do rm "$file" ; done
for file in nuggets/*; do rm "$file" ; done
for file in linked_arguments/*; do rm "$file" ; done
rm corpusLinking/*
