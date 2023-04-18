import sys
sys.path.append("../")
from bloom_filter import BloomFilter


def test_bloom_filter():
    # Create a Bloom filter with size 10000 and hash count 7
    bf = BloomFilter(1000)

    # Add 1000 elements to the filter
    for i in range(1000):
        bf.insert(str(i))

    # Check that all added elements are in the filter
    for i in range(1000):
        assert bf.contains(str(i)), f"Element {i} not found in Bloom filter"

    # Check that some non-added elements are not in the filter (with a low false positive rate)
    false_positives = 0
    for i in range(1000, 2000):
        if bf.contains(str(i)):
            false_positives += 1
    fpr = false_positives / 1000
    assert fpr < 0.02, f"False positive rate too high: {fpr}"


test_bloom_filter()
