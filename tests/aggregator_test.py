#!/usr/bin/env python3.6


import unittest
import os
import time

from mconf_aggr.aggregator import Aggregator
from mconf_aggr.dummy import CounterReader, FileWriter
import mconf_aggr.cfg as cfg


class TestAggregator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg.config.setup_logging()

    def setUp(self):
        self.aggregator = Aggregator()
        self.reader = CounterReader()
        self.writer = FileWriter("aggregator_test.txt")

        self.aggregator.register_callback(self.writer, channel='test')

        self.aggregator.setup()
        self.reader.setup(1, 10)
        self.writer.setup()

        self.publisher = self.aggregator.publisher


    def test_create_aggregator(self):
        try:
            os.remove("aggregator_tests.txt")
        except OSError:
            pass

        while True:
            data = self.reader.read()
            if data is None: break
            self.publisher.publish(data, channel='test')

        time.sleep(5)
        with open("aggregator_test.txt", 'r') as f:
            try:
                for expected in range(1, 10):
                    actual = int(f.readline())

                    self.assertEqual(expected, actual)
            except:
                raise
            finally:
                self.aggregator.stop()
