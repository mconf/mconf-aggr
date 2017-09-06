from aggregator import AggregatorCallback
from utils import print_json


class DummyReader():
    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def teardown(self):
        pass

    def run(self):
        data = input("Reading with dummy reader: ")

        return data


class DummyWriter(AggregatorCallback):
    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def teardown(self):
        pass

    def run(self, data):
        print_json(data)


class FileReader():
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    def setup(self):
        self.file = open(self.filename, 'r')

    def teardown(self):
        self.file.close()

    def run(self):
        return self.file.readline()


class FileWriter(AggregatorCallback):
    def __init__(self, filename="file_writer.txt"):
        self.filename = filename

    def setup(self):
        pass

    def teardown(self):
        print("teardown", self)

    def run(self, data):
        with open(self.filename, 'a') as f:
            f.write(str(data)+"\n")
