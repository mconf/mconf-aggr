#!/usr/bin/env python3.6


"""This module provides all classes related to the main logic of the aggregator.

The client of aggregator needs only to know the main class `Aggregator` and
the interface `AggregatorCallback` which client's callback should inherit from.
All other classes are for internal use and should not be instantiated outside
this module.
"""

import itertools
import logging
import queue
import threading
from collections import namedtuple


class SetupError(Exception):
    """Raised if something goes wrong while setting aggregator up.
    """
    def __init__(self, msg=''):
        super().__init__(msg)


class ChannelClosed(Exception):
    """Raised if a channel is closed.

    It is not an error, just a signaling exception.
    """
    def __init__(self, msg=''):
        super().__init__(msg)


class PublishError(Exception):
    """Raised if something goes wrong while publishing data.
    """
    def __init__(self, msg=''):
        super().__init__(msg)


"""Represent a subscriber of the aggregator.

It encapsulates a `Channel` object and a callback in a single
`Subscriber` object. It subscriber has its own channel.

Attributes
----------
    channel : channel
        The channel where the subscriber received data from.
    callback : `AggregatorCallback` subclass
        The callback that processes the data.
"""
Subscriber = namedtuple('Subscriber', ('channel', 'callback'))


class AggregatorCallback:
    """Interface to be implemented by callbacks.

    It should not be instantiated. Although not formally an abstract class,
    this class does not implement any of its methods. All your consuming
    callbacks must inherit from this class and implement at least the
    `run` method. It is highly advised to implement also the `setup` and
    `teardown` methods.
    """
    def setup(self):
        """Prepare the callback before it starts receiving data.

        This method is called while setting the aggregator up.
        Any file or database connection opening etc should be performed here.

        Raises
        ------
        NotImplementedError
            If not implemented in the subclass.
        """
        raise NotImplementedError()

    def teardown(self):
        """Finish the callback properly.

        This method is called while aggregator is stoping.
        Any file or database connection closing etc should be performed here.

        Raises
        ------
        NotImplementedError
            If not implemented in the subclass.
        """
        raise NotImplementedError()

    def run(self, data):
        """This method is called by the aggregator to send data to the callback.

        The implementation of this method is mandatory.
        It serves to receive data from the aggregator after it is published
        to the channel the callback subscribed. What to do with the data
        received is up to the callback.

        Raises
        ------
        NotImplementedError
            If not implemented in the subclass.
        """
        raise NotImplementedError()


class SubscriberThread(threading.Thread):
    """This class represents the thread to be run for a subscriber.
    """
    def __init__(self, subscriber, group=None, target=None, name=None,
                 args=(), kwargs=None, daemon=None, logger=None):
        """Constructor of the `SubscriberThread`.

        Parameters
        ----------
        subscriber : Subscriber
            A Subscriber with channel and callback objetcs.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        threading.Thread.__init__(self, group=group, target=target,
                                  name=name, daemon=daemon)
        self.subscriber = subscriber
        self._stopevent = threading.Event()
        self.logger = logger or logging.getLogger(__name__)

    def run(self):
        """Run thread's main loop.

        It runs while the thread is signaled to exit (by calling its `exit`
        method). The data is popped out from the `subscriber`'s channel and
        sent to the `subscriber`'s callback `run` method. When signaled to
        exit, it simply returns and the thread is done.
        """
        self.logger.debug(
            "Running thread with callback {}"
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
        """Exit the thread.

        This method prepares the thread to exit by signaling its main loop
        to finish, closing the `subscriber`'s channel and waiting for the
        thread to join.
        """
        self._stopevent.set()
        self.subscriber.channel.close()

        threading.Thread.join(self)
        self.logger.debug(
            "Thread with callback {} exited with success."
            .format(self.subscriber.callback)
        )


class Channel:
    """Channel to send and receive data.

    This class encapsulates a thread communicating pipe between the
    aggregator and its subscribers.
    """
    def __init__(self, name, maxsize=0, logger=None):
        """Constructor of the Channel class.

        Parameters
        ----------
        name : str
            An identifier of the channel.
        maxsize : int
            The maximum size of the channel. If it is zero or negative, the
            channel accepts any number of elements.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.name = name
        self.queue = queue.Queue(maxsize=maxsize)
        self.logger = logger or logging.getLogger(__name__)

    def close(self):
        """Close the channel.

        It simply puts None in the queue to signal that the channel must be
        closed.
        """
        self.logger.debug("Closing channel {}.".format(self.name))
        if not self.empty():
            self.logger.warn("There are data not consumed in channel {}."
                             .format(self.name))
        self.queue.put(None)

    def publish(self, data):
        """Publish data to channel.

        Parameters
        ----------
        data
            Any data to be sent over the channel.
        """
        self.logger.debug("Putting data into the channel.")
        self.queue.put(data)

    def pop(self):
        """Pop data from the channel.

        It reads data from the channel's queue.
        If None is read from the queue, it raises a `ChannelClosed` exception
        to signal the caller that the channel was closed.

        Returns
        -------
        data
            Any data received by the channel.

        Raises
        ------
        ChannelClosed
            If the channel was closed.
        """
        self.logger.debug("Popping data from the channel.")
        data = self.queue.get()

        if data is None:
            self.logger.debug("Signaling closing channel {} for clients \
                waiting for data.".format(self.name))
            raise ChannelClosed()

        self.queue.task_done()

        return data

    def qsize(self):
        """Current size of the channel.

        Returns
        -------
        int
            Number of elements in the channel.
        """
        return self.queue.qsize()

    def empty(self):
        """Is the channel empty?

        Returns
        -------
        bool
            True if the channel is empty. False, otherwise.
        """
        return self.queue.empty()

    def full(self):
        """Is the channel full?

        It only makes sense if a `maxsize` is set for the channel.

        Returns
        -------
        bool
            True if the channel is full, ie. the number of elements in it is
            the same as its `maxsize`. False, otherwise.
        """
        return self.queue.full()

    def __repr__(self):
        return "{!s}(name={!r}, maxsize={!r})".format(
            self.__class__.__name__, self.name, self.maxsize)


class Publisher:
    """Data publisher.
    """
    def __init__(self, logger=None):
        """Constructor of the Publisher class.

        Parameters
        ----------
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.channels = None
        self.logger = logger or logging.getLogger(__name__)

    def update_channels(self, channels):
        """Update the channels to publish to.

        Parameters
        ----------
        channels : dict
            Dict of channels in the format channel:list of subscribers.
        """
        self.logger.debug("Updating channels in publisher.")
        self.channels = channels

    def publish(self, data, channel='default'):
        """Publish data to the subscribers of the channel.

        Parameters
        ----------
        data
            Any data to send over the channel.
        channel : str
            Identifier of the channel. Defaults to 'default'.

        Raises
        ------
        PublishError
            If no channel was found.
        """
        self.logger.debug("Publishing data to subscribers.")

        if self.channels is None:
            self.logger.exception("No channel was found for this publisher.")
            raise PublishError()

        for subscriber in self.channels[channel]:
            subscriber.channel.publish(data)

    def __repr__(self):
        return "{!s}(channels={!r})".format(self.__class__.__name__,
                                            self.channels)


class Aggregator:
    """Aggregator main class.

    This class is responsible for aggregator's logic. It can be viewed as the
    controller as it initializes all data structures, delegates tasks and
    clean everything at the end of execution. It also provides the main API for
    client's code.

    Attributes
    ----------
    publisher : Publisher
        Data publisher that effectively publishes data to subscribers.
    logger : logging.Logger
        If not supplied, it will instantiate a new logger from __name__.
    """
    def __init__(self, logger=None):
        self.channels = {}
        self.publisher = Publisher()
        self.threads = []
        self.logger = logger or logging.getLogger(__name__)

        self.logger.info("Aggregator created.")

    def setup(self):
        """Set up the aggregator and its components.

        It calls `setup` method for each of its subscribers' callback and
        starts a thread for each of them.

        If something goes wrong while starting a thread for a callback, it
        stops every already running thread and raises a `SetupError`.
        In other words, the aggregator only starts with success if _all_
        threads are started properly.

        Raises
        ------
        SetupError
            If any thread fails to start.
        """
        self.logger.info("Setting up aggregator.")

        for subscriber in self.subscribers:
            try:
                self.logger.debug(
                    "Setting up callback {}."
                    .format(subscriber.callback)
                )
                subscriber.callback.setup()
            except NotImplementedError as err:
                self.logger.warn(
                    "setup() not implemented for callback {}."
                    .format(subscriber.callback)
                )
                continue
            except Exception as err:
                self.logger.exception(
                    "Something went wrong while setting up callback {}."
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
        """Stop the aggregator.

        It calls `teardown` method for each of its subscribers' callback and
        stops all threads. The aggregator is considered to have stopped with
        success if all threads exit properly.
        """
        self.logger.info("Stopping aggregator.")

        self.logger.info("Tearing down callbacks.")
        for subscriber in self.subscribers:
            try:
                self.logger.debug(
                    "Tearing down callback {}."
                    .format(subscriber.callback)
                )
                subscriber.callback.teardown()
            except NotImplementedError as err:
                self.logger.warn(
                    "teardown() not implemented for callback {}."
                    .format(subscriber.callback)
                )
                continue
            except Exception as err:
                self.logger.exception(
                    "Something went wrong while tearing down callback {}."
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
        """Register a new callback.

        A callback is an instance of a class implementing the
        `AggregatorCallback` interface. Its purpose is to handle received data
        on a given channel.

        Parameters
        ----------
        callback : `AggregatorCallback` subclass
            The handler of the received data.
        channel : str
            Channel to subscribe. Defaults to 'default'.
        """
        self.logger.debug("Registering new callback {}.".format(callback))

        try:
            subscribers = self.channels[channel]
        except KeyError:
            self.logger.debug(
                "Creating new list of subscribers for channel {}."
                .format(channel)
            )
            subscribers = []

        channel_obj = Channel(channel)
        subscriber = Subscriber(channel_obj, callback)
        subscribers.append(subscriber)
        self.channels[channel] = subscribers

        self.publisher.update_channels(self.channels)

    def remove_callback(self, callback):
        """Remove a callback.

        This methods exists if you need to remove a callback for any reason.
        """
        self.logger.debug(
            "Removing callback {} from subscribers."
            .format(callback)
        )
        for channel, subscribers in self.channels.items():
            filtered_subscribers = filter(lambda subscriber:
                                          subscriber.callback != callback,
                                          subscribers)
            filtered_subscribers = list(filtered_subscribers)

            self.channels[channel] = filtered_subscribers

        self.channels = {channel: subscribers
                         for channel, subscribers
                         in self.channels.items()
                         if subscribers}

    @property
    def subscribers(self):
        return set(itertools.chain(*self.channels.values()))
