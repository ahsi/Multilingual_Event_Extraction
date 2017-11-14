# script to take the (1-file-per-class) NER output and unify into a single file PER DOCUMENT
import sys

def main():
    if len(sys.argv) != 4:
        print "Expect createSetFiles file, list of files, output directory."
        sys.exit()

    # for each line read, record the word, a set of entity labels, and the documentID
    words = []  
    labels = []
    documents = []

    docSet = set()

    files = []
    input = open(sys.argv[2], "r")
    for line in input:
        files.append(line.strip())
    input.close()

    input = open(sys.argv[1], "r")
    for line in input:
        if line.strip() != "":
            tokens = line.strip().split("\t")
            word = tokens[2]
            docid = tokens[5]

            words.append(word)
            labels.append(set())
            documents.append(docid)

            docSet.add(docid)
    input.close()

    for filename in files:
        input = open(filename, "r")
        count = 0
        for line in input:
            if line.strip() != "":
                tokens = line.strip().split("\t")
                word = tokens[0]
                label = tokens[2]

                if label != "O":
                    labels[count].add(label)

                count += 1
        input.close()

    outPrefix = sys.argv[3]

    prevDoc = documents[0]
    prevSet = set()
    output = open(outPrefix + documents[0], "w")
    for index in range(len(words)):
        curWord = words[index]
        curDoc = documents[index]
        labelSet = labels[index]

        if curDoc != prevDoc:
            output.close()
            output = open(outPrefix + curDoc, "w")

        output.write(curWord + "\t")
        if len(labelSet) == 0:
            output.write("EMPTY\n")
        else:
            first = True
            for label in labelSet:
                if first:
                    if label not in prevSet:
                        output.write("B-" + label)
                    else:
                        output.write("I-" + label)
                    first = False
                else:
                    if label not in prevSet:
                        output.write(";B-" + label)
                    else:
                        output.write(";I-" + label)
            output.write("\n")

        prevDoc = curDoc
        prevSet = labelSet
    output.close()


main()
