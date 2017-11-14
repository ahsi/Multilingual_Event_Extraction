# script to adjust the filepaths as needed
import sys

def parseConfigFile(filename):
	input = open(filename, "r")

	embeddingPath = ""
	corenlpPath = ""
	parserPath = ""
	nerPath = ""
	for line in input:
		if line.startswith("WORD_EMBEDDING_DIR"):
			embeddingPath = line.strip().split("=")[1]
		elif line.startswith("CORENLP_DIR"):
			corenlpPath = line.strip().split("=")[1]
		elif line.startswith("MALTPARSER_DIR"):
			parserPath = line.strip().split("=")[1]
		elif line.startswith("NER_DIR"):
			nerPath = line.strip().split("=")[1]
		elif line.startswith("MODEL_DIR"):
			modelPath = line.strip().split("=")[1]
		elif line.startswith("LIBLINEAR_DIR"):
			liblinearPath = line.strip().split("=")[1]
		elif line.startswith("POS_DIR"):
			posPath = line.strip().split("=")[1]
	input.close()

	return corenlpPath, embeddingPath, parserPath, nerPath, modelPath, liblinearPath, posPath

def main():
	try:
		corenlpDir, embeddingDir, parserDir, nerDir, modelDir, liblinearDir, posDir = parseConfigFile("CONFIG.txt")
	except:
		print "Please run in same directory as CONFIG.txt."
		sys.exit()

	# update the Chinese code for running Maltparser
	curInput = open("preprocessing_2.0/processChinese.sh", "r")
	lines = []
	for line in curInput:
		lines.append(line)
	curInput.close()
	output = open("preprocessing_2.0/processChinese.sh", "w")
	for line in lines:
		if line.startswith("python") or line.startswith("java"):
			tokens = line.strip().split()
			for tok in tokens:
				if tok.startswith("python") or tok.startswith("java"):
					output.write(tok)
				elif tok.endswith(".map"):
					if "/" not in tok:
						output.write(" " + posDir + "/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + posDir + "/" + tmpToks[len(tmpToks)-1])
				elif tok.endswith(".jar"):
					if "/" not in tok:
						output.write(" " + parserDir + "/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + parserDir + "/" + tmpToks[len(tmpToks)-1])
				else:
					output.write(" " + tok)
			output.write("\n")
		elif line.startswith("cp"):
			tokens = line.strip().split()
			for tok in tokens:
				if tok == "cp":
					output.write(tok)
				elif tok.endswith(".mco"):
					if "/" not in tok:
						output.write(" " + modelDir + "/maltparser/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + modelDir + "/maltparser/" + tmpToks[len(tmpToks)-1])
				else:
					output.write(" " + tok)
			output.write("\n")
		else:
			output.write(line)
	output.close()
		
	# update the Spanish code for running Maltparser
	curInput = open("preprocessing_2.0/processSpanish.sh", "r")
	lines = []
	for line in curInput:
		lines.append(line)
	curInput.close()
	output = open("preprocessing_2.0/processSpanish.sh", "w")
	for line in lines:
		if line.startswith("python") or line.startswith("java"):
			tokens = line.strip().split()
			for tok in tokens:
				if tok.startswith("python") or tok.startswith("java"):
					output.write(tok)
				elif tok.endswith(".map"):
					if "/" not in tok:
						output.write(" " + posDir + "/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + posDir + "/" + tmpToks[len(tmpToks)-1])
				elif tok.endswith(".jar"):
					if "/" not in tok:
						output.write(" " + parserDir + "/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + parserDir + "/" + tmpToks[len(tmpToks)-1])
				else:
					output.write(" " + tok)
			output.write("\n")
		elif line.startswith("cp"):
			tokens = line.strip().split()
			for tok in tokens:
				if tok == "cp":
					output.write(tok)
				elif tok.endswith(".mco"):
					if "/" not in tok:
						output.write(" " + modelDir + "/maltparser/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + modelDir + "/maltparser/" + tmpToks[len(tmpToks)-1])
				else:
					output.write(" " + tok)
			output.write("\n")
		else:
			output.write(line)
	output.close()


	# update the output formatting code
	filenames = ["outputFormatting/English_run.sh", "outputFormatting/Chinese_run.sh", "outputFormatting/Spanish_run.sh"]
	for filename in filenames:
		curInput = open(filename, "r")
		lines = []
		for line in curInput:
			lines.append(line)
		curInput.close()
		output = open(filename, "w")
		for line in lines:
			if line.startswith("python"):
				tokens = line.strip().split()
				for tok in tokens:
					if tok.startswith("python"):
						output.write(tok)
					elif tok.endswith(".dict"):
						if "/" not in tok:
							output.write(" " + modelDir + "/liblinear/" + tok)
						else:
							tmpToks = tok.split("/")
							output.write(" " + modelDir + "/liblinear/" + tmpToks[len(tmpToks)-1])
					else:
						output.write(" " + tok)
				output.write("\n")
			else:
				output.write(line)
		output.close()

	# update the liblinear files
	filenames = ["runArguments.sh", "runArguments_providedTriggers.sh", "runRealis_providedTriggers.sh", "runRealis.sh", "runTriggers.sh"]

	curInput = open("all_predictions_4.0/code/writeTriggerLiblinear.py", "r")
	lines = []
	for line in curInput:
		lines.append(line)
	curInput.close()
	output = open("all_predictions_4.0/code/writeTriggerLiblinear.py", "w")
	for line in lines:
		if line.startswith("WORD_EMBEDDING_PATH="):
			output.write("WORD_EMBEDDING_PATH=\"" + embeddingDir + "\"\n")
		elif line.startswith("UNIV_POS_PATH="):
			output.write("UNIV_POS_PATH=\"" + posDir + "\"\n")
		else:
			output.write(line)
	output.close()

	for filename in filenames:
		liblinearInput = open("all_predictions_4.0/" + filename, "r")
		lines = []
		for line in liblinearInput:
			lines.append(line)
		liblinearInput.close()
		output = open("all_predictions_4.0/" + filename, "w")
		for line in lines:
			if line.startswith("LIBLINEAR_PATH="):
				output.write("LIBLINEAR_PATH=" + liblinearDir + "\n")
			elif line.startswith("${LIBLINEAR_PATH}") or line.startswith("python"):
				tokens = line.strip().split()
				for tok in tokens:
					if tok.startswith("${LIBLINEAR_PATH}") or tok.startswith("python"):
						output.write(tok)
					elif tok.endswith(".model") or tok.endswith(".dict"):
						if "/" not in tok:
							output.write(" " + modelDir + "/liblinear/" + tok)
						else:
							tmpToks = tok.split("/")
							output.write(" " + modelDir + "/liblinear/" + tmpToks[len(tmpToks)-1])
					else:
						output.write(" " + tok)
				output.write("\n")
			else:
				output.write(line)
		output.close()

	# update the CoreNLP filepath - English
	corenlpInput = open("preprocessing_2.0/CoreNLP_scripts/runCoreNLP_Eng.sh", "r")
	lines = []
	for line in corenlpInput:
		lines.append(line)
	corenlpInput.close()
	output = open("preprocessing_2.0/CoreNLP_scripts/runCoreNLP_Eng.sh", "w")
	for line in lines:
		if line.startswith("STANFORD_CORENLP"):
			output.write("STANFORD_CORENLP=" + corenlpDir + "\n")
		else:
			output.write(line)
	output.close()

	# update the NER filepath - English
	corenlpInput = open("preprocessing_2.0/entityExtraction/runEntities.sh", "r")
	lines = []
	for line in corenlpInput:
		lines.append(line)
	corenlpInput.close()
	output = open("preprocessing_2.0/entityExtraction/runEntities.sh", "w")
	for line in lines:
		if line.startswith("STANFORD_NER"):
			output.write("STANFORD_NER=" + nerDir + "\n")
		elif line.startswith("\tjava -mx16g -cp"):
			tokens = line.strip().split()
			output.write("\t")
			for tok in tokens:
				if tok.endswith(".gz"):
					if "/" not in tok:
						output.write(" " + modelDir + "/entities/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + modelDir + "/entities/" + tmpToks[len(tmpToks)-1])
				elif tok == "java":
					output.write(tok)
				else:
					output.write(" " + tok)
			output.write("\n")
		else:
			output.write(line)
	output.close()
	
	# update the CoreNLP filepath - Chinese
	corenlpInput = open("preprocessing_2.0/CoreNLP_scripts/runCoreNLP_Chn.sh", "r")
	lines = []
	for line in corenlpInput:
		lines.append(line)
	corenlpInput.close()
	output = open("preprocessing_2.0/CoreNLP_scripts/runCoreNLP_Chn.sh", "w")
	for line in lines:
		if line.startswith("STANFORD_CORENLP"):
			output.write("STANFORD_CORENLP=" + corenlpDir + "\n")
		else:
			output.write(line)
	output.close()

	# update the NER filepath - Chinese
	corenlpInput = open("preprocessing_2.0/entityExtraction/runEntities_Chinese.sh", "r")
	lines = []
	for line in corenlpInput:
		lines.append(line)
	corenlpInput.close()
	output = open("preprocessing_2.0/entityExtraction/runEntities_Chinese.sh", "w")
	for line in lines:
		if line.startswith("STANFORD_NER"):
			output.write("STANFORD_NER=" + nerDir + "\n")
		elif line.startswith("\tjava -mx16g -cp"):
			tokens = line.strip().split()
			output.write("\t")
			for tok in tokens:
				if tok.endswith(".gz"):
					if "/" not in tok:
						output.write(" " + modelDir + "/entities/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + modelDir + "/entities/" + tmpToks[len(tmpToks)-1])
				elif tok == "java":
					output.write(tok)
				else:
					output.write(" " + tok)
			output.write("\n")
		else:
			output.write(line)
	output.close()

	# update the CoreNLP filepath - Spanish
	corenlpInput = open("preprocessing_2.0/CoreNLP_scripts/runCoreNLP_Span.sh", "r")
	lines = []
	for line in corenlpInput:
		lines.append(line)
	corenlpInput.close()
	output = open("preprocessing_2.0/CoreNLP_scripts/runCoreNLP_Span.sh", "w")
	for line in lines:
		if line.startswith("STANFORD_CORENLP"):
			output.write("STANFORD_CORENLP=" + corenlpDir + "\n")
		else:
			output.write(line)
	output.close()

	# update the NER filepath - Spanish
	corenlpInput = open("preprocessing_2.0/entityExtraction/runEntities_Spanish.sh", "r")
	lines = []
	for line in corenlpInput:
		lines.append(line)
	corenlpInput.close()
	output = open("preprocessing_2.0/entityExtraction/runEntities_Spanish.sh", "w")
	for line in lines:
		if line.startswith("STANFORD_NER"):
			output.write("STANFORD_NER=" + nerDir + "\n")
		elif line.startswith("\tjava -mx16g -cp"):
			tokens = line.strip().split()
			output.write("\t")
			for tok in tokens:
				if tok.endswith(".gz"):
					if "/" not in tok:
						output.write(" " + modelDir + "/entities/" + tok)
					else:
						tmpToks = tok.split("/")
						output.write(" " + modelDir + "/entities/" + tmpToks[len(tmpToks)-1])
				elif tok == "java":
					output.write(tok)
				else:
					output.write(" " + tok)
			output.write("\n")
		else:
			output.write(line)
	output.close()

main()
