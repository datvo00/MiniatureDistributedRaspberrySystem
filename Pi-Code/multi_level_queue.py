from queue import Queue
from thread_safe_ordered_dict import ThreadSafeOrderedDict
from thread_safe_ordered_set import ThreadSafeOrderedSet
from crash_recovery_log import CrashRecoveryLog

class MultiLevelQueue:

    def __init__(self):
        self.get_queue = Queue()
        self.store_queue = ThreadSafeOrderedSet()
        self.delete_queue = ThreadSafeOrderedSet()
        self.crash_recovery_log = CrashRecoveryLog("crash_log.txt")
        self.crash_recovery_log.recover(self.store_queue, self.delete_queue)

    def get(self, key):
        self.get_queue.put(key)
        self.crash_recovery_log.append(self.store_queue, self.delete_queue)

    def store(self, key):
        self.store_queue.add(key)
        self.crash_recovery_log.append(self.store_queue, self.delete_queue)


    def delete(self, key):
        self.delete_queue.add(key)
        self.crash_recovery_log.append(self.store_queue, self.delete_queue)


    def GetRetrieveTask(self):
        task = self.get_queue.get()
        return task

    def GetStoreTask(self):
        task = self.store_queue.pop()
        return str(task)

    def GetDeleteTask(self):
        task = self.delete_queue.pop()
        return str(task)
