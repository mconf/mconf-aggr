#!/usr/bin/env python3.6


import cfg
from zabbix import ZabbixDataReader
from dummy import FileWriter
from aggregator import Aggregator
import time


def main():
    cfg.config.load_config("config.json")

    zabbix_reader = ZabbixDataReader()
    file_writer1 = FileWriter("file1.txt")
    file_writer2 = FileWriter("file2.txt")

    aggregator = Aggregator()
    aggregator.register_callback(file_writer1, channel='zabbix')
    aggregator.register_callback(file_writer2, channel='zabbix')

    aggregator.setup()
    zabbix_reader.setup()

    publisher = aggregator.publisher

    while True:
        try:
            data = zabbix_reader.read()

            publisher.publish(data, channel='zabbix')

            time.sleep(5)
        except:
            break
        finally:
            aggregator.stop()

if __name__ == '__main__':
    main()
