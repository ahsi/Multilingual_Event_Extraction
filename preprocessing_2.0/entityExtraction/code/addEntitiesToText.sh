#!/bin/sh

# clean the directory first
rm tmp_formatted/*

while read -r line
do
	name=$line
	python ../../readCoreNLP/read_CoreNLP_XML.py ${2}${name}.out tmp.txt
	python addEntitiesToText.py unify/out_processed/${name} tmp.txt tmp_formatted/${name}.mergedAnnotations
	python ../../readCoreNLP/write_parsing_from_CoreNLP.py ${2}${name}.out tmp_formatted/${name}.parsingAnnotations 
done < ${1}
rm tmp.txt
