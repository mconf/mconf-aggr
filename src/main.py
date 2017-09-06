#!/usr/bin/env python3.6


import cfg
from zabbix import ZabbixDataReader
from dummy import FileWriter, DummyWriter
from aggregator import Aggregator
import time


def main():
    cfg.config.load_config("config.json")

    zabbix_reader = ZabbixDataReader()
    file_writer = FileWriter("file1.txt")
    dummy_writer = DummyWriter()

    aggregator = Aggregator()
    aggregator.register_callback(file_writer, channel='zabbix')
    aggregator.register_callback(dummy_writer, channel='zabbix')

    aggregator.setup()
    zabbix_reader.setup()

    publisher = aggregator.publisher

    while True:
        try:
            data = zabbix_reader.read()

            publisher.publish(data, channel='zabbix')

            time.sleep(cfg.config['period'])
        except:
            break

    aggregator.stop()

if __name__ == '__main__':
    main()
