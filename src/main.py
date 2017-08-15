#!/usr/bin/env python3.6

from connection import ConnectionPool, ZabbixConnection
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
        self.pool = None

    def run(self):
        period = self.config['period']

        self.create_pool()

        while True:
            for conn in self.pool.connections:
                # Read from Zabbix API.
                last_values = conn.conn.item.get({"output": ["lastvalue"], "host": "mconf-live-test01", "application": "BigBlueButton"})

                # Write to database.
                for result in last_values:
                    print_json(result['lastvalue'])

            time.sleep(period)

    def create_pool(self):
        self.pool = ConnectionPool()

        for server in self.config['servers']:
            self.pool.add_connection(ZabbixConnection(server['url'],
                                                      server['login'],
                                                      server['password']))

def main():
    #logging.basicConfig(level=logging.INFO)
    #logger = logging.getLogger(__name__)

    config = read_config("config.json")

    controller = Controller(config)

    controller.run()


if __name__ == '__main__':
    main()
