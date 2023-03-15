from comm import ConnectedDevices

command = ""

#while command != "exit":
for i in range(0, 3):
    connected_devices = ConnectedDevices()
    print(i)
    print(connected_devices)
    print("")