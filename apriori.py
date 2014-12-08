# Lauren Kroenung & John Tegtmeyer

import sys
import re

def determineCoverage(dataset, attributes, itemset):    
    # send in one item set not all of them
    coverage = 0
    for instance in dataset:
        instanceItems = instance.split(',')
        # print "instance", instanceItems     # ['sunny', 'hot', 'high', 'FALSE', 'no']
        # print "itemset", itemset            # set([('play', 'yes')])
        covers = True
        for item in itemset:
            # print "item", item              # ('play', 'yes')
            # if i go through every item in itemset and they all
            # exist in this instance then coverage should increase by 1
            if instanceItems[attributes[item[0]]['index']] != item[1]:
                covers = False
        if covers == True:
            coverage += 1
    return coverage

filename = raw_input("Name of the input file: ")
if not filename.lower().endswith(".arff"):
    print "The file must be of type .arff"
    sys.exit()
else:
    datasetFile = open(filename, "r")
    datasetLines = [line.strip('\n') for line in datasetFile.readlines() if line.strip('\n') != '']

minCoverage = int(raw_input("Minimum coverage: "))
maxSize = int(raw_input("Maximum size of sets to consider: "))
# minAccuracy = raw_input("Minimum accuracy: ")
# reportNumber = raw_input("Number of rules to report back: ")
# if reportNumber.lower() == 'all':
#     print "Report back all rules"

print ""
print ""

dataStart = False
dataset = []
attributes = {}
decision = None
index = 0
for line in datasetLines:
    # print line
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

sets = []
for key, value in attributes.items():
    # print attributes[key]
    for each in attributes[key]['options']:
        item = []
        item.append((key, each))
        # check against min coverage
        print item, determineCoverage(dataset, attributes, item)
        if determineCoverage(dataset, attributes, item) >= minCoverage:
            sets.append(item)
print "all 1 item sets", sets
print ""


currentSize = 2
oneItemSets = [x for x in sets if len(x) == 1]
while currentSize <= maxSize:

    print "####### ", currentSize
    currentItemSets = [x for x in sets if len(x) == currentSize-1]

    addSets = []
    for x in oneItemSets:
        for y in currentItemSets:
            # print "current: ", x, y
            attrsY = [z[0] for z in y]
            # print "x", x[0][0]
            # # print "set", y
            # print "firsts in tuples", [hey for hey in attrsY]
            if x[0][0] not in attrsY and sorted(x+y) not in addSets:
                # print "###### adding!"
                if determineCoverage(dataset, attributes, sorted(x+y)) >= minCoverage:
                    print sorted(x+y), determineCoverage(dataset, attributes, sorted(x+y))
                    addSets.append(sorted(x+y))
    sets.extend(addSets)
    currentSize += 1
print ""
print "final"
print sets