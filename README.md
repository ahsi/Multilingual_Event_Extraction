CMU Multilingual Event Extractor
===============================

Requirements:
-------------
- Python
- Stanford CoreNLP
- MaltParser
- LIBLINEAR
- Stanford NER
- Model Files (available at http://cairo.lti.cs.cmu.edu/~ahsi/CMUCS_multilingual_event_extraction_models/CMUCS_Multilingual_Event_Extractor_models.tar.gz)

Installation:
-------------
Modify the CONFIG.txt file to point to the directories containing the required software and model files, then run "python config.py" from this directory.

Usage:
------
Usage is split by language.  Although all model files use multilingual training, testing on different languages must be done separately (due to differences in preprocessing steps across different languages).

To run the code, cd into "preprocessing_2.0", then run one of the following:

- "./processEnglish.sh FILELIST"
- "./processChinese.sh FILELIST"
- "./processSpanish.sh FILELIST"

where FILELIST is a list of raw text files to be processed with absolute paths, one per line.

Output files are stored in outputFormatting/out/store/, containing the following subdirectories:

arguments/
corpusLinking/
linking/
nuggets/

The overall output format closely matches that of the the 2016 TAC KBP Event Argument Extraction and Linking (EAL) Task, with some slightly modifications.  Files in the arguments/ subdirectory are exactly the same, except for two additional columns at the end of each line, providing the starting offset and ID for the associated event nugget. Files in the corpusLinking/ sudirectory and linking/ subdirectory exactly match the EAL Task specifications.  Files in the nuggets/ directory exactly match the format of the 2016 TAC KBP Event Nugget Detection Task.
