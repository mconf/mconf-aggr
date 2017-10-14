import unittest
import unittest.mock as mock

from mconf_aggr.aggregator import Publisher, Subscriber, \
                                  Channel, PublishError


class TestPublisher(unittest.TestCase):
    def setUp(self):
        self.publisher = Publisher()

    def test_update(self):
        # Mock it?
        channel_11 = Channel("channel_1")
        channel_12 = Channel("channel_1")
        channel_13 = Channel("channel_1")

        channel_21 = Channel("channel_2")
        channel_22 = Channel("channel_2")
        channel_23 = Channel("channel_2")
        channel_24 = Channel("channel_2")

        sub_11 = Subscriber(channel_11, 'callback_11')
        sub_12 = Subscriber(channel_12, 'callback_12')
        sub_13 = Subscriber(channel_13, 'callback_13')

        sub_21 = Subscriber(channel_21, 'callback_21')
        sub_22 = Subscriber(channel_22, 'callback_22')
        sub_23 = Subscriber(channel_23, 'callback_23')
        sub_24 = Subscriber(channel_24, 'callback_24')


        channels = {'channel_1': [sub_11, sub_12, sub_13],
                    'channel_2': [sub_21, sub_22, sub_23, sub_24]}

        self.publisher.update_channels(channels)

        self.assertEqual(self.publisher.channels, channels)

    def test_publish_error(self):
        with self.assertRaises(PublishError):
            self.publisher.publish(None)

    @mock.patch('mconf_aggr.aggregator.Subscriber')
    def test_publish(self, MockChannel):
        mock_channel = MockChannel('channel')
        subscriber = Subscriber(mock_channel, 'callback')

        self.publisher.update_channels({'channel': [subscriber]})

        data = {'key': 'value'}
        self.publisher.publish(data, channel='channel')

        mock_channel.publish.assert_called_with(data)
