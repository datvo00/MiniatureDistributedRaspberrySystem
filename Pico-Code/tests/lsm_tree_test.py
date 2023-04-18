from lsm_tree import LSMTree
import _thread


def test1():
    '''
    Testing one insert, then retrieval
    '''
    tree = LSMTree(10)
    tree.store("test", "hello")
    result = tree.retrieve("test")
    assert result == "hello"
    tree.clear_tree()
    print("test1 finished")


def test2():
    '''
    Testing eleven inserts, then retrieving,
    this will store the keys in sstable and one in memtable
    '''
    tree = LSMTree(10)
    for i in range(11):
        tree.store(str(i), str(i))
    for i in range(11):
        result = tree.retrieve(str(i))
        assert result == str(i)
    tree.clear_tree()
    print("test2 finished")


def test3():
    '''
    Storing 50 elements, utilizing second core for merging.
    No way to stop second core, so after this test, pico must be manually stopped.
    '''
    tree = LSMTree(10)

    def second_thread():
        while True:
            tree.merge()

    second_thread = _thread.start_new_thread(second_thread, ())

    for i in range(50):
        tree.store(str(i), str(i))
    for i in range(50):
        data = tree.retrieve(str(i))
        assert data == str(i)
    print("test3 finished")


'''
Simple tests
'''

test1()
test2()
test3()

