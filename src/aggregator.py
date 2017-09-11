#!/usr/bin/env python3.6


import threading
import queue
import itertools
import cfg
from collections import namedtuple
from abc import ABC, abstractmethod


class SetupError(Exception):
    def __init__(self, msg=''):
        super().__init__(msg)


class ChannelClosed(Exception):
    def __init__(self, msg=''):
        super().__init__(msg)


class ChannelNotFoundError(Exception):
    def __init__(self, msg=''):
        super().__init__(msg)


Subscriber = namedtuple('Subscriber', ('channel', 'callback'))


class AggregatorCallback(ABC):
    @abstractmethod
    def setup(self):
        raise NotImplementedError()

    @abstractmethod
    def teardown(self):
        raise NotImplementedError()

    @abstractmethod
    def run(self, data):
        raise NotImplementedError()


class SubscriberThread(threading.Thread):
    def __init__(self, subscriber, group=None, target=None, name=None,
                 args=(), kwargs=None, daemon=None):
        threading.Thread.__init__(self, group=group, target=target,
                                  name=name, daemon=daemon)
        self.subscriber = subscriber
        self._stopevent = threading.Event()

    def run(self):
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

    def start_(self):
        raise RuntimeError()


class Channel:
    def __init__(self, name):
        self.name = name
        self.queue = queue.Queue()

    def close(self):
        self.queue.put(None)

    def publish(self, data):
        self.queue.put(data)

    def pop(self):
        data = self.queue.get()

        if data is None:
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
    def __init__(self):
        self.channels = None

    def update_channels(self, channels):
        self.channels = channels

    def publish(self, data, channel='default'):
        if self.channels is None:
            raise ChannelNotFoundError()

        for subscriber in self.channels[channel]:
            subscriber.channel.publish(data)


class Aggregator:
    def __init__(self):
        self.channels = {}
        self.publisher = Publisher()
        self.threads = []

    def setup(self):
        for subscriber in self.subscribers:
            try:
                subscriber.callback.setup()
            except NotImplementedError as err:
                continue

        self.threads = []

        for subscriber in self.subscribers:
            self.threads.append(SubscriberThread(subscriber=subscriber))

        try:
            for thread in self.threads:
                thread.start()
        except RuntimeError as err:
            for thread in self.threads:
                if thread.is_alive():
                    thread.exit()

            raise SetupError("something went wrong while starting thread")

    def stop(self):
        for subscriber in self.subscribers:
            try:
                subscriber.callback.teardown()
            except NotImplementedError as err:
                pass

        for thread in self.threads:
            thread.exit()

    def register_callback(self, callback, channel='default'):
        try:
            subscribers = self.channels[channel]
        except KeyError:
            subscribers = []

        channel_obj = Channel(channel)
        subscriber = Subscriber(channel_obj, callback)
        subscribers.append(subscriber)
        self.channels[channel] = subscribers

        self.publisher.update_channels(self.channels)

    @property
    def subscribers(self):
        return set(itertools.chain(*self.channels.values()))
