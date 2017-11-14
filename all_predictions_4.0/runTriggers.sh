#!/bin/bash

LIBLINEAR_PATH=/home/andrew/ML_tools/LIBLINEAR/liblinear-1.94

if [ "$#" -ne 2 ]; then
	echo "Illegal number of parameters, provide a value for C parameter, test file"
	exit 1
fi

# create the input liblinear files
cd code/
# write English Liblinear
python writeTriggerLiblinear.py test ../$2 test.out /home/andrew/DEFT_code_testing/dependencies/models/liblinear/triggers.features.dict /home/andrew/DEFT_code_testing/dependencies/models/liblinear/triggers.roles.dict

cd ../
# running on the test set
${LIBLINEAR_PATH}/predict code/test.out /home/andrew/DEFT_code_testing/dependencies/models/liblinear/triggers.model output.test.triggers

# report results on the data
python code/convertOutputTriggers.py /home/andrew/DEFT_code_testing/dependencies/models/liblinear/triggers.roles.dict output.test.triggers code/test.out.easyRead currentPredictionsForTriggers/testSet.predictions
# record trigger easyRead data
cp code/test.out.easyRead triggers.out.easyRead
