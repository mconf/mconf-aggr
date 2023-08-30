import unittest
from contextlib import contextmanager

from loguru import logger

from mconf_aggr.aggregator.aggregator import Channel


@contextmanager
def capture_logs(level="INFO", format="{level}:{name}:{message}"):
    """Capture loguru-based logs."""
    output = []
    handler_id = logger.add(output.append, level=level, format=format)
    yield output
    logger.remove(handler_id)


class TestChannel(unittest.TestCase):
    def setUp(self):
        self.channel = Channel(name="test_channel", maxsize=5)

    def test_publish(self):
        self.channel.publish(1)
        self.assertEqual(self.channel.pop(), 1)

        self.channel.publish(2)
        self.channel.publish(3)
        self.assertEqual(self.channel.pop(), 2)
        self.assertEqual(self.channel.pop(), 3)

        self.channel.publish(4)
        self.assertEqual(self.channel.pop(), 4)

        self.channel.publish(5)
        self.assertEqual(self.channel.pop(), 5)

    def test_qsize(self):
        for i in range(5):
            self.channel.publish(i)

        self.assertEqual(self.channel.qsize(), 5)

    def test_empty(self):
        self.assertTrue(self.channel.empty())

    def test_full(self):
        for i in range(5):
            self.channel.publish(i)

        self.assertTrue(self.channel.full())

    def test_size_after(self):
        self.channel.publish(1)
        self.assertEqual(self.channel.pop(), 1)

        self.channel.publish(2)
        self.channel.publish(3)
        self.assertEqual(self.channel.pop(), 2)

        self.assertEqual(self.channel.qsize(), 1)

    def test_empty_after(self):
        self.channel.publish(1)
        self.channel.pop()

        self.channel.publish(2)
        self.channel.publish(3)
        self.channel.pop()
        self.channel.pop()

        self.assertTrue(self.channel.empty())

    def test_log_unwritten(self):
        self.channel.publish(1)

        with capture_logs(level="WARNING") as cm:
            self.channel.close()
            self.assertIn(
                "WARNING:mconf_aggr.aggregator.aggregator:There is data not consumed in channel test_channel.\n",
                cm,
            )
