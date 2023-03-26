import textwrap
import math
import comm


# reads file from a .txt file, ignores all newlines
def readFile(file):
    with open(file, "r") as f:
        data = f.read().replace('\n', '')
    return data


# splits the string up so that each pico can have a similar amount of work to do
def splitString(string, count):
    split_num = math.ceil(len(string) / count)
    splitStringArr = textwrap.wrap(string, split_num)
    return splitStringArr


# takes in an array of the data already split, make sure the array size is same as num of picos
def sendDataToPicos(data):
    responseArr = []
    devices = comm.GetConnectedDevices()
    for index, device in enumerate(devices):
        response = comm.SendMessage(device, "mapreduce", data[index])
        responseArr.append(response)
    return responseArr


# goes through the data and adds the counts received from the picos together
def reduce(dataArr):
    charCountMap = {}
    for data in dataArr:
        cleanStr = data.replace("\n", "").replace("\r", "")
        splitStr = cleanStr.split()
        for subStr in splitStr:
            keyValuePair = subStr.split("=")
            key = keyValuePair[0]
            value = keyValuePair[1]
            if key not in charCountMap:
                charCountMap[key] = 0
            charCountMap[key] += int(value)
    return charCountMap

