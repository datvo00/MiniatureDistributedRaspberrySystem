from multi_level_queue import MultiLevelQueue
from encodingdecoding import *
from uhashring import HashRing
from comm import Comm
import json
import numpy as np


class ProcessQueues:
    def __init__(self):
        self.comm = Comm()

        self.devices_ids = set(self.comm.device_unique_ids.values())

        self.hash_ring = HashRing(list(self.comm.device_unique_ids.values()))

        self.queue = MultiLevelQueue()

        self.data_bits = 3
        self.parity_bits = 2

        self.encoding_matrix = self.GetEncodingMatrix()

        self.shards_map = {}
        self.devices_shard_map = {}

        self.queue_empty = True

        self.RecoverMetaData()

        self.CheckFixConnectedDevices()

    def GetEncodingMatrix(self):
        vandermonde_matrix = getVandermondeMatrix(self.data_bits, self.parity_bits)
        encoded_matrix = getEncodingMatrix(vandermonde_matrix)
        return encoded_matrix

    def EncodeData(self, data):
        data_byte_array = StringToByteArray(data)
        data_matrix = getDataMatrix(data_byte_array, self.data_bits)
        encoded_data = GetEncodedData(self.encoding_matrix, data_matrix)
        return encoded_data

    def FixHashRing(self, devices_to_remove, devices_to_add):
        for device in devices_to_remove:
            try:
                self.hash_ring.remove_node(device)
            except:
                pass
        for device in devices_to_add:
            self.hash_ring.add_node(device)

    def FixDisconnectNode(self, disconnected_node):
        data_to_move = []
        shards = set()
        for shard in self.devices_shard_map[disconnected_node]:
            data_to_move.append(shard[:-2])
            shards.add(shard)

        files_to_retrieve = set(data_to_move)

        recreated_data_to_fix = []
        for files in files_to_retrieve:
            files = files.replace("-", "/")
            data = self.ProcessGet(files)
            if len(data) > 0:
                recreated_data_to_fix.append((files, data))

        shards_to_store = {}
        for files, data in recreated_data_to_fix:
            encoded_data = self.EncodeData(data)
            for (index, data) in enumerate(encoded_data):
                data = data.tolist()
                shard_name = f"{files}_{index}"
                shard_name = shard_name.replace("/", "-")
                if shard_name in shards:
                    shards_to_store[shard_name] = data

        print("Moving recreated data to new devices")

        for shard, data in shards_to_store.items():
            node = self.hash_ring.get(shard)
            node_name = node["hostname"]

            if shard in self.devices_shard_map[node_name]:
                continue

            device_ttyACM_name = self.comm.unique_ids_device[node_name]
            response = self.comm.SendMessage(device_ttyACM_name, "id")
            if response != node_name:
                self.CheckFixConnectedDevices()
                node = self.hash_ring.get(shard)
                node_name = node["hostname"]
                device_ttyACM_name = self.comm.unique_ids_device[node_name]

            response = self.comm.SendMessage(device_ttyACM_name, f"store {shard} {str(data)}")

            while response != "store finished":
                print(f"Error storing {shard}")
                self.CheckFixConnectedDevices()
                node = self.hash_ring.get(shard)
                node_name = node["hostname"]
                device_ttyACM_name = self.comm.unique_ids_device[node_name]
                response = self.comm.SendMessage(device_ttyACM_name, f"store {shard} {str(data)}")

            if node_name in self.devices_shard_map:
                self.devices_shard_map[node_name].add(shard)
            else:
                self.devices_shard_map[node_name] = set([shard])
            print(f"Moved Data from {disconnected_node} to {node_name}")

        for shard in shards:
            self.devices_shard_map[disconnected_node].remove(shard)

        print("Finished moving recreated data")

    def FixRecoveredNode(self, recovered_node):
        data_to_move = []
        for device in self.devices_shard_map:
            for shard in self.devices_shard_map[device]:
                if self.hash_ring.get_node_hostname(shard) == recovered_node:
                    data_to_move.append((device, shard))

        for device, shard in data_to_move:
            if device == recovered_node:
                continue
            device_ttyACM_name1 = self.comm.unique_ids_device[device]
            device_ttyACM_name2 = self.comm.unique_ids_device[recovered_node]
            response = self.comm.SendMessage(device_ttyACM_name1, f"retrieve {shard}")
            response = self.comm.SendMessage(device_ttyACM_name2, f"store {shard} {response}")
            response = self.comm.SendMessage(device_ttyACM_name1, f"delete {shard}")
            self.devices_shard_map[device].remove(shard)
            if recovered_node in self.devices_shard_map:
                self.devices_shard_map[recovered_node].add(shard)
            else:
                self.devices_shard_map[recovered_node] = set(shard)

            print(f"Moved data from {device} to {recovered_node}")

        print("Finished Moving Data")

    def CheckFixConnectedDevices(self):
        self.comm.ResetHub()
        self.comm.SetConnectedDevices()
        self.comm.OpenSerialPorts()
        self.comm.GetIDs()

        old_devices = self.devices_ids
        new_devices = list(self.comm.device_unique_ids.values())

        old_devices_set = set(old_devices)

        new_devices_to_add = []
        old_devices_to_remove = []

        for device in new_devices:
            if device not in old_devices_set:
                print(f"New Device Detected: {device}")
                new_devices_to_add.append(device)
            if device in old_devices_set:
                old_devices_set.remove(device)

        for old_device in old_devices_set:
            print(f"Cannot find: {old_device}")
            old_devices_to_remove.append(old_device)

        if len(old_devices_to_remove) == 0 and len(new_devices_to_add) == 0:
            return

        print(f"Fixing HashRing")
        self.FixHashRing(old_devices_to_remove, new_devices_to_add)

        for new_device in new_devices_to_add:
            print(f"Moving data to connected device")
            self.FixRecoveredNode(new_device)

        for old_device in old_devices_to_remove:
            print(f"Recovering data from lost device")
            self.FixDisconnectNode(old_device)

        self.devices_ids = new_devices
        self.StoreMetaData()

    def StoreMetaData(self):
        with open("metadata/shards_map.txt", "w") as f:
            json.dump(self.shards_map, f)
        with open("metadata/devices_shard_map.txt", "w") as f:
            hashmap_with_lists = {key: list(value) for key, value in self.devices_shard_map.items()}
            json.dump(hashmap_with_lists, f)
        with open("metadata/devices.txt", "w") as f:
            json.dump(list(self.devices_ids), f)

    def RecoverMetaData(self):
        with open("metadata/shards_map.txt", "r") as f:
            data = f.read()
            if len(data) > 0:
                self.shards_map = json.loads(data)
        with open("metadata/devices_shard_map.txt", "r") as f:
            data = f.read()
            if len(data) > 0:
                hashmap_with_lists = json.loads(data)
                devices_shard_map = {key: set(value) for key, value in hashmap_with_lists.items()}
                self.devices_shard_map = devices_shard_map
        with open("metadata/devices.txt", "r") as f:
            data = f.read()
            if len(data) > 0:
                self.devices_ids = set(json.loads(data))

    def ProcessStore(self, filename):
        with open(filename, "r") as f:
            data = f.read()

        encoded_data = self.EncodeData(data)
        shards = {}
        self.shards_map[filename] = []

        for (index, data) in enumerate(encoded_data):
            data = data.tolist()
            shard_name = f"{filename}_{index}"
            shard_name = shard_name.replace("/", "-")
            shards[shard_name] = data
            self.shards_map[filename].append(shard_name)

        for shard, data in shards.items():
            node = self.hash_ring.get(shard)
            node_name = node["hostname"]
            device_ttyACM_name = self.comm.unique_ids_device[node_name]
            response = self.comm.SendMessage(device_ttyACM_name, "id")
            if response != node_name:
                self.CheckFixConnectedDevices()
                node = self.hash_ring.get(shard)
                node_name = node["hostname"]
                device_ttyACM_name = self.comm.unique_ids_device[node_name]

            response = self.comm.SendMessage(device_ttyACM_name, f"store {shard} {str(data)}")

            while response != "store finished":
                print(f"Error storing {shard}")
                self.CheckFixConnectedDevices()
                node = self.hash_ring.get(shard)
                node_name = node["hostname"]
                device_ttyACM_name = self.comm.unique_ids_device[node_name]
                response = self.comm.SendMessage(device_ttyACM_name, f"store {shard} {str(data)}")

            if node_name in self.devices_shard_map:
                self.devices_shard_map[node_name].add(shard)
            else:
                self.devices_shard_map[node_name] = set([shard])

        self.StoreMetaData()
        print(f"Finished Storing {filename}")

    def ProcessGet(self, filename):
        if filename not in self.shards_map:
            print("File not found in database")
            return ""
        print(f"Retrieving {filename}")
        shards = self.shards_map[filename]
        data = []
        order = []
        for shard in shards:
            # we got all the databits needed, we can stop
            if len(order) == self.data_bits:
                break
            node = self.hash_ring.get(shard)
            node_name = node["hostname"]

            if node_name not in self.comm.unique_ids_device:
                data.append("")
                continue

            device_ttyACM_name = self.comm.unique_ids_device[node_name]
            response = self.comm.SendMessage(device_ttyACM_name, "id")

            if response != node_name:
                self.CheckFixConnectedDevices()
                data.append("")
                continue

            response = self.comm.SendMessage(device_ttyACM_name, f"retrieve {shard}")

            if len(response) == 0 or response is None or response == "None":
                data.append("")
                continue

            data.append(response)
            order.append(int(shard[-1]))

        if len(order) < self.data_bits:
            print("Not enough shards, data lost")
            return ""

        data_matrix = []

        for string in data:
            if len(string) == 0:
                data_matrix.append([])
                continue
            row = [float(x) for x in string.strip('[]').split(', ')]
            data_matrix.append(row)

        data_matrix = numpy.array(data_matrix, dtype=object)

        print(f"Using Shards {order}")
        decoded_data = DecodeData(self.encoding_matrix, data_matrix, order)

        print(f"Data Retrieved: \n{decoded_data}")
        return decoded_data

    def ProcessDelete(self, filename):
        if filename not in self.shards_map:
            print("File not found in database")
            return

        shards = self.shards_map[filename]

        for shard in shards:
            node = self.hash_ring.get(shard)
            node_name = node["hostname"]

            if shard not in self.devices_shard_map[node_name]:
                continue

            device_ttyACM_name = self.comm.unique_ids_device[node_name]
            response = self.comm.SendMessage(device_ttyACM_name, "id")

            if response != node_name:
                self.CheckFixConnectedDevices()
                data.append("")
                continue

            self.comm.SendMessage(device_ttyACM_name, f"delete {shard}")

            self.devices_shard_map[node_name].remove(shard)

        print(f"Removed {filename}")
        self.shards_map.pop(filename)
        self.StoreMetaData()

    def ProcessTasks(self):
        if len(self.comm.devices) != len(self.comm.GetConnectedDevices()):
            print("Detected device count change... fixing")
            self.CheckFixConnectedDevices()

        if len(self.queue.get_queue.queue) > 0:
            self.queue_empty = False
            filename = self.queue.GetRetrieveTask()
            if filename in self.queue.store_queue:
                self.ProcessStore(filename)
                self.queue.store_queue.pop(filename)
            self.ProcessGet(filename)
            self.queue.PopGetQueue()
        elif len(self.queue.store_queue) > 0:
            self.queue_empty = False
            filename, time = self.queue.GetStoreTask()
            if filename in self.queue.delete_queue:
                if time > self.queue.delete_queue[filename]:
                    self.queue.delete_queue.pop(filename)
            self.ProcessStore(filename)
            self.queue.PopStoreQueue()
        elif len(self.queue.delete_queue) > 0:
            self.queue_empty = False
            filename, time = self.queue.GetDeleteTask()
            self.ProcessDelete(filename)
            self.queue.PopDeleteQueue()
        else:
            self.queue_empty = True

    def Clear(self):
        self.comm.Clear()
        print("Done Clearing")