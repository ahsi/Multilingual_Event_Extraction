#!/bin/sh

if [ "$#" -ne 1 ]; then
	echo "Illegal number of parameters.  Expect list of files to read (with absolute filepaths)."
	exit 1
fi

# store processed documents in tmp/
rm CoreNLP_scripts/tmp_Eng/*
./CoreNLP_scripts/runCoreNLP_Eng.sh $1

# readCoreNLP
python readCoreNLP/getRootnames.py $1 tmp.list
cd readCoreNLP/
rm tmp_formatted/*
./convertCoreNLPFormat.sh ../tmp.list ../CoreNLP_scripts/tmp_Eng/ tmp_formatted/
cd ../

# createSetFiles
find readCoreNLP/tmp_formatted/ -name "*.mergedAnnotations" > mergedFilenames.tmp
rm createSetFiles/*.tmp
rm createSetFiles/*.parsing
python createSetFiles/writeDataFromFiles.py mergedFilenames.tmp createSetFiles/setFile.noEntities.tmp
rm mergedFilenames.tmp

# entity extraction
cd entityExtraction/
python convertTestSet.py ../createSetFiles/setFile.noEntities.tmp ../createSetFiles/setFile.noEntities.tmp.parsing entityTestSet.tmp
./runEntities.sh entityTestSet.tmp
cd ../
find entityExtraction/code/tmp_formatted/ -name "*.mergedAnnotations" > mergedFilenames.tmp
python createSetFiles/writeDataFromFiles.py mergedFilenames.tmp createSetFiles/setFile.withEntities.tmp
rm mergedFilenames.tmp
rm tmp.list

# predictions
cd ../all_predictions_4.0/
./runAll.sh ../preprocessing_2.0/createSetFiles/setFile.withEntities.tmp
cd ../preprocessing_2.0/

# outputFormatting
python ../outputFormatting/writeDocMap.py $1
cd ../outputFormatting/
./English_run.sh
cd ../preprocessing_2.0/

# clear the tmp folders

#rm CoreNLP_scripts/tmp_Eng/*
#rm createSetFiles/*.tmp
#rm createSetFiles/*.parsing
#rm entityExtraction/*.tmp
#rm entityExtraction/code/tmp_formatted/*
#rm readCoreNLP/tmp_formatted/*
#rm *.tmp

#rm ../all_predictions_4.0/output.*
#rm ../all_predictions_4.0/*.easyRead
#rm ../all_predictions_4.0/*.entityCoref
#rm ../all_predictions_4.0/currentPredictionsForTriggers/testSet.predictions
#rm ../all_predictions_4.0/currentPredictionsForArgs/testSet.predictions
#rm ../all_predictions_4.0/currentPredictionsForRealis/testSet.predictions
#rm ../all_predictions_4.0/code/test.*
#rm ../outputFormatting/formatTriggers/format_andrew_triggers/andrew.triggers.out
