import glob
import serial
import select

DEVICE_PATH_PI = "/dev/ttyACM*"

def DeviceID(device):
    device_serial = serial.Serial(device, 9600)
    poll = select.poll()
    poll.register(device_serial, select.POLLIN)
    comm_attempt = 1
    while comm_attempt <= 3:
        device_serial.write("id \n".encode()) # makes id request
        events = poll.poll(500) # waits 0.5 second for response
        for fd, status in events:
            if status & select.POLLIN:
                device_id = device_serial.read_all()
                device_id = device_id.decode("utf-8", "ignore")
                return device_id
        comm_attempt = comm_attempt + 1
    return ""


def ConnectedDevices():
    device_list = {}
    devices_path = glob.glob(DEVICE_PATH_PI)
    for device in devices_path:
        print(device)
        device_id = DeviceID(device)
        if len(device_id) > 0:
            device_list[device_id] = device
    return device_list
    