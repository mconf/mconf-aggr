#!/usr/bin/env python3.6


import logging
import time

import mconf_aggr.cfg as cfg
from mconf_aggr.zabbix import ZabbixDataReader
from mconf_aggr.dummy import FileWriter, DummyWriter
from mconf_aggr.aggregator import Aggregator, SetupError, PublishError


def main():
    cfg.config.setup_config("config/config.json")
    cfg.config.setup_logging()

    logger = logging.getLogger(__name__)

    zabbix_reader = ZabbixDataReader()
    file_writer = FileWriter("tmp/file1.txt")
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

    zabbix_reader.setup()

    publisher = aggregator.publisher

    period = cfg.config['period']

    while True:
        try:
            data = zabbix_reader.read()

            if data: # What to publish when fetching data fails?
                try:
                    publisher.publish(data, channel='zabbix')
                except PublishError as err:
                    continue

            time.sleep(period)
        except:
            break

    aggregator.stop()
    zabbix_reader.stop()

if __name__ == '__main__':
    main()
