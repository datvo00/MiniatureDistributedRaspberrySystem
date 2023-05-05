import glob
import serial
import select
import time

DEVICE_PATH_PI = "COM*"

def SendMessage(device, message):
    device_serial = serial.Serial(device, 9600)
    poll = select.poll()
    poll.register(device_serial, select.POLLIN)
    start_time = time.time()
    # assume pico is dead after 5 seconds
    while (time.time() - start_time) < 5:
        device_serial.write(f"{message}\n".encode()) # makes id request
        events = poll.poll(500) # waits 0.5 second for response
        for fd, status in events:
            if status & select.POLLIN:
                response = device_serial.read_all()
                response = response.decode("utf-8", "ignore")
                return response
    return ""


def GetConnectedDevices():
    devices = glob.glob(DEVICE_PATH_PI)
    return devices
