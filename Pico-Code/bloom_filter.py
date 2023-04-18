import array
import hashlib
import math


# (1 - e^(-hash_count * n / size))^hash_count to calculate false positive rate
class BloomFilter:
    def __init__(self, size):
        self.size = (((size * 10) + 31) // 32) * 32
        self.hash_count = 7
        self.bit_array = array.array('B', [0] * self.size)
        self.element_count = 0

    def insert(self, string):
        for seed in range(self.hash_count):
            result = hashlib.sha256(f"{seed}{string}".encode()).digest()
            index = int.from_bytes(result, 'big') % self.size
            self.bit_array[index] = 1
        self.element_count += 1

    def contains(self, string):
        for seed in range(self.hash_count):
            result = hashlib.sha256(f"{seed}{string}".encode()).digest()
            index = int.from_bytes(result, 'big') % self.size
            if self.bit_array[index] == 0:
                return False
        return True

    def set_bit_array_from_list(self, bit_array_list):
        for i in range(len(bit_array_list)):
            self.bit_array[i] = int(bit_array_list[i])

    def clear(self):
        self.bit_array = array.array('B', [0] * self.size)
        self.element_count = 0

    def false_positive_rate(self):
        numerator = (1 - math.exp(-self.hash_count * self.element_count / self.size)) ** self.hash_count
        denominator = 1 - math.exp(-self.hash_count * self.element_count / self.size)
        return numerator / denominator

    def get_bit_array(self):
        return self.bit_array


