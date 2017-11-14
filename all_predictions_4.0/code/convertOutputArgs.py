# script to convert the liblinear output files to work with my evaluation script
import sys

def main():
    if len(sys.argv) != 5:
        print "Expect roles dict, prediction file, easy reading file, output file."
        sys.exit()

    predictions = []
    labelOnly = True
    input = open(sys.argv[2], "r")
    for line in input:
        if line.startswith("labels"):
            labelOnly = False
            continue
        if labelOnly:
            predictions.append(line.strip())
        else:
            temp = line.split(" ")[0]
            predictions.append(temp)
    input.close()

    roleDict = dict()
    input = open(sys.argv[1], "r")
    for line in input:
        tokens = line.strip().split(":")
        roleDict[tokens[1]] = tokens[0]
    input.close()

    input = open(sys.argv[3], "r")
    output = open(sys.argv[4], "w")
    index = 0
    for line in input:
        tokens = line.strip().split("\t")
        sentStr = tokens[0]
        text = tokens[2]

        predictedRole = predictions[index]

        output.write(text + "|||" + sentStr + "|||" + roleDict[predictedRole] + "\n")
        index += 1
    input.close()
    output.close()

main()
