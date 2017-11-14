import sys
import xml.etree.ElementTree as ET
import string
from xml.sax.saxutils import escape

# set to maintain unique coref labels across all entities
corefSet = set()

def processEvents(root, triggerDict, argDict):
    if root.tag == "event":
        eventType = root.attrib["TYPE"]
        eventSubtype = root.attrib["SUBTYPE"]

        for child in root:
            if child.tag == "event_mention":
                processEventMentions(child, triggerDict, argDict, eventType, eventSubtype)

    else:
        for child in root:
            processEvents(child, triggerDict, argDict)

def processEventMentions(root, triggerDict, argDict, eventType, eventSubtype):
    anchorText = ""
    anchorIndex = -1
    for child in root:
       anchorText, anchorIndex = processEvent_Helper_Anchor(child, triggerDict, argDict, eventType, eventSubtype)
       if anchorText != "":
           break
 
    for child in root:
       processEvent_Helper_Arg(child, triggerDict, argDict, eventType, eventSubtype, anchorText, anchorIndex)

def processEvent_Helper_Anchor(root, triggerDict, argDict, eventType, eventSubtype):
    if root.tag == "anchor":
        for child in root:
            return processEvent_Anchor(child, triggerDict, eventType, eventSubtype)
    else:
        returnStr = ""
        returnNum = -1
        for child in root:
            returnStr, returnNum = processEvent_Helper_Anchor(child, triggerDict, argDict, eventType, eventSubtype)
            if returnStr != "":
                break

        return returnStr, returnNum

def processEvent_Helper_Arg(root, triggerDict, argDict, eventType, eventSubtype, eventText, eventIndex):
    if root.tag == "event_mention_argument":
        role = root.attrib["ROLE"]
        for child in root:
            processEvent_Argument(child, argDict, role, eventText, eventIndex)
    else:
        for child in root:
            processEvent_Helper_Arg(child, triggerDict, argDict, eventType, eventSubtype, eventText, eventIndex)

def processEvent_Argument(root, argDict, role, eventText, eventIndex):
    if root.tag == "charseq":
        start = int(root.attrib["START"])
        end = int(root.attrib["END"])
        text = escape(root.text)

        # write the characters to the dict
        index = start

        while index <= end:
            if index not in argDict:
                argDict[index] = []
            if index == start:
                argDict[index].append( ("B", role, text, eventText, eventIndex) )
            else:
                argDict[index].append( ("I", role, text, eventText, eventIndex) )
            index += 1
    else:
        for child in root:
            processEvent_Argument(child, argDict, role, eventText, eventIndex)

def processEvent_Anchor(root, triggerDict, eventType, eventSubtype):
    if root.tag == "charseq":
        start = int(root.attrib["START"])
        end = int(root.attrib["END"])
        text = escape(root.text)

        # write the characters to the dict
        index = start

        while index <= end:
            triggerDict[index] = (eventType, eventSubtype, text)
            index += 1
        return text, start
    else:
        for child in root:
            return processEvent_Anchor(child, triggerDict, eventType, eventSubtype)

def processExtent(root):
    for child in root:
        if child.tag == "charseq":
            start = int(child.attrib["START"])
            end = int(child.attrib["END"])
            text = escape(child.text)

            return start, end, text
    raise RuntimeError("Improper XML detected.")

def cleanWhitespace(text):
    clean = ""
    for char in text:
        if char in string.whitespace:
            clean += " "
        else:
            clean += char
    return clean

def processHead(root):
    for child in root:
        if child.tag == "charseq":
            return child.text
    raise RuntimeError("Improper XML detected.")


def processEntities(root, labelDict):
    if root.tag == "entity":
        entityType = root.attrib["TYPE"]
        entitySubtype = root.attrib["SUBTYPE"]

        corefLabel = len(corefSet)
        corefSet.add(corefLabel)

        # process and write each mention to the dict
        for mention in root:
            if mention.tag == "entity_mention":
                start = -1
                end = -1
                head = ""
                text = ""

                for child in mention:
                    if child.tag == "head":
                        head = cleanWhitespace(processHead(child))
                    elif child.tag == "extent":
                        start, end, text = processExtent(child)


                # write the characters to the dict
                if start < 0:
                    raise ValueError('Did not read indexes for entity')
                index = start

                while index <= end:
                    if index not in labelDict:
                        labelDict[index] = []

                    if index == start:
                        labelDict[index].append( ("B", entityType, entitySubtype, text, head, corefLabel) )
                    else:
                        labelDict[index].append( ("I", entityType, entitySubtype, text, head, corefLabel) )
                    index += 1

    elif root.tag == "timex2":
        corefLabel = len(corefSet)
        corefSet.add(corefLabel)

        for child in root:
            processTime(child, labelDict, corefLabel)
    elif root.tag == "value":
        corefLabel = len(corefSet)
        corefSet.add(corefLabel)

        valueType = root.attrib["TYPE"]
        if "SUBTYPE" in root.attrib:
            valueSubtype = root.attrib["SUBTYPE"]
        else:
            valueSubtype = root.attrib["TYPE"]

        for child in root:
            processValue(child, labelDict, corefLabel, valueType, valueSubtype)
    else:
        for child in root:
            processEntities(child, labelDict)

def processEntity_Helper(root, labelDict, entityType, entitySubtype):
    if root.tag == "extent":
        for child in root:
           processExtent(child, labelDict, entityType, entitySubtype)
    else:
        for child in root:
          processEntity_Helper(child, labelDict, entityType, entitySubtype)

def processTime(root, labelDict, corefLabel):
    if root.tag == "charseq":
        start = int(root.attrib["START"])
        end = int(root.attrib["END"])
        text = escape(root.text)

        # write the characters to the dict
        index = start

        while index <= end:
            if index not in labelDict:
                labelDict[index] = []
    
            # NOTE: timex values don't have heads -- just use the text again
            if index == start:
                labelDict[index].append( ("B", "TIME", "TIME", text, cleanWhitespace(text), corefLabel) )
            else:
                labelDict[index].append( ("I", "TIME", "TIME", text, cleanWhitespace(text), corefLabel) )
            index += 1
    else:
        for child in root:
            processTime(child, labelDict, corefLabel)

def processValue(root, labelDict, corefLabel, valueType, valueSubtype):
    if root.tag == "charseq":
        start = int(root.attrib["START"])
        end = int(root.attrib["END"])
        text = escape(root.text)

        # write the characters to the dict
        index = start

        while index <= end:
            if index not in labelDict:
                labelDict[index] = []
    
            # NOTE: timex values don't have heads -- just use the text again
            if index == start:
                labelDict[index].append( ("B", valueType, valueSubtype, text, cleanWhitespace(text), corefLabel) )
            else:
                labelDict[index].append( ("I", valueType, valueSubtype, text, cleanWhitespace(text), corefLabel) )
            index += 1
    else:
        for child in root:
            processValue(child, labelDict, corefLabel, valueType, valueSubtype)


def main():
    if len(sys.argv) != 4:
        print "Expect stanford annotations (XML), coreNLP features (extracted), output file."
        sys.exit()

    print "Starting document " + sys.argv[3]

    # read the annotation XML
    labelDict = dict()  # dict from offset -> (B/I, labelType, labelSubtype, fullName)
    triggerDict = dict() # dict from offset -> (triggerType, triggerSubtype)
    argDict = dict() # dict from offset -> (argument role)

    corefCount = 0

    # read the Stanford mentions
    input = open(sys.argv[1], "r")
    wordDict = dict()   # dict from word count -> (B/I, labelType, labelSubtype, fullName, head)
    for line in input:
        tokens = line.strip().split('\t')
        wordCount = int(tokens[0])
        entityName = tokens[1]
        entityType = tokens[2]

        numWords = entityName.count(" ") + 1
        lastWord = entityName
        if numWords > 1:
            start = entityName.rfind(" ")
            lastWord = entityName[start+1:] 
        corefCount + 1

        for index in range(numWords):
            if index == 0:
                if wordCount not in wordDict:
                    wordDict[wordCount] = []
                wordDict[wordCount].append( ("B", entityType, entityType, entityName, lastWord, str(corefCount)) )
            else:
                if wordCount + index not in wordDict:
                    wordDict[wordCount + index] = []
                wordDict[wordCount + index].append( ("I", entityType, entityType, entityName, lastWord, str(corefCount)) )
    input.close()


    input = open(sys.argv[2], "r")
    output = open(sys.argv[3], "w")


    lineCounter = 0
    wordCount = 0
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

            labelDict[startOffset] = []
            if wordCount in wordDict:
                labelDict[startOffset] = wordDict[wordCount]
            wordCount += 1

            entityInfo = "EntitesGold["

            if startOffset in labelDict:
                for curTuple in labelDict[startOffset]:
                    begin = curTuple[0]
                    entType = curTuple[1]
                    entSubtype = curTuple[2]
                    head = curTuple[4]#.encode('utf-8')

                    coref = "coref_" + str(curTuple[5])

                    entityInfo += (begin + "|||" + entType + "|||" + entSubtype + "|||" + head + "|||" + coref + ";;;")

                    # for debugging only
                    tupleFullName = curTuple[3]#.encode('utf-8')

                    # below: good for verifying alignment, but final version should not contain.
                    #output.write(clean + "\t" + begin + "-" + entType + "\t" + begin + "-" + entSubtype + "\t" + tupleFullName + "\n")
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

                    eventText = replaceWhiteSpace(eventText)

                    argInfo += (begin + "|||" + argRole + "|||" + eventText.encode('utf-8') + "|||" + str(eventIndex) + ";;;")
            argInfo += "]"

            output.write(clean + "\t" + entityInfo + "\t" + eventType + "\t" + eventSubtype + "\t" + argInfo + "\n")
    output.write("\n")
    input.close()
    output.close()

    print "Finished processing document!  Written to " + sys.argv[3]

def replaceWhiteSpace(text):
    newStr = ""
    for character in text:
        if character in string.whitespace:
            newStr += " "
        else:
            newStr += character
    return newStr


main()        
