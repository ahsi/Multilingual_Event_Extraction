# script to read the CoreNLP parsing output
import sys
import xml.etree.ElementTree as ET

def main():
    if len(sys.argv) != 3:
        print "Expect input XML file, output file for dependency parsing."
        sys.exit()

    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    
    output = open(sys.argv[2], "w")

    # output dependency info.  Add line of white space between each sentence.
    writeInfo(root, output)    

    output.close()

def writeInfo(root, output):
    if root.tag == "dependencies" and root.attrib["type"] == "basic-dependencies":
        for child in root:
            processDependencies(child, output)
        output.write("\n")
    else:
        for child in root:
            writeInfo(child, output)

def processDependencies(root, output):
    depType = root.attrib["type"]

    governor = ""
    dependent = ""

    govIndex = -1
    depIndex = -1

    # extract the needed info
    for child in root:
        if child.tag == "governor":
            governor = child.text.encode('utf-8')
            govIndex = child.attrib["idx"]
        elif child.tag == "dependent":
            dependent = child.text.encode('utf-8')
            depIndex = child.attrib["idx"]

    output.write(depType.encode('utf-8'))
    output.write("|||")
    output.write(governor)
    output.write("|||")
    output.write(str(govIndex))
    output.write("|||")
    output.write(dependent)
    output.write("|||")
    output.write(str(depIndex))
    output.write("\n")

main()
