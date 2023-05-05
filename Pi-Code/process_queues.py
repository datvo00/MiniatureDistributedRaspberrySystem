from multi_level_queue import MultiLevelQueue
from encodingdecoding import *
from uhashring import HashRing
from comm import *

class ProcessQueues:
    def __init__(self):
        self.hash_ring = HashRing(["pico1", "pico2", "pico3", "pico4", "pico5", "pico6", "pico7", "pico8", "pico9", "pico10"])

        self.queue = MultiLevelQueue()

        self.picos = GetConnectedDevices()

        self.encoding_matrix = self.GetEncodingMatrix()

        self.shards_map = {}


    def GetEncodingMatrix(self):
        vandermonde_matrix = getVandermondeMatrix(7, 3)
        encoded_matrix = getEncodingMatrix(vandermonde_matrix)
        return encoded_matrix


    def EncodeData(self, data):
        data_byte_array = StringToByteArray(data)
        data_matrix = getDataMatrix(data_byte_array, 7)
        encoded_data = GetEncodedData(self.encoding_matrix, data_matrix)
        return encoded_data


    def ProcessStore(self):
        filename = self.queue.GetStoreTask()
        with open(filename, "r") as f:
            data = f.read()

        encoded_data = self.EncodeData(data)

        shards = {}
        for (index, data) in enumerate(encoded_data):
            shards[f"{filename}_{index}"] = data

        self.shards_map[filename] = shards

        for shard in shards:
            node = self.hash_ring.get(shard)
            response = SendMessage(node, f"store {filename} {shard}")
            if response == "store complete":
                print(f"Successfully stored: {filename}")
            # else:
                # pico ded

    def ProcessGet(self):
        filename = self.queue.GetRetrieveTask()
        shards = self.shards_map[filename]
        data = []
        order = []
        for shard in shards:
            node = self.hash_ring.get(shard)
            response = SendMessage(node, f"store {filename} {shard}")
            data.append(response)
            order.append(node)

        DecodeData(self.encoding_matrix, data, order)

    # def ProcessDelete(self):
    #     # to do

    def ProcessTasks(self):
        if len(self.queue.get_queue.queue) > 0:
            print("Processing get")
            self.ProcessGet()
        elif len(self.queue.store_queue) > 0:
            print("Processing store")
            self.ProcessStore()
        # else:
        #     self.ProcessDelete()

