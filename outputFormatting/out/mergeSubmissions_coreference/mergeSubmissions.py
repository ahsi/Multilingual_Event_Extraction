# script to merge the submissions from three sources into a single directory
import sys

def main():
    if len(sys.argv) != 2:
        print "Writes the nuggets/ and arguments/ files.  Use another script for linking."
        print "Expect a list of files to read.  Assuming directories are under andrew/ hector/ and jun/"
        sys.exit()

    filenames = []
    input = open(sys.argv[1], "r")
    for line in input:
        filenames.append(line.strip())

    dirList = ["hector", "jun", "andrew"]

    corpusID = 1
    for filename in filenames:
        # Begin Nugget Writing
        # process nuggets first
        output = open("all/nuggets/" + filename, "w")
        output.write("#BeginOfDocument" + " " + filename + "\n")

        writtenNuggetKeys = set()
        writtenNuggets = set()
        nuggetID_toKey = dict()
        corefDict = dict()  # dict from key -> set of coreferent nugget ids
        for inDir in dirList:
            try:
                input = open(inDir + "/nuggets/" + filename, "r")
            except:
                continue

            for line in input:
                if line.startswith("#"):
                    continue
                elif line.startswith("@"):
                    tokens = line.strip().split("\t")[2].split(",")
                    first = inDir + "_" + tokens[0]
                    firstKey = nuggetID_toKey[first]
                    rest = tokens[1:]

                    # add the remaining nuggets to the corefSet of the first nugget
                    for tok in rest:
                        curID = inDir + "_" + tok
                        corefDict[firstKey].add(curID)


                        # maybe I don't need this?  Merging later may take care of it
                        '''
                        # delete the corefSets of the other nuggets
                        curKey = nuggetID_toKey[curID]
                        if curKey in corefDict:
                            del corefDict[curKey]
                        '''
                        


                else:
                    tokens = line.strip().split("\t")
                    key = tokens[3] + "_" + tokens[5]   # key = offset_label
                    nuggetID = inDir + "_" + tokens[2]

                    # if we haven't seen the key yet, add it
                    if key not in writtenNuggetKeys:
                        output.write("mergedSystem\t" + filename + "\t" + nuggetID + "\t" + tokens[3] + "\t" + tokens[4] + "\t" + tokens[5] + "\t" + tokens[6] + "\n")
                        writtenNuggetKeys.add(key)
                        writtenNuggets.add(nuggetID)
                        curSet = set()
                        curSet.add(nuggetID)
                        corefDict[key] = curSet

                        nuggetID_toKey[nuggetID] = key
                    # if we have seen it, then need to add to right corefSet
                    else:
                        corefDict[key].add(nuggetID)
                        nuggetID_toKey[nuggetID] = key

            input.close()

        # before writing coref, merge together any overlapping coref sets
        done = True
        first = True
        while not done or first:
            first = False
            done = True

            removeKey = None
            # if we find overlap, break out and start over again
            for key in corefDict:
                curSet = corefDict[key]
                for altKey in corefDict:
                    if key == altKey:
                        continue

                    altSet = corefDict[altKey]
                    overlap = False

                    for nugget in curSet:
                        if nugget in altSet:
                            overlap = True
                            done = False
                            break

                    if overlap:
                        for nugget in altSet:
                            corefDict[key].add(nugget)

                        removeKey = altKey
                        break

                if removeKey != None:
                    break
            if removeKey != None:
                print removeKey
                del corefDict[removeKey]

        corefID = 1
        for key in corefDict:
            writeList = []
            for nugget in corefDict[key]:
                if nugget in writtenNuggets:
                    writeList.append(nugget)

            if len(writeList) > 1:
                output.write("@Coreference\tR" + str(corefID) + "\t")
                first = True
                for nugget in writeList:
                    if first:
                        output.write(nugget)
                        first = False
                    else:
                        output.write("," + nugget)
                output.write("\n")
                corefID += 1
        output.write("#EndOfDocument\n")
        ### End Nugget writing

        ### Begin argument writing
        idCount = 1
        linesToWrite = []
        output = open("all/arguments/" + filename, "w")

        # write everything EXCEPT the last column.  Use the other script to get that.
        for inDir in dirList:
            input = open(inDir + "/arguments/" + filename, "r")

            for line in input:
                start = line.find("\t") + 1
                end = line.rfind("\t")
                data = line[start:end]

                if data not in linesToWrite:
                    linesToWrite.append(data)
                    output.write(str(idCount) + "\t" + data + "\n")

                    idCount += 1
            input.close()

        output.close()

main()
