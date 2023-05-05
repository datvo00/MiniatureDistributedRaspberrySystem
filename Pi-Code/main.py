import os.path
import threading
from process_queues import ProcessQueues
import signal
import sys

task_processor = ProcessQueues()

queue = task_processor.queue

stop_flag = False

def HandleCommand(command):
    task, filename = command.split(" ", 1)

    if task == "store":
        if not os.path.exists(filename):
            print("Error: File Does Not Exist")
        queue.store(filename)
        if queue.delete_queue[filename]:
            queue.delete_queue.remove(filename)

    elif task == "get":
        queue.get(filename)
        if filename in queue.store_queue:
            data = queue.store_queue[filename]
            # store right away

    elif task == "delete":
        queue.delete(filename)

    else:
        print("Error: Request Type Doesn't Exist ")


def SecondThread():
    while not stop_flag:
        task_processor.ProcessTasks()


def signal_handler(sig, frame):
    global stop_flag
    stop_flag = True
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

thread = threading.Thread(target=SecondThread)

thread.start()

while True:
    # single store request
    command = input("Enter Command in format: store/retrieve/delete filepath: ")
    HandleCommand(command)
