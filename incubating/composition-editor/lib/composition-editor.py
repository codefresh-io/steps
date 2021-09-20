import os
import yaml
import sys
import operator
from functools import reduce

def walkDict(dataDict, key, answer=None, sofar=None):
    if sofar is None:
        sofar = []
    if answer is None:
        answer = []
    for k,v in dataDict.items():
        if k == key:
            answer.append(sofar + [k])
        if isinstance(v, dict):
            walkDict(v, key, answer, sofar+[k])
    return answer


# Used to delete ports not required for service to service communication
def delKeysFromDict(dataDict, key):
    for path in walkDict(dataDict, key):
        dd = dataDict
        while len(path) > 1:
            dd = dd[path[0]]
            path.pop(0)
        dd.pop(path[0])


def getFromDict(dataDict, mapList):
    for k in mapList: 
        dataDict = dataDict[k]
    return dataDict


def getSpecificKeyFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList[:-1], dataDict)


# Used to update values for specific keys
def setValueInDict(dataDict, mapList, value):
    keyOrIndex = mapList[-1]
    try:
        # If the last part of mapList can be converted to an integer without error...
        convertedToInt = int(keyOrIndex)
        # then assume it represents an array index and convert it to an integer.
        keyOrIndex = convertedToInt
    except:
        # Else, assume it represents a key and leave it as a string
        pass
    getFromDict(dataDict, mapList[:-1])[keyOrIndex] = value
    return dataDict


# Used to rename key in file
def renameKeyInDict(dataDict, keyDict):
    new_dict = { }
    for key in dataDict.keys():
        new_key = keyDict.get(key, key)
        if isinstance(dataDict[key], dict):
            new_dict[new_key] = renameKeyInDict(dataDict[key], keyDict)
        else:
            new_dict[new_key] = dataDict[key]
    return new_dict


def main():

    directory = os.getenv('DIRECTORY')
    yaml_file = os.getenv('YAMLFILE')
    payload = os.getenv('PAYLOAD')
    edit_object = os.getenv('EDIT_OBJECT')
    yaml_path = os.path.join(directory, yaml_file)

    # Open YAML file for editing
    try:
        with open(yaml_path) as f:
            dataDict = yaml.safe_load(f)
    except:
        print('File Not Found')
        print(yaml_path)
        sys.exit(1)

    if edit_object == 'composition':
        # Replace version
        key = 'version'
        mapList = key.split('.')
        setValueInDict(dataDict, mapList, '3.0')
        # Remove ports
        delKeysFromDict(dataDict, 'ports')
    elif edit_object == 'key':
        # Rename Keys
        keyDict = { }
        oldKey, NewKey = payload.split(";")
        if NewKey:
            keyDict[oldKey] = NewKey
            dataDict = renameKeyInDict(dataDict, keyDict)
        # Delete key if new key is empty
        else: 
            mapList = oldKey.split('.')
            del getSpecificKeyFromDict(dataDict, mapList)[mapList[-1]]
    elif edit_object == 'value':
        # Update values
        key, value = payload.split('=')
        mapList = key.split('.')
        setValueInDict(dataDict, mapList, value)
    else:
        print(f'Edit Object: {edit_object} !Not Recognized.')
        sys.exit(1)

    # Write YAML file
    with open(yaml_path, 'w') as f:
        yaml.dump(dataDict, f)

    # Setting indicator step completed successfully to skip compose step
    file_env_to_export_path = '/meta/env_vars_to_export'

    print("Set Environment Variable COMPOSITION_MODIFIED to true")
    with open(file_env_to_export_path, 'a') as file:
        file.write("COMPOSITION_MODIFIED=true")

if __name__ == "__main__":
    main()