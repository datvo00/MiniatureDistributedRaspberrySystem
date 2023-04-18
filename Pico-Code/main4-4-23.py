import select
import sys
import utime
import io
import machine
import os
import _thread
import time
import bloom_filter
import avl_tree
import gc

from display import display

display('Ready')

lock = _thread.allocate_lock() 
second_thread_alive = False

def GetSerialID():
    serial_id = machine.unique_id()
    serial_id = "".join("%02x" % b for b in serial_id)
    return serial_id


def HandleID():
    serial_id = GetSerialID()
    print(serial_id)


def HandleStore(data):
    data = data.split(" ", 1)
    filename = data[0]
    data = data[1]
    with open(filename, 'w') as file:
        file.write(data)
        file.flush()


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
        pass


def HandleCommand(command):
    commands = command.split(" ", 1)
    display(commands[0])
    if commands[0] == "id":
        HandleID()
    elif commands[0] == "store" and len(commands) > 1:
        HandleStore(commands[1])
    elif commands[0] == "delete" and len(commands) > 1:
        HandleDelete(command[1])
    elif commands[0] == "read" and len(commands) > 1:
        HandleRead(command[1])
    elif commands[0] == "output":
        return
    global lock, second_thread_alive
    with lock:
        second_thread_alive = False
        print("Second Thread Exit")


print("b4", str(gc.mem_free()))

command = "store test.txt AWIN CHEATS"
with lock:
    second_thread_alive = True 
_thread.start_new_thread(HandleCommand, (command,))

# bloom_filter.test_bloom_filter()
# print("done")
print(gc.mem_free())
doOnce = True
while True:
    if doOnce:
        doOnce = False
        avl_tree.test_tree()
        print("--------------------")
        bloom_filter.test_bloom_filter()
    print("First Thread Alive")
    with lock:
        if second_thread_alive:
            print("Second Thread Alive")
    print(gc.mem_free())
    time.sleep(1)

# while True:
#     if select.select([sys.stdin], [], [], 1)[0]:
#         command = sys.stdin.readline()
#         command = command[:-1]  # removes \n from end of command
#         display(str(command))
#         HandleCommand(command)

