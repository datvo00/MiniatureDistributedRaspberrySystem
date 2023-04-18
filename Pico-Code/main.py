import _thread
import time
import select
import sys
from display import display


"""
Global Variables 
"""

second_thread_alive = False


def HandleStore(data):
    print("Store")


def HandleRetrieve(data):
    print("Retrieve")


def HandleDelete(data):
    print("Delete")


def HandleCommand(command):
    commands = command.split(" ", 1)
    if commands[0] == "store":
        HandleStore(commands[1])
    elif commands[0] == "retrieve":
        HandleRetrieve(commands[1])
    elif commands[0] == "delete":
        HandleRetrieve(commands[1])


while True:
    if select.select([sys.stdin], [], [], 1)[0]:
        command = sys.stdin.readline()
        command = command[:-1]  # removes \n from end of command
        display(str(command))
