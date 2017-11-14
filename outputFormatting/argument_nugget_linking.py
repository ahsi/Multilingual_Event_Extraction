# script to link together the argument and nugget files
import sys

def main():
    if len(sys.argv) != 2:
        print "Expect list of filenames."
        sys.exit()

    argDir = "out/arguments/"
    argModDir = "out/linked_arguments/"
    nuggetDir = "out/nuggets/"
    linkingDir = "out/linking/"
    corpusLinking = "out/corpusLinking/corpusLinking"

    filenames = []
    input = open(sys.argv[1], "r")
    for line in input:
        filenames.append(line.strip())
    input.close()

    corpusID = 1
    corpusOut = open(corpusLinking, "w")

    for filename in filenames:
        nuggetDict = dict() # eventType -> offset -> ID
        nuggetNameDict = dict() # eventType -> offset -> nugget_string
        argumentDict = dict()   # nuggetID -> attached_arguments

        try:
            input = open(nuggetDir + filename, "r")
            for line in input:
                if not line.startswith("#") and not line.startswith("@"):
                    tokens = line.strip().split("\t")
                    eventType = tokens[5]
                    startOffset = tokens[3].split(",")[0]
                    nuggetID = tokens[2]
                    nuggetName = tokens[4]

                    if eventType not in nuggetDict:
                        nuggetDict[eventType] = dict()
                        nuggetNameDict[eventType] = dict()
                    nuggetDict[eventType][startOffset] = nuggetID
                    nuggetNameDict[eventType][startOffset] = nuggetName

            input.close()
        except:
            print "No nugget file found for " + filename + "; continuing..."

        input = open(argDir + filename, "r")
        output = open(argModDir + filename, "w")
        for line in input:
            tokens = line.strip().split("\t")
            triggerOffset = tokens[11]
            eventType = tokens[2]
            argumentID = tokens[0]


            # rewrite the arguments/ file
            nuggetID = nuggetDict[eventType][triggerOffset]
            nuggetSpan = triggerOffset + "-" + str(len(nuggetNameDict[eventType][triggerOffset]) + int(triggerOffset) - 1)
            count = 0
            for tok in tokens:
                if count == 6:
                    output.write(nuggetSpan + "\t")
                else:
                    output.write(tok + "\t")
                count += 1
            output.write(nuggetID + "\n")

            # store information for linking file
            if nuggetID not in argumentDict:
                argumentDict[nuggetID] = []
            argumentDict[nuggetID].append(argumentID)
        input.close()
        output.close()

        # reread coreference and write linking file
        seenNuggets = set()
        linkingID = 1

        output = open(linkingDir + filename, "w")

        try:
            input = open(nuggetDir + filename, "r")
            for line in input:
                if line.startswith("@"):
                    tokens = line.strip().split("\t")
                    nuggets = tokens[2].split(",")
                    first = True

                    outputArgs = []

                    for nuggetID in nuggets:
                        if nuggetID in argumentDict:
                            seenNuggets.add(nuggetID)

                            argumentList = argumentDict[nuggetID]
                            for arg in argumentList:
                                outputArgs.append(arg)


                    if len(outputArgs) > 0:
                        output.write(str(linkingID) + "\t")
                        corpusOut.write(str(corpusID) + "\t" + filename + "-" + str(linkingID) + "\n")
                        corpusID += 1

                        for index in range(len(outputArgs)):
                            if index == 0:
                                output.write(outputArgs[index])
                            else:
                                output.write(" " + outputArgs[index])
                        output.write("\n")

                        linkingID += 1

            # now, write any singleton nuggets
            for nugget in argumentDict:
                if nugget not in seenNuggets:
                    output.write(str(linkingID) + "\t")
                    corpusOut.write(str(corpusID) + "\t" + filename + "-" + str(linkingID) + "\n")
                    corpusID += 1

                    argumentList = argumentDict[nugget]
                    for index in range(len(argumentList)):
                        if index == 0:
                            output.write(argumentList[index])
                            linkingID += 1
                        else:
                            output.write(" " + argumentList[index])
                    output.write("\n")

            input.close()
        except:
            print "Skipping empty nugget file again..."

        output.close()


    corpusOut.close()

main()
