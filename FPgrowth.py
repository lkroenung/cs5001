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
		return str(self.value)
	def addChild(self, child):
		self.children.append(child)
		self.count = self.count + 1
	def incrementCount(self):
		self.count = self.count + 1
	def containsChild(self, attribute):
		if self.children == None:
			return None
		for child in self.children:
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

# [TODO] nothing calls this atm dumby
def buildTree(_node, instance, attribute, sets):
	child = _node.containsChild(attribute)
	if child:
		child.incrementCount()
		# is there another attribute?
		if instance.index(attribute) < len(instance)-1:
			buildTree(child, instance, instance[instance.index(attribute)+1], sets)
		else:
			return
	else:
		newNode = node(attribute, sets.getFrequencyForItem(attribute), _node)
		_node.addChild(newNode)
		# is there another attribute?
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


########################
# read in a .arff file #
########################
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


# print "attributes", attributes
# print "decision", decision

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

attributeList = [] # stores the attribute names in the order presented from the input file
for i in xrange(len(attributes)):
	for attribute in attributes:
		if attributes[attribute]['index'] == i:
			attributeList.append(attribute)
			break

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

print instances

###############
# create tree #
###############
root = node(None, None, None) # access tree through root
for instance in instances:
	buildTree(root, instance, instance[0], sets)

############################################################
# create header table and link nodes with same 1-item sets #
############################################################
headerTable = []
createHeaderTable(root, headerTable)
# for header in headerTable:
# 	for item in header:
# 		print item
# 	print ""