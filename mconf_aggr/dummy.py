#!/usr/bin/env python3.6


import json
import time

from .aggregator import AggregatorCallback


def print_json(obj):
    print(json.dumps(obj, indent=True))


class UserReader():
    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    def teardown(self):
        pass

    def read(self):
        data = input("reading: ")

        return data


class CounterReader():
    def __init__(self):
        super().__init__()

    def setup(self, start, end):
        self.counter = start
        self.end = end

    def teardown(self):
        pass

    def read(self):
        data = self.counter if self.counter < self.end else None
        self.counter += 1

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

    def read(self):
        return self.file.readline()


class FileWriter(AggregatorCallback):
    def __init__(self, filename="file_writer.txt"):
        self.filename = filename

    def setup(self):
        pass

    def teardown(self):
        pass

    def run(self, data):
        with open(self.filename, 'a') as f:
            f.write(str(data) + "\n")

class DbWriter(AggregatorCallback):
    def __init__(self, filename="db.txt"):
        self.filename = filename

    def setup(self):
        pass

    def teardown(self):
        pass

    def run(self, data):
        time.sleep(2)
        with open(self.filename, 'a') as f:
            f.write(str(data) + "\n")
