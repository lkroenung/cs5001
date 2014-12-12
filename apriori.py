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
    return (numerator/denominator)

########################
# read in a .arff file #
########################

print ""
filename = raw_input("Name of the input file: ")
if not filename.lower().endswith(".arff"):
    print "The file must be of type .arff"
    sys.exit()
else:
    # open the file and read all the lines in, getting rid of new lines and discarding blank lines
    datasetFile = open(filename, "r")
    datasetLines = [line.strip('\n') for line in datasetFile.readlines() if line.strip('\n') != '']

# get input from the user
minCoverage = 0
while minCoverage < 1:
    minCoverage = raw_input("Minimum coverage (1-n): ")
    try:
        minCoverage = int(minCoverage)
    except ValueError:
        minCoverage = 0
    if int(minCoverage) < 1:
        print "Min coverage should be 1 or more, try again:"

maxSize = 0
while maxSize < 1:
    maxSize = raw_input("Maximum size of sets to consider (1-n): ")
    try:
        maxSize = int(maxSize)
    except ValueError:
        maxSize = 0
    if int(maxSize) < 1:
        print "Max size should be 1 or more, try again:"

minAccuracy = -1
while minAccuracy < 0 or minAccuracy > 1:
    minAccuracy = raw_input("Minimum accuracy (0.0-1.0): ")
    try:
        minAccuracy = float(minAccuracy)
    except ValueError:
        minAccuracy = -1
    if float(minAccuracy) < 0 or float(minAccuracy) > 1:
        print "Min accuracy should be between 0-1, try again:"

reportNumber = -1
while reportNumber <= 0 and reportNumber != 'all':
    reportNumber = raw_input("Number of rules to report back (1-n, 'all'): ")
    if reportNumber != 'all':
        try:
            if int(reportNumber) <= 0:
                reportNumber = -1
        except ValueError:
            reportNumber = -1
        if int(reportNumber) < 1:
            print "Report number should be an integer above 0 or 'all', try again:"

dataStart = False
dataset = []
attributes = {}
decision = None
index = 0

# for each line from the file
for line in datasetLines:
    # if we passed "@data", the lines after are our instances
    if line.lower().startswith("%"):
        dataStart = False
    if dataStart == True:
        dataset.append(line)
    # if line starts with @relation
    if line.lower().startswith("@relation"):
        pass
    # if a line starts with @attribute
    # add it to the attribute dict with its respective options and index (used later)
    elif line.lower().startswith("@attribute"):
        attributeMatch = re.search('(?<=@attribute) (\w+)', line, re.IGNORECASE)
        optionsMatch = re.search(r'{(.*)}', line)
        if optionsMatch:
            optionsList = optionsMatch.group(0).lstrip('{').rstrip('}').split(',')
            optionsList = [x.strip() for x in optionsList]
            attributes[attributeMatch.group(0).strip()] = {
                'index': index,
                'options': optionsList
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
    elif line.lower() == "@data":
        dataStart = True

# find all of the options in the data instances for attributes that are numeric
for attribute, attrDict in attributes.items():
    if attrDict['options'] == 'real' or attrDict['options'] == 'REAL':
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
print "All sets that meet Minimum Coverage and are no more than the Max Size of Item Sets (" + str(maxSize) + "):"
print ""
for each in sets:
    print "Item set: ", ", ".join([str(x) for x in each]), "   Coverage: ", determineCoverage(dataset, attributes, each)


rules = []
# create all possible rules that have a single consequent
for itemset in sets:
    # if the item-set is longer than one, we need to manually account for if _ then all
    if len(itemset) > 1:
        newRule = Rule([], itemset)
        if determineAccuracy(dataset, attributes, newRule) >= minAccuracy:
            rules.append(newRule)

    # for each combination of rules
    for x in itemset:
        indexOfEach = itemset.index(x)
        newRule = Rule(itemset[:indexOfEach]+itemset[indexOfEach+1:], [x])
        if determineAccuracy(dataset, attributes, newRule) >= minAccuracy and newRule not in rules:
            # passes min accuracy
            rules.append(newRule)

currentConsequentSize = 1
addRules = []
stillRules = True

while stillRules:
    # find all rules with current consequent size and more than 1 in antecedent
    currentRules = [rule for rule in rules if len(rule.consequent) == currentConsequentSize and len(rule.antecedent) > 1]
    addRules = []
    # if there are any rules that meet current rule requirements
    if currentRules:
        for rule in currentRules:
            # move over every itemset in antecedent once seperately to make new rules
            for each in rule.antecedent:
                indexOfEach = rule.antecedent.index(each)
                newRule = Rule(rule.antecedent[:indexOfEach]+rule.antecedent[indexOfEach+1:], rule.consequent + [each])
                if determineAccuracy(dataset, attributes, newRule) >= minAccuracy and newRule not in addRules:
                    # passes min accuracy
                    addRules.append(newRule)
    else:
        stillRules = False
    currentConsequentSize += 1
    rules.extend(addRules)

print ""
# sort and print out the final rules
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
