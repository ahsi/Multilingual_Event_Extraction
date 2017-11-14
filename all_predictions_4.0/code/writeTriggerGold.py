import sys
import copy
from random import shuffle
import string
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
    curWords = curSentence.words
    curGold = curSentence.labels
    for triggerIndex in range(len(curWords)):
        word = curWords[triggerIndex]
        triggerLabel = curGold[triggerIndex]

        output.write(triggerLabel + "\n")

def main():
    if len(sys.argv) != 3:
        print "Expect input training data, output args file."
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
    while True:
        sentence, valid, nothing = readInput(input, parsingInput)

        if count % 1000 == 0:
            print "Processing sentence " + str(count)
            if DEBUG:
                print "Sentence length: " + str(len(sentence.words))
                print "Total entities: " + str(len(sentence.entities))

        if sentence != None:
            processSentence(sentence, possibleLabels, possibleArgs, output, count)

        count += 1
        if not valid:
            break
    output.close()

if __name__ == "__main__":
    main()
