import unittest
import unittest.mock as mock

from mconf_aggr.aggregator.aggregator import Aggregator


class TestAggregator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregator = Aggregator()
        cls.channel = "channel"

    def test_no_channel(self):
        with self.assertRaises(KeyError):
            self.aggregator.channels[self.channel]

    def test_register_callback(self):
        callback_mock = mock.Mock()
        publisher_mock = mock.Mock()
        self.aggregator.publisher = publisher_mock

        self.aggregator.register_callback(callback_mock)
        channels = self.aggregator.channels

        publisher_mock.update_channels.assert_called_with(channels)

    def test_remove_callback(self):
        channel_1 = "channel_1"
        channel_2 = "channel_2"
        callbacks_1 = [mock.Mock() for i in range(10)]
        callbacks_2 = [mock.Mock() for i in range(10)]
        subscribers_1 = []
        for callback in callbacks_1:
            subscriber = mock.Mock()
            subscriber.callback = callback
            subscribers_1.append(subscriber)

        subscribers_2 = []
        for callback in callbacks_2:
            subscriber = mock.Mock()
            subscriber.callback = callback
            subscribers_2.append(subscriber)

        subscribers_1 = [mock.Mock().callback(cb) for cb in callbacks_1]
        subscribers_2 = [mock.Mock().callback(cb) for cb in callbacks_2]

        self.aggregator.channels = {channel_1: subscribers_1, channel_2: subscribers_2}

        self.assertEqual(len(self.aggregator.channels[channel_1]), 10)
        self.assertEqual(len(self.aggregator.channels[channel_2]), 10)

        self.aggregator.remove_callback(subscribers_1[0].callback)
        self.aggregator.remove_callback(subscribers_1[3].callback)
        self.aggregator.remove_callback(subscribers_1[5].callback)

        for subscriber in subscribers_2:
            self.aggregator.remove_callback(subscriber.callback)

        self.assertEqual(len(self.aggregator.channels[channel_1]), 7)
        self.assertIn(channel_1, self.aggregator.channels)

        self.assertNotIn(channel_2, self.aggregator.channels.keys())
