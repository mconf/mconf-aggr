#!/usr/bin/env python3.6


import time

import mconf_aggr.cfg as cfg
from mconf_aggr.event_listener.db_operations import DataWritter
from mconf_aggr.event_listener.webhooks_listener import DataReader, app
from mconf_aggr.aggregator import Aggregator, SetupError, PublishError


def main():
    cfg.config.setup_config("config/config.json")

    db_reader = DataReader()
    db_writter = DataWritter()

    aggregator = Aggregator()
    aggregator.register_callback(db_writter, channel='webhooks')
    
    try:
        aggregator.setup()
    except SetupError:
        exit(1)

    publisher = aggregator.publisher

    db_reader.setup(publisher)

    # when?
    #aggregator.stop()
    #db_reader.stop()

if __name__ == '__main__':
    main()
