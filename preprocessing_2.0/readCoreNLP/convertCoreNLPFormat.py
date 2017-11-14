import sys
import xml.etree.ElementTree as ET
import string
from xml.sax.saxutils import escape

def cleanWhitespace(text):
    clean = ""
    for char in text:
        if char in string.whitespace:
            clean += " "
        else:
            clean += char
    return clean

def main():
    if len(sys.argv) != 3:
        print "Expect coreNLP features (extracted), output file."
        sys.exit()

    labelDict = dict()  # dict from offset -> (B/I, labelType, labelSubtype, fullName)
    triggerDict = dict() # dict from offset -> (triggerType, triggerSubtype)
    argDict = dict() # dict from offset -> (argument role)

    entityDict = dict() # dict from mentionID -> (start, end, text)

    input = open(sys.argv[1], "r")
    output = open(sys.argv[2], "w")

    lineCounter = 0
    for line in input:
        lineCounter += 1

        if line.startswith("BEGIN_SENTENCE"):
            output.write("\n")
        else:
            clean = line.strip()
            tokens = clean.split("\t")
            startOffset = int(tokens[0])
            endOffset = int(tokens[1])
            curWord = tokens[2] 

            entityInfo = "EntitesGold["

            if startOffset in labelDict:
                for curTuple in labelDict[startOffset]:
                    begin = curTuple[0]
                    entType = curTuple[1]
                    entSubtype = curTuple[2]
                    head = curTuple[4].encode('utf-8')

                    coref = "coref_" + str(curTuple[5])

                    entityInfo += (begin + "|||" + entType + "|||" + entSubtype + "|||" + head + "|||" + coref + ";;;")

                    tupleFullName = curTuple[3].encode('utf-8')
            entityInfo += "]"

            eventType = "not_trigger"
            eventSubtype = "not_trigger"

            if startOffset in triggerDict:
                curTuple = triggerDict[startOffset]
                eventType = curTuple[0]
                eventSubtype = curTuple[1]

            argInfo = "ArgsGold["
            if startOffset in argDict:
                for curTuple in argDict[startOffset]:
                    begin = curTuple[0]
                    argRole = curTuple[1]
                    eventText = curTuple[3]
                    eventIndex = curTuple[4]
                    argRealis = curTuple[5]

                    eventText = replaceWhiteSpace(eventText)

                    argInfo += (begin + "|||" + argRole + "|||" + eventText.encode('utf-8') + "|||" + str(eventIndex) + "|||" + argRealis + ";;;")
            argInfo += "]"

            output.write(clean + "\t" + entityInfo + "\t" + eventType + "\t" + eventSubtype + "\t" + argInfo + "\n")
    output.write("\n")
    input.close()
    output.close()


def replaceWhiteSpace(text):
    newStr = ""
    for character in text:
        if character in string.whitespace:
            newStr += " "
        else:
            newStr += character
    return newStr


main()        
