# Lauren Kroenung & John Tegtmeyer

import sys
import re

class node:
    def __init__(self, value, frequency, parent):
        self.frequency = frequency
        self.parent = parent
        self.children = []
        self.value = value
        self.count = 1
    def __str__(self):
        return "Node:  value = " + str(self.value) + ", count = " + str(self.count)  + ", frequency = " + str(self.frequency)
    def __repr__(self):
        return str(self.value)
    def addChild(self, child):
        self.children.append(child)
        self.count = self.count + 1
    def incrementCount(self):
        self.count = self.count + 1
    def containsChild(self, attribute):
        # print "attribute being searched for in children of this node: ", attribute
        if self.children == None:
            return None
        for child in self.children:
            # print "searching this child: ", child
            if child.value == attribute:
                return child

class OneItemSets:
    def __init__(self):
        self.dict = {}
    def addItemWithFrequency(self, item, frequency):
        temp = str( str(item[0][0]) + str(item[0][1]) )
        self.dict.update({temp: frequency})
    def getFrequencyForItem(self, item):
        return self.dict.get(str(str(item[0]) + str(item[1])))

class Rule():
    def __init__(self, ant, cons):
        # self.antecedent = sorted(ant)
        # self.consequent = sorted(cons)
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

# [TODO] nothing calls this atm dumby
def buildTree(_node, instance, attribute, sets):
    child = _node.containsChild(attribute)
    # print "child:  ", child
    if child:
        child.incrementCount()
        # is there another attribute in this instance?
        if instance.index(attribute) < len(instance)-1:
            buildTree(child, instance, instance[instance.index(attribute)+1], sets)
        else:
            return
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

def makeItemsetFrom(node):
    current = node
    itemset = []
    itemset.append(current.value)

    while current.parent != None:
        current = current.parent
        if current.value != None:
            itemset.append(current.value)

    return itemset

def findPathsInTree(root, minCoverage):
    resultingItemsets = []
    queue = [root]

    while queue:
        current = queue.pop(0)
        # this is the root of the tree, ignore it
        if current.value == None:
            for each in current.children:
                queue.append(each)
        # if node's freq is higher than min coverage
        elif current.count >= minCoverage:
                itemset = makeItemsetFrom(current)
                # get rid of trivial item sets
                if len(itemset) > 1:
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
minCoverage = int(raw_input("Minimum coverage: "))
# maxSize = int(raw_input("Maximum size of sets to consider: ")) # [TODO] may not need this
minAccuracy = float(raw_input("Minimum accuracy: "))

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
        # print item, determineCoverage(dataset, attributes, item)
        # if this 1 item-set passes minCoverage, add it to total sets
        if determineCoverage(dataset, attributes, item) >= minCoverage:
            # sets.append(item)
            sets.addItemWithFrequency(item, determineCoverage(dataset, attributes, item))

# print ""
# print "sets.dict (OneItemSets)  ", sets.dict
# print ""
# print attributes

# stores the attribute names in the order presented from the input file
attributeList = []
for i in xrange(len(attributes)):
    for attribute in attributes:
        if attributes[attribute]['index'] == i:
            attributeList.append(attribute)
            break

# turning each instance into tuple ordered values in a list
instances = []
for instance in dataset:
    items = instance.split(',')
    temp = []
    for i in xrange(len(items)):
        temp.append((attributeList[i], items[i]))
    instances.append(temp)

# print ""
# print "instances:   ", instances
# print ""

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

########################
# find small item sets #
########################

smallItemsets = findPathsInTree(root, minCoverage)

print ""
print "Small item sets:"
print smallItemsets

###### build assocciation rules from smallItemsets and check accuracy

totalRules = buildRulesFromItemsets(smallItemsets, dataset, attributes, minAccuracy)

print ""
print "Total rules after generating rules from small item sets:"
print totalRules
print ""

############################################################
# create header table and link nodes with same 1-item sets #
############################################################

headerTable = []
createHeaderTable(root, headerTable)
for header in headerTable:
    for item in header:
        # print item
    # print ""

#########################
# find larger item sets #
#########################

largerItemsets = []

# repeat all these steps again until you reach the root as the node to be removed, cause ha dont do that

    # choose the lowest freq item set (would bottom of the header table yes)
    # change counts of this node's ancestors to reflect only the number of instances in node's subtree where chosen itemset is true
    # and remove chosen lowest itemset nodes from tree (all of them I guess)

    # Walk through this new tree and find possible item sets (findPathsInTree())
    # Do this using the function findPathsInTree() and everytime you use this function you should extend the returned results onto the list called largerItemsets
    # these newly made item sets will "include" the item set that was removed (cause the counts were changed)

    # restore the original counts (but not the original tree structure)
    # [she says to restore counts in one example but doesn't mention it in the other, confused, but i would assume restore counts]
    # remove the next lowest freq item

    # repeat steps until you reach the root as the node to be removed


# so now, you should have all found itemsets from every iteration and they should be together in largerItemsets
# use the buildRulesFromItemsets() function and pass in largerItemsets to compute all possible rules from largerItemsets

# combine the rules I found from smallItemsets (these are in totalRules list)
# and the ones you just found from largerItemsets (so just extend your results onto totalRules)

# order them in the combined list in ascending order of accuracy of the rule
# you can do this to order them:

# finalRules = [[each, determineAccuracy(dataset, attributes, each)] for each in totalRules]
# finalRules.sort(key=lambda x: x[1])
# finalRules.reverse()


# we need to ask the user for number of rules to report, this will be how many of finalRules we output to screen
# look at apriori.py if you want code for this