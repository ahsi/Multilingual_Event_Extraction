#!/bin/sh
if [ "$#" -ne 3 ]; then
	echo "Illegal number of parameters"
	echo "Use format: './convertCoreNLPFormat.sh [list_of_files] [path_to_files] [output_dir]"
	echo "-- list_of_files: text document containing filenames for documents"
	echo "-- path_to_files: path to the filenames contained in list_of_files"
	echo "-- output_dir: output directory"
	exit 1
fi

while read -r line
do
	name=$line
	python read_CoreNLP_XML.py	${2}${name}.out tmp.txt
	python convertCoreNLPFormat.py tmp.txt ${3}/${name}.mergedAnnotations
	python write_parsing_from_CoreNLP.py ${2}${name}.out ${3}/${name}.parsingAnnotations 
done < ${1}
rm tmp.txt
