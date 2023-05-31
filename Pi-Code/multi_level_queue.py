from queue import Queue
from crash_recovery_log import CrashRecoveryLog
import time
import uuid


class MultiLevelQueue:

    def __init__(self):
        self.get_queue = Queue()
        self.store_queue = {}
        self.delete_queue = {}
        self.crash_recovery_log = CrashRecoveryLog()
        self.crash_recovery_log.RecoverQueues(self.store_queue, self.delete_queue)

    def get(self, key):
        self.get_queue.put(key)

    def store(self, key):
        timestamp = f"{time.time_ns()}-{uuid.uuid4()}"
        self.store_queue[key] = timestamp
        self.crash_recovery_log.AppendStore(key, timestamp)

    def delete(self, key):
        timestamp = f"{time.time_ns()}-{uuid.uuid4()}"
        self.delete_queue[key] = timestamp
        self.crash_recovery_log.AppendDelete(key, timestamp)

    def GetRetrieveTask(self):
        task = self.get_queue.queue[0]
        return task

    def GetStoreTask(self):
        task = next(iter(self.store_queue))
        return str(task), self.store_queue[task]

    def GetDeleteTask(self):
        task = next(iter(self.delete_queue))
        return str(task), self.delete_queue[task]

    def PopGetQueue(self):
        self.get_queue.get()

    def PopStoreQueue(self):
        k = next(iter(self.store_queue))
        self.crash_recovery_log.AppendCompleteStore(k, self.store_queue[k])
        self.store_queue.pop(k)

    def PopDeleteQueue(self):
        k = next(iter(self.delete_queue))
        self.crash_recovery_log.AppendCompleteDelete(k, self.delete_queue[k])
        self.delete_queue.pop(k)
