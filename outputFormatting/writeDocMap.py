# script to write the docmap file
import sys

def getRootname(line):
	# first, remove any absolute path
	text = line
	if "/" in text:
		start = text.rfind("/") + 1
		text = text[start:]
	
	# remove the extension
	if "." in text:
		end = text.rfind(".")
		text = text[:end]

	return text

def main():
	if len(sys.argv) != 2:
		print "Expect list of documents with absolute paths."
		sys.exit()

	input = open(sys.argv[1], "r")
	lines = []
	for line in input:
		lines.append(line.strip())
	input.close()

	output = open("documents.paths.tmp", "w")
	for line in lines:
		rootname = getRootname(line)
		output.write(rootname + "\t" + line + "\n")
	output.close()

	output = open("documents.rootnames.tmp", "w")
	for line in lines:
		rootname = getRootname(line)
		output.write(rootname + "\n")
	output.close()
	

main()
