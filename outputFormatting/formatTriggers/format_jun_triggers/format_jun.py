# script to convert my output files to the Event Nugget Output format
import sys

def main():
    if len(sys.argv) != 3:
        print "Need nuggets from Jun, output file."
        sys.exit()

    input = open(sys.argv[1], "r")
    output = open(sys.argv[2], "w")

    docID = ""
    for line in input:
        if line.startswith("#BeginOfDocument"):
            tokens = line.strip().split()
            name = tokens[1]
            if name.endswith(".xml"):
                name = name[:-4]
            output.write(tokens[0] + " " + name + "\n")
        elif line.startswith("#EndOfDocument"):
            output.write(line)
        elif line.startswith("@Coreference"):
            output.write(line)
        else:
            tokens = line.strip().split("\t")

            labelTokens = tokens[5].split(".")
            label = labelTokens[0] + "_" + labelTokens[1]

#            output.write("junSystem" + "\t" + tokens[1] + "\t" + tokens[2] + "\t" + tokens[3] + "\t" + tokens[4] + "\t" + tokens[5].lower() + "\t" + tokens[6] + "\n")
#            output.write("junSystem" + "\t" + tokens[1] + "\t" + tokens[2] + "\t" + tokens[3] + "\t" + tokens[4] + "\t" + label.lower() + "\t" + tokens[6] + "\n")
            output.write("junSystem" + "\t" + tokens[1] + "\t" + tokens[2] + "\t" + tokens[3] + "\t" + tokens[4] + "\t" + label.lower() + "\t" + tokens[6] + "\t" + tokens[8] + "\n")
    input.close()
    output.close()







main()
