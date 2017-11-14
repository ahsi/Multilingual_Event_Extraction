# script to change the format to the TAC KBP 2015 required formatting
import string
import sys

responseIDs = set()
eventIDs = dict()   # dict from eventString -> ID

seenResponses = set()

stopwordSet = set()

corefClusters = dict()  # dict from corefID -> set of strings

docDict = dict()    # dict from docID -> filename

# example below:
#sent_1	Phrase:	they	CorefStr:	coref_2	Role:	Person	Trigger:	arriving	EventType:	Movement_Transport	EntityType:	PER.Group	DOCID:	CNNHL_ENG_20030416_133739.9	START:	127	END:	131
class ProcessedArgument:
    def __init__(self, easyReadLine, assignedRole, confArg, curRealis):
        tokens = easyReadLine.strip().split("\t")
        sentStr = tokens[0]
        self.text = tokens[2]

        self.corefID = tokens[4] + "_" + tokens[14]
        self.triggerText = tokens[8]

        eventTokens = tokens[10].split("_")
        self.eventType = convertEventType(eventTokens[0])+ "." + convertEventType(eventTokens[1])

        self.realis = curRealis
        if self.realis == "UNK_REALIS":
            self.realis = "ACTUAL"
        
        self.entityType = convertEntityType(tokens[12].split(".")[0])

        self.role = assignedRole

        self.JET_role = tokens[6]

        self.confidence = confArg
        self.docID = tokens[14] 
        if self.docID.endswith(".mpdf"):
            self.docID = self.docID[:-5]

        if self.docID.startswith("CMN"):
            tmp = removeWhitespace(self.text)
            self.text = tmp

        self.baseStart = tokens[16]
        self.baseEnd = str(int(tokens[18]) - 1) # note that we should be one less -- ACE vs KBP differences

        self.sentStart = tokens[20]
        self.sentEnd = str(int(tokens[22]) - 1) # note that we should be one less -- ACE vs KBP differences

        # use this to integrate with the event nugget data (Feb. 10, 2017)
        self.triggerOffset = tokens[24]

        # ACE -> KBP changes
        if self.eventType == "Contact.Phone-Write":
            self.eventType = "Contact.Correspondence"

        if self.eventType == "Transaction.Transfer-Ownership":
            if self.role == "Artifact":
                self.role == "Thing"

        if self.eventType == "Movement.Transport":
            if self.role == "Artifact":
                self.eventType = "Movement.Transport-Artifact"
            else:
                self.eventType = "Movement.Transport-Person"

        if self.role.startswith("Time"):
            self.role = "Time"

        if self.JET_role.startswith("Time"):
            self.JET_role = "Time"

    def activateJET(self):
        self.role = self.JET_role

def removeWhitespace(arg):
    alt = ""
    for character in arg:
        if character not in string.whitespace:
            alt += character
    return alt

def convertWhitespace(arg):
    alt = ""
    for character in arg:
        if character in string.whitespace:
            alt += " "
        else:
            alt += character
    return alt

def isYear(text):
    if len(text) != 4:
        return False
    for index in range(4):
        if text[index] not in string.digits:
            return False
    return True

def isNumber(text):
    for character in text:
        if character not in string.digits:
            return False
    return True

def isDay(text, prevMonth):
    if prevMonth and (len(text) == 1 or len(text) == 2):
        if isNumber(text):
            num = int(text)
            if num >= 1 and num <= 31:
                if len(text) == 1:
                    return "0" + str(num)
                else:
                    return str(num)
        return ""
    if len(text) == 3:
        numPart = text[0]
        if isNumber(numPart):
            num = int(numPart)
            if num >=1 and num <= 31:
                return "0" + str(num)
        return ""
    if len(text) == 4:
        numPart = text[0] + text[1]
        if isNumber(numPart):
            num = int(numPart)
            if num >=1 and num <= 31:
                return str(num)
        return ""

    return ""

def isMonth(text):
    temp = text.lower()
    if temp == "january" or temp == "jan" or temp == "jan.":
        return "01"
    elif temp == "february" or temp == "feb" or temp == "feb.":
        return "02"
    elif temp == "march" or temp == "mar" or temp == "mar.":
        return "03"
    elif temp == "april" or temp == "apr" or temp == "apr.":
        return "04"
    elif temp == "may":
        return "05"
    elif temp == "june" or temp == "jun" or temp == "jun.":
        return "06"
    elif temp == "july" or temp == "jul" or temp == "jul.":
        return "07"
    elif temp == "august" or temp == "aug" or temp == "aug.":
        return "08"
    elif temp == "september" or temp == "sept" or temp == "sept." or temp == "sep" or temp == "sep.":
        return "09"
    elif temp == "october" or temp == "oct" or temp == "oct.":
        return "10"
    elif temp == "november" or temp == "nov" or temp == "nov.":
        return "11"
    elif temp == "december" or temp == "dec" or temp == "dec.":
        return "12"
    else:
        return ""

def timeNormalization(timeString):
    year = "XXXX"
    month = "XX"
    day = "XX"

    prevMonth = False
    
    tokens = convertWhitespace(timeString).split(" ")
    for tok in tokens:
        if isYear(tok):
            year = tok
            continue
        monthStr = isMonth(tok)
        if monthStr != "":
            month = monthStr
            prevMonth = True
            continue

        dayStr = isDay(tok, prevMonth)
        if dayStr != "":
            day = dayStr
            continue
        prevMonth = False

    finalString = year + "-" + month + "-" + day
    return finalString

def validEntityType(argument):
    role = argument.role
    entityType = argument.entityType

    # if we don't know the entity type, assume valid
    if entityType == "NULL":
        return True

    validSet = set()

    if role == "Adjudicator":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Agent":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
        validSet.add("FAC")
    elif role == "Artifact":
        validSet.add("VEH")
        validSet.add("WEA")
        validSet.add("FAC")
        validSet.add("ORG")
        validSet.add("COM")
    elif role == "Attacker":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Beneficiary":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Buyer":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Crime":
        validSet.add("CRIME")
    elif role == "Defendant":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Destination":
        validSet.add("GPE")
        validSet.add("LOC")
        validSet.add("FAC")
    elif role == "Entity":
        validSet.add("ORG")
        validSet.add("GPE")
        validSet.add("PER")
    elif role == "Giver":
        validSet.add("ORG")
        validSet.add("GPE")
        validSet.add("PER")
    elif role == "Instrument":
        validSet.add("WEA")
        validSet.add("VEH")
    elif role == "Money":
        validSet.add("MONEY")
        validSet.add("NUM")
    elif role == "Org":
        validSet.add("ORG")
    elif role == "Origin":
        validSet.add("GPE")
        validSet.add("LOC")
        validSet.add("FAC")
    elif role == "Person":
        validSet.add("PER")
    elif role == "Place":
        validSet.add("GPE")
        validSet.add("LOC")
        validSet.add("FAC")
    elif role == "Plaintiff":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Position":
        validSet.add("JOB")
    elif role == "Price":
        validSet.add("MONEY")
        validSet.add("NUM")
    elif role == "Prosecutor":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Recipient":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Seller":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Sentence":
        validSet.add("SENTENCE")
    elif role == "Target":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("VEH")
        validSet.add("FAC")
        validSet.add("WEA")
    elif role == "Vehicle":
        validSet.add("VEH")
    elif role == "Victim":
        validSet.add("PER")
    elif role.startswith("Time"):
        validSet.add("TIME")
    elif role == "Audience":
        validSet.add("PER")
        validSet.add("ORG")
        validSet.add("GPE")
    elif role == "Thing":
        validSet.add("VEH")
        validSet.add("WEA")
        validSet.add("ORG")
        validSet.add("FAC")
    else:
        print "Don't recognize this role: " + role
        return False

    if entityType not in validSet:
        return False
    return True

def validRole(argument):
    eventType = argument.eventType
    role = argument.role

    validSet = set()

    notKBP2016_set = set(["Business.Mergeorg", "Business.Startorg", "Business.Endorg", "Life.Beborn", "Business.Declarebankruptcy", "Justice.Releaseparole", "Justice.Chargeindict", "Justice.Trialhearing", "Business.Declare-Bankruptcy", "Business.Merge-Org", "Life.Marry", "Life.Divorce", "Personnel.Nominate", "Justice.Release-Parole", "Justice.Trial-Hearing", "Justice.Sentence", "Justice.Fine", "Justice.Charge-Indict", "Justice.Sue", "Justice.Extradite", "Justice.Acquit", "Justice.Convict", "Justice.Appeal", "Justice.Execute", "Justice.Pardon", "Manufacture.Artifact"])
    if eventType in notKBP2016_set:
        return False


#    if eventType == "Business.Declare-Bankruptcy":
#        validSet.add("Org")
#    elif eventType == "Business.Merge-Org":
#        validSet.add("Org")
    if eventType == "Conflict.Attack":
        validSet.add("Attacker")
        validSet.add("Target")
        validSet.add("Instrument")
    elif eventType == "Conflict.Demonstrate":
        validSet.add("Entity")
    elif eventType == "Contact.Meet":
        validSet.add("Entity")
    elif eventType == "Contact.Correspondence":
        validSet.add("Entity")
    elif eventType == "Contact.Contact":
        validSet.add("Entity")
    elif eventType == "Contact.Broadcast":
        validSet.add("Audience")
        validSet.add("Entity")
#    elif eventType == "Life.Marry":
#        validSet.add("Person")
#    elif eventType == "Life.Divorce":
#        validSet.add("Person")
    elif eventType == "Life.Injure":
        validSet.add("Agent")
        validSet.add("Victim")
        validSet.add("Instrument")
    elif eventType == "Life.Die":
        validSet.add("Agent")
        validSet.add("Victim")
        validSet.add("Instrument")
    elif eventType == "Movement.Transport-Person":
        validSet.add("Agent")
        validSet.add("Person")
        validSet.add("Instrument")
        validSet.add("Origin")
        validSet.add("Destination")
    elif eventType == "Movement.Transport-Artifact":
        validSet.add("Agent")
        validSet.add("Artifact")
        validSet.add("Instrument")
        validSet.add("Origin")
        validSet.add("Destination")
    elif eventType == "Personnel.Start-Position":
        validSet.add("Person")
        validSet.add("Entity")
        validSet.add("Position")
    elif eventType == "Personnel.End-Position":
        validSet.add("Person")
        validSet.add("Entity")
        validSet.add("Position")
#    elif eventType == "Personnel.Nominate":
#        validSet.add("Agent")
#        validSet.add("Person")
#        validSet.add("Position")
    elif eventType == "Personnel.Elect":
        validSet.add("Person")
        validSet.add("Agent")
        validSet.add("Position")
    elif eventType == "Transaction.Transaction":
        validSet.add("Giver")
        validSet.add("Recipient")
        validSet.add("Beneficiary")
    elif eventType == "Transaction.Transfer-Ownership":
        validSet.add("Giver")
        validSet.add("Recipient")
        validSet.add("Beneficiary")
        validSet.add("Thing")
    elif eventType == "Transaction.Transfer-Money":
        validSet.add("Giver")
        validSet.add("Recipient")
        validSet.add("Beneficiary")
        validSet.add("Money")
    elif eventType == "Justice.Arrest-Jail":
        validSet.add("Agent")
        validSet.add("Person")
        validSet.add("Crime")
#    elif eventType == "Justice.Release-Parole":
#        validSet.add("Entity")
#        validSet.add("Person")
#        validSet.add("Crime")
#    elif eventType == "Justice.Trial-Hearing":
#        validSet.add("Prosecutor")
#        validSet.add("Adjudicator")
#        validSet.add("Defendant")
#        validSet.add("Crime")
#    elif eventType == "Justice.Sentence":
#        validSet.add("Adjudicator")
#        validSet.add("Defendant")
#        validSet.add("Sentence")
#        validSet.add("Crime")
#    elif eventType == "Justice.Fine":
#        validSet.add("Adjudicator")
#        validSet.add("Entity")
#        validSet.add("Money")
#        validSet.add("Crime")
#    elif eventType == "Justice.Charge-Indict":
#        validSet.add("Prosecutor")
#        validSet.add("Adjudicator")
#        validSet.add("Defendant")
#        validSet.add("Crime")
#    elif eventType == "Justice.Sue":
#        validSet.add("Plantiff")
#        validSet.add("Adjudicator")
#        validSet.add("Defendant")
#        validSet.add("Crime")
#    elif eventType == "Justice.Extradite":
#        validSet.add("Agent")
#        validSet.add("Person")
#        validSet.add("Origin")
#        validSet.add("Destination")
#        validSet.add("Crime")
#    elif eventType == "Justice.Acquit":
#        validSet.add("Adjudicator")
#        validSet.add("Defendant")
#        validSet.add("Crime")
#    elif eventType == "Justice.Convict":
#        validSet.add("Adjudicator")
#        validSet.add("Defendant")
#        validSet.add("Crime")
#    elif eventType == "Justice.Appeal":
#        validSet.add("Prosecutor")
#        validSet.add("Adjudicator")
#        validSet.add("Defendant")
#        validSet.add("Crime")
#    elif eventType == "Justice.Execute":
#        validSet.add("Agent")
#        validSet.add("Person")
#        validSet.add("Crime")
#    elif eventType == "Justice.Pardon":
#        validSet.add("Adjudicator")
#        validSet.add("Defendant")
#        validSet.add("Crime")
#    elif eventType == "Manufacture.Artifact":
#        validSet.add("Agent")
#        validSet.add("Artifact")
#        validSet.add("Instrument")
    else:
        print "Don't recognize this event type: " + eventType
        return False

    if role == "Place" and eventType.startswith("Movement"):
        return False

    if role == "Place" or role.startswith("Time"):
        return True

    if role not in validSet:
        return False
    return True



def main():
    if len(sys.argv) != 8:
        print "Expect predictions file, easyRead file, roles dict, coref file, docID dictionary file, stopwords list, realisOutput."
        print "Output to be placed in out/arguments/ and out/linking"
        sys.exit()

    # first, write an empty file for each docID.  At least make sure we have a file, even if we don't find any arguments
    input = open(sys.argv[6], "r")
    for line in input:
        word = line.strip()
        stopwordSet.add(word)
    input.close()

    input = open(sys.argv[5], "r")
    for line in input:
        tokens = line.strip().split("\t")
        key = tokens[0]

        if key.endswith(".mpdf"):
            key = key[:-5]


        filename = tokens[1]
        docDict[key] = filename

        output = open("out/arguments/" + key, "w")
        output.close()
        output = open("out/linking/" + key, "w")
        output.close()
        output = open("out/corpusLinking/corpusLinking", "w")

    input.close()

    predictionsRaw = []
    confidence = []
    input = open(sys.argv[1], "r")
    labelOnly = True
    for line in input:
        if line.startswith("labels"):
            labelOnly = False
            continue
        if labelOnly:
            predictionsRaw.append(line.strip())
            confidence.append("0.5")
        else:
            tempTokens = line.split(" ")
            temp = tempTokens[0]
            predictionsRaw.append(temp)
            confidence.append(tempTokens[int(temp)])
    input.close()

    input = open(sys.argv[4], "r")
    for line in input:
        tokens = line.strip().split("\t")
        text = tokens[0]
        corefID = tokens[1]
        start = tokens[2]
        end = str(int(tokens[3]) - 1)

        if corefID not in corefClusters:
            corefClusters[corefID] = set()
        corefClusters[corefID].add(text + "|||" + start + "|||" + end)
    input.close()

    roleDict = dict()
    input = open(sys.argv[3], "r")
    for line in input:
        tokens = line.strip().split(":")

        ### 2016 -- convert labels to correct format
        roleDict[tokens[1]] = convertRoleLabels(tokens[0])
    input.close()

    # read the realis labels
    realis = []
    input = open(sys.argv[7], "r")
    for line in input:
        start = line.strip().rfind("|")
        realis.append(line.strip()[start+1:])
    input.close()

    predictions = []
    input = open(sys.argv[2], "r")
    index = 0
    for line in input:
        predictedRole = roleDict[predictionsRaw[index]]
        curConf = confidence[index]
        curRealis = realis[index]

        arg = ProcessedArgument(line, predictedRole, curConf, curRealis)
        predictions.append(arg)

        index += 1
    input.close()

    docDict_Args = dict()    # dict from docID -> set of string
    docDict_Linking = dict()    # dict from docID -> dict:{eventID -> set of responseIDs}

    # the system predicted ones
    for arg in predictions: 
        if arg.role == "NONE":
            continue

        if not validRole(arg) or not validEntityType(arg):
            continue


        argString, docID, eventID, responseID, responseString = readArgument(arg)

        if responseString in seenResponses:
            continue

        seenResponses.add(responseString)

        if docID not in docDict_Args:
            docDict_Args[docID] = set()
            docDict_Linking[docID] = dict()
        docDict_Args[docID].add(argString)

        if arg.realis != "GENERIC":
            if eventID not in docDict_Linking[docID]:
                docDict_Linking[docID][eventID] = set()
            docDict_Linking[docID][eventID].add(responseID)

    for docID in docDict_Args:
        output = open("out/arguments/" + docID, "w")
        for line in docDict_Args[docID]:
            output.write(line)
        output.close()

    corpusOutput = open("out/corpusLinking/corpusLinking", "w")
    corpusCount = 1
    for docID in docDict_Linking:
        output = open("out/linking/" + docID, "w")
        eventCount = 1
        for eventID in docDict_Linking[docID]:
            output.write(str(eventCount) + "\t")
            corpusOutput.write(str(corpusCount) + "\t" + docID + "-" + str(eventCount) + "\n")

            eventCount += 1
            corpusCount += 1

            idSet = docDict_Linking[docID][eventID]
            line = ""
            for item in idSet:
                line += str(item) + " "
            line = line.strip()
            output.write(line.strip() + "\n")
        output.close()
    corpusOutput.close()

def properNoun(text):
    tokens = text.split(" ")
    proper = False
    for tok in tokens:
        if tok.lower() in stopwordSet:
            continue
        elif tok.lower() != tok:
            proper = True
    return proper

def canonicalForm(stringSet):
    best = ""
    bestStart = -1
    bestEnd = -1
    bestCapital = False
    containsComma = False
    for item in stringSet:
        tokens = item.split("|||")
        text = tokens[0]
        start = tokens[1]
        end = tokens[2]

        proper = properNoun(text)

        if best == "":
            best = text
            bestStart = start
            bestEnd = end
            if "," in text:
                containsComma = True
            if proper:
                bestCapital = True
        elif proper:
            if not bestCapital:
                best = text
                bestStart = start
                bestEnd = end
                bestCapital = True
                if "," in text:
                    containsComma = True
            elif "," not in text and (len(text) > len(best) or containsComma):
                best = text
                bestStart = start
                bestEnd = end
                bestCapital = True
        elif not bestCapital and "," not in text and (len(text) > len(best) or containsComma):
            best = text
            bestStart = start
            bestEnd = end

    return best, bestStart, bestEnd

def convertOffset(value, docID):
    ### counting the XML now in offsets, don't need below
    return value

    #filename = docDict[docID]
    #input = open(filename, "r")
    #nonXML_Index = 0
    #withXML_Index = 0

    #debug = ""

    #inXML = False
    #broke = False
    #for line in input:
    #    for character in line:
    #        if nonXML_Index == value:
    #            broke = True
    #            break

    #        withXML_Index += 1
    #        if character == "<":
    #            inXML = True
    #        elif character == ">":
    #            inXML = False
    #        elif not inXML:
    #            nonXML_Index += 1
    #            debug += character

    #input.close()

    #if not broke:
    #    print nonXML_Index
    #    print value
    #    print filename
    #    print "ERROR!!!!"
    #    sys.exit()

    #print "\t\t" + debug
    
    #return withXML_Index

def readArgument(inputArg):
    responseID = len(responseIDs)
    responseIDs.add(responseID)

    docID = inputArg.docID
    ### NEW -- remove .xml extension
    if docID.endswith(".xml"):
        docID = docID[:-4]


    eventType = inputArg.eventType
    role = inputArg.role

    CAS_String, CAS_start, CAS_end = canonicalForm(corefClusters[inputArg.corefID])
    # adjust whitespace
    temp = convertWhitespace(CAS_String)
    CAS_String = temp

    if role == "Time":
        alternate_CAS_String = timeNormalization(CAS_String)
        CAS_String = alternate_CAS_String

    #offsets = CAS_start + "-" + CAS_end
    adjusted_CAS_start = convertOffset(int(CAS_start), docID)
    adjusted_CAS_end = convertOffset(int(CAS_end), docID)

    if adjusted_CAS_end < adjusted_CAS_start:
        adjusted_CAS_end = adjusted_CAS_start

    offsets = str(adjusted_CAS_start) + "-" + str(adjusted_CAS_end)

    adjusted_sentStart = convertOffset(int(inputArg.sentStart), docID)
    adjusted_sentEnd = convertOffset(int(inputArg.sentEnd), docID)
    justificationOffset = str(adjusted_sentStart) + "-" + str(adjusted_sentEnd)

    baseFiller = inputArg.text
    adjusted_baseStart = convertOffset(int(inputArg.baseStart), docID)
    adjusted_baseEnd = convertOffset(int(inputArg.baseEnd), docID)

    ### Linking with nuggets -- ColdStart++
    triggerOffset = inputArg.triggerOffset

    ### KBP2016 -- no entity coref
    CAS_String = baseFiller
    CAS_start = adjusted_baseStart
    CAS_end = adjusted_baseEnd
    offsets = str(CAS_start) + "-" + str(CAS_end)

    ### KBP2016 -- justification must be < 200 characters
    while adjusted_sentEnd - adjusted_sentStart >= 200:
        if adjusted_baseEnd != adjusted_sentEnd:
            adjusted_sentEnd -= 1
        elif adjusted_baseStart != adjusted_sentStart:
            adjusted_sentStart += 1
        else:
            adjusted_sentEnd -= 1
    justificationOffset = str(adjusted_sentStart) + "-" + str(adjusted_sentEnd)

    if adjusted_baseEnd < adjusted_baseStart:
        adjusted_baseEnd = adjusted_baseStart
    baseFillerOffsets = str(adjusted_baseStart) + "-" + str(adjusted_baseEnd)

    argJustificationOffsets = "NIL"
    realis = inputArg.realis
    confidence = inputArg.confidence  # [0-1]

    # 2016 -- link things together if they have the same docID and same eventType
    eventString = docID + "_" + eventType   
    if eventString not in eventIDs:
        eventIDs[eventString] = len(eventIDs)


    ### original version below (before ColdStart++, used for TAC KBP 2016)
    #outputString = str(responseID) + "\t" + docID + "\t" + eventType + "\t" + role + "\t" + CAS_String + "\t" + offsets + "\t" + justificationOffset + "\t" + baseFillerOffsets + "\t" + argJustificationOffsets + "\t" + realis + "\t" + confidence + "\n"
    # new version -- used for ColdStart++ merging with nuggets
    outputString = str(responseID) + "\t" + docID + "\t" + eventType + "\t" + role + "\t" + CAS_String + "\t" + offsets + "\t" + justificationOffset + "\t" + baseFillerOffsets + "\t" + argJustificationOffsets + "\t" + realis + "\t" + confidence + "\t" + triggerOffset + "\n"

    # below: not for output, but for identifying arguments that end up having the same ID (e.g. both play the AGENT role of some trigger in the same sentence)
    responseString = docID + "\t" + eventType + "\t" + role + "\t" + CAS_String + "\t" + offsets + "\t" + justificationOffset + "\t" + baseFillerOffsets + "\t" + argJustificationOffsets + "\t" + realis + "\n"

    return outputString, docID, eventIDs[eventString], responseID, responseString

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

def convertEntityType(text):
    if text == "weapon":
        return "WEA"
    elif text == "vehicle":
        return "VEH"
    elif text == "sentence":
        return "Sentence"
    elif text == "crime":
        return "CRIME"
    elif text == "title":
        return "Title"
    elif text == "money":
        return "MONEY"
    elif text == "time":
        return "TIME"
    return text

main()
