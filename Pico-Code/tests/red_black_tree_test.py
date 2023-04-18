import sys
sys.path.append("../")
from red_black_tree import RedBlackTree

def test1():
    tree = RedBlackTree()
    tree.insert("sup", "hello")
    assert tree.search("sup").value == "hello"
    print("Test 1 finish")

def test2():
    tree = RedBlackTree()
    for i in range(50):
        tree.insert(str(i), str(i))
    for i in range(50):
        assert tree.search(str(i)).value == str(i)
    print("Test 2 Finish")

def test3():
    tree = RedBlackTree()
    for i in range(50):
        tree.insert(str(i), str(i))
    for i in range(51, 100):
        result = tree.search(str(i))
        if result:
            assert tree.search(str(i)).value != str(i)
    print("Test 2 Finish")


test1()
test2()
test3()