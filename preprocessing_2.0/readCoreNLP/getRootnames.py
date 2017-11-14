# script to extract the relative filenames for each file in a list
import sys

def main():
    if len(sys.argv) != 3:
        print "Expect an input file, output file."
        sys.exit()

    input = open(sys.argv[1], "r")
    output = open(sys.argv[2], "w")

    for line in input:
        name = line.strip()
        if "/" in name:
            index = name.rfind("/") + 1
            name = name[index:]
        output.write(name + "\n")

    input.close()
    output.close()


if __name__ == "__main__":
    main()
