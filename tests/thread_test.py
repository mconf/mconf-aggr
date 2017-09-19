#!/usr/bin/env python3.6


import unittest
import unittest.mock as mock

from mconf_aggr.aggregator import Publisher, Subscriber, Channel, \
                                  PublishError


class TestPublisher(unittest.TestCase):
    def setUp(self):
        pass

    @mock.patch('mconf_aggr.aggregator.Subscriber')
    @mock.patch('mconf_aggr.aggregator.SubscriberThread')
    def test_run(self, MockThread, MockSubscriber):
        #mock_sub = MockSubscriber()
        sub = Subscriber(None, 'callback')
        mock_thread = MockThread(subscriber=sub)

        self.assertIs(mock_thread.subscriber, sub)

    """
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
    """
