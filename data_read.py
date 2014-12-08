import sys
import re

filename = raw_input("Name of the input file: ")
if not filename.lower().endswith(".arff"):
    print "The file must be of type .arff"
    sys.exit()
else:
    datasetFile = open(filename, "r")
    datasetLines = [line.strip('\n') for line in datasetFile.readlines() if line.strip('\n') != '']

dataStart = False
dataset = []
attributes = {}
decision = None
index = 0
for line in datasetLines:
    print line
    if dataStart == True:
        dataset.append(line)
    if line.startswith("@relation"):
        pass
    elif line.startswith("@attribute"):
        attributeMatch = re.search('(?<=@attribute) (\w+)', line)
        optionsMatch = re.search(r'{(.*)}', line)
        attributes[attributeMatch.group(0).strip()] = {
            'index': index,
            'options': optionsMatch.group(0).lstrip('{').rstrip('}').split(', ')
        }
        decision = attributeMatch.group(0).strip()
        index += 1
    elif line == "@data":
        dataStart = True

# print "attributes", attributes
# print "decision", decision