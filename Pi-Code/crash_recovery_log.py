import json
import os.path


class CrashRecoveryLog:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path

    def append(self, store_queue, delete_queue):
        data = (list(store_queue), list(delete_queue))
        with open(self.log_file_path, 'w') as f:
            json.dump(data, f)

    def recover(self, store_queue, delete_queue):
        if not os.path.exists(self.log_file_path):
            return
        with open(self.log_file_path, "r") as f:
            data = json.load(f)
            for key in data[0]:
                store_queue.add(key)
            for key in data[1]:
                delete_queue.add(key)
