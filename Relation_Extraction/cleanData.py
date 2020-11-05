import pandas as pd
import sys
import csv
import re

# Does:
#   Removes:
#       HTML tags
#       Escape characters
#       Extra spaces
#       Extra brackets
#       Extra double and single quotes
#   Replaces:
#       Multiple spaces with a single
# Input:
#   Corpus: String that holds the text that you need cleaned
# Output:
#   result8: String that has the "Removes" section removed 
#            and "Replaces" section replaced
def clean(corpus):
    result2 = re.sub("\<.*?\>", " ", corpus)
    result3 = re.sub(r"\\\w", "", result2)
    result4 = re.sub(" {2,}", " ", result3)
    result5 = re.sub("\'", "", result4)
    result6 = re.sub(r"\[ ", "", result5)
    result7 = re.sub(r" \]", "", result6)
    result8 = re.sub("\"", "", result7)
    return result8

# Does:
#   Takes a csv file and removes any unnecessary characters, 
#   then writes it to a new file
# Input:
#   csvFile:    The name of the csv file of two columns. One column 
#               for the name and the second for description
#
#   outputFile: The name of the txt file that you want the cleaned 
#               text to be outputted
# Output:
#   None
def cleanData(csvFile, outputFile):
    firstLine = True
    output = open(outputFile, 'w')
    with open(csvFile) as csvOpened:
        readCsv = csv.reader(csvOpened)
        for row in readCsv:
            # Skips the first line because its the label of the columns
            if firstLine:
                firstLine = False
                continue
            print(i)
            content = clean(row[1] + "\n")
            output.write(str(content))
        output.close()

def main():
    numOfArgs = len(sys.argv)
    if (numOfArgs > 3):
        print("Too many arguments")
    elif (numOfArgs < 3):
        print("Too few arguments")
    else:
        argList = sys.argv

        csvFile = argList[1]
        outputFile = argList[2]

        cleanData(csvFile, outputFile)

if __name__ == '__main__':
    main()
