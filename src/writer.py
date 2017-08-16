from utils import print_json


class DataWriter:
    def __init__(self, config):
        self.config = config

    def write(self, data):
        print_json(data)
        # # Write to database.
        # for result in data:
        #     print_json(result)
