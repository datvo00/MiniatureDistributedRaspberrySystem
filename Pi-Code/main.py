import os.path
import threading
from process_queues import ProcessQueues
import signal
import sys
from comm import *

task_processor = ProcessQueues()

queue = task_processor.queue

stop_flag = False


def HandleCommand(command):
    task, filename = command.split(" ", 1)
    if task == "store":
        if not os.path.exists(filename):
            print("Error: File Does Not Exist")
            return
        queue.store(filename)
    elif task == "retrieve":
        queue.get(filename)
    elif task == "delete":
        queue.delete(filename)
    elif task == "batch":
        HandleCommandsFromFile(filename)
    elif task == "clear":
        task_processor.Clear()
    else:
        print("Error: Request Type Doesn't Exist \n")


def SecondThread():
    while not stop_flag:
        task_processor.ProcessTasks()


def signal_handler(sig, frame):
    global stop_flag
    stop_flag = True
    sys.exit(0)

def HandleCommandsFromFile(filename):
    with open(filename, "r") as f:
        line = f.readline()
        while line:
            command = line.strip()
            HandleCommand(command)
            line = f.readline()

signal.signal(signal.SIGINT, signal_handler)

thread = threading.Thread(target=SecondThread)

thread.start()

while True:
    if task_processor.queue_empty:
        command = input("Enter Command in format: store/retrieve/delete filepath: ")
        HandleCommand(command)
        time.sleep(3)

