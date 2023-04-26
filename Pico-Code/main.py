import select
import sys
import _thread

from display import display
from lsm_tree import LSMTree

# tree = LSMTree(4)


def HandleStore(data):
    global tree
    key, value = data.split(" ", 1)
    tree.store(key, value)
    print("store finished")

def HandleRetrieve(data):
    global tree
    print(tree.retrieve(data))


def HandleDelete(data):
    global tree
    tree.delete(data)
    print("delete finished")

def HandleCommand(command):
    commands = command.split(" ", 1)
    if commands[0] == "store":
        HandleStore(commands[1])
    elif commands[0] == "retrieve":
        HandleRetrieve(commands[1])
    elif commands[0] == "delete":
        HandleRetrieve(commands[1])


def HandleSecondThread():
    global tree
    while True:
        tree.merge()

# _thread.start_new_thread(HandleSecondThread, ())

# display("Idle")
#
# while True:
#     if select.select([sys.stdin], [], [], 1)[0]:
#         command = sys.stdin.readline()
#         command = command[:-1]
#         display(command)
#         HandleCommand(command)

