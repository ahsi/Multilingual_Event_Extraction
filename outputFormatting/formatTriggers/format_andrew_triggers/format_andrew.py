# script to convert my output files to the Event Nugget Output format
import sys

def main():
    if len(sys.argv) != 4:
        print "Need output triggers (with role names), createSetFiles file, output file."
        sys.exit()

    triggers = []
    input = open(sys.argv[1], "r")
    for line in input:
        triggers.append(line.strip().lower())
    input.close()

    input = open(sys.argv[2], "r")
    output = open(sys.argv[3], "w")

    curDoc = ""
    mentionID = 1
    index = 0

    for line in input:
        clean = line.strip()
        if clean != "":
            tokens = line.strip().split("\t")
            docID = tokens[5]

            if docID.endswith(".xml"):
                docID = docID[:-4]

            if docID != curDoc:
                if curDoc != "":
                    output.write("#EndOfDocument\n")
                output.write("#BeginOfDocument " + docID + "\n")
                curDoc = docID
                mentionID = 1

            startOffset = tokens[0]
            endOffset = tokens[1]
            word = tokens[2]

            # skip rest if the word isn't a trigger
            if triggers[index] == "not_trigger_not_trigger":
                index += 1
                continue

            output.write("andrewSystem\t" + curDoc + "\t" + str(mentionID) + "\t" + startOffset + "," + endOffset + "\t" + word + "\t" + triggers[index] + "\tActual" + "\t0.5" + "\n")
            mentionID += 1
            index += 1

    output.write("#EndOfDocument\n")
    input.close()
    output.close()







main()
