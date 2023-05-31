import json
import os.path


class CrashRecoveryLog:
    def __init__(self):
        self.log_file_path = "queue_logs"
        self.complete_file_path = "complete_logs"
        self.InitFiles()

    def InitFiles(self):
        try:
            with open(self.log_file_path + "/store.txt", "x"):
                pass;
        except:
            pass
        try:
            with open(self.log_file_path + "/delete.txt", "x"):
                pass;
        except:
            pass
        try:
            with open(self.complete_file_path + "/store.txt", "x"):
                pass;
        except:
            pass
        try:
            with open(self.complete_file_path + "/delete.txt", "x"):
                pass;
        except:
            pass

    def AppendStore(self, filename, time):
        with open(self.log_file_path + "/store.txt", "a") as f:
            f.write(f"{filename} {time}\n")

    def AppendDelete(self, filename, time):
        with open(self.log_file_path + "/delete.txt", "a") as f:
            f.write(f"{filename} {time}\n")

    def AppendCompleteStore(self, filename, time):
        with open(self.complete_file_path + "/store.txt", "a") as f:
            f.write(f"{filename} {time}\n")

    def AppendCompleteDelete(self, filename, time):
        with open(self.complete_file_path + "/delete.txt", "a") as f:
            f.write(f"{filename} {time}\n")

    def repair_paths(self, queue, path, complete_path, temp_path, temp_complete_path):
        with open(path, "r") as f:
            with open(complete_path, "r") as f2:
                with open(temp_path, "a") as w:
                    with open(temp_complete_path, "a") as w2:
                        line1 = f.readline()
                        line2 = f2.readline()

                        while line1 == line2:
                            if len(line1) == 0 or len(line2) == 0:
                                break
                                # means that write didn't complete, probably last line
                            if "\n" not in line1:
                                line1 = f.readline()
                                line2 = f2.readline()
                                continue
                            if "\n" not in line2:
                                w.write(line1)
                                w2.write(line1)
                                line1 = f.readline()
                                line2 = f2.readline()
                                continue

                            w.write(line1)
                            w2.write(line2)

                            line1 = f.readline()
                            line2 = f2.readline()

                        while line1:
                            w.write(line1)
                            key, time = line1.strip().split(" ", 1)
                            queue[key] = time
                            line1 = f.readline()

        os.remove(path)
        os.rename(temp_path, path)

        os.remove(complete_path)
        os.rename(temp_complete_path, complete_path)


    def RecoverQueues(self, store_queue, delete_queue):
        store_path = self.log_file_path + "/store.txt"
        temp_store_path = self.log_file_path + "/temp_store.txt"
        complete_store_path = self.complete_file_path + "/store.txt"
        temp_complete_store_path = self.complete_file_path + "/temp_store.txt"

        if os.path.exists(temp_store_path) and not os.path.exists(store_path):
            os.rename(temp_store_path, store_path)
            return
        elif os.path.exists(temp_store_path) and os.path.exists(store_path):
            with open(temp_store_path, "w") as f:
                pass

        if os.path.exists(temp_complete_store_path) and not os.path.exists(complete_store_path):
            os.rename(temp_complete_store_path, complete_store_path)
            return
        elif os.path.exists(temp_complete_store_path) and os.path.exists(complete_store_path):
            with open(temp_complete_store_path, "w") as f:
                pass

        self.repair_paths(store_queue, store_path, complete_store_path, temp_store_path, temp_complete_store_path)

        delete_path = self.log_file_path + "/delete.txt"
        temp_delete_path = self.log_file_path + "/temp_delete.txt"
        complete_delete_path = self.complete_file_path + "/delete.txt"
        temp_complete_delete_path = self.complete_file_path + "/temp_delete.txt"

        if os.path.exists(temp_delete_path) and not os.path.exists(delete_path):
            os.rename(temp_delete_path, delete_path)
            return
        elif os.path.exists(temp_delete_path) and os.path.exists(delete_path):
            with open(temp_delete_path, "w") as f:
                pass

        if os.path.exists(temp_complete_delete_path) and not os.path.exists(complete_delete_path):
            os.rename(temp_complete_delete_path, complete_delete_path)
            return
        elif os.path.exists(temp_complete_delete_path) and os.path.exists(complete_delete_path):
            with open(temp_complete_delete_path, "w") as f:
                pass

        self.repair_paths(delete_queue, delete_path, complete_delete_path, temp_delete_path, temp_complete_delete_path)
