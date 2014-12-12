# Lauren Kroenung & John Tegtmeyer

import sys
import re
import copy

class node:
    def __init__(self, value, frequency, parent):
        self.frequency = frequency
        self.parent = parent
        self.children = []
        self.value = value
        self.count = 0
        self.originalCount = None

    def __str__(self):
        return "Node:  value = " + str(self.value) + ", count = " + str(self.count)  + ", frequency = " + str(self.frequency)

    def __repr__(self):
        return str(self.value)

    def printTree(self, level=0):
        ret = "\t"*level+repr(self.value)+"\n"
        for child in self.children:
            ret += child.printTree(level+1)
        return ret

    def addChild(self, _child):
        # add child node to list of children
        self.children.append(_child)
        # sort the children so that the child with the highest count is fist
        for child in self.children:    
            sorted = False
            while not sorted: # bubble sort
                sorted = True
                for i in xrange(len(self.children)-1):
                    if self.children[i].count < self.children[i+1].count:
                        sorted = False
                        self.children[i], self.children[i+1] = self.children[i+1], self.children[i]
        # increment the count of this node because it has one additional child
        self.count = self.count + 1

    def incrementCount(self):
        self.count = self.count + 1

    def makeCurrentCountOriginal(self):
        # save the current count of each node
        # this is usefull because when we start to manipulate the tree
        # we need to restore it's original counts each time we iterate
        # this function saves the count values for later
        self.originalCount = self.count
        for child in self.children: # recurse down
            child.makeCurrentCountOriginal()

    def restoreOriginalCount(self):
        # restores the count in originalCount for purposes described above
        self.count = self.originalCount
        for child in self.children:
            child.restoreOriginalCount()

    def containsChild(self, attribute):
        # if this node has a child with the same attribute as the given attribute
        #   return that child
        # else return None
        if self.children == None:
            return None
        for child in self.children:
            if child.value == attribute:
                return child

# dict containing attributes and their frequency
class OneItemSets:
    def __init__(self):
        self.dict = {}

    def addItemWithFrequency(self, item, frequency):
        # add the item to the dict with frequency as its value
        temp = str( str(item[0][0]) + str(item[0][1]) )
        self.dict.update({temp: frequency})

    def getFrequencyForItem(self, item):
        # returns the frequency of the one item set
        # this makes searching much faster for larger datasets
        #   after the value is generated the first time
        return self.dict.get(str(str(item[0]) + str(item[1])))

class Rule():
    def __init__(self, ant, cons):
        self.antecedent = ant
        self.consequent = cons
        (self.antecedent).sort()
        (self.consequent).sort()

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

def buildTree(_node, instance, attribute, sets):
    child = _node.containsChild(attribute)
    # check to see if passed in node has this attribute as a child already
    if child:
        _node.incrementCount()
        # is there another attribute in this instance?
        if instance.index(attribute) < len(instance)-1:
            buildTree(child, instance, instance[instance.index(attribute)+1], sets)
        else:
            return
    # if the attribute is not in this node's children, add it
    else:
        newNode = node(attribute, sets.getFrequencyForItem(attribute), _node)
        _node.addChild(newNode)
        # is there another attribute in this instance?
        if instance.index(attribute) < len(instance)-1:
            buildTree(newNode, instance, instance[instance.index(attribute)+1], sets)
        else:
            return

# do breadth first search
# if node attribute has not been encountered before, add it and make that node the header
# else add that node as the next node in the list for that attribute
def createHeaderTable(_node, headerTable):
    # if not the root node
    if _node.value:
        found = False
        for entry in headerTable:
            if entry[0].value == _node.value:
                found = True
                # link this node in the header table
                entry.append(_node)
        if not found:
            # add node and make it the header
            headerTable.append( [_node] )
    for child in _node.children:
        createHeaderTable(child, headerTable)
    return

# changes the count attribute of each node so that it reflects the number of times it's children
# have the attribute given
def extendTree(_node, attribute): # [TODO] check this function
    if _node.children:
        _node.count = 0
        # recurse down
        for child in _node.children:
            _node.count = _node.count + extendTree(child, attribute)
        return _node.count
    else:
        if _node.value == attribute:
            return _node.count
        else:
            _node.count = 0
            return _node.count

# removes all nodes in tree with the given attribute
# assumes that the attribute given is a leaf node
def removeAllNodesWithAttribute(_node, attribute): # [TODO] check this function
    removeMe = []
    for child in _node.children:
        if child.value == attribute:
            removeMe.append(child)
        else:
            for each in child.children:
                removeAllNodesWithAttribute(each, attribute)
    for me in removeMe:
        _node.children.remove(me)

def makeItemsetFrom(_node):
    current = _node
    itemset = []
    itemset.append(current.value)

    # while we haven't hit the root, keep going up the tree
    while current.parent != None:
        current = current.parent
        if current.value != None:
            itemset.append(current.value)

    return itemset

def findPathsInTree(root, minCoverage, dataset, attributes):
    resultingItemsets = []
    queue = [root]

    while queue:
        current = queue.pop(0)
        # this is the root of the tree, ignore it
        if current.value == None:
            for each in current.children:
                queue.append(each)
        # if node's count is higher than min coverage
        elif current.count >= minCoverage:
            itemset = makeItemsetFrom(current)
            # get rid of trivial item sets and itemsets bigger than maxSize
            if len(itemset) > 1 and len(itemset) <= maxSize:
                resultingItemsets.append(itemset)
            # continue down the tree
            for each in current.children:
                queue.append(each)

    return resultingItemsets

def buildRulesFromItemsets(itemsets, dataset, attributes, minAccuracy):
    rules = []
    # create all possible rules that have a single consequent
    for itemset in itemsets:
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

    return rules


########################
# read in a .arff file #
########################

print ""
filename = raw_input("Name of the input file: ")
if not filename.lower().endswith(".arff"):
    print "The file must be of type .arff"
    sys.exit()
else:
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

print ""

########################################
# compute frequency of each 1-item set #
########################################

# find all 1 item-sets
sets = OneItemSets()
# go through the attributes dict
for key, value in attributes.items():
    # pair each attribute name with each of its options
    for each in attributes[key]['options']:
        item = []
        item.append((key, each))
        # check against min coverage
        # if this 1 item-set passes minCoverage, add it to total sets
        if determineCoverage(dataset, attributes, item) >= minCoverage:
            sets.addItemWithFrequency(item, determineCoverage(dataset, attributes, item))

# stores the attribute names in the order presented from the input file
attributeList = []
for i in xrange(len(attributes)):
    for attribute in attributes:
        if attributes[attribute]['index'] == i:
            attributeList.append(attribute)
            break

# turning each instance into tuple of ordered values in a list
instances = []
for instance in dataset:
    items = instance.split(',')
    temp = []
    for i in xrange(len(items)):
        temp.append((attributeList[i], items[i]))
    instances.append(temp)

#################################################
# for each instance in dataset, sort attributes #
#     in descending order by frequency value    #
#################################################
for instance in instances:    
    sorted = False
    while not sorted:
        sorted = True
        for i in xrange(len(instance)-1):
            if sets.getFrequencyForItem(instance[i]) < sets.getFrequencyForItem(instance[i+1]):
                sorted = False
                instance[i], instance[i+1] = instance[i+1], instance[i]

# prune instances so that we remove non-high-frequency sets
for instance in instances:
    removeMe = []
    for attribute in instance:
        if sets.getFrequencyForItem(attribute) < minCoverage:
            removeMe.append(attribute)
    for me in removeMe:
        instance.remove(me)

###############
# create tree #
###############

root = node(None, None, None) # access tree through root
for instance in instances:
    buildTree(root, instance, instance[0], sets)
root.makeCurrentCountOriginal()

########################
# find small item sets #
########################

smallItemsets = findPathsInTree(root, minCoverage, dataset, attributes)

print ""
for each in smallItemsets:
    print each, determineCoverage(dataset, attributes, each), determineCoverage(dataset, attributes, each)
print ""

# build assocciation rules from smallItemsets and check accuracy

totalRules = buildRulesFromItemsets(smallItemsets, dataset, attributes, minAccuracy)

############################################################
# create header table and link nodes with same 1-item sets #
############################################################

headerTable = []
createHeaderTable(root, headerTable)

#########################
# find larger item sets #
#########################

largerItemsets = []

# create copy of original tree
newRoot = copy.deepcopy(root)

for header in headerTable:
    # change counts in nodes to only be the number instances in that node's subtree for which current attribute from header table is true
    extendTree(newRoot, header[0].value)

    # delete nodes from the extended FP-tree with the current attribute from the header table
    removeAllNodesWithAttribute(newRoot, header[0].value)

    # walk through this new tree and find possible item sets
    largerItemsets.extend(findPathsInTree(newRoot, minCoverage, dataset, attributes))

    # restore the original counts (but not the original tree structure)
    newRoot.restoreOriginalCount()

print "All sets that meet Minimum Coverage and are no more than the Max Size of Item Sets (" + str(maxSize) + "):"
print ""
for each in smallItemsets:
    print "Item set: ", ", ".join([str(x) for x in each]), "   Coverage: ", determineCoverage(dataset, attributes, each)
print ""

totalRules.extend(buildRulesFromItemsets(largerItemsets, dataset, attributes, minAccuracy))

# sort and print out the final rules
finalRules = [[each, determineAccuracy(dataset, attributes, each)] for each in totalRules]
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