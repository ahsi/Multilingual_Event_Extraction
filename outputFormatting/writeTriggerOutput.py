# script to write the trigger output -- one file per document
import sys
import string

def main():
    if len(sys.argv) != 2:
        print "Expect list of triggers."
        sys.exit()

    storeDir = "out/nuggets/"

    input = open(sys.argv[1], "r")
    curDoc = ""
    for line in input:
        if line.startswith("#BeginOfDocument"):
            tokens = line.strip().split()
            name = tokens[1]
            if name.endswith(".xml"):
                name = name[:-4]
            
            curDoc = name
            output = open(storeDir + curDoc, "w")

            output.write(tokens[0] + " " + name + "\n")
        elif line.startswith("#EndOfDocument"):
            output.write(line)
            output.close()
        elif line.startswith("@Coreference"):
            output.write(line)
        else:
            tokens = line.strip().split("\t")

            sysName = tokens[0]
            docID = tokens[1]
            mentionID = tokens[2]
            offsets = tokens[3]
            word = tokens[4]
            label = tokens[5]
            realis = tokens[6]

            confidence = tokens[7]

            eventTokens = label.split("_")
            eventType = convertEventType(eventTokens[0])+ "." + convertEventType(eventTokens[1])

            if eventType == "Contact.Phone-Write":
                eventType = "Contact.Correspondence"

            if eventType == "Movement.Transport":
                self.eventType = "Movement.Transport-Person"

            output.write(sysName + "\t" + docID + "\t" + mentionID + "\t" + offsets + "\t" + word + "\t" + eventType + "\t" + realis + "\t" + confidence + "\n")


    input.close()

def convertRoleLabels(label):
    newLabel = ""
    prevChar = ""
    first = True
    for character in label:
        if first:
            newLabel += character.upper()
            first = False
        elif prevChar in string.punctuation:
            newLabel += character.upper()
        else:
            newLabel += character

        prevChar = character
    
    return newLabel

def convertEventType(text):
    tmp = convertRoleLabels(text)

    if tmp == "Transportperson":
        return "Transport-Person"
    elif tmp == "Transportartifact":
        return "Transport-Artifact"
    elif tmp == "Endposition":
        return "End-Position"
    elif tmp == "Startposition":
        return "Start-Position"
    elif tmp == "Arrestjail":
        return "Arrest-Jail"
    elif tmp == "Transfermoney":
        return "Transfer-Money"
    elif tmp == "Transferownership":
        return "Transfer-Ownership"
    else:
        return tmp

main()
