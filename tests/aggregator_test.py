#!/usr/bin/env python3.6


import unittest

from mconf_aggr.aggregator import Aggregator
from mconf_aggr.dummy import DummyReader, DummyWriter


class TestAggregator(unittest.TestCase):
    def setUp(self):
        reader = DummyReader()
        writer = DummyWriter()

    def test_create_aggregator(self):
        self.assertEqual(1, 1)
