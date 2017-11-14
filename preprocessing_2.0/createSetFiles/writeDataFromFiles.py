# reads each line, write the data from those files to a single file

import sys

def main():
    if len(sys.argv) != 3:
        print "Expect list of files, output file."
        sys.exit()

    files = []
    input = open(sys.argv[1], "r")
    for line in input:
        files.append(line.strip())
    input.close()

    output = open(sys.argv[2], "w")
    parsingOutput = open(sys.argv[2] + ".parsing", "w")
    for filename in files:
        tempIndex = filename.find(".mergedAnnotations")
        tempName = filename[:tempIndex]
        parsingFilename = tempName + ".parsingAnnotations"

        input = open(filename, "r")
        for line in input:
            output.write(line)
        input.close()

        try:
            input = open(parsingFilename, "r")
            for line in input:
                parsingOutput.write(line)
            input.close()
        except IOError:
            print "Could not open file: " + parsingFilename
            print "Continuing..."
    output.close()
    parsingOutput.close()

main()
