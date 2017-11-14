#!/bin/bash

LIBLINEAR_PATH=/home/andrew/ML_tools/LIBLINEAR/liblinear-1.94

if [ "$#" -ne 2 ]; then
	echo "Illegal number of parameters, provide a value for C parameter, test file"
	exit 1
fi

# create the input liblinear files
cd code/
# write English Liblinear
python writeArgLiblinear.py test ../$2 test.out /home/andrew/DEFT_code_testing/dependencies/models/liblinear/arguments.features.dict /home/andrew/DEFT_code_testing/dependencies/models/liblinear/arguments.roles.dict ../currentPredictionsForTriggers/testSet.predictions

cd ../
# running on the test set
${LIBLINEAR_PATH}/predict code/test.out /home/andrew/DEFT_code_testing/dependencies/models/liblinear/arguments.model output.test.arguments

# report results on the data
python code/convertOutputArgs.py /home/andrew/DEFT_code_testing/dependencies/models/liblinear/arguments.roles.dict output.test.arguments code/test.out.easyRead currentPredictionsForArgs/testSet.predictions
# record trigger easyRead data
cp code/test.out.easyRead arguments.out.easyRead
cp code/test.out.entityCoref arguments.out.entityCoref
