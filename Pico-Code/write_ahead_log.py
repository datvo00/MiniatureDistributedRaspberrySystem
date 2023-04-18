class WriteAheadLog:
    def __init__(self, file):
        self.file = file
        self.filestream = open(file, "a+")

    def write(self, data):
        self.filestream.write(data + "\n")
        self.filestream.flush()

    def read(self):
        self.filestream.seek(0)
        data = self.filestream.read()
        self.filestream.seek(0, 2)
        return data

    def clear(self):
        self.filestream.close()
        with open(self.file, "w"):
            pass
