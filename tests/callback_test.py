import unittest

from mconf_aggr.aggregator import AggregatorCallback


class TestCallback(unittest.TestCase):
    def setUp(self):
        self.callback = AggregatorCallback()

    def test_setup(self):
        with self.assertRaises(NotImplementedError):
            self.callback.setup()

    def test_teardown(self):
        with self.assertRaises(NotImplementedError):
            self.callback.teardown()

    def test_run(self):
        with self.assertRaises(NotImplementedError):
            self.callback.run(None)
