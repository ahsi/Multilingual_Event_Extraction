# script to convert from createSetFiles file to CoNLL format
import sys
import string

def convertPOS(pos, converter):
    newPOS = ""
    for character in pos:
        if character not in string.digits:
            newPOS += character

    copyPOS = newPOS
    while len(copyPOS) > 0:
        if copyPOS in converter:
            return converter[copyPOS], copyPOS
        else:
            copyPOS = copyPOS[:-1]

    return newPOS, newPOS

def removeDigits(pos):
    newPOS = ""
    for character in pos:
        if character not in string.digits:
            newPOS += character
    return newPOS

def main():
    if len(sys.argv) != 4:
        print "Expect createSetFiles data, output file, universal POS Tag file."
        sys.exit()
    posConverter = dict()

    input = open(sys.argv[3], "r")
    for line in input:
        tokens = line.strip().split("\t")
        posConverter[tokens[0]] = tokens[1]
    input.close()

    input = open(sys.argv[1], "r")
    output = open(sys.argv[2], "w")

    prevBlank = True
    wordCount = 0
    for line in input:
        if line.strip() != "":
            tokens = line.strip().split("\t")
            if wordCount == 0:
                output.write("# " + tokens[5] + "\n")

            wordCount += 1
            word = tokens[2]
            pos = tokens[4]

            newPOS, originalPOS = convertPOS(pos, posConverter)

            if len(newPOS) == 0:
                newPOS = "_"
                originalPOS = "_"

            output.write(str(wordCount) + "\t" + word + "\t_\t" + newPOS + "\t" + originalPOS + "\t_\t_\t_\t_\t_\n")
            prevBlank = False
        else:
            wordCount = 0
            if not prevBlank:
                output.write("\n")
                prevBlank = True

    input.close()
    output.close()

main()
