# file to contain the most up-to-date version of readInput()

class Sentence:
    def __init__(self, wordsArg, lemmasArg, labelsArg, posTagsArg, entityArg, goldArgParam, docIDParam, startParam, endParam, realisArg, allStarts=[]):
        self.words = wordsArg
        self.lemmas = lemmasArg
        self.labels = labelsArg
        self.posTags = posTagsArg
        self.entities = entityArg
        self.goldArgs = goldArgParam
        self.depByGovIndex = dict()
        self.depByDepIndex = dict()

        self.startOffset = startParam
        self.endOffset = endParam

        self.docID = docIDParam

        self.realisLabels = realisArg

        self.offsets = allStarts

    def addDependency(self, dep):
        gIndex = dep.gIndex
        dIndex = dep.dIndex

        if gIndex not in self.depByGovIndex:
            self.depByGovIndex[gIndex] = set()
        if dIndex not in self.depByDepIndex:
            self.depByDepIndex[dIndex] = set()

        self.depByGovIndex[gIndex].add(dep)
        self.depByDepIndex[dIndex].add(dep)

class Dependency:
    def __init__(self, depTypeArg, governorArg, gIndexArg, dependentArg, dIndexArg):
        self.depType = depTypeArg
        self.governor = governorArg
        self.gIndex = gIndexArg
        self.dependent = dependentArg
        self.dIndex = dIndexArg

class ArgumentParse:
    def __init__(self, beginArg, roleArg, triggerArg, triggerIndexArg):
        self.begin = beginArg
        self.role = roleArg
        self.triggerText = triggerArg
        self.triggerIndex = triggerIndexArg

class Argument:
    def __init__(self, textParam, roleParam, associatedIndexesParam, triggerTextParam, triggerIndexParam):
        self.text = textParam
        self.role = roleParam
        self.associatedIndexes = associatedIndexesParam
        self.triggerText = triggerTextParam
        self.triggerIndex = triggerIndexParam

    def minIndex(self):
        minVal = -1
        for index in self.associatedIndexes:
            if index < minVal or minVal == -1:
                minVal = index
        return minVal
        

# extracts argument info, returns as a list
# FORMAT: "ArgsGold[begin|||ROLE|||triggerText|||triggerStart;]"
def readArguments(line, realisMode):
    argList = []

    start = line.find("[")

    cleaned = line[start+1:]
    tokens = cleaned.split(";;;")
    for tok in tokens:
        if tok != "]":
            subparts = tok.split("|||")
            if realisMode:
                if len(subparts) == 4:
                    curArg = ArgumentParse(subparts[0], "UNK_REALIS", subparts[2], int(subparts[3]))
                else:
                    curArg = ArgumentParse(subparts[0], subparts[4], subparts[2], int(subparts[3]))
            else:
                curArg = ArgumentParse(subparts[0], subparts[1], subparts[2], int(subparts[3]))
            argList.append(curArg)

    return argList

# input: list of argument information (one ArgumentParse list per word)
# output: list of Arguments for the sentence
def extractGoldArgs(argLists, words, converter):
    outputList = []

    for index in range(len(argLists)):
        curList = argLists[index]

        for parse in curList:
            if parse.begin == "B":
                textParam, associatedIndexes = extractArgument(argLists, index, parse.role, words, parse.triggerIndex)

                converted = -1  # can be -1 if trigger is not within sentence boundaries (e.g. our sentence segmentation is off)
                if parse.triggerIndex in converter:
                    converted = converter[parse.triggerIndex]

                curArg = Argument(textParam, parse.role, associatedIndexes, parse.triggerText, converted)
                outputList.append(curArg)

    return outputList

# extract the words/indexes associated with a particular entity candidate
def extractArgument(argLists, index, role, words, triggerIndex):
    text = words[index]
    indexes = set()
    indexes.add(index)

    altIndex = index + 1
    while altIndex < len(words):
        curList = argLists[altIndex]
        found = False
        for parse in curList:
            if parse.begin != "I":
                continue
            if role == parse.role and triggerIndex == parse.triggerIndex:
                indexes.add(altIndex)
                text += " " + words[altIndex]
                found = True
                break
        if found == False:
            break

        altIndex += 1

    return text, indexes

class EntityParse:
    def __init__(self, beginArg, typeArg, subtypeArg, headArg, corefArg):
        self.begin = beginArg
        self.entType = typeArg
        self.subtype = subtypeArg
        self.head = headArg
        self.corefStr = corefArg

class Entity:
    def __init__(self, textParam, typeParam, subtypeParam, associatedIndexesParam, argRoleParam, argTriggerParam, headParam, corefParam, startParam, endParam):
        self.text = textParam
        self.entType = typeParam
        self.subtype = subtypeParam
        self.associatedIndexes = associatedIndexesParam
        self.head = headParam
        self.corefStr = corefParam

        self.start = startParam
        self.end = endParam

        self.argRole = argRoleParam
        self.argTrigger = argTriggerParam

    def minIndex(self):
        minVal = -1
        for index in self.associatedIndexes:
            if index < minVal or minVal == -1:
                minVal = index
        return minVal

    def maxIndex(self):
        maxVal = -1
        for index in self.associatedIndexes:
            if index > maxVal or maxVal == -1:
                maxVal = index
        return maxVal

# extracts entity info, returns as a list
# FORMAT: "EntitiesGold[begin|||PER|||Individual|||headWord;]"
def readEntities(line):
    entList = []

    start = line.find("[")

    cleaned = line[start+1:]
    tokens = cleaned.split(";;;")
    for tok in tokens:
        if tok != "]":
            subparts = tok.split("|||")
            curEnt = EntityParse(subparts[0], subparts[1], subparts[2], subparts[3], subparts[4])
            entList.append(curEnt)

    return entList

# input: list of entity information (one EntityParse list per word)
# output: list of Entities for the sentence
def extractCandidateArgs(entityLists, words, starts, ends):
    outputList = []

    for index in range(len(entityLists)):
        curList = entityLists[index]

        for parse in curList:
            if parse.begin == "B":
                textParam, associatedIndexes, entStart, entEnd = extractCandidate(entityLists, index, parse.entType, parse.subtype, words, parse.head, starts, ends)

                curEntity = Entity(textParam, parse.entType, parse.subtype, associatedIndexes, "", "", parse.head, parse.corefStr, entStart, entEnd)
                outputList.append(curEntity)

    return outputList

# extract the words/indexes associated with a particular entity candidate
def extractCandidate(entityLists, index, entType, subtype, words, head, starts, ends):
    typeName = entType + "_" + subtype
    text = words[index]
    indexes = set()
    indexes.add(index)

    entStart = starts[index]
    entEnd = ends[index]

    altIndex = index + 1
    while altIndex < len(words):
        curList = entityLists[altIndex]
        found = False
        for parse in curList:
            if parse.begin != "I":
                continue
            curName = parse.entType + "_" + parse.subtype
            if curName == typeName and parse.head == head:
                indexes.add(altIndex)
                text += " " + words[altIndex]
                found = True
                entEnd = ends[altIndex]
                break
        if found == False:
            break

        altIndex += 1

    return text, indexes, entStart, entEnd

def scanInput(filename, parsingFilename, inputTriggers = None, entityOut = None, realisMode = False):
    print "Reading " + filename
    input = open(filename, "r")
    parsingInput = open(parsingFilename, "r")

    possibleLabels = set()
    possibleArgs = set()
    possibleArgs.add("NONE")

    words = []
    lemmas = []
    posTags = []
    labels = []

    docID = ""

    entityInfo = []
    argInfo = []

    starts = []
    ends = []

    indexConverter = dict() # converts from character offsets -> within-sentence word indexes

    count = 0
    for line in input:
        # if empty line
        if line.strip() == "":
            # if we have data, process and reset
            if len(words) > 0:
                entCandidates = extractCandidateArgs(entityInfo, words, starts, ends)

                goldArgs = extractGoldArgs(argInfo, words, indexConverter)
                for arg in goldArgs:
                    possibleArgs.add(arg.role)

                words = []
                lemmas = []
                posTags = []
                labels = []
                entityInfo = []
                argInfo = []

                starts = []
                ends = []

                realisList = []

                docID = ""

                indexConverter = dict()
        else:
            tokens = line.strip().split("\t")
            ### How to read input (by token):
            ### 0: start index, 1: end index, 2: word, 3: lemma, 4: posTag, 5: docID, 6:gold entities, 7: trigger type, 8: trigger subtype, 9: argument role, 10: trigger realis (optional)

            start = int(tokens[0])
            indexConverter[start] = len(words)

            starts.append(int(tokens[0]))
            ends.append(int(tokens[1]))

            curWord = tokens[2]
            curPOS = tokens[4]
            curLabel = tokens[7] + "_" + tokens[8]

            docID = tokens[5]

            words.append(curWord)
            lemmas.append(tokens[3])
            posTags.append(curPOS)

            if inputTriggers != None:
                labels.append(inputTriggers[count])
            else:
                labels.append(curLabel)

            if len(tokens) >= 11:
                realisList.append(tokens[10])

            curEnt = readEntities(tokens[6])
            entityInfo.append(curEnt)

            curArg = readArguments(tokens[9], realisMode)
            argInfo.append(curArg)

            possibleLabels.add(curLabel)

            count += 1

    return possibleLabels, possibleArgs

def readInput(input, parsingInput, inputTriggers = None, entityOut = None, count=0, realisMode = False):
    words = []
    lemmas = []
    posTags = []
    labels = []

    docID = ""

    entityInfo = []
    argInfo = []

    starts = []
    ends = []

    realisList = []

    indexConverter = dict() # converts from character offsets -> within-sentence word indexes

    eof = False

    sentence = None

    while True:
        line = input.readline()
        eof = line == ""

        # if empty line
        if line.strip() == "":
            # if we have data, process and reset
            if len(words) > 0:
                entCandidates = extractCandidateArgs(entityInfo, words, starts, ends)
                goldArgs = extractGoldArgs(argInfo, words, indexConverter)

                sentence = Sentence(words, lemmas, labels, posTags, entCandidates, goldArgs, docID, starts[0], ends[len(ends)-1], realisList, starts)

                if entityOut != None:
                    for ent in entCandidates:
                        text = ent.text
                        coref = ent.corefStr + "_" + docID
                        #print text + "\t" + coref + "\t" + str(ent.start) + "\t" + str(ent.end)
                        entityOut.write(text + "\t" + coref + "\t" + str(ent.start) + "\t" + str(ent.end) + "\n")

                words = []
                lemmas = []
                posTags = []
                labels = []
                entityInfo = []
                argInfo = []

                starts = []
                ends = []

                realisList = []

                docID = ""

                indexConverter = dict()
        else:
            tokens = line.strip().split("\t")
            ### How to read input (by token):
            ### 0: start index, 1: end index, 2: word, 3: lemma, 4: posTag, 5: docID, 6:gold entities, 7: trigger type, 8: trigger subtype, 9: argument role, 10: trigger realis (optional)

            start = int(tokens[0])
            indexConverter[start] = len(words)

            starts.append(int(tokens[0]))
            ends.append(int(tokens[1]))

            curWord = tokens[2]
            curPOS = tokens[4]
            curLabel = tokens[7] + "_" + tokens[8]

            docID = tokens[5]

            words.append(curWord)
            lemmas.append(tokens[3])
            posTags.append(curPOS)

            if inputTriggers != None:
                labels.append(inputTriggers[count])
            else:
                labels.append(curLabel)

            if len(tokens) >= 11:
                realisList.append(tokens[10])

            curEnt = readEntities(tokens[6])
            entityInfo.append(curEnt)

            curArg = readArguments(tokens[9], realisMode)
            argInfo.append(curArg)

            count += 1
        if eof or sentence != None:
            break

    if entityOut != None:
        entityOut.close()

    # add dependencies
    while True:
        line = parsingInput.readline()
        clean = line.strip()

        if clean == "":
            break
        else:
            # rare case -- we have a token "|", can't do splitting like normal
            if "||||" in clean:
                depType, gov, govIndex, dep, depIndex = parseDep_Exception(clean)
            else:
                tokens = clean.split("|||")
                depType = tokens[0]
                gov = tokens[1]
                govIndex = int(tokens[2])
                dep = tokens[3]
                depIndex = int(tokens[len(tokens) - 1])
                ###depIndex = int(tokens[4])

            # account for off-by-one (in CoreNLP, 0 = Root, rather than first word)
            curDependency = Dependency(depType, gov, govIndex - 1, dep, depIndex - 1)
            sentence.addDependency(curDependency)

    return sentence, not eof, count

# method to parse a dependency when one of the words contains "|" at the front or end
def parseDep_Exception(clean):
    # depType
    tempIndex = clean.find("|||")
    depType = clean[:tempIndex]
    clean = clean[tempIndex+3:]

    # gov word
    tempIndex = clean.find("|||")
    altIndex = clean.find("||||")
    curWord = ""
    while tempIndex == altIndex:
        curWord += clean[0]
        clean = clean[1:]

        tempIndex = clean.find("|||")
        altIndex = clean.find("||||")
    curWord += clean[:tempIndex]
    gov = curWord
    clean = clean[tempIndex+3:]

    # govIndex
    tempIndex = clean.find("|||")
    govIndex = int(clean[:tempIndex])
    clean = clean[tempIndex+3:]

    # dep word
    tempIndex = clean.find("|||")
    altIndex = clean.find("||||")
    curWord = ""
    while tempIndex == altIndex:
        curWord += clean[0]
        clean = clean[1:]

        tempIndex = clean.find("|||")
        altIndex = clean.find("||||")
    curWord += clean[:tempIndex]
    dep = curWord
    clean = clean[tempIndex+3:]

    try:
        depIndex = int(clean)
    except ValueError:
        start = clean.rfind("|")
        depIndex = int(clean[start+1:])

    return depType, gov, govIndex, dep, depIndex
