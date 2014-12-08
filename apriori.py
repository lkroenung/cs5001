# Lauren Kroenung & John Tegtmeyer

import sys
import re

# determine the coverage of an item-set on the dataset instances
def determineCoverage(dataset, attributes, itemset):    
    coverage = 0
    # for every line in the @data set
    for instance in dataset:
        # split the instance at the commas
        instanceItems = instance.split(',')
        covers = True
        # for each attribute in the item-set
        for item in itemset:
            # if I go through every item in itemset and they all
            # exist in this instance then coverage should increase by 1
            if instanceItems[attributes[item[0]]['index']] != item[1]:
                covers = False
        if covers == True:
            coverage += 1
    return coverage

# read in an .arff file
filename = raw_input("Name of the input file: ")
if not filename.lower().endswith(".arff"):
    print "The file must be of type .arff"
    sys.exit()
else:
    # open the file and read all the lines in, getting rid of new lines and discarding blank lines
    datasetFile = open(filename, "r")
    datasetLines = [line.strip('\n') for line in datasetFile.readlines() if line.strip('\n') != '']

# get input from the user
minCoverage = int(raw_input("Minimum coverage: "))
maxSize = int(raw_input("Maximum size of sets to consider: "))
# minAccuracy = raw_input("Minimum accuracy: ")
# reportNumber = raw_input("Number of rules to report back: ")
# if reportNumber.lower() == 'all':
#     print "Report back all rules"

print ""

dataStart = False
dataset = []
attributes = {}
decision = None
index = 0
# for each line from the file
for line in datasetLines:
    # if we passed "@data", the lines after are our instances
    if dataStart == True:
        dataset.append(line)
    # if line starts with @relation
    if line.startswith("@relation"):
        pass
    # if a line starts with @attribute
    # add it to the attribute dict with its respective options and index (used later)
    elif line.startswith("@attribute"):
        attributeMatch = re.search('(?<=@attribute) (\w+)', line)
        optionsMatch = re.search(r'{(.*)}', line)
        attributes[attributeMatch.group(0).strip()] = {
            'index': index,
            'options': optionsMatch.group(0).lstrip('{').rstrip('}').split(', ')
        }
        # last line is the decision attribute
        decision = attributeMatch.group(0).strip()
        index += 1
    # set dataStart if we hit "@data"
    elif line == "@data":
        dataStart = True

# find all 1 item-sets
sets = []
# go through the attributes dict
for key, value in attributes.items():
    # pair each attribute name with each of its options
    for each in attributes[key]['options']:
        item = []
        item.append((key, each))
        # check against min coverage
        print item, determineCoverage(dataset, attributes, item)
        # if this 1 item-set passes minCoverage, add it to total sets
        if determineCoverage(dataset, attributes, item) >= minCoverage:
            sets.append(item)
print "all 1 item sets", sets
print ""

# what size item-set we are on (starts at 2 since we just did 1 item-sets)
currentSize = 2
# get all 1 item sets
oneItemSets = [x for x in sets if len(x) == 1]
while currentSize <= maxSize:

    # get all item sets of size currentSize - 1
    # 1 + currentSize-1 will equal the size of item-set we want
    # since we are just adding on 1 item-sets each time
    currentItemSets = [x for x in sets if len(x) == currentSize-1]

    addSets = []
    # for each 1 item-set
    for x in oneItemSets:
        # for each currentSize-1 item sets
        for y in currentItemSets:
            # check to see if attribute of x is in any of the attributes in y
            # trying to make sure we arent adding 2 different values of the same attribute
            attrsY = [z[0] for z in y]
            if x[0][0] not in attrsY and sorted(x+y) not in addSets:
                # if this new item-set passes minCoverage
                if determineCoverage(dataset, attributes, sorted(x+y)) >= minCoverage:
                    print sorted(x+y), determineCoverage(dataset, attributes, sorted(x+y))
                    addSets.append(sorted(x+y))
    # add all new item-sets to total sets
    sets.extend(addSets)
    currentSize += 1

print ""
print "all sets that met minCoverage and are no more than maxSize"
print sets

'''
rule = {
    antecedent: []
    consequent: []
}
'''

for itemset in sets:
    pass


