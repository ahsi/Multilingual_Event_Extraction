import sys

def main():

    if len(sys.argv) != 4:
        print "Expect input, output, $PWD."
        sys.exit()

    input = open(sys.argv[1], "r")
    output = open(sys.argv[2], "w")
    pwd = sys.argv[3]

    for line in input:
        output.write(pwd + line[1:])
    input.close()

    output.close()

main()
