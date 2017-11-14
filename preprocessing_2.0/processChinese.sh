#!/bin/sh

if [ "$#" -ne 1 ]; then
	echo "Illegal number of parameters.  Expect list of files to read (with absolute filepaths)."
	exit 1
fi

# store processed documents in tmp/
rm CoreNLP_scripts/tmp_Chn/*
./CoreNLP_scripts/runCoreNLP_Chn.sh $1

# readCoreNLP
python readCoreNLP/getRootnames.py $1 tmp.chinese.list
cd readCoreNLP/
rm tmp_formatted_Chn/*
./convertCoreNLPFormat.sh ../tmp.chinese.list ../CoreNLP_scripts/tmp_Chn/ tmp_formatted_Chn/
cd ../

# createSetFiles
find readCoreNLP/tmp_formatted_Chn/ -name "*.mergedAnnotations" > mergedFilenames.tmp.Chn
rm createSetFiles/*.tmp
rm createSetFiles/*.parsing
python createSetFiles/writeDataFromFiles.py mergedFilenames.tmp.Chn createSetFiles/setFile.noEntities.tmp.Chn
rm mergedFilenames.tmp.Chn

# add dependency parsing via MaltParser
python MaltParser_scripts/convertToCoNLL.py createSetFiles/setFile.noEntities.tmp.Chn MaltParser_scripts/Chinese.conll.tmp /home/andrew/DEFT_code_testing/dependencies/pos/zh-ctb6.map
cp /home/andrew/DEFT_code_testing/dependencies/models/maltparser/UD.Chinese.model.mco UD.Chinese.model.mco.tmp
mv UD.Chinese.model.mco.tmp UD.Chinese.model.mco
java -jar /home/andrew/NLP_tools/MaltParser/maltparser-1.9.0/maltparser-1.9.0.jar -c UD.Chinese.model.mco -i MaltParser_scripts/Chinese.conll.tmp -o MaltParser_scripts/Chinese.conll.tmp.output -m parse
rm UD.Chinese.model.mco
python MaltParser_scripts/convertToParsingFile.py MaltParser_scripts/Chinese.conll.tmp.output createSetFiles/setFile.noEntities.tmp.Chn.parsing

# entity extraction
cd entityExtraction/
python convertTestSet.py ../createSetFiles/setFile.noEntities.tmp.Chn ../createSetFiles/setFile.noEntities.tmp.Chn.parsing entityTestSet.tmp.chn
./runEntities_Chinese.sh entityTestSet.tmp.chn
cd ../
find entityExtraction/code/tmp_formatted/ -name "*.mergedAnnotations" > mergedFilenames.tmp.chn
python createSetFiles/writeDataFromFiles.py mergedFilenames.tmp.chn createSetFiles/setFile.withEntities.tmp.Chn
python MaltParser_scripts/convertToParsingFile.py MaltParser_scripts/Chinese.conll.tmp.output createSetFiles/setFile.withEntities.tmp.Chn.parsing
rm mergedFilenames.tmp.chn
rm tmp.chinese.list

# predictions
cd ../all_predictions_4.0/
./runAll.sh ../preprocessing_2.0/createSetFiles/setFile.withEntities.tmp.Chn
cd ../preprocessing_2.0/

# outputFormatting
python ../outputFormatting/writeDocMap.py $1
cd ../outputFormatting/
./Chinese_run.sh
cd ../preprocessing_2.0/


# clear the tmp folders
rm CoreNLP_scripts/tmp_Chn/*
rm createSetFiles/*.Chn
rm createSetFiles/*.parsing
rm entityExtraction/*.chn
rm entityExtraction/code/tmp_formatted/*
rm readCoreNLP/tmp_formatted_Chn/*
rm MaltParser_scripts/Chinese.conll.tmp.output
rm MaltParser_scripts/Chinese.conll.tmp
rm *.tmp

rm ../all_predictions_4.0/output.*
rm ../all_predictions_4.0/*.easyRead
rm ../all_predictions_4.0/*.entityCoref
rm ../all_predictions_4.0/currentPredictionsForTriggers/testSet.predictions
rm ../all_predictions_4.0/currentPredictionsForArgs/testSet.predictions
rm ../all_predictions_4.0/currentPredictionsForRealis/testSet.predictions
rm ../all_predictions_4.0/code/test.*
rm ../outputFormatting/formatTriggers/format_andrew_triggers/andrew.triggers.out
