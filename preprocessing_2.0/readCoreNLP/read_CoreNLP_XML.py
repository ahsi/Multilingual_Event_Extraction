# script to read the CoreNLP output
import sys
import xml.etree.ElementTree as ET

def getRootname(text):
    name = text
    if "/" in name:
        index = name.rfind("/") + 1
        name = name[index:]
    if ".out" in name:
        index = name.find(".out")
        name = name[:index]

#    if ".sgm" in name:
#        index = name.find(".sgm")
#        name = name[:index]
#    elif ".mpdf" in name:
#        index = name.find(".mpdf")
#        name = name[:index]
#    elif ".cmp" in name:
#        index = name.find(".cmp")
#        name = name[:index]
#    elif ".txt" in name:
#        index = name.find(".txt")
#        name = name[:index]
#    elif ".xml" in name:
#        index = name.find(".xml")
#        name = name[:index]

    return name


def main():
    if len(sys.argv) != 3:
        print "Expect input XML file, output file."
        sys.exit()

    print "Reading: " + sys.argv[1]
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    rootName = getRootname(sys.argv[1])

    wordIndexDict = dict()  # maps word indexes to character level indexes

    output = open(sys.argv[2], "w")

    # print word, start offset, end offset, POS tag for each character in the data
    printWordInfo(root, rootName, wordIndexDict, output, 0)    

    output.close()

def printWordInfo(root, rootName, wordIndexDict, output, sentenceNum):
    if root.tag == "coreference":
        return

    if root.tag == "sentence":
        output.write("BEGIN_SENTENCE\n")
        sentenceNum = root.attrib["id"]

    if root.tag == "token":
        processWord(root, rootName, wordIndexDict, sentenceNum + "_" + root.attrib["id"], output)
    else:
        for child in root:
            printWordInfo(child, rootName, wordIndexDict, output, sentenceNum)

def processWord(root, rootName, wordIndexDict, wordID, output):
    pos = ""
    offsetStart = -1

    word = ""
    lemma = ""
    # extract the needed info
    for child in root:
        if child.tag == "POS":
            pos = child.text
        elif child.tag == "CharacterOffsetBegin":
            offsetStart = int(child.text)
            wordIndexDict[wordID] = offsetStart
        elif child.tag == "word":
            word = child.text
        elif child.tag == "CharacterOffsetEnd":
            offsetEnd = int(child.text)
        elif child.tag == "lemma":
            lemma = child.text

    outString = str(offsetStart) + "\t" + str(offsetEnd) + "\t" + word.encode('utf-8') + "\t" + lemma.encode('utf-8') + "\t" + pos + "\t" + rootName
    output.write(outString + "\n")

main()
