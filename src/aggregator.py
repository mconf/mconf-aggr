#!/usr/bin/env python3.6


import threading
import queue
import itertools
import cfg
from collections import namedtuple
from abc import ABC, abstractmethod
import logging


class SetupError(Exception):
    def __init__(self, msg=''):
        super().__init__(msg)


class ChannelClosed(Exception):
    def __init__(self, msg=''):
        super().__init__(msg)


class PublishError(Exception):
    def __init__(self, msg=''):
        super().__init__(msg)


Subscriber = namedtuple('Subscriber', ('channel', 'callback'))


class AggregatorCallback:
    def setup(self):
        raise NotImplementedError()

    def teardown(self):
        raise NotImplementedError()

    def run(self, data):
        raise NotImplementedError()


class SubscriberThread(threading.Thread):
    def __init__(self, subscriber, group=None, target=None, name=None,
                 args=(), kwargs=None, daemon=None, logger=None):
        threading.Thread.__init__(self, group=group, target=target,
                                  name=name, daemon=daemon)
        self.subscriber = subscriber
        self._stopevent = threading.Event()
        self.logger = logger or logging.getLogger(__name__)

    def run(self):
        self.logger.debug(
            "Running thread with callback {}" \
            .format(self.subscriber.callback)
        )
        while not self._stopevent.is_set():
            try:
                data = self.subscriber.channel.pop()
            except ChannelClosed as err:
                continue
            else:
                self.subscriber.callback.run(data)

        return

    def exit(self):
        self._stopevent.set()
        self.subscriber.channel.close()

        threading.Thread.join(self)
        self.logger.debug(
            "Thread with callback {} exited with success." \
            .format(self.subscriber.callback)
        )


class Channel:
    def __init__(self, name, logger=None):
        self.name = name
        self.queue = queue.Queue()
        self.logger = logger or logging.getLogger(__name__)

    def close(self):
        self.queue.put(None)

    def publish(self, data):
        self.queue.put(data)

    def pop(self):
        data = self.queue.get()

        if data is None:
            self.logger.debug("Closing channel {}.".format(self.name))
            raise ChannelClosed()

        self.queue.task_done()

        return data

    def qsize(self):
        return self.queue.qsize()

    def empty(self):
        return self.queue.empty()

    def full(self):
        return self.queue.full()


class Publisher:
    def __init__(self, logger=None):
        self.channels = None
        self.logger = logger or logging.getLogger(__name__)

    def update_channels(self, channels):
        self.logger.debug("Updating channels in publisher.")
        self.channels = channels

    def publish(self, data, channel='default'):
        self.logger.debug("Publishing data to subscribers.")

        if self.channels is None:
            self.logger.exception("No channel was found for this publisher.")
            raise PublishError()

        for subscriber in self.channels[channel]:
            subscriber.channel.publish(data)


class Aggregator:
    def __init__(self, logger=None):
        self.channels = {}
        self.publisher = Publisher()
        self.threads = []
        self.logger = logger or logging.getLogger(__name__)

        self.logger.info("Aggregator created.")

    def setup(self):
        self.logger.info("Setting up aggregator.")

        for subscriber in self.subscribers:
            try:
                self.logger.debug("Setting up callback {}." \
                    .format(subscriber.callback)
                )
                subscriber.callback.setup()
            except NotImplementedError as err:
                self.logger.warn(
                    "setup() not implemented for callback {}." \
                    .format(subscriber.callback)
                )
                continue
            except Exception as err:
                self.logger.exception(
                    "Something went wrong while setting up callback {}." \
                    .format(subscriber.callback)
                )
                self.remove_callback(subscriber.callback)
                continue

        self.threads = []

        for subscriber in self.subscribers:
            self.threads.append(SubscriberThread(subscriber=subscriber))

        self.logger.info("Starting threads for callbacks.")
        try:
            for thread in self.threads:
                thread.start()
        except RuntimeError as err:
            self.logger.exception("Error while starting thread. Cleaning up.")
            for thread in self.threads:
                if thread.is_alive():
                    thread.exit()

            raise SetupError("something went wrong while starting thread")

        if all([thread.is_alive() for thread in self.threads]):
            self.logger.info("All threads started with success.")

        self.logger.info("Aggregator running.")

    def stop(self):
        self.logger.info("Stopping aggregator.")

        self.logger.info("Tearing down callbacks.")
        for subscriber in self.subscribers:
            try:
                self.logger.debug(
                    "Tearing down callback {}."\
                    .format(subscriber.callback)
                )
                subscriber.callback.teardown()
            except NotImplementedError as err:
                self.logger.warn(
                    "teardown() not implemented for callback {}." \
                    .format(subscriber.callback)
                )
                continue
            except Exception as err:
                self.logger.exception(
                    "Something went wrong while tearing down callback {}." \
                    .format(subscriber.callback)
                )
                continue

        self.logger.info("Exiting threads.")
        for thread in self.threads:
            thread.exit()

        if not any([thread.is_alive() for thread in self.threads]):
            self.logger.info("All threads exited with success.")

        self.logger.info("Aggregator finished with success.")

    def register_callback(self, callback, channel='default'):
        self.logger.debug("Registering new callback {}.".format(callback))

        try:
            subscribers = self.channels[channel]
        except KeyError:
            self.logger.debug(
                "Creating new list of subscribers for channel {}."\
                .format(channel)
            )
            subscribers = []

        channel_obj = Channel(channel)
        subscriber = Subscriber(channel_obj, callback)
        subscribers.append(subscriber)
        self.channels[channel] = subscribers

        self.publisher.update_channels(self.channels)

    def remove_callback(self, callback):
        for subscribers in self.channels.values():
            for subscriber in subscribers:
                if callback == subscriber.callback:
                    self.logger.debug(
                        "Removing callback {} from subscribers." \
                        .format(callback)
                    )
                    subscribers.remove(subscriber)

    @property
    def subscribers(self):
        return set(itertools.chain(*self.channels.values()))
