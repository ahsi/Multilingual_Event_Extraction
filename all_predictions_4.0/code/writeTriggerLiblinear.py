import sys
import copy
from random import shuffle
import string
import os
from readLargeInput import *


#### FILEPATHS TO BE SET BY USER
WORD_EMBEDDING_PATH="/home/andrew/DEFT_code_testing/dependencies/wordVectors"
UNIV_POS_PATH="/home/andrew/DEFT_code_testing/dependencies/pos"


DEBUG=False
SMALLDEBUG=False
PREDICTION_DEBUG=False
# for when the input data is too big, turn this off.
EASY_READ_OUTPUT=False
EMPTY_TRIGGER="not_trigger_not_trigger"
stepSize=1
beamSize=1
maxIters=20

### Original word vectors
# English vectors only
WORD2VEC_FILENAME=WORD_EMBEDDING_PATH+"/en-wiki-april-6-2015.word2vec_vectors"
# Chinese vectors only
CHINESE_WORD2VEC_FILENAME=WORD_EMBEDDING_PATH+"/chinese-wiki-20160305.word2vec"
# Spanish vectors only
SPANISH_WORD2VEC_FILENAME=WORD_EMBEDDING_PATH+"/es-wiki-may-2-2016.word2vec_vectors"
# multilingual -- Noah
#MULTI_WORD2VEC_FILENAME="/home/andrew/data/LORELEI/word_vectors_noah/embeddings/andrew_scripts/eng-chn-noah.wordVectors"

### ACE subset word vectors
#WORD2VEC_FILENAME="../../multilingualWordVectors/createWordVectorSubset/en-wiki-april-6-2015.word2vec.ACE.subset"
#CHINESE_WORD2VEC_FILENAME="../../multilingualWordVectors/createWordVectorSubset/chinese-wiki-march-5-2016.word2vec.ACE.subset"
#SPANISH_WORD2VEC_FILENAME="empty.txt"
#MULTI_WORD2VEC_FILENAME="../../multilingualWordVectors/vectorAlignment/out/multilingualEngChn.formatted.final"

### empty word vectors
#WORD2VEC_FILENAME="empty.txt"
#CHINESE_WORD2VEC_FILENAME="empty.txt"
#SPANISH_WORD2VEC_FILENAME="empty.txt"
MULTI_WORD2VEC_FILENAME="empty.txt"

### dictionary based on CEDICT, containing the ACE English trigger words
#TRIGGER_BILINGUAL_DICTIONARY_LIST="../../multilingualWordVectors/extractTriggerWords/ACE.English.triggerWords.translations"
TRIGGER_BILINGUAL_DICTIONARY_LIST="empty.txt"
### dictionary based on CEDICT, containing the entire ACE English lexicon
#BILINGUAL_DICTIONARY_LIST="../../multilingualWordVectors/extractTriggerWords/ACE.English.lexicon.translations"
BILINGUAL_DICTIONARY_LIST="empty.txt"

wordVecs = dict()   # dict: word -> vector
chineseWordVecs = dict()
multiWordVecs = dict()
spanishWordVecs = dict()
bilingualDictionary = dict()
triggerBilingualDictionary = dict()

univPOS_EngFile=UNIV_POS_PATH+"/en-ptb.map"
univPOS_ChnFile=UNIV_POS_PATH+"/zh-ctb6.map"
univPOS_SpanFile=UNIV_POS_PATH+"/es-cast3lb.map"
universalPOS_converter = dict()

def readConfigFile(filename):
	input = open(filename, "r")
	returnPath = ""
	for line in input:
		if line.startswith("WORD_EMBEDDING_DIR"):
			returnPath = line.strip().split("=")[1]
	input.close()

	return returnPath

class State:
    def __init__(self, triggerParam = None, entParam = None, scoreParam = 0.0):
        if triggerParam == None:
            self.triggerStates = []
        else:
            self.triggerStates = triggerParam
        if entParam == None:
            self.entStates = dict()
        else:
            self.entStates = entParam

        self.score = scoreParam

    def addTrigger(self, trigger):
        self.triggerStates.append(trigger)

    def updateScore(self, val):
        self.score += val

    def addEntityAssignment(self, arg):
        key = arg.text + "|||" + str(arg.minIndex()) + "|||" + str(arg.triggerIndex)
        self.entStates[key] = arg.role
        
    def copy(self):
        altScore = self.score
        altTriggerStates = []
        altEntStates = dict()

        for state in self.triggerStates:
            altTriggerStates.append(state)
        for key in self.entStates:
            altEntStates[key] = self.entStates[key]

        return State(altTriggerStates, altEntStates, altScore)

def processSentence(curSentence, output, easyOutput, roleIndexDict, featureIndexDict, sentenceIndex, testMode=False):
    # handle each word in the sentence
    triggerIndex = 0
    curWords = curSentence.words
    curGold = curSentence.labels
    curEnts = curSentence.entities

    for triggerIndex in range(len(curWords)):
        word = curWords[triggerIndex]
        triggerLabel = curGold[triggerIndex]

        processWord(curSentence, triggerIndex, triggerLabel, output, easyOutput, roleIndexDict, featureIndexDict, sentenceIndex, testMode)

def processWord(curSentence, triggerIndex, triggerLabel, output, easyOutput, roleIndexDict, featureIndexDict, sentenceIndex, testMode):
    curWords = curSentence.words
    triggerWord = curWords[triggerIndex]

    features = genFeatures(curSentence, triggerIndex, triggerLabel)

    if triggerLabel not in roleIndexDict:
        roleIndexDict[triggerLabel] = len(roleIndexDict) + 1
    argID = roleIndexDict[triggerLabel]
    output.write(str(argID))
    if EASY_READ_OUTPUT:
        easyOutput.write("sent_" + str(sentenceIndex) + "\tPhrase:\t" + curWords[triggerIndex] + "\tRole:\t" + triggerLabel)

        for feature in features:
            easyOutput.write("\t" + feature)

    # place all feature names in here
    featureIDs = [] 
    # place word embedding features in here (i.e. non-binary features)
    word2vecDict = dict()

    for feature in features:
        if testMode and feature not in featureIndexDict and not feature.startswith("WORD2VEC"):
            continue

        if feature.startswith("WORD2VEC"):
            temp = feature.find("=")
            featureName = feature[:temp]
            featureVal = feature[temp+1:]

            if featureName not in featureIndexDict:
                featureIndexDict[featureName] = len(featureIndexDict) + 1

            # add the corresponding feature ID to the list(s)
            featureIDs.append(featureIndexDict[featureName])
            word2vecDict[featureIndexDict[featureName]] = featureVal
        else:
            if feature not in featureIndexDict:
                featureIndexDict[feature] = len(featureIndexDict) + 1
            featureID = featureIndexDict[feature]
            featureIDs.append(featureID)

    sortedIDs = sorted(featureIDs)
    for featureID in sortedIDs:
        if featureID in word2vecDict:
            val = word2vecDict[featureID]
            output.write(" " + str(featureID) + ":" + str(val))
        else:
            output.write(" " + str(featureID) + ":1")
    output.write("\n")
    if EASY_READ_OUTPUT:
        easyOutput.write("\n")

def main():
    if len(sys.argv) != 4 and len(sys.argv) != 6:
        print len(sys.argv)
        print "Expect mode (train/test), feature file, output liblinear file, and (if test-mode) feature dictionary, role dictionary."
        print "Expect input training data, output liblinear file, input dev data, output liblinear file, input test data, output liblinear file."
        sys.exit()

	try:
		WORD_EMBEDDING_PATH = readConfigFile("../CONFIG.txt")
	except:
		print "Could not find CONFIG.txt.  Terminating..."
		sys.exit()

    trainMode = (sys.argv[1] == "train")
    if not trainMode and sys.argv[1] != "test":
        sys.exit()

    textFile = sys.argv[2]
    outputFile = sys.argv[3]

    roleIndexDict = dict()
    featureIndexDict = dict()
    if not trainMode:
        featureIndexDict = readDict(sys.argv[4])
        roleIndexDict = readDict(sys.argv[5])

    # open UniversalPOS converter
    input = open(univPOS_EngFile, "r")
    for line in input:
        tokens = line.strip().split("\t")
        source = tokens[0]
        target = tokens[1]

        universalPOS_converter[source] = target
    input.close()
    input = open(univPOS_ChnFile, "r")
    for line in input:
        tokens = line.strip().split("\t")
        source = tokens[0]
        target = tokens[1]

        universalPOS_converter[source] = target
    input.close()
    input = open(univPOS_SpanFile, "r")
    for line in input:
        tokens = line.strip().split("\t")
        source = tokens[0]
        target = tokens[1]

        universalPOS_converter[source] = target
    input.close()

    # open the bilingual dictionary
    # usage: add a new feature.  For english words, activates if the word appears; for chinese words, activates any associated translations
    input = open(BILINGUAL_DICTIONARY_LIST, "r")
    for line in input:
        tokens = line.strip().split()
        chineseWord = tokens[0]
        englishWord = tokens[1]

        if chineseWord not in bilingualDictionary:
            bilingualDictionary[chineseWord] = set()
        if englishWord not in bilingualDictionary:
            bilingualDictionary[englishWord] = set()
        bilingualDictionary[chineseWord].add(englishWord)
    input.close()

    input = open(TRIGGER_BILINGUAL_DICTIONARY_LIST, "r")
    for line in input:
        tokens = line.strip().split()
        chineseWord = tokens[0]
        englishWord = tokens[1]

        if chineseWord not in triggerBilingualDictionary:
            triggerBilingualDictionary[chineseWord] = set()
        if englishWord not in triggerBilingualDictionary:
            triggerBilingualDictionary[englishWord] = set()
        triggerBilingualDictionary[chineseWord].add(englishWord)
    input.close()
        

    # open and read word vectors
    input = open(WORD2VEC_FILENAME, "r")
    for line in input:
        # skip any headers
        if line.count(" ") < 5:
            continue
        else:
            index = line.find(" ")
            curWord = line[:index]
            rest = line[index+1:]
            tokens = rest.strip().split(" ")

            numTokens = []
            for tok in tokens:
                numTokens.append(float(tok))

            wordVecs[curWord] = numTokens
    input.close()

    input = open(CHINESE_WORD2VEC_FILENAME, "r")
    for line in input:
        # skip any headers
        if line.count(" ") < 5:
            continue
        else:
            index = line.find(" ")
            curWord = line[:index]
            rest = line[index+1:]
            tokens = rest.strip().split(" ")

            numTokens = []
            for tok in tokens:
                numTokens.append(float(tok))

            chineseWordVecs[curWord] = numTokens
    input.close()

    input = open(SPANISH_WORD2VEC_FILENAME, "r")
    for line in input:
        # skip any headers
        if line.count(" ") < 5:
            continue
        else:
            index = line.find(" ")
            curWord = line[:index]
            rest = line[index+1:]
            tokens = rest.strip().split(" ")

            numTokens = []
            for tok in tokens:
                numTokens.append(float(tok))

            spanishWordVecs[curWord] = numTokens
    input.close()

    input = open(MULTI_WORD2VEC_FILENAME, "r")
    for line in input:
        # skip any headers
        if line.count(" ") < 5:
            continue
        else:
            index = line.find(" ")
            curWord = line[:index]
            rest = line[index+1:]
            tokens = rest.strip().split(" ")

            numTokens = []
            for tok in tokens:
                numTokens.append(float(tok))

            multiWordVecs[curWord] = numTokens
    input.close()

    ### Training
    if trainMode:
        possibleLabels, possibleArgs = scanInput(textFile, textFile + ".parsing")

        print "Total # of trigger labels to predict over: " + str(len(possibleLabels))
        print "Total # of argument roles to predict over: " + str(len(possibleArgs))


        # go over each sentence in the training data
        # NOTE: in this version, using gold triggers, gold entity mentions
        output = open(outputFile, "w")
        easyOutput = open(outputFile + ".easyRead", "w")

        input = open(textFile, "r")
        parsingInput = open(textFile + ".parsing", "r")
        count = 0

        print "Writing training set"
        while True:
            sentence, valid, nothing = readInput(input, parsingInput)

            if count % 1000 == 0:
                print "Processing sentence " + str(count)
                if DEBUG:
                    print "Sentence length: " + str(len(sentence.words))
                    print "Total entities: " + str(len(sentence.entities))

            if sentence != None:
                processSentence(sentence, output, easyOutput, roleIndexDict, featureIndexDict, count)

            count += 1

            if not valid:
                break
        output.close()
        easyOutput.close()
        input.close()
        parsingInput.close()

        writeDicts(featureIndexDict, roleIndexDict, "features.dict", "roles.dict")
    ### Testing
    else:
        output = open(outputFile, "w")
        easyOutput = open(outputFile + ".easyRead", "w")

        input = open(textFile, "r")
        parsingInput = open(textFile + ".parsing", "r")

        count = 0
        print "Writing test set"
        while True:
            sentence, valid, nothing = readInput(input, parsingInput)

            if count % 1000 == 0:
                print "Processing sentence " + str(count)
                if DEBUG:
                    print "Sentence length: " + str(len(sentence.words))
                    print "Total entities: " + str(len(sentence.entities))

            if sentence != None:
                processSentence(sentence, output, easyOutput, roleIndexDict, featureIndexDict, count, testMode=True)

            count += 1

            if not valid:
                break
        output.close()
        easyOutput.close()
        input.close()
        parsingInput.close()


def writeDicts(featureDict, roleDict, filenameF, filenameR):
    output = open(filenameF, "w")
    for feature in featureDict:
        curID = featureDict[feature]
        output.write(feature + ":" + str(curID) + "\n")
    output.close()

    output = open(filenameR, "w")
    for role in roleDict:
        curID = roleDict[role]
        output.write(role + ":" + str(curID) + "\n")
    output.close()

def readDict(filename):
    input = open(filename, "r")
    curDict = dict()
    for line in input:
        clean = line.strip()
        splitPoint = clean.rfind(":")
        index = clean[:splitPoint]
        val = int(clean[splitPoint+1:])
        curDict[index] = val
    return curDict

def isYear(text):
    if len(text) < 4:
        return False
    for index in range(4):
        if text[index] not in string.digits:
            return False
    # sometimes errors from Stanford segmenter
    if len(text) != 4:
        if text[4] not in string.punctuation:
            return False
    return True


# returns (absolute value) of distance between entity and trigger
def calcArgTriggerDistance(triggerIndex, start, end):
    if triggerIndex < start:
        return start - triggerIndex
    elif triggerIndex > end:
        return triggerIndex - end
    else:
        return 0

def toUnivPOS(tag):
    # removeNumbers at end of POS tag if needed (Stanford Spanish seems to add this)
    tempTag = ""
    for character in tag:
        if character not in string.digits:
            tempTag += character

    copyPOS = tempTag
    while len(copyPOS) > 0:
        if copyPOS in universalPOS_converter:
            return universalPOS_converter[copyPOS]
        else:
            copyPOS = copyPOS[:-1]
    return tempTag

# assuming each can be represented by an indicator function
# i.e. binary features
# GOTOFEATURES
def genFeatures(curSentence, index, proposedLabel):
    words = curSentence.words
    lemmas = curSentence.lemmas
    posTags = curSentence.posTags

    # default
    previousWord = "<START>"
    prevPOS = "<START>"
    previousWord_2 = "<START>"
    prevPOS_2 = "<START>"
    if index != 0:
        previousWord = words[index-1]
        prevPOS = posTags[index-1]
        if index != 1:
            previousWord_2 = words[index-2]
            prevPOS_2 = posTags[index-2]

    nextWord = "<END>"
    nextPOS = "<END>"
    nextWord_2 = "<END>"
    nextPOS_2 = "<END>"
    if index != len(words) - 1:
        nextWord = words[index+1]
        nextPOS = posTags[index+1]
        if index != len(words) - 2:
            nextWord_2 = words[index+2]
            nextWord_2 = posTags[index+2]

    word = words[index]
    lemma = lemmas[index]
    curPOS = posTags[index]

    featureSet = set()

    # if the sentence is for the title (approximate)
    foundUnderscore = False
    foundNEWS = False
    for word in words:
        if "_" in word:
            foundUnderscore = True
        if "NEWS" in word:
            foundNEWS = True
    isTitle = foundUnderscore and foundNEWS
    if isTitle:
        featureSet.add("isTitle")

    # length of current word
    featureSet.add(str(len(word)) + "_lengthCurWord")

    # unigrams -- words
    featureSet.add(word + "_curWord")
    featureSet.add(previousWord + "_prevWord")
    featureSet.add(nextWord + "_nextWord")
    featureSet.add(previousWord_2 + "_prevWord2")
    featureSet.add(nextWord_2 + "_nextWord2")

    # unigrams -- words lowercase
    featureSet.add(word.lower() + "_curWordLower")
    featureSet.add(previousWord.lower() + "_prevWordLower")
    featureSet.add(nextWord.lower() + "_nextWordLower")
    featureSet.add(previousWord_2.lower() + "_prevWord2Lower")
    featureSet.add(nextWord_2.lower() + "_nextWord2Lower")

    # unigrams -- lemma
    featureSet.add(lemma + "_curLemma")

    # bigrams -- words
    featureSet.add(word + "_curWord" + "|||" + previousWord + "_prevWord")
    featureSet.add(word + "_curWord" + "|||" + nextWord + "_nextWord")
    featureSet.add(word + "_curWord" + "|||" + previousWord_2 + "_prevWord2")
    featureSet.add(word + "_curWord" + "|||" + nextWord_2 + "_nextWord2")

    # bigrams -- words lowercase
    featureSet.add(word.lower() + "_curWordLower" + "|||" + previousWord.lower() + "_prevWordLower")
    featureSet.add(word.lower() + "_curWordLower" + "|||" + nextWord.lower() + "_nextWordLower")
    featureSet.add(word.lower() + "_curWordLower" + "|||" + previousWord_2.lower() + "_prevWordLower2")
    featureSet.add(word.lower() + "_curWordLower" + "|||" + nextWord_2.lower() + "_nextWordLower2")

    # bigrams -- word + POS
    featureSet.add(word + "_curWord" + "|||" + curPOS + "_curPOS")
    featureSet.add(word + "_curWord" + "|||" + toUnivPOS(curPOS) + "_curUNIVPOS")


    # word-"shape" features
    if "_" in word:
        featureSet.add("containsUnderscore")

    # if number
    number = True
    for character in word:
        if character not in string.digits:
            number = False
            break
    if number:
        featureSet.add("isNumber")

    # capitalized
    firstChar = word[0]
    if firstChar in string.ascii_uppercase:
        featureSet.add("isCapitalized")
    else:
        featureSet.add("isNotCapitalized")

    # punctuationOnly
    punct = True
    for character in word:
        if character not in string.punctuation:
            punct = False
            break
    if punct:
        featureSet.add("isPunctuation")

    # POS features
    if curPOS.startswith("V"):
        featureSet.add("POS_VType")
    featureSet.add(curPOS + "_curPOS")
    featureSet.add(prevPOS + "_prevPOS")
    featureSet.add(nextPOS + "_nextPOS")
    featureSet.add(prevPOS_2 + "_prevPOS2")
    featureSet.add(nextPOS_2 + "_nextPOS2")

    if toUnivPOS(curPOS).startswith("V"):
        featureSet.add("UNIVPOS_VType")
    featureSet.add(toUnivPOS(curPOS) + "_curUNIVPOS")
    featureSet.add(toUnivPOS(prevPOS) + "_prevUNIVPOS")
    featureSet.add(toUnivPOS(nextPOS) + "_nextUNIVPOS")
    featureSet.add(toUnivPOS(prevPOS_2) + "_prevUNIVPOS2")
    featureSet.add(toUnivPOS(nextPOS_2) + "_nextUNIVPOS2")

    # POS bigrams
    featureSet.add(curPOS + "_curPOS" + "|||" + prevPOS + "_prevPOS")
    featureSet.add(curPOS + "_curPOS" + "|||" + nextPOS + "_nextPOS")
    featureSet.add(curPOS + "_curPOS" + "|||" + prevPOS_2 + "_prevPOS2")
    featureSet.add(curPOS + "_curPOS" + "|||" + nextPOS_2 + "_nextPOS2")

    featureSet.add(toUnivPOS(curPOS) + "_curUNIVPOS" + "|||" + toUnivPOS(prevPOS) + "_prevUNIVPOS")
    featureSet.add(toUnivPOS(curPOS) + "_curUNIVPOS" + "|||" + toUnivPOS(nextPOS) + "_nextUNIVPOS")
    featureSet.add(toUnivPOS(curPOS) + "_curUNIVPOS" + "|||" + toUnivPOS(prevPOS_2) + "_prevUNIVPOS2")
    featureSet.add(toUnivPOS(curPOS) + "_curUNIVPOS" + "|||" + toUnivPOS(nextPOS_2) + "_nextUNIVPOS2")

    # dependency parsing features -- governor
    if index in curSentence.depByGovIndex:
        for dependency in curSentence.depByGovIndex[index]:
            depType = dependency.depType
            dependent = dependency.dependent

            featureSet.add("ParsingGov_" + depType + "_type")
            featureSet.add("ParsingGov_" + dependent + "_dependent")
            featureSet.add("ParsingGov_" + depType + "_type" + "|||" + dependent + "_dependent")

    # dependency parsing features -- dependent
    if index in curSentence.depByDepIndex:
        for dependency in curSentence.depByDepIndex[index]:
            depType = dependency.depType
            governor = dependency.governor

            featureSet.add("ParsingDep_" + depType + "_type")
            featureSet.add("ParsingDep_" + governor + "_governor")
            featureSet.add("ParsingDep_" + depType + "_type" + "|||" + governor + "_governor")
    
    # only include if we have the word as one of our vectors
    word = words[index]
    if word in wordVecs:
        curVector = wordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC_ENG_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1

    word = words[index]
    if word in chineseWordVecs:
        curVector = chineseWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC_CHN_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1

    word = words[index]
    if word in spanishWordVecs:
        curVector = spanishWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC_SPAN_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1

    word = words[index]
    if word in multiWordVecs:
        curVector = multiWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC_MULTI_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1

    # bilingual dictionary features
    word = words[index]
    if word in bilingualDictionary:
        wordSet = bilingualDictionary[word]
        # if English word:
        if len(wordSet) == 0:
            featureSet.add("WORD_TRANSLATION_" + word)
        else:
            for translation in wordSet:
                featureSet.add("WORD_TRANSLATION_" + translation)

    word = words[index]
    if word in triggerBilingualDictionary:
        wordSet = triggerBilingualDictionary[word]
        # if English word:
        if len(wordSet) == 0:
            featureSet.add("TRIGGER_WORD_TRANSLATION_" + word)
        else:
            for translation in wordSet:
                featureSet.add("TRIGGER_WORD_TRANSLATION_" + translation)

    return featureSet

if __name__ == "__main__":
    main()
