# script to convert from the CoNLL output back to my createSetFiles output
import sys

def printDep(dep, output, wordDict):
    relation = dep[0]
    relationIndex = dep[1]
    wordIndex = dep[2]

    output.write(relation + "|||" + wordDict[relationIndex] + "|||" + relationIndex + "|||" + wordDict[wordIndex] + "|||" + wordIndex + "\n")

def main():
    if len(sys.argv) != 3:
        print "Expect input file, output file."
        sys.exit()

    input = open(sys.argv[1], "r")
    output = open(sys.argv[2], "w")

    wordDict = dict()
    wordDict["0"] = "ROOT"
    depList = []
    for line in input:
        if line.strip() == "":
            # print out dependencies if needed
            if len(wordDict) != 0:
                for dep in depList:
                    printDep(dep, output, wordDict)
                wordDict = dict()
                wordDict["0"] = "ROOT"
                depList = []
            output.write("\n")
        elif not line.startswith("#"):
            tokens = line.strip().split("\t")
            wordIndex = tokens[0]
            word = tokens[1]
            relation = tokens[7]
            relationIndex = tokens[6]

            wordDict[wordIndex] = word

            depList.append( (relation, relationIndex, wordIndex) )

    if len(wordDict) != 0:
        for dep in depList:
            printDep(dep, output)
        wordDict = dict()
        depList = []
    output.write("\n")

    input.close()
    output.close()

main()
