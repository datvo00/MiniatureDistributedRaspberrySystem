import threading
from ordered_set import OrderedSet

class ThreadSafeOrderedSet(OrderedSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()

    def add(self, item):
        with self._lock:
            super().add(item)

    def remove(self, item):
        with self._lock:
            super().remove(item)

    def discard(self, item):
        with self._lock:
            super().discard(item)

    def update(self, iterable):
        with self._lock:
            super().update(iterable)

    def pop(self):
        with self._lock:
            super().items.pop()
