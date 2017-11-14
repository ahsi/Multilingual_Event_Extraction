#!/bin/bash

# extract nugget output
cd formatTriggers/format_andrew_triggers/
python format_andrew.py ../../../all_predictions_4.0/currentPredictionsForTriggers/testSet.predictions ../../../preprocessing_2.0/createSetFiles/setFile.withEntities.tmp.Span andrew.triggers.out
cd ../../

# arguments:	1.) test.out file, from ../argumentPrediction/	2.) Easy-read arguments file	3.) Roles dictionary	4.) Entity coref output	5.) docmap file	6.) stopwords file 7.) realis file
python finalForm_KBP.py ../all_predictions_4.0/output.test.arguments ../all_predictions_4.0/arguments.out.easyRead /home/andrew/DEFT_code_testing/dependencies/models/liblinear/arguments.roles.dict ../all_predictions_4.0/arguments.out.entityCoref ../preprocessing_2.0/documents.paths.tmp stopwords.txt ../all_predictions_4.0/currentPredictionsForRealis/testSet.predictions

# write nugget output, one per document
python writeTriggerOutput.py formatTriggers/format_andrew_triggers/andrew.triggers.out

# connect arguments and nuggets together
python argument_nugget_linking.py ../preprocessing_2.0/documents.rootnames.tmp

cd out
./moveToStore.sh
