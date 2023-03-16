# counts each character in the string and stores in map, returns a string
def mapper(dataStr):
    charMap = {}
    for char in dataStr:
        if char not in charMap.keys():
            charMap[char] = 0
        charMap[char] += 1
    totalStr = ""
    for key, value in charMap.items():
        totalStr += str(key) + "=" + str(value) + " "
    totalStr = totalStr[:-1]
    return totalStr
