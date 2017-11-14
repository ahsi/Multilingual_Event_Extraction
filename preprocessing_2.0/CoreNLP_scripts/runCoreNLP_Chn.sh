#!/bin/sh

STANFORD_CORENLP=/home/andrew/NLP_tools/CoreNLP/stanford-corenlp-full-2016-10-31
INPUTS=$1

CURRENT_PATH=${PWD}

echo "Call Stanford CoreNLP..."
java -cp "$STANFORD_CORENLP/*" -Xmx16g edu.stanford.nlp.pipeline.StanfordCoreNLP -filelist $INPUTS -props ${CURRENT_PATH}/CoreNLP_scripts/StanfordCoreNLP-chinese.properties.simple -threads 8 -outputDirectory ${CURRENT_PATH}/CoreNLP_scripts/tmp_Chn/ -outputExtension .out
