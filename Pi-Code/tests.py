from comm import ConnectedDevices
import mapreduce
from threading import Thread

command = ""


# while command != "exit":
def testComm():
    connected_devices = ConnectedDevices()
    print(connected_devices)


def testMultipleThreads():
    thread = Thread(target=testComm)
    thread1 = Thread(target=testComm)
    thread2 = Thread(target=testComm)
    thread3 = Thread(target=testComm)

    thread.start()
    thread1.start()
    thread2.start()
    thread3.start()

def testMapReduce():
    picoCount = len(ConnectedDevices())
    if picoCount <= 0:
        print("No Picos Connected")
        return

    data = mapreduce.readFile("mapreducetest.txt")
    print("String Read: " + data)

    arr = mapreduce.splitString(data, picoCount)
    print("Splitted String: ", arr)

    response = mapreduce.sendDataToPicos(arr)
    print("Response from Picos: ", response)

    countMap = mapreduce.reduce(response)
    print("Count Map: ", countMap)