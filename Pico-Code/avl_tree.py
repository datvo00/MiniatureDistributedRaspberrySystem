class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    def __init__(self):
        self.root = None
        self.size = 0
        self.min = None
        self.max = None

    # get height of a node
    def height(self, node):
        if not node:
            return 0
        return node.height

    # get balance factor of a node
    def balance_factor(self, node):
        if not node:
            return 0
        return self.height(node.left) - self.height(node.right)

    # perform left rotation
    def left_rotate(self, node):
        new_root = node.right
        node.right = new_root.left
        new_root.left = node

        # update heights
        node.height = max(self.height(node.left), self.height(node.right)) + 1
        new_root.height = max(self.height(new_root.left), self.height(new_root.right)) + 1

        return new_root

    # perform right rotation
    def right_rotate(self, node):
        new_root = node.left
        node.left = new_root.right
        new_root.right = node

        # update heights
        node.height = max(self.height(node.left), self.height(node.right)) + 1
        new_root.height = max(self.height(new_root.left), self.height(new_root.right)) + 1

        return new_root

    # insert a key-value pair into the AVL tree
    def insert(self, key, value):
        def _insert(node, key, value):
            # perform BST insertion
            if not node:
                self.size += 1
                return AVLNode(key, value)

            if key < node.key:
                node.left = _insert(node.left, key, value)
            else:
                node.right = _insert(node.right, key, value)

            # update height of the node
            node.height = max(self.height(node.left), self.height(node.right)) + 1

            # check balance factor and perform rotations if necessary
            balance_factor = self.balance_factor(node)
            if balance_factor > 1:
                if self.balance_factor(node.left) < 0:
                    node.left = self.left_rotate(node.left)
                return self.right_rotate(node)
            elif balance_factor < -1:
                if self.balance_factor(node.right) > 0:
                    node.right = self.right_rotate(node.right)
                return self.left_rotate(node)

            return node

        self.root = _insert(self.root, key, value)

        if self.min is None or key < self.min:
            self.min = key
        if self.max is None or key > self.max:
            self.max = key

    # search for a key in the AVL tree and return the corresponding value
    def search(self, key):
        def _search(node, key):
            if not node:
                return None
            elif node.key == key:
                return node
            elif key < node.key:
                return _search(node.left, key)
            else:
                return _search(node.right, key)

        return _search(self.root, key)

    def print_tree(self):
        def _print_tree(node, prefix, is_left):
            if not node:
                return
            _print_tree(node.right, prefix + ("│   " if is_left else "    "), False)
            print(prefix + ("└── " if is_left else "┌── ") + str(node.key) + ":" + str(node.value) + " (" + str(
                node.height) + ")")
            _print_tree(node.left, prefix + ("    " if is_left else "│   "), True)

        _print_tree(self.root, "", False)

    def items(self):
        def _items(node):
            if not node:
                return []
            return _items(node.left) + [(node.key, node.value)] + _items(node.right)

        return _items(self.root)

    def clear(self):
        self.root = None
        self.size = 0
        self.min = None
        self.max = None

    def getSize(self):
        return self.size


