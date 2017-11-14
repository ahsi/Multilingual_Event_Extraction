import sys
import os
import copy
from random import shuffle
import string
from readLargeInput import *

DEBUG=False
SMALLDEBUG=False
PREDICTION_DEBUG=False
EMPTY_TRIGGER="not_trigger_not_trigger"
stepSize=1
beamSize=1
maxIters=20

# English vectors only
#WORD2VEC_FILENAME="/home/andrew/TAC_KBP_2015/CMU_Chinese_Event_Extractor/word2vec_vectors/en-wiki-april-6-2015.word2vec_vectors"
WORD2VEC_FILENAME="empty.txt"
# Chinese vectors only
#CHINESE_WORD2VEC_FILENAME="/home/andrew/data/Wikipedia/word2vec_vectors/chinese-wiki-20160305.word2vec"
CHINESE_WORD2VEC_FILENAME="empty.txt"
# Spanish vectors only
#SPANISH_WORD2VEC_FILENAME="/home/andrew/data/Wikipedia/word2vec_vectors/es-wiki-may-2-2016.word2vec_vectors"
SPANISH_WORD2VEC_FILENAME="empty.txt"
# multilingual -- CEDICT
#MULTI_WORD2VEC_FILENAME="../../multilingualWordVectors/vectorAlignment/out/multilingualEngChn.formatted.final"
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
        triggerOffset = curSentence.offsets[triggerIndex]

        if triggerLabel != EMPTY_TRIGGER:
            for entityIndex in range(len(curEnts)):
                processEntity(curSentence, entityIndex, triggerIndex, triggerLabel, output, easyOutput, roleIndexDict, featureIndexDict, sentenceIndex, testMode, triggerOffset)

def processEntity(curSentence, entityIndex, triggerIndex, triggerLabel, output, easyOutput, roleIndexDict, featureIndexDict, sentenceIndex, testMode, triggerOffset):
    curWords = curSentence.words
    triggerWord = curWords[triggerIndex]
    curEntity = curSentence.entities[entityIndex]

    goldArgRole = "NONE"

    # find what the gold val is for this entity
    curGoldArgs = curSentence.goldArgs
    for arg in curGoldArgs:
        argText = arg.text
        minIndex = arg.minIndex()
        argTriggerIndex = arg.triggerIndex

        # if same entity (text and location) and same associated trigger
        if argText == curEntity.text and minIndex == curEntity.minIndex() and argTriggerIndex == triggerIndex:
            goldArgRole = arg.role
            break

    features = genArgFeatures(curSentence, entityIndex, triggerIndex, goldArgRole, triggerLabel)

    if goldArgRole not in roleIndexDict:
        roleIndexDict[goldArgRole] = len(roleIndexDict) + 1
    argID = roleIndexDict[goldArgRole]
    output.write(str(argID))
    easyOutput.write("sent_" + str(sentenceIndex) + "\tPhrase:\t" + curEntity.text + "\tCorefStr:\t" + curEntity.corefStr + "\tRole:\t" + goldArgRole + "\tTrigger:\t" + triggerWord + "\tEventType:\t" + triggerLabel + "\tEntityType:\t" + curEntity.entType + "." + curEntity.subtype + "\tDOCID:\t" + curSentence.docID + "\tSTART:\t" + str(curEntity.start)  + "\tEND:\t" + str(curEntity.end) + "\tSent_START:\t" + str(curSentence.startOffset) + "\tSent_END:\t" + str(curSentence.endOffset) + "\tTrigger_offset:\t" + str(triggerOffset))
    
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
            featureVal = float(feature[temp+1:])

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
    easyOutput.write("\n")

def main():
    if len(sys.argv) != 4 and len(sys.argv) != 7:
        print "Expect mode (train/test), feature file, output liblinear file and (if test-mode) feature dictionary, role dictionary, input triggers (or NONE for gold)"
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
        triggerFile = sys.argv[6]

    # open and read word vectors
    input = open(WORD2VEC_FILENAME, "r")
    first = True
    for line in input:
        if first:
            first = False
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
    first = True
    for line in input:
        if first:
            first = False
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
    first = True
    for line in input:
        if first:
            first = False
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
    first = True
    for line in input:
        if first:
            first = False
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

    ### Training
    if trainMode:
        possibleLabels, possibleArgs = scanInput(textFile, textFile + ".parsing")

        print "Total # of trigger labels to predict over: " + str(len(possibleLabels))
        print "Total # of argument roles to predict over: " + str(len(possibleArgs))

        output = open(outputFile, "w")
        easyOutput = open(outputFile + ".easyRead", "w")

        input = open(textFile, "r")
        parsingInput = open(textFile + ".parsing", "r")
        count = 0

        print "Writing training set"
        triggerCount = 0
        while True:
            if count == 0:
                sentence, valid, temp = readInput(input, parsingInput, count=triggerCount, entityOut=open(outputFile + ".entityCoref", 'w'))
                triggerCount = temp
            else:
                sentence, valid, temp = readInput(input, parsingInput, count=triggerCount, entityOut=open(outputFile + ".entityCoref", 'a'))
                triggerCount = temp

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
        triggerCount = 0

        if triggerFile != "NONE":
            testTriggers = []
            inputTrigger = open(triggerFile, "r")
            for line in inputTrigger:
                testTriggers.append(line.strip())
            inputTrigger.close()

        while True:
            if triggerFile == "NONE":
                if count == 0:
                    sentence, valid, temp = readInput(input, parsingInput, entityOut=open(outputFile + ".entityCoref", "w"))
                else:
                    sentence, valid, temp = readInput(input, parsingInput, entityOut=open(outputFile + ".entityCoref", "a"))
            else:
                if count == 0:
                    sentence, valid, temp = readInput(input, parsingInput, testTriggers, count=triggerCount, entityOut=open(outputFile + ".entityCoref", "w"))
                    triggerCount = temp
                else:
                    sentence, valid, temp = readInput(input, parsingInput, testTriggers, count=triggerCount, entityOut=open(outputFile + ".entityCoref", "a"))
                    triggerCount = temp

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

# assuming each can be represented by an indicator function
# i.e. binary features
# GOTOFEATURES
def genArgFeatures(curSentence, entIndex, triggerIndex, role, triggerTag):
    words = curSentence.words
    lemmas = curSentence.lemmas
    posTags = curSentence.posTags
    entities = curSentence.entities

    curEntity = entities[entIndex]
    curEntText = curEntity.text
    curTriggerWord = words[triggerIndex]
    curTriggerType = triggerTag

    phraseTokens = curEntText.split(" ")

    curEntStartIndex = curEntity.minIndex()
    curEntEndIndex = curEntity.maxIndex()

    featureSet = set()

    ### context words of entity
    featureSet.add(curEntity.head + "_headPhrase")

    # previous word
    if curEntStartIndex != 0:
        featureSet.add(words[curEntStartIndex - 1] + "_prevWord")
        if curEntStartIndex != 1:
            featureSet.add(words[curEntStartIndex - 2] + "_prevPrevWord")
    if curEntEndIndex != len(words) - 1:
        featureSet.add(words[curEntEndIndex + 1] + "_nextWord")
        if curEntEndIndex != len(words) - 2:
            featureSet.add(words[curEntEndIndex + 2] + "_nextNextWord")

    # context words merged with trigger text
    if curEntStartIndex != 0:
        featureSet.add(words[curEntStartIndex - 1] + "_prevWord_" + curTriggerWord + "_triggerWord")
        if curEntStartIndex != 1:
            featureSet.add(words[curEntStartIndex - 2] + "_prevPrevWord_" + curTriggerWord + "_triggerWord")
    if curEntEndIndex != len(words) - 1:
        featureSet.add(words[curEntEndIndex + 1] + "_nextWord_" + curTriggerWord + "_triggerWord")
        if curEntEndIndex != len(words) - 2:
            featureSet.add(words[curEntEndIndex + 2] + "_nextNextWord_" + curTriggerWord + "_triggerWord")

    # gazetteer -- phrase level
    if isYear(curEntText):
        featureSet.add("phrase_isYear")

    # gazetteer -- word level
    for tok in phraseTokens:
        if isYear(tok):
            featureSet.add("word_isYear")
            break

    # entity type features
    featureSet.add(curEntity.entType + "_entType")
    featureSet.add(curEntity.subtype + "_subtype")

    # only entity with this type
    fullType = curEntity.entType + "_" + curEntity.subtype
    onlyOne = True
    for index in range(len(entities)):
        if index != triggerIndex:
            tempEnt = entities[index]
            tempType = tempEnt.entType + "_" + tempEnt.subtype

            if tempType == fullType:
                onlyOne = False
    featureSet.add("onlyTypeInSentence_" + fullType + "_" + str(onlyOne))

    # closest entity to trigger
    closest = True
    closestOfSameType = True
    distToTrigger = calcArgTriggerDistance(triggerIndex, curEntStartIndex, curEntEndIndex)
    for altIndex in range(len(entities)):
        if altIndex != triggerIndex:
            altEntity = entities[altIndex]
            altType = altEntity.entType + "_" + altEntity.subtype
            altDist = calcArgTriggerDistance(triggerIndex, altEntity.minIndex(), altEntity.maxIndex())

            if altDist < distToTrigger:
                closest = False
                if altType == fullType:
                    closestOfSameType = False
    featureSet.add("closestEntity_" + str(closest))
    featureSet.add("closestEntitySameType_" + str(closestOfSameType))

    # unigrams -- word in entity
    for tok in phraseTokens:
        featureSet.add(tok + "_entWord")
    
    # full phrase
    featureSet.add(curEntText + "_entPhrase")
    # NEW unigrams merged with trigger
    for tok in phraseTokens:
        featureSet.add(tok + "_entWord_" + curTriggerWord + "_triggerWord")

    # NEW full phrase merged with trigger
    # full phrase
    featureSet.add(curEntText + "_entPhrase_" + curTriggerWord + "_triggerWord")
    # trigger text
    featureSet.add(curTriggerWord + "_triggerWord")

    # relative location features
    if triggerIndex < curEntStartIndex:
        featureSet.add("trigger_before_entity")
    elif triggerIndex > curEntEndIndex:
        featureSet.add("trigger_after_entity")
    else:
        featureSet.add("trigger_within_entity")

    # lexical distance between arg and trigger
    dist = 0
    if triggerIndex < curEntStartIndex:
        dist = triggerIndex - curEntStartIndex
    elif triggerIndex > curEntEndIndex:
        dist = curEntEndIndex - triggerIndex

    featureSet.add("trigger_ent_distance_" + str(dist))
    featureSet.add("trigger_ent_abs_distance_" + str(abs(dist)))

    # punctuation between trigger and arg
    punctFound = False
    if triggerIndex < curEntStartIndex:
        curIndex = triggerIndex + 1
        while curIndex < curEntStartIndex:
            curPOS = posTags[curIndex]
            if curPOS == "PU":
                punctFound = True
            curIndex += 1
    elif triggerIndex > curEntEndIndex:
        curIndex = curEntEndIndex + 1
        while curIndex < triggerIndex:
            curPOS = posTags[curIndex]
            if curPOS == "PU":
                punctFound = True
            curIndex += 1
    featureSet.add("punct_between_trigger_arg_" + str(punctFound))

    # dependency parsing features -- governor
    if triggerIndex in curSentence.depByGovIndex:
        for dependency in curSentence.depByGovIndex[triggerIndex]:
            depIndex = dependency.dIndex
            if depIndex in curEntity.associatedIndexes:
                depType = dependency.depType
                dependent = dependency.dependent
                governor = dependency.governor

                featureSet.add("ArgParsing_" + depType + "_type")
                featureSet.add("ArgParsing_" + dependent + "_dependent")
                featureSet.add("ArgParsing_" + governor + "_governor")
                featureSet.add("ArgParsing_" + depType + "_type" + "|||" + dependent + "_dependent")
                featureSet.add("ArgParsing_" + depType + "_type" + "|||" + governor + "_governor")
                featureSet.add("ArgParsing_" + depType + "_type" + "|||" + dependent + "_dependent" + "|||" + governor + "_governor")


    # contains capitalization at start of first word (any of them)
    capitalizationFound = False
    for curIndex in curEntity.associatedIndexes:
        curWord = words[curIndex]
        firstChar = curWord[0]
        if firstChar in string.uppercase:
            capitalizationFound = True
    featureSet.add("ContainsCapitalization_" + str(capitalizationFound))

    # contains capitalization at start of every word
    capitalizationFound = True
    for curIndex in curEntity.associatedIndexes:
        curWord = words[curIndex]
        firstChar = curWord[0]
        if firstChar in string.lowercase:
            capitalizationFound = False
    featureSet.add("AllWordsContainCapitalization_" + str(capitalizationFound))

    # English
    ### trigger word vector
    word = curTriggerWord 
    if word in wordVecs:
        curVector = wordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC-ENG-TRIGGER_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1
    ### head word vector
    word = curEntity.head
    if word in wordVecs:
        curVector = wordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC-ENG-HEAD_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1

    # Chinese
    ### trigger word vector
    word = curTriggerWord 
    if word in chineseWordVecs:
        curVector = chineseWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC-CHN-TRIGGER_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1
    ### head word vector
    word = curEntity.head
    if word in chineseWordVecs:
        curVector = chineseWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC-CHN-HEAD_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1

    # Spanish
    ### trigger word vector
    word = curTriggerWord 
    if word in spanishWordVecs:
        curVector = spanishWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC-SPAN-TRIGGER_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1
    ### head word vector
    word = curEntity.head
    if word in spanishWordVecs:
        curVector = spanishWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC-SPAN-HEAD_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1

    # multilingual
    ### trigger word vector
    word = curTriggerWord 
    if word in multiWordVecs:
        curVector = multiWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC-MULTI-TRIGGER_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1
    ### head word vector
    word = curEntity.head
    if word in multiWordVecs:
        curVector = multiWordVecs[word]
        vecLocation = 0
        for tok in curVector:
            featureSet.add("WORD2VEC-MULTI-HEAD_" + str(vecLocation) + "=" + str(tok))
            vecLocation += 1

    # bilingual dictionary features
    # trigger word first
    word = curTriggerWord
    if word in bilingualDictionary:
        wordSet = bilingualDictionary[word]
        # if English word:
        if len(wordSet) == 0:
            featureSet.add("WORD_TRANSLATION_" + word)
        else:
            for translation in wordSet:
                featureSet.add("WORD_TRANSLATION_" + translation)

    word = curTriggerWord
    if word in triggerBilingualDictionary:
        wordSet = triggerBilingualDictionary[word]
        # if English word:
        if len(wordSet) == 0:
            featureSet.add("TRIGGER_WORD_TRANSLATION_" + word)
        else:
            for translation in wordSet:
                featureSet.add("TRIGGER_WORD_TRANSLATION_" + translation)

    # trigger word first
    word = curEntity.head
    if word in bilingualDictionary:
        wordSet = bilingualDictionary[word]
        # if English word:
        if len(wordSet) == 0:
            featureSet.add("WORD_TRANSLATION_HEAD_" + word)
        else:
            for translation in wordSet:
                featureSet.add("WORD_TRANSLATION_HEAD_" + translation)

    word = curTriggerWord
    if word in triggerBilingualDictionary:
        wordSet = triggerBilingualDictionary[word]
        # if English word:
        if len(wordSet) == 0:
            featureSet.add("TRIGGER_WORD_TRANSLATION_HEAD_" + word)
        else:
            for translation in wordSet:
                featureSet.add("TRIGGER_WORD_TRANSLATION_HEAD_" + translation)

    appendedFeatures = set()
    for feature in featureSet:
        if not feature.startswith("WORD2VEC"):
            appendedFeatures.add(feature + "<<<TRIGGER_" + curTriggerType + ">>>")

    finalFeatures = set()
    for feature in featureSet:
        finalFeatures.add(feature)
    for feature in appendedFeatures:
        finalFeatures.add(feature)
    return finalFeatures

# assuming each can be represented by an indicator function
# i.e. binary features
# GOTOFEATURES
def genFeatures(predictions, curSentence, index, proposedLabel):
    words = curSentence.words
    lemmas = curSentence.lemmas
    posTags = curSentence.posTags

    # default
    previousTag = "<START>"
    previousWord = "<START>"
    prevPOS = "<START>"
    if index != 0:
        previousTag = predictions[index-1]
        previousWord = words[index-1]
        prevPOS = posTags[index-1]

    nextWord = "<END>"
    nextPOS = "<END>"
    if index != len(words) - 1:
        nextWord = words[index+1]
        nextPOS = posTags[index+1]

    word = words[index]
    lemma = lemmas[index]
    curPOS = posTags[index]

    featureSet = set()

    # unigrams -- words
    featureSet.add(word + "_curWord")
    featureSet.add(previousWord + "_prevWord")
    featureSet.add(nextWord + "_nextWord")

    # unigrams -- lemma
    featureSet.add(lemma + "_curLemma")

    # bigrams -- words
    featureSet.add(word + "_curWord" + "|||" + previousWord + "_prevWord")
    featureSet.add(word + "_curWord" + "|||" + nextWord + "_nextWord")

    # bigrams -- word + POS
    featureSet.add(word + "_curWord" + "|||" + curPOS + "_curPOS")

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

    # POS bigrams
    featureSet.add(curPOS + "_curPOS" + "|||" + prevPOS + "_prevPOS")
    featureSet.add(curPOS + "_curPOS" + "|||" + nextPOS + "_nextPOS")

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

    # append <<<LABEL>>> to denote the currently proposed label
    appendedFeatures = set()
    for feature in featureSet:
        appendedFeatures.add(feature + "<<<" + proposedLabel + ">>>")

    # 2nd condition in case of identification only run
    if proposedLabel != "not_trigger_not_trigger" and "_" in proposedLabel:
        tokens = proposedLabel.split("_")
        generalType = tokens[0]
        for feature in featureSet:
            appendedFeatures.add(feature + "<<<" + generalType + ">>>")

    return appendedFeatures

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

if __name__ == "__main__":
    main()
