# script that takes a txt file and prepends the given string to each line
import sys

def main():
    if len(sys.argv) != 4:
        print "Expect text file, string to prepend, output file."
        sys.exit()

    input = open(sys.argv[1], "r")
    output = open(sys.argv[3], "w")

    prefix = sys.argv[2]

    for line in input:
        output.write(prefix + line)
    input.close()
    output.close()

main()
