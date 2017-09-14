#!/usr/bin/env python3.6


import cfg
from zabbix import ZabbixDataReader
from dummy import FileWriter, DummyWriter
from aggregator import Aggregator, SetupError, ChannelNotFoundError
import time
import logging


def main():
    cfg.config.setup_config("config.json")
    cfg.config.setup_logging()

    logger = logging.getLogger(__name__)

    zabbix_reader = ZabbixDataReader()
    file_writer = FileWriter("file1.txt")
    dummy_writer1 = DummyWriter()
    dummy_writer2 = DummyWriter()

    aggregator = Aggregator()
    aggregator.register_callback(file_writer, channel='zabbix')
    aggregator.register_callback(dummy_writer1, channel='zabbix')
    aggregator.register_callback(dummy_writer2, channel='zabbix')


    try:
        aggregator.setup()
    except SetupError:
        exit(1)

    zabbix_reader.start()

    publisher = aggregator.publisher

    while True:
        try:
            data = zabbix_reader.read()

            try:
                publisher.publish(data, channel='zabbix')
            except ChannelNotFoundError as err:
                pass

            time.sleep(cfg.config['period'])
        except:
            break

    aggregator.stop()
    zabbix_reader.stop()

if __name__ == '__main__':
    main()
