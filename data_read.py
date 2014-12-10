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
            # print line, "within {}"
            attributes[attributeMatch.group(0).strip()] = {
                'index': index,
                'options': optionsMatch.group(0).lstrip('{').rstrip('}').split(', ')
            }
        else:
            # print line, line.split()[-1].strip()
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