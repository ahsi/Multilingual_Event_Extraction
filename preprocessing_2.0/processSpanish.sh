#!/bin/sh

if [ "$#" -ne 1 ]; then
	echo "Illegal number of parameters.  Expect list of files to read (with absolute filepaths)."
	exit 1
fi

# store processed documents in tmp/
rm CoreNLP_scripts/tmp_Span/*
./CoreNLP_scripts/runCoreNLP_Span.sh $1

# readCoreNLP
python readCoreNLP/getRootnames.py $1 tmp.spanish.list
cd readCoreNLP/
rm tmp_formatted_Span/*
./convertCoreNLPFormat.sh ../tmp.spanish.list ../CoreNLP_scripts/tmp_Span/ tmp_formatted_Span/
cd ../

# createSetFiles
find readCoreNLP/tmp_formatted_Span/ -name "*.mergedAnnotations" > mergedFilenames.tmp.Span
rm createSetFiles/*.tmp
rm createSetFiles/*.parsing
python createSetFiles/writeDataFromFiles.py mergedFilenames.tmp.Span createSetFiles/setFile.noEntities.tmp.Span
rm mergedFilenames.tmp.Span

# add dependency parsing via MaltParser
python MaltParser_scripts/convertToCoNLL.py createSetFiles/setFile.noEntities.tmp.Span MaltParser_scripts/Spanish.conll.tmp /home/andrew/DEFT_code_testing/dependencies/pos/es-cast3lb.map
cp /home/andrew/DEFT_code_testing/dependencies/models/maltparser/UD.Spanish.model.mco UD.Spanish.model.mco.tmp
mv UD.Spanish.model.mco.tmp UD.Spanish.model.mco
java -jar /home/andrew/NLP_tools/MaltParser/maltparser-1.9.0/maltparser-1.9.0.jar -c UD.Spanish.model.mco -i MaltParser_scripts/Spanish.conll.tmp -o MaltParser_scripts/Spanish.conll.tmp.output -m parse
rm UD.Spanish.model.mco
python MaltParser_scripts/convertToParsingFile.py MaltParser_scripts/Spanish.conll.tmp.output createSetFiles/setFile.noEntities.tmp.Span.parsing

# entity extraction
cd entityExtraction/
python convertTestSet.py ../createSetFiles/setFile.noEntities.tmp.Span ../createSetFiles/setFile.noEntities.tmp.Span.parsing entityTestSet.tmp.span
./runEntities_Spanish.sh entityTestSet.tmp.span
cd ../
find entityExtraction/code/tmp_formatted/ -name "*.mergedAnnotations" > mergedFilenames.tmp.span
python createSetFiles/writeDataFromFiles.py mergedFilenames.tmp.span createSetFiles/setFile.withEntities.tmp.Span
python MaltParser_scripts/convertToParsingFile.py MaltParser_scripts/Spanish.conll.tmp.output createSetFiles/setFile.withEntities.tmp.Span.parsing
rm mergedFilenames.tmp.span
rm tmp.spanish.list

# predictions
cd ../all_predictions_4.0/
./runAll.sh ../preprocessing_2.0/createSetFiles/setFile.withEntities.tmp.Span
cd ../preprocessing_2.0/

# outputFormatting
python ../outputFormatting/writeDocMap.py $1
cd ../outputFormatting/
./Spanish_run.sh
cd ../preprocessing_2.0/


# clear the tmp folder
rm CoreNLP_scripts/tmp_Span/*
rm createSetFiles/*.Span
rm createSetFiles/*.parsing
rm entityExtraction/*.span
rm entityExtraction/code/tmp_formatted/*
rm readCoreNLP/tmp_formatted_Span/*
rm *.tmp

rm MaltParser_scripts/Spanish.conll.tmp.output
rm MaltParser_scripts/Spanish.conll.tmp


rm ../all_predictions_4.0/output.*
rm ../all_predictions_4.0/*.easyRead
rm ../all_predictions_4.0/*.entityCoref
rm ../all_predictions_4.0/currentPredictionsForTriggers/testSet.predictions
rm ../all_predictions_4.0/currentPredictionsForArgs/testSet.predictions
rm ../all_predictions_4.0/currentPredictionsForRealis/testSet.predictions
rm ../all_predictions_4.0/code/test.*
rm ../outputFormatting/formatTriggers/format_andrew_triggers/andrew.triggers.out

