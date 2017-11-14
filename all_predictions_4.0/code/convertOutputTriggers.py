# script to convert the liblinear output files to work with my evaluation script
import sys

def main():
    if len(sys.argv) != 5:
        print "Expect roles dict, prediction file, easy reading file, output file."
        sys.exit()

    predictions = []
    input = open(sys.argv[2], "r")
    for line in input:
        predictions.append(line.strip())
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

    for index in range(len(predictions)):
        predictedRole = roleDict[predictions[index]]
        output.write(predictedRole + "\n")
    input.close()
    output.close()

main()
