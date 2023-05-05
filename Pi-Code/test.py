from comm import *
command = ""

#while command != "exit":
connected_devices = GetConnectedDevices()

print(connected_devices)

response = SendMessage(COM7, "store AWIN10 KID BEATER2")
response = SendMessage(COM7, "store AWIN20 KID BEATER3")
response = SendMessage(COM7, "store AWIN30 KID BEATER4")
response = SendMessage(COM7, "store AWIN40 KID BEATER5")
response = SendMessage(COM7, "store AWIN50 KID BEATER6")
response = SendMessage(COM7, "store AWIN60 KID BEATER7")
response = SendMessage(COM7, "store AWIN70 KID BEATER8")
response = SendMessage(COM7, "store AWIN80 KID BEATER9")
response = SendMessage(COM7, "store AWIN90 KID BEATER10")
response = SendMessage(COM7, "store AWIN100 KID BEATER11")

# response = SendMessage(connected_devices[0], "delete AWIN90")

# print(response)
# response = SendMessage(connected_devices[0], "retrieve AWIN90")
# print(response)

