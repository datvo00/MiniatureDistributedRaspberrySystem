import select
import sys
import _thread
import machine

import uos
import os

from display import display
from lsm_tree import LSMTree

tree = LSMTree(4)


def HandleID():
    serial_id = machine.unique_id()
    serial_id = "".join("%02x" % b for b in serial_id)
    print(serial_id)


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
        HandleDelete(commands[1])
    elif commands[0] == "id":
        HandleID()
    elif commands[0] == "clear":
        tree.lock.acquire()
        delete_except_py(".")
        tree.lock.release()


def delete_except_py(path='.'):
    try:
        for file in os.listdir(path):
            file_path = path + '/' + file
            stat = os.stat(file_path)

            if stat[0] & 0x4000:
                delete_except_py(file_path)
                os.rmdir(file_path)
            else:
                if not file.endswith('.py'):
                    os.remove(file_path)
    except OSError:
        pass


def HandleSecondThread():
    global tree
    while True:
        tree.merge()


display("Idle", uos.statvfs("/"))

_thread.start_new_thread(HandleSecondThread, ())

poll_object = select.poll()
poll_object.register(sys.stdin, select.POLLIN)

while True:
    if poll_object.poll():
        command = sys.stdin.readline()
        command = command[:-1]
        HandleCommand(command)


