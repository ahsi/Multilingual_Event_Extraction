# script to merge the submissions from three sources into a single directory
import sys

def main():
    if len(sys.argv) != 2:
        print "Expect a list of files to read.  Assuming directories are under andrew/ hector/ and jun/"
        sys.exit()

    filenames = []
    input = open(sys.argv[1], "r")
    for line in input:
        filenames.append(line.strip())

    dirList = ["andrew", "hector", "jun"]

    corpusOutput = open("all/corpusLinking/corpusLinking", "w")
    corpusID = 1

    for filename in filenames:
        idCount = 1
        linesToWrite = []
        output = open("all/arguments/" + filename, "w")

        # for making the linking file -- link together all arguments with the same event type
        idsByEventType = dict() # eventType -> list of ids

        for inDir in dirList:
            input = open(inDir + "/arguments/" + filename, "r")

            for line in input:
                start = line.find("\t") + 1
                data = line[start:]

                if data not in linesToWrite:
                    linesToWrite.append(data)
                    output.write(str(idCount) + "\t" + data)

                    tokens = line.strip().split("\t")
                    eventType = tokens[2]

                    if eventType not in idsByEventType:
                        idsByEventType[eventType] = []
                    idsByEventType[eventType].append(idCount)

                    idCount += 1
            input.close()

        output.close()

        output = open("all/linking/" + filename, "w")
        linkingID = 1

        for eventType in idsByEventType:
            idList = idsByEventType[eventType]
            output.write(str(linkingID) + "\t")
            corpusOutput.write(str(corpusID) + "\t" + filename + "-" + str(linkingID) + "\n")

            for index in range(len(idList)):
                if index == len(idList) - 1:
                    output.write(str(idList[index]) + "\n")
                else:
                    output.write(str(idList[index]) + " ")

            linkingID += 1
            corpusID += 1


    corpusOutput.close()













main()
