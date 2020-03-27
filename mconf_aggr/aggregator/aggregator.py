#!/usr/bin/env python3.6


"""This module provides all classes related to the main logic of the aggregator.

The client of aggregator needs only to know the main class `Aggregator` and
the interface `AggregatorCallback` which client's callback should inherit from.
All other classes are for internal use and should not be instantiated outside
this module.
"""

import itertools
import logging
import logaugment
import queue
import reprlib
import threading
from collections import namedtuple

class AggregatorNotRunning(Exception):
    """Raised if the aggregator has stopped for some reason.

    It is raised to notify users of aggregator that it is no longer running.
    At this time, the aggregator is already stopped and there is no need to
    call its stop method.
    """
    pass


class CallbackError(Exception):
    """Raised if something goes wrong while running a callback.

    It should be raised by callbacks (or Writers) when something goes wrong.
    As an example of unexpected behavior that should trigger this error is
    database operational error.
    """
    pass


class SetupError(Exception):
    """Raised if something goes wrong while setting aggregator up.
    """
    pass


class ChannelClosed(Exception):
    """Raised if a channel is closed.

    It is not an error, just a signaling exception.
    """
    pass


class PublishError(Exception):
    """Raised if something goes wrong while publishing data.
    """
    pass


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
    def __init__(self, subscriber, errorevent, logger=None, **kwargs):
        """Constructor of the `SubscriberThread`.

        Parameters
        ----------
        subscriber : Subscriber
            A Subscriber with channel and callback objetcs.
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        threading.Thread.__init__(self, **kwargs)
        self.subscriber = subscriber
        self._errorevent = errorevent
        self._stopevent = threading.Event()
        self.logger = logger or logging.getLogger(__name__)
        logaugment.add(self.logger, code="", site="SubscriberThread", server="", event="", keywords="null")

    def run(self):
        """Run thread's main loop.

        It runs while the thread is signaled to exit (by calling its `exit`
        method). The data is popped out from the `subscriber`'s channel and
        sent to the `subscriber`'s callback `run` method. When signaled to
        exit, it simply returns and the thread is done.
        """
        logging_extra = {
            "code": "Subscriber run",
            "site": "SubscriberThread.run",
            "keywords": ["run", "thread", "subscriber", "callback"]
        }
        self.logger.debug(
            "Running thread with callback {}"
            .format(self.subscriber.callback),
            extra=logging_extra
        )
        while not self._stopevent.is_set():
            try:
                data = self.subscriber.channel.pop()
                self.subscriber.callback.run(data)
            except ChannelClosed:
                continue
            except CallbackError:
                logging_extra["keywords"] = ["run", "thread", "subscriber", "callback", "exception", "error"]

                self.logger.info("An error occurred while running a subscriber.", extra=logging_extra)
                #self._errorevent.set()

        return

    def exit(self):
        """Exit the thread.

        This method prepares the thread to exit by signaling its main loop
        to finish, closing the `subscriber`'s channel and waiting for the
        thread to join.
        """
        logging_extra = {
            "code": "Exit threads",
            "site": "SubscriberThread.exit",
            "keywords": ["exit", "thread", "subscriber", "callback", "finish", "sucess"]
        }

        self._stopevent.set()
        self.subscriber.channel.close()

        threading.Thread.join(self)
        self.logger.debug(
            "Thread with callback {} exited with success."
            .format(self.subscriber.callback),
            extra=logging_extra
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
        logaugment.add(self.logger, code="", site="Channel", server="", event="", keywords="null")

    def close(self):
        """Close the channel.

        It simply puts None in the queue to signal that the channel must be
        closed.
        """
        logging_extra = {
            "code": "Channel close",
            "site": "Channel.close",
            "keywords": ["close", "signal", "queue", f"channel={self.name}"]
        }

        self.logger.debug("Closing channel {}.".format(self.name), extra=logging_extra)
        if not self.empty():
            logging_extra["keywords"] += ["warning"] if("warning" not in logging_extra["keywords"]) else []
            self.logger.warn("There are data not consumed in channel {}."
                             .format(self.name),
                             extra=logging_extra)
        self.queue.put(None)

    def publish(self, data):
        """Publish data to channel.

        Parameters
        ----------
        data
            Any data to be sent over the channel.
        """
        logging_extra = {
            "code": "Channel publish",
            "site": "Channel.publish",
            "keywords": ["publish", "data", "queue", f"channel={self.name}"]
        }

        self.logger.debug("Putting data into the channel.", extra=logging_extra)
        self.queue.put(data)
        self.logger.debug("Channel {} has {} element(s)."
                          .format(self.name, self.qsize()),
                          extra=logging_extra)

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
        logging_extra = {
            "code": "Channel pop data",
            "site": "Channel.pop",
            "keywords": ["pop", "data", "queue", f"channel={self.name}"]
        }

        self.logger.debug("Popping data from the channel.", extra=logging_extra)
        data = self.queue.get()

        if data is None:
            self.logger.debug("Signaling closing channel {} for clients "
                              "waiting for data.".format(self.name),
                              extra=logging_extra)
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
            self.__class__.__name__, self.name, self.queue.maxsize)


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
        self._running = True
        self.logger = logger or logging.getLogger(__name__)
        logaugment.add(self.logger, code="", site="Publisher", server="", event="", keywords="null")

    def update_channels(self, channels):
        """Update the channels to publish to.

        Parameters
        ----------
        channels : dict
            Dict of channels in the format channel:list of subscribers.
        """
        logging_extra = {
            "code": "Updating channel",
            "site": "Publisher.update_channels",
            "keywords": ["update", "channel", "subscriber"]
        }

        self.logger.debug("Updating channels in publisher.", extra=logging_extra)
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
        AggregatorNotRunning
            If the aggregator is not currently running.
            It may have stopped due to some failure occurred in
            callbacks or by the stop method of aggregator being called.
        """
        logging_extra = {
            "code": "Publisher publish",
            "site": "Publisher.publish",
            "keywords": ["publish", "subscriber", "channel", "data"]
        }
        
        if self._running:
            self.logger.debug("Publishing data to subscribers.", extra=logging_extra)

            if self.channels is None:
                logging_extra["keywords"] += ["error", "exception"]
                self.logger.exception("No channel was found for this publisher.", extra=logging_extra)
                raise PublishError()

            for subscriber in self.channels[channel]:
                subscriber.channel.publish(data)
        else:
            raise AggregatorNotRunning()

    def stop(self):
        """Stop the publisher.
        """
        logging_extra = {
            "code": "Publisher stop",
            "site": "Publisher.stop",
            "keywords": ["Publisher", "stop"]
        }
        self.logger.debug("Stopping the publisher.", extra=logging_extra)
        self._running = False

    def __repr__(self):
        channels = list(self.channels.keys())

        return "{!s}(channels={!r})".format(self.__class__.__name__,
                                            reprlib.repr(channels))


def error_handler(aggregator, errorevent):
    """Error-waiting thread.

    Parameters
    ----------
    aggregator : Aggregator
        The aggregator object which this thread monitors errors for.
    errorevent : threading.Event
        Shared Event that serves as a channel for communicating errors between
        subscriber threads and this one.
    """
    errorevent.wait()  # This call blocks until a thread set this Event.
    aggregator.stop()  # Notify the aggregator to stop.

    return


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
        self._error_thread = None
        self._running = False  # It is considered running only after its setup.
        self.logger = logger or logging.getLogger(__name__)
        logaugment.add(self.logger, code="", site="Aggregator", server="", event="", keywords="null")

        logging_extra = {
            "code": "Initialize",
            "site": "Aggregator.__init__",
            "keywords": ["aggregator", "init", "data structure", "controller"]
        }

        self.logger.info("Aggregator created.", extra=logging_extra)

    def setup(self):
        """Set up the aggregator and its components.

        It calls `setup` method for each of its subscribers' callback.

        If something goes wrong while setting callbacks up, it removes the
        callback from its list.

        It also creates an error-waiting thread that awaits for errors
        coming from callback threads and an threading.Event to communicate
        errors between them.
        """
        logging_extra = {
            "code": "Aggregator setup",
            "site": "Aggregator.setup",
            "keywords": ["aggregator", "setup", "subscriber", "callback"]
        }

        self.logger.info("Setting up aggregator.", extra=logging_extra)

        logging_extra["code"] = "Callback setup"
        for subscriber in self.subscribers:
            try:
                logging_extra["keywords"] = ["aggregator", "setup", "subscriber", "callback"]
                self.logger.debug(
                    "Setting up callback {}."
                    .format(subscriber.callback),
                    extra=logging_extra
                )
                subscriber.callback.setup()
            except NotImplementedError:
                logging_extra["keywords"] = ["aggregator", "setup", "subscriber", "callback", "exception", "warning", "not implemented"]
                self.logger.warn(
                    "setup() not implemented for callback {}."
                    .format(subscriber.callback),
                    extra=logging_extra
                )
                continue
            except Exception:
                logging_extra["keywords"] = ["aggregator", "setup", "subscriber", "callback", "exception", "error"]
                self.logger.exception(
                    "Something went wrong while setting up callback {}."
                    .format(subscriber.callback),
                    extra=logging_extra
                )
                self.remove_callback(subscriber.callback)
                continue

        errorevent = threading.Event()  # Shared Event between subscriber
                                        # threads and error-waiting thread.
        self.threads = []

        for subscriber in self.subscribers:
            self.threads.append(SubscriberThread(subscriber=subscriber,
                                                 errorevent=errorevent))

        # Create error-waiting thread.
        self._error_thread = threading.Thread(name="error_handler",
                                              target=error_handler,
                                              args=(self, errorevent),
                                              daemon=True)

    def start(self):
        """Start the aggregator and its components.

        It calls `start` method for each of its subscribers' threads.

        If something goes wrong while starting a thread for a callback, it
        stops every already running thread and raises a `SetupError`.
        In other words, the aggregator only starts with success if all
        threads are started properly.

        Raises
        ------
        SetupError
            If any thread fails to start.
        """
        logging_extra = {
            "code": "Aggregator start",
            "site": "Aggregator.start",
            "keywords": ["aggregator", "start", "subscriber", "callback", "thread"]
        }

        self.logger.info("Starting threads for callbacks.", extra=logging_extra)

        self._error_thread.start()

        logging_extra["code"] = "Thread start"
        try:
            for thread in self.threads:
                thread.start()
        except RuntimeError:
            logging_extra["keywords"] += ["error", "exception"]
            self.logger.exception("Error while starting thread. Cleaning up.", extra=logging_extra)
            for thread in self.threads:
                if thread.is_alive():
                    thread.exit()

            raise SetupError("something went wrong while starting thread")

        if all([thread.is_alive() for thread in self.threads]):
            logging_extra["code"] = "Aggregator start"
            logging_extra["keywords"] += ["success"]
            self.logger.info("All threads started with success.", extra=logging_extra)

        self._running = True

        logging_extra["code"] = "Aggregator is running"
        self.logger.info("Aggregator running.", extra=logging_extra)

    def stop(self):
        """Stop the aggregator.

        It calls `teardown` method for each of its subscribers' callback and
        stops all threads. The aggregator is considered to have stopped with
        success if all threads exit properly.
        """
        logging_extra = {
            "code": "Aggregator stop",
            "site": "Aggregator.stop",
            "keywords": ["aggregator", "stop", "subscriber", "callback", "thread"]
        }

        if not self._running:
            self.logger.info("Aggregator already stopped.", extra=logging_extra)

            return

        self.logger.info("Stopping aggregator.", extra=logging_extra)

        logging_extra["code"] = "Tear down callbacks"
        logging_extra["keywords"] += ["tear down"]
        self.logger.info("Tearing down callbacks.", extra=logging_extra)
        for subscriber in self.subscribers:
            try:
                self.logger.debug(
                    "Tearing down callback {}."
                    .format(subscriber.callback), extra=logging_extra
                )
                subscriber.callback.teardown()
            except NotImplementedError:
                logging_extra["keywords"] = ["not implemented", "warning", "aggregator", "stop", "subscriber", "callback", "thread", "tear down"]
                self.logger.warn(
                    "teardown() not implemented for callback {}."
                    .format(subscriber.callback),
                    extra=logging_extra
                )
                logging_extra["keywords"] = ["aggregator", "stop", "subscriber", "callback", "thread", "tear down"]
                continue
            except Exception:
                logging_extra["keywords"] = ["exception", "aggregator", "stop", "subscriber", "callback", "thread", "tear down"]
                self.logger.exception(
                    "Something went wrong while tearing down callback {}."
                    .format(subscriber.callback),
                    extra=logging_extra
                )
                logging_extra["keywords"] = ["aggregator", "stop", "subscriber", "callback", "thread", "tear down"]
                continue

        logging_extra["code"] = "Threads exit"
        logging_extra["keywords"] += ["exit"]
        self.logger.info("Exiting threads.", extra=logging_extra)
        for thread in self.threads:
            thread.exit()

        if not any([thread.is_alive() for thread in self.threads]):
            logging_extra["keywords"] += ["sucess"]
            self.logger.info("All threads exited with success.", extra=logging_extra)

        self.publisher.stop()

        self._running = False

        logging_extra["keywords"] = ["aggregator", "stop", "subscriber", "callback", "thread", "finished"]
        self.logger.info("Aggregator finished with success.", extra=logging_extra)

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
        logging_extra = {
            "code": "Aggregator callback register",
            "site": "Aggregator.register_callback",
            "keywords": ["aggregator", "callback", "register"]
        }

        self.logger.debug("Registering new callback {}.".format(callback), extra=logging_extra)

        try:
            subscribers = self.channels[channel]
        except KeyError:
            logging_extra["code"] = "Channel create"
            logging_extra["keywords"] += ["subscribers", f"channel={channel}"]

            self.logger.debug(
                "Creating new list of subscribers for channel {}."
                .format(channel),
                extra=logging_extra
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
        logging_extra = {
            "code": "Aggregator callback register remove",
            "site": "Aggregator.remove_callback",
            "keywords": ["aggregator", "callback", "register", "remove"]
        }

        self.logger.debug(
            "Removing callback {} from subscribers."
            .format(callback),
            extra=logging_extra
        )
        for channel, subscribers in self.channels.items():
            filtered_subscribers = list(filter(lambda subscriber:
                                               subscriber.callback != callback,
                                               subscribers))

            self.channels[channel] = filtered_subscribers

        self.channels = {channel: subscribers
                         for channel, subscribers
                         in self.channels.items()
                         if subscribers}

    @property
    def subscribers(self):
        return set(itertools.chain(*self.channels.values()))
