# Relation Extraction

## cleanData.py

### How to use

'''
$ cleanData.py [inputCsv] [outputTxtFile]
'''

### Uses

- Removes:
    - HTML Tags
    - Escape characters
    - Extra spaces
    - Extra brackets
    - Extra double and single quotes
- Replaces:
    - Multiple spaces with a single space

### Input

- Csv file with two columns, where col[0] is the drug name and col[1] is the scraped text

### Output

- A text file where each row starts with the drug name and then has the scraped text after.

