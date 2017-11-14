# script to convert from the "createSetFiles" output to the training format for Stanford NER
import sys
import string

def main():
    if len(sys.argv) != 4:
        print "Expect input file, parsing file, output file."
        sys.exit()

    labelDict = dict()
    labelDict["WEA"] = "weapon"
    labelDict["Sentence"] = "sentence"
    labelDict["Crime"] = "crime"
    labelDict["Job-Title"] = "title"
    labelDict["VEH"] = "vehicle"
    labelDict["TIME"] = "time"
    labelDict["Numeric"] = "money"

    sentences = []
    sentencesRelation = []
    governorDict = dict()   # wordIndex -> governor word
    relationDict = dict()   # wordIndex -> dependency relationship
    wordCount = 0
    input = open(sys.argv[2], "r")
    for line in input:
        if line.strip() != "":
            wordCount += 1
            tokens = line.strip().split("|||")
            governor = tokens[1]
            start = line.strip().rfind("|") + 1
            wordIndex = int(line.strip()[start:])

            governorDict[wordIndex] = governor

            relation = tokens[0]
            relationDict[wordIndex] = relation
        else:
            sentences.append(governorDict)
            sentencesRelation.append(relationDict)
            wordCount = 0
            governorDict = dict()
            relationDict = dict()
    if len(governorDict) != 0:
        sentences.append(governorDict)
        sentencesRelation.append(relationDict)
    input.close()

    input = open(sys.argv[1], "r")
    prefix = sys.argv[3]

    labelSet = set()

    # first, scan the text, figure out how many labels
    for line in input:
        clean = line.strip()
        if clean != "":
            tokens = clean.split("\t")
            entity = tokens[6]

            if entity != "EntitesGold[]":
                start = entity.find("[") + 1
                end = entity.find(";;;")
                substring = entity[start:end]

                entTokens = substring.split(";;;")
                for tok in entTokens:
                    tmpLabel = substring.split("|||")[1]
                    if tmpLabel in labelDict:
                        tmpLabel = labelDict[tmpLabel]
                    #labelSet.add(substring.split("|||")[1])
                    labelSet.add(tmpLabel)

    input.close()

    output = open(sys.argv[3], "w")

    sentenceCount = 0
    wordCount = 0

    input = open(sys.argv[1], "r")
    prevEmpty = True
    for line in input:
        clean = line.strip()
        if clean != "":
            prevEmpty = False

            wordCount += 1
            tokens = clean.split("\t")
            word = tokens[2]
            entity = tokens[6]

            governor = "<NONE>"
            relation = "<NONE>"
            if wordCount in sentences[sentenceCount]:
                governor = sentences[sentenceCount][wordCount]
                relation = sentencesRelation[sentenceCount][wordCount]
            if governor.strip() == "":
                governor = "<NONE>"
            if relation.strip() == "":
                relation = "<NONE>"

            output.write(removeWhitespace(word) + "\tO\t" + removeWhitespace(governor) + "_" + removeWhitespace(relation) + "\n")
        elif not prevEmpty:
            output.write("\n")
            wordCount = 0
            sentenceCount += 1
            prevEmpty = True

    input.close()
    for label in labelSet:
        outputs[label].close()

def removeWhitespace(text):
    newText = ""
    for character in text:
        if character not in string.whitespace:
            newText += character
        else:
            newText += "_"

    return newText

main()
