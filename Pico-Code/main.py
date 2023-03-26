import select
import sys
import utime
import io
import machine
import os
import mapreduce
from display import display

display('Ready')


def GetSerialID():
    serial_id = machine.unique_id()
    serial_id = "".join("%02x" % b for b in serial_id)
    return serial_id


def HandleID():
    serial_id = GetSerialID()
    print(serial_id)


def HandleStore(data):
    data = data.split(" ")
    filename = data[0]
    data = data[1]
    with open(filename, 'w') as file:
        file.write(data)


def HandleDelete(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


def HandleRead(filename):
    try:
        with open(filename, 'r') as file:
            print(file.read())
    except FileNotFoundError:
        print("")


def HandleMapReduce(dataStr):
    result = mapreduce.mapper(dataStr)
    print(result)


def HandleCommand(command):
    commands = command.split(" ", 1)
    display(commands[0])
    if commands[0] == "id":
        HandleID()
    elif commands[0] == "store" and len(commands) > 1:
        HandleStore(command[1])
    elif commands[0] == "delete" and len(commands) > 1:
        HandleDelete(command[1])
    elif commands[0] == "read" and len(commands) > 1:
        HandleRead(command[1])
    elif commands[0] == "mapreduce" and len(commands) > 1:
        HandleMapReduce(commands[1])
    elif commands[0] == "output":
        print("output")


while True:
    if select.select([sys.stdin], [], [], 1)[0]:
        command = sys.stdin.readline()
        command = command[:-1]  # removes \n from end of command
        display(str(command))
        HandleCommand(command)
