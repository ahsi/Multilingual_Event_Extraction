# script to change from 1-line per word, to 1-line per entity
import sys

def main():
    if len(sys.argv) != 4:
        print "Expect list of files, input directory, output directory."
        sys.exit()


    filenames = []
    input = open(sys.argv[1], "r")
    for line in input:
        filenames.append(line.strip())
    input.close()

    inDir = sys.argv[2]
    outDir = sys.argv[3]

    for filename in filenames:
        print "Processing: " + filename
        input = open(inDir + filename, "r")
        output = open(outDir + filename, "w")

        lines = input.readlines()

        for index in range(len(lines)):
            curLine = lines[index]

            tokens = curLine.strip().split("\t")
            word = tokens[0]
            label = tokens[1]


            labels = [label]
            if ";" in label:
                labels = label.split(";")

            for label in labels:
                if label.startswith("B"):
                    # find how long this goes for
                    entityName = word

                    suffix = label[1:]
                    altIndex = index + 1
                    while altIndex < len(lines):
                        altLine = lines[altIndex]
                        altTokens = altLine.strip().split("\t")
                        altWord = altTokens[0]
                        altLabel = altTokens[1]

                        altLabels = [altLabel]

                        if ";" in altLabel:
                            altLabels = altLabel.split(";")
                        found = False
                        for altLabel in altLabels:
                            if altLabel.endswith(suffix):
                                entityName += " " + altWord
                                found = True
                                continue

                        if not found:
                            break
                        else:
                            altIndex += 1

                    output.write(str(index) + "\t" + entityName + "\t" + suffix[1:] + "\n")
        input.close()
        output.close()

main()

