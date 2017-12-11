import threading
import unittest
import unittest.mock as mock

from mconf_aggr.aggregator import SubscriberThread, Subscriber, Channel


class TestPublisher(unittest.TestCase):
    def setUp(self):
        callback_mock = mock.Mock()
        channel = Channel('channel_1')
        subscriber = Subscriber(channel, callback_mock)
        self.thread = SubscriberThread(subscriber=subscriber, errorevent=None)

    def test_stop_is_false(self):
        self.assertFalse(self.thread._stopevent.is_set())

    def test_start_exit(self):
        self.thread.start()

        try:
            self.assertTrue(self.thread.is_alive())
            self.assertFalse(self.thread._stopevent.is_set())
        except:
            raise
        finally:
            self.thread.exit()

        self.assertFalse(self.thread.is_alive())
        self.assertTrue(self.thread._stopevent.is_set())

    def test_run_callback(self):
        self.thread.start()

        data  = "data"
        self.thread.subscriber.channel.publish(data)

        self.thread.exit()

        try:
            self.thread.subscriber.callback.run.assert_called_with(data)
        except:
            raise
        finally:
            self.thread.exit()
