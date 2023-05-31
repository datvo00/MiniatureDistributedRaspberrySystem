import glob
import serial
import select
import time
import usb.core

DEVICE_PATH_PI = "/dev/ttyACM*"


class Comm:
    def __init__(self):
        self.devices = []
        self.device_serial_map = {}
        self.device_unique_ids = {}
        self.unique_ids_device = {}

        self.ResetHub()
        self.SetConnectedDevices()
        self.OpenSerialPorts()
        self.GetIDs()

    def OpenSerialPorts(self):
        for device in self.devices:
            self.device_serial_map[device] = serial.Serial(device, 115200)

    def GetIDs(self):
        self.device_unique_ids.clear()
        self.unique_ids_device.clear()
        for device in self.devices:
            device_serial = self.device_serial_map[device]
            poll = select.poll()
            poll.register(device_serial)
            device_serial.write("id\n".encode())
            events = poll.poll(5000)
            for (fd, status) in events:
                if status > 0:
                    response = device_serial.readline()
                    response = response[:-2]
                    response = response.decode("utf-8", "ignore")
                    self.device_unique_ids[device] = response.strip()
                    self.unique_ids_device[self.device_unique_ids[device]] = device
                    poll.unregister(device_serial)

    def SendMessage(self, device, message):
        device_serial = self.device_serial_map[device]
        message = message + "\n"
        poll = select.poll()
        poll.register(device_serial)
        try:
            device_serial.write(f"{message}".encode())  # makes id request
        except:
            pass
        events = poll.poll(5000)  # waits 5 seconds for response
        start_time = time.time()
        while time.time() - start_time < 5:
            for fd, status in events:
                if status > 0:
                    try:
                        response = device_serial.readline()
                        response = response[:-2]
                        response = response.decode("utf-8", "ignore")
                        if len(response) == 0:
                            continue
                        poll.unregister(device_serial)
                        return response.strip()
                    except:
                        poll.unregister(device_serial)
                        return ""

        # no response pico dead
        poll.unregister(device_serial)
        return ""

    def Clear(self):
        for device in self.devices:
            device_serial = self.device_serial_map[device]
            message = "clear\n"
            try:
                device_serial.write(f"{message}".encode())  # makes id request
            except:
                pass
        return ""

    def SetConnectedDevices(self):
        self.devices = glob.glob(DEVICE_PATH_PI)

    def GetConnectedDevices(self):
        devices = glob.glob(DEVICE_PATH_PI)
        return devices

    def ResetHub(self):
        vid = 0x05e3
        pid = 0x0608
        pid2 = 0x0610
        hubs = []
        usb_devices = usb.core.find(find_all=True)

        for device in usb_devices:
            if device.idVendor == vid and device.idProduct == pid or device.idVendor == vid and device.idProduct == pid2:
                hubs.append(device)

        for hub in hubs:
            try:
                hub.reset()
            except Exception as e:
                pass
        time.sleep(2)

