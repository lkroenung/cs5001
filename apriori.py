# Lauren Kroenung & John Tegtmeyer

import sys
import re

class Rule():
    def __init__(self, ant, cons):
        self.antecedent = sorted(ant)
        self.consequent = sorted(cons)
    def __eq__(self, other):
        return (self.antecedent == other.antecedent and self.consequent == other.consequent)
    def __repr__(self):
        return "Rule:  if " + (", ".join([str(x) for x in self.antecedent]) if self.antecedent != [] else '_') + " then " + ", ".join([str(x) for x in self.consequent])

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

# determine the accuracy of a rule
def determineAccuracy(dataset, attributes, rule):
    # instances where ALL CONDITIONS in the rule are true
    # divided by
    # instance where only conditions in ANTECENDENT are true

    numerator = float(determineCoverage(dataset, attributes, rule.antecedent + rule.consequent))
    denominator = float(determineCoverage(dataset, attributes, rule.antecedent))
    # print "numer: ", numerator
    # print "denom: ", denominator
    return (numerator/denominator)

print ""
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
minAccuracy = float(raw_input("Minimum accuracy: "))
reportNumber = raw_input("Number of rules to report back: ")

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
        if optionsMatch:
            attributes[attributeMatch.group(0).strip()] = {
                'index': index,
                'options': optionsMatch.group(0).lstrip('{').rstrip('}').split(', ')
            }
        else:
            attributes[attributeMatch.group(0).strip()] = {
                'index': index,
                'options': line.split()[-1].strip()
            }
        # last line is the decision attribute
        decision = attributeMatch.group(0).strip()
        index += 1
    # set dataStart if we hit "@data"
    elif line == "@data":
        dataStart = True

for attribute, attrDict in attributes.items():
    if attrDict['options'] == 'real':
        numberOptions = []
        for line in dataset:
            line2 = line.split(',')
            if line2[attrDict['index']] not in numberOptions:
                numberOptions.append(line2[attrDict['index']])
        attrDict['options'] = numberOptions


# find all 1 item-sets
sets = []
# go through the attributes dict
for key, value in attributes.items():
    # pair each attribute name with each of its options
    for each in attributes[key]['options']:
        item = []
        item.append((key, each))
        # check against minCoverage
        # print item, determineCoverage(dataset, attributes, item)
        # if this 1 item-set passes minCoverage, add it to total sets
        if determineCoverage(dataset, attributes, item) >= minCoverage:
            sets.append(item)

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
                    addSets.append(sorted(x+y))
    # add all new item-sets to total sets
    sets.extend(addSets)
    currentSize += 1

print ""
print "All sets that meet Minimum Coverage and are no more than the Max Size of Item Sets:"
print ""
for each in sets:
    print "Item set: ", ", ".join([str(x) for x in each]), "   Coverage: ", determineCoverage(dataset, attributes, each)


rules = []
# create all possible rules that have a single consequent
for itemset in sets:
    # if the item-set is longer than one, we need to manually account for if _ then all
    if len(itemset) > 1:
        newRule = Rule([], itemset)
        # print newRule, determineAccuracy(dataset, attributes, newRule)
        if determineAccuracy(dataset, attributes, newRule) >= minAccuracy:
            rules.append(newRule)

    # for each combination of rules
    for x in itemset:
        indexOfEach = itemset.index(x)
        newRule = Rule(itemset[:indexOfEach]+itemset[indexOfEach+1:], [x])
        # print newRule, determineAccuracy(dataset, attributes, newRule)
        if determineAccuracy(dataset, attributes, newRule) >= minAccuracy and newRule not in rules:
            # passes min accuracy
            rules.append(newRule)

currentConsequentSize = 1
addRules = []
stillRules = True

while stillRules:
    currentRules = [rule for rule in rules if len(rule.consequent) == currentConsequentSize and len(rule.antecedent) > 1]
    addRules = []
    if currentRules:
        for rule in currentRules:
            for each in rule.antecedent:
                indexOfEach = rule.antecedent.index(each)
                newRule = Rule(rule.antecedent[:indexOfEach]+rule.antecedent[indexOfEach+1:], rule.consequent + [each])
                # print newRule, determineAccuracy(dataset, attributes, newRule)
                if determineAccuracy(dataset, attributes, newRule) >= minAccuracy and newRule not in addRules:
                    # passes min accuracy
                    addRules.append(newRule)
    else:
        stillRules = False
    currentConsequentSize += 1
    rules.extend(addRules)

print ""
finalRules = [[each, determineAccuracy(dataset, attributes, each)] for each in rules]
finalRules.sort(key=lambda x: x[1])
finalRules.reverse()

if reportNumber.lower() == 'all':
    print "Reporting back all association rules that meet requirements:"
    print ""
    for each in finalRules:
        print each[0], "   Confidence: ", each[1]
    print ""
else:
    reportNumber = int(reportNumber)
    print "Reporting back the most accurate ", reportNumber, " association rules that meet requirements:"
    print ""
    for each in finalRules[:reportNumber]:
        print each[0], "   Confidence: ", each[1]
    print ""
