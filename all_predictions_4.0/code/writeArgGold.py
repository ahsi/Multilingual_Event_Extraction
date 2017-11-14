import sys
import copy
from random import shuffle
import string
from nltk.stem.wordnet import WordNetLemmatizer
from readLargeInput import *


DEBUG=False
SMALLDEBUG=False
PREDICTION_DEBUG=False
EMPTY_TRIGGER="not_trigger_not_trigger"
EMPTY_ROLE="NONE"
stepSize=1
beamSize=1
maxIters=20

def processSentence(curSentence, possibleLabels, possibleArgs, output, sentIndex):
    writtenSet = set()
    for arg in curSentence.goldArgs:
        argString = arg.text + "|||sent_" + str(sentIndex) + "|||" + arg.role
        if argString not in writtenSet:
            output.write(argString + "\n")
            writtenSet.add(argString)

def processEntity(curSentence, entityIndex, possibleArgs, triggerIndex, triggerLabel, output, sentIndex):
    curWords = curSentence.words
    triggerWord = curWords[triggerIndex]
    curEntity = curSentence.entities[entityIndex]

    goldArgRole = "NONE"

    # find what the gold val is for this entity
    curGoldArgs = curSentence.goldArgs
    foundArg = None
    for arg in curGoldArgs:
        argText = arg.text
        minIndex = arg.minIndex()
        argTriggerIndex = arg.triggerIndex

        # if same entity (text and location) and same associated trigger
        if argText == curEntity.text and minIndex == curEntity.minIndex() and argTriggerIndex == triggerIndex and goldArgRole == "NONE":
            goldArgRole = arg.role
            foundArg = arg
        elif argText == curEntity.text and minIndex == curEntity.minIndex() and argTriggerIndex == triggerIndex:
            print "Found duplicate!"
            print argText + "\t" + arg.triggerText + "\t" + arg.role
            print "Alternate:"
            print foundArg.text + "\t" + foundArg.triggerText + "\t" + goldArgRole
            sys.exit()
    if goldArgRole != EMPTY_ROLE:
        output.write(curEntity.text + "|||" + "sent_" + str(sentIndex) + "|||" + goldArgRole + "\n")

def main():
    if len(sys.argv) != 4:
        print "Expect input training data, output args file, output sentences file."
        sys.exit()

    possibleLabels, possibleArgs = scanInput(sys.argv[1], sys.argv[1] + ".parsing")

    print "Total # of trigger labels to predict over: " + str(len(possibleLabels))
    print "Total # of argument roles to predict over: " + str(len(possibleArgs))

    output = open(sys.argv[2], "w")

    # go over each sentence in the training data
    # NOTE: in this version, using gold triggers, gold entity mentions
    input = open(sys.argv[1], "r")
    parsingInput = open(sys.argv[1] + ".parsing", "r")
    count = 0

    sentenceOutput = open(sys.argv[3], "w")
    while True:
        sentence, valid, dummy = readInput(input, parsingInput)

        if count % 1000 == 0:
            print "Processing sentence " + str(count)
            if DEBUG:
                print "Sentence length: " + str(len(sentence.words))
                print "Total entities: " + str(len(sentence.entities))

        if sentence != None:
            processSentence(sentence, possibleLabels, possibleArgs, output, count)

            for word in sentence.words:
                sentenceOutput.write(word + " ")
            sentenceOutput.write("\n")

        count += 1
        if not valid:
            break
    output.close()
    sentenceOutput.close()

if __name__ == "__main__":
    main()
