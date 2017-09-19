#!/usr/bin/env python3.6


import time
import logging

import mconf_aggr.cfg as cfg
from mconf_aggr.dummy import UserReader, DbWriter
from mconf_aggr.aggregator import Aggregator, SetupError, PublishError


def main():
    cfg.config.setup_config("config/config.json")
    cfg.config.setup_logging()

    logger = logging.getLogger(__name__)

    reader = UserReader()
    writer = DbWriter()

    aggregator = Aggregator()
    aggregator.register_callback(writer, channel='db')


    try:
        aggregator.setup()
    except SetupError:
        exit(1)

    reader.setup()

    publisher = aggregator.publisher

    period = cfg.config['period']

    while True:
        try:
            data = reader.read()

            if data: # What to publish when fetching data fails?
                try:
                    publisher.publish(data, channel='db')
                except PublishError as err:
                    continue

            #time.sleep(period)
        except:
            break

    aggregator.stop()
    reader.teardown()

if __name__ == '__main__':
    main()
