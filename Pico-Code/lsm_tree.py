from bloom_filter import BloomFilter
from write_ahead_log import WriteAheadLog
from red_black_tree import RedBlackTree
from display import display
import time
import utime
import uos
import ujson
import _thread
import uhashlib
import gc


class LSMTree:
    def __init__(self, table_size):
        self.memtable = RedBlackTree()
        self.max_memtable_size = table_size
        self.bloomfilter = BloomFilter(table_size)
        self.writeaheadlog = WriteAheadLog("write_ahead_log")

        # multithreading
        self.lock = _thread.allocate_lock()
        self.second_core_busy = False

        # store in metadata
        self.sstable_level = 0

        # initialize directories and files
        self.init_directories_files()

        # crash recovery
        self.lock.acquire()
        self.restore_memtable()
        self.restore_metadata()
        self.restore_merge()
        display(self.second_core_busy, uos.statvfs("/"))
        self.lock.release()

        self.level_multipler = 2

        self.tombstone = "tomb"

        self.merge_status = {}

    def store(self, key, value):
        """ (self, str, str) -> None
        Stores a file (key) and the contents (value)
        """
        filename = str(time.time_ns())
        self.lock.acquire()
        self.writeaheadlog.write(f"{key} {filename}")
        self.lock.release()
        # key is in memtable, just replace
        if self.bloomfilter.contains(key):
            node = self.memtable.search(key)
            old_node_value = node.value
            node.value = filename
            self.lock.acquire()
            self.write_value_to_disk(f"/data/{key}/{filename}", value)
            if old_node_value != self.tombstone:
                uos.remove(f"/data/{key}/{old_node_value}")
            self.lock.release()
        else:
            self.lock.acquire()
            try:
                uos.mkdir(f"/data/{key}")
            except OSError:
                pass
            self.write_value_to_disk(f"/data/{key}/{filename}", value)
            self.lock.release()
            self.memtable.insert(key, filename)
            self.bloomfilter.insert(key)
        self.lock.acquire()
        if self.memtable.size >= self.max_memtable_size:
            self.flush_memtable_to_disk()
        display(self.second_core_busy, uos.statvfs("/"))
        self.lock.release()

    def retrieve(self, key):
        """ (self, str) -> value
        Checks in memory for the key. If it exists, return the value.
        If the key doesn't exist in memory, then the disk will be searched.
        """
        # check if in memory
        if self.bloomfilter.contains(key):
            node = self.memtable.search(key)
            if not node:
                return
            self.lock.acquire()
            if node.value == self.tombstone:
                self.lock.release()
                return None
            with open(f"/data/{key}/{node.value}", "r") as file:
                display(self.second_core_busy, uos.statvfs("/"))
                self.lock.release()
                return file.read()

        # check disk
        self.lock.acquire()
        sstable_level = self.sstable_level
        for level in range(sstable_level + 1):
            dirs = uos.listdir(f"/sstables/{level}")
            dirs.sort(reverse=True)
            for table in dirs:
                with open(f"/sstables/{level}/{table}", "r") as file:
                    line = file.readline()
                    ss_min, ss_max = line.split(" ")
                    if ss_min > key > ss_max:
                        continue
                    line = file.readline()
                    size, bitarr_str = line.split(" ", 1)
                    bitarr_list = eval(bitarr_str.strip())
                    temp_bf = BloomFilter(int(size))
                    temp_bf.set_bit_array_from_list(bitarr_list)
                    if not temp_bf.contains(key):
                        continue
                    line = file.readline()
                    while line:
                        k, v = line.split(" ", 1)
                        if k == key:
                            v = v[:-1]
                            if v == self.tombstone:
                                self.lock.release()
                                return None
                            with open(f"/data/{key}/{v}", "r") as f:
                                display(self.second_core_busy, uos.statvfs("/"))
                                self.lock.release()
                                return f.read()
                        line = file.readline()
        display(self.second_core_busy, uos.statvfs("/"))
        self.lock.release()

    def delete(self, key):
        """
        Checks if key is in memory if so, then replace the value with tomb
        otherwise, we can just add tomb to memory.
        """
        self.lock.acquire()
        self.writeaheadlog.write(f"{key} tomb")
        self.lock.release()
        if self.bloomfilter.contains(key):
            node = self.memtable.search(key)
            old_node_value = node.value
            node.value = self.tombstone
            self.lock.acquire()
            uos.remove(f"/data/{key}/{old_node_value}")
            display(self.second_core_busy, uos.statvfs("/"))
            self.lock.release()
            return
        self.memtable.insert(key, self.tombstone)
        self.bloomfilter.insert(key)
        self.lock.acquire()
        if self.memtable.size >= self.max_memtable_size:
            self.flush_memtable_to_disk()
        display(self.second_core_busy, uos.statvfs("/"))
        self.lock.release()

    def restore_memtable(self):
        """
        Reads recent inputs from the WAL, used to recovery data in memory in case of crash
        """
        data = self.writeaheadlog.read()
        for line in data.splitlines():
            key, value = line.split(" ")
            if self.bloomfilter.contains(key):
                node = self.memtable.search(key)
                node.value = value
            else:
                self.memtable.insert(key, value)
                self.bloomfilter.insert(key)

    def restore_metadata(self):
        with open("metadata", "r") as file:
            line = file.readline()
            while line:
                key, value = line.split(" ", 1)
                if key == "sstable_level":
                    sstable_level = int(value)
                    self.sstable_level = sstable_level
                line = file.readline()

    def store_metadata(self):
        with open("metadata", "w") as file:
            file.write(f"sstable_level {self.sstable_level}\n")

    def write_value_to_disk(self, filename, value):
        with open(filename, "w") as file:
            file.write(value)

    def init_directories_files(self):
        try:
            uos.mkdir("/data")
        except:
            pass
        try:
            uos.mkdir("/sstables")
            uos.mkdir("/sstables/0")
        except:
            pass
        try:
            with open("metadata", "x"):
                pass
        except:
            pass
        try:
            with open("merge_log", "x"):
                pass
        except:
            pass

    def flush_memtable_to_disk(self):
        timestamp = str(time.time_ns())
        sstable_filename = f"/sstables/0/{time.time_ns()}_{utime.ticks_ms()}"

        try:
            uos.mkdir("/sstables/0")
        except:
            pass

        with open(sstable_filename, "ab+") as file:
            min_key = self.memtable.min
            max_key = self.memtable.max
            file.write(f"{min_key} {max_key}\n")
            bitarray = self.bloomfilter.get_bit_array()
            file.write(f"{self.bloomfilter.element_count} {str(list(bitarray))}\n")
            for key, value in self.memtable.items():
                file.write(f"{key} {value}\n")

        self.store_metadata()
        self.writeaheadlog.clear()
        self.writeaheadlog = WriteAheadLog("write_ahead_log")
        self.memtable.clear()
        self.bloomfilter.clear()

    def merge_two_tables(self, table1, table2, level):
        """(self, str, str (newer table), int
        Merges table1 and table2 into a new table.
        Creates a new level if at bottom of tree.
        """
        self.second_core_busy = True

        display(self.second_core_busy, uos.statvfs("/"))

        new_level = level + 1
        try:
            uos.mkdir(f"/sstables/{new_level}")
        except:
            pass
        new_path = f"/sstables/{new_level}/{time.time_ns()}_{utime.ticks_ms()}"

        self.sstable_level = max(self.sstable_level, new_level)
        self.store_metadata()

        self.merge_status[new_path] = {"merge": True, "delete0": table1, "delete1": table2, "level": new_level}
        self.write_merge()

        with open(new_path, "w") as new_file:
            with open(table1, "r") as file1:
                with open(table2, "r") as file2:
                    # grab the min and max
                    line1, line2 = file1.readline(), file2.readline()
                    min1, max1 = line1.split(" ")
                    min2, max2 = line2.split(" ")
                    max1 = max1.strip()
                    max2 = max2.strip()

                    # skip the bloomfilter lines
                    line1, line2 = file1.readline(), file2.readline()
                    line1, line2 = file1.readline(), file2.readline()

                    # merge the sstables, write to file, priorize table2 (most up to date)
                    while line1 and line2:
                        key1, key2 = line1.split(" ")[0], line2.split(" ")[0]
                        if key1 == key2:
                            if line2.split(" ")[1] != self.tombstone:
                                new_file.write(line2)
                            value = line1.split(" ")[1]
                            value = value[:-1]
                            uos.remove(f"/data/{key1}/{value}")
                            line1 = file1.readline()
                            line2 = file2.readline()
                        elif key1 < key2:
                            if line1.split(" ")[1] != self.tombstone:
                                new_file.write(line1)
                            line1 = file1.readline()
                        else:
                            if line2.split(" ")[1] != self.tombstone:
                                new_file.write(line2)
                            line2 = file2.readline()

                    # write what's left in each file
                    while line1:
                        if line1.split(" ")[1] != self.tombstone:
                            new_file.write(line1)
                        line1 = file1.readline()
                    while line2:
                        if line2.split(" ")[1] != self.tombstone:
                            new_file.write(line2)
                        line2 = file2.readline()

        new_min = min(min1, min2)
        new_max = max(max1, max2)
        new_min_max = new_min + " " + new_max

        with open(new_path, "r") as new_file:
            merged_data = new_file.readlines()

        new_bloomfilter = BloomFilter(len(merged_data))
        for data in merged_data:
            key, value = data.split(" ")
            new_bloomfilter.insert(key)

        with open(new_path, "w") as new_file:
            new_file.write(new_min_max + "\n")
            bitarray = new_bloomfilter.get_bit_array()
            new_file.write(f"{new_bloomfilter.element_count} {str(list(bitarray))}\n")
            new_file.write("".join(merged_data))

        self.merge_status[new_path] = {"merge": False, "delete0": table1, "delete1": table2, "level": new_level}
        self.write_merge()

        uos.remove(table1)
        self.merge_status[new_path] = {"merge": False, "delete0": None, "delete1": table2, "level": new_level}
        self.write_merge()

        uos.remove(table2)
        self.merge_status = {}
        self.write_merge()

        self.second_core_busy = False

        display(self.second_core_busy, uos.statvfs("/"))

    def merge(self):
        """
        Checks if we need to merge, then performs merges if necessary
        """
        self.lock.acquire()
        for index in range(self.sstable_level + 1):
            max_num = self.level_multipler ** index
            dirs = []
            dirs = uos.listdir(f"/sstables/{index}")
            if len(dirs) > max_num:
                dirs.sort()
                self.merge_two_tables(f"/sstables/{index}/{dirs[0]}", f"/sstables/{index}/{dirs[1]}", index)
        self.lock.release()

    def write_merge(self):
        with open("merge_log", "w") as file:
            file.write(ujson.dumps(self.merge_status))

    def restore_merge(self):
        with open("merge_log", "r") as file:
            file_content = file.read()
            if len(file_content) == 0:
                return
            merge_status = ujson.loads(file_content)
            if len(merge_status) == 0:
                return
            filename = list(merge_status)[0]

            value = merge_status[filename]["merge"]
            level = merge_status[filename]["level"]

            if value == True:
                uos.remove(filename)
                with open("merge_log", "w") as file:
                    pass
                return

            level = level - 1

            value = merge_status[filename]["delete0"]
            if value is not None:
                uos.remove(value)

            value = merge_status[filename]["delete1"]
            if value is not None:
                uos.remove(value)

        # clear the file
        with open("merge_log", "w") as file:
            pass

    def remove_dir(self, path):
        """
        Recursively removes all files and subdirectories inside the specified path,
        and then removes the empty directory itself.
        """
        for file_name in uos.listdir(path):
            file_path = path + "/" + file_name
            file_stat = uos.stat(file_path)
            if file_stat[0] & 0o170000 == 0o040000:
                self.remove_dir(file_path)
            else:
                uos.remove(file_path)
        uos.rmdir(path)

    def clear_tree(self):
        try:
            uos.remove("metadata")
        except:
            pass
        try:
            uos.remove("write_ahead_log")
        except:
            pass
        try:
            self.remove_dir("/sstables")
        except:
            pass
        try:
            self.remove_dir("/data")
        except:
            pass

