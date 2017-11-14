#!/bin/bash
STANFORD_NER=/home/andrew/NLP_tools/StanfordNER/stanford-ner-2016-10-31

for i in crime FAC GPE title LOC ORG PER sentence time weapon vehicle age commodity
do
	java -mx16g -cp "$STANFORD_NER/*:$STANFORD_NER/lib/*" edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier /home/andrew/DEFT_code_testing/dependencies/models/entities/RichERE-Spanish.ner-model.${i}.dependency.full.ser.gz -testfile $1 > code/unify/in/${1}_${i}
done

ls code/unify/in/* > code/unify/in.txt
python code/unify/unifyEntities.py ../createSetFiles/setFile.noEntities.tmp.Span code/unify/in.txt code/unify/out/
ls code/unify/out/ > code/unify/out.txt
python code/unify/processEntities.py code/unify/out.txt code/unify/out/ code/unify/out_processed/

cd code/
./addEntitiesToText.sh ../../tmp.spanish.list ../../CoreNLP_scripts/tmp_Span/
cd ../

rm code/unify/in.txt
rm code/unify/out.txt
rm -r code/unify/in/
rm -r code/unify/out/
rm -r code/unify/out_processed/
mkdir code/unify/in/
mkdir code/unify/out/
mkdir code/unify/out_processed/
