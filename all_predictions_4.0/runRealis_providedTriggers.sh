#!/bin/bash

LIBLINEAR_PATH=/home/andrew/ML_tools/LIBLINEAR/liblinear-1.94

if [ "$#" -ne 2 ]; then
	echo "Illegal number of parameters, provide a value for C parameter, test file"
	exit 1
fi

# create the input liblinear files
cd code/
# write English Liblinear
python writeRealisLiblinear.py test ../$2 test.out /home/andrew/DEFT_code_testing/dependencies/models/liblinear/realis.features.dict /home/andrew/DEFT_code_testing/dependencies/models/liblinear/realis.roles.dict NONE

cd ../

# testing on the training/validation/testing sets
${LIBLINEAR_PATH}/predict code/test.out /home/andrew/DEFT_code_testing/dependencies/models/liblinear/realis.model output.test.realis

# report results on the data
python code/convertOutputArgs.py /home/andrew/DEFT_code_testing/dependencies/models/liblinear/realis.roles.dict output.test.realis code/test.out.easyRead currentPredictionsForRealis/testSet.predictions
cp code/test.out.easyRead realis.out.easyRead
