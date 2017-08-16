#!/usr/bin/env python3.6

from reader import DataReader
from writer import DataWriter
from utils import print_json
import json
import logging
import time


def read_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)

    return config


class Controller:
    def __init__(self, config):
        self.config = config
        self.reader = DataReader(self.config)
        self.writer = DataWriter(self.config)

    def run(self):
        period = self.config['period']

        self.reader.connect()

        while True:
            results = self.reader.read()
            self.writer.write(results)

            time.sleep(period)


def main():
    #logging.basicConfig(level=logging.INFO)
    #logger = logging.getLogger(__name__)

    config = read_config("config.json")

    controller = Controller(config)

    controller.run()


if __name__ == '__main__':
    main()
