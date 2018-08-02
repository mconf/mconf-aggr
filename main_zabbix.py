#!/usr/bin/env python3.6


import argparse
import logging
import time
import sys

import mconf_aggr.aggregator.cfg as cfg
from mconf_aggr.zabbix.zabbix import ZabbixDataWriter, ZabbixDataReader
from mconf_aggr.aggregator.aggregator import (Aggregator,
                                   SetupError,
                                   PublishError,
                                   AggregatorNotRunning)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="custom JSON configuration file")
    args = parser.parse_args()

    if args.config:
        cfg.config.setup_config(args.config)

    cfg.config.setup_logging()

    logger = logging.getLogger(__name__)

    zabbix_reader = ZabbixDataReader()
    zabbix_writer = ZabbixDataWriter()

    aggregator = Aggregator()
    aggregator.register_callback(zabbix_writer, channel='zabbix')


    try:
        aggregator.setup()
    except SetupError:
        sys.exit(1)

    zabbix_reader.setup()

    publisher = aggregator.publisher

    period = cfg.config.zabbix['period']

    aggregator.start()

    while True:
        try:
            data = zabbix_reader.read()

            if data: # What to publish when fetching data fails?
                try:
                    publisher.publish(data, channel='zabbix')
                except PublishError:
                    logger.warn("Something went wrong while publishing.")

                    continue
                except AggregatorNotRunning:
                    logger.info("Aggregator stopped.")

                    zabbix_reader.stop()
                    logger.info("Application finished due some failure. "
                                "Exit status 1.")
                    sys.exit(1)

            time.sleep(period)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt signal received. "
                        "Finishing application.")
            break
        except Exception as err:
            logger.error("Unexpected exception received: {}. "
                         "Finishing application".format(err))
            break

    aggregator.stop()
    zabbix_reader.stop()

    logger.info("Application finished with success. Exit status 0.")

if __name__ == '__main__':
    main()
