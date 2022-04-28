API
***

This page shows how to use the aggregator. First, we present how Mconf-Aggregator
architecture is thought and structured. Then, we show how you can extend it
to meet your needs.

Components
==========

The Mconf-Aggregator has three main parts:

* Data readers
* Data writers
* Controller

Data readers
------------

Data readers are responsible for receiving data from external source. They may
do it for example by querying an API, reading from other components' databases or
providing its own API for receiving data from other components.

The data reader implementation is not provided by the aggregator itself.
Instead, it is seen as a client of the aggregator API and you are free to code
it any way you need.

An example of data reader embedded in the aggregator is the :class:`ZabbixDataReader`
class in the :mod:`zabbix` module.

Data writers
------------

Data writers are responsible for writing data to external source. They receive
data from the aggregator (that in turn is received from some data reader) and
write it to some output. The outputs may be of any kind such as databases, files
or even the console.

Contrary to data readers, data writers must follow some rules to work smoothly.
They are must implement the :class:`AggregatorCallback` interface from the module
:mod:`aggregator`.

The interface has the following three methods:

.. autoclass:: aggregator.aggregator.AggregatorCallback
    :members:
    :noindex:

As you can see, the interface does not implement any of these methods and
raises :class:`NotImplementedError`.

All your data writers should inherit from this class and provide a concrete
implementation for all methods. In fact, only the ``run`` method is mandatory,
but it is highly advised to implement the other methods as well.

The ``run`` method is delegated to a thread to execute. It means that this method
will run in a separate thread and you should be aware of this. Both ``setup`` and
``teardown`` are run in the main thread.

In code, data writers are referred to as **callbacks** as their code is called
whenever a new data is received by the aggregator.

An example of data writer embedded in the aggregator is the :class:`ZabbixDataWriter`
in the :mod:`zabbix` module.

Controller
----------

The controller is the main component of the architecture. The implementation is
the :class:`Aggregator` in the :mod:`aggregator` module.

The controller is responsible for putting it all together. The main tasks the
controller performs are:

* Provide an API for registering callbacks.
* Set callbacks up.
* Create and start threads for callbacks.
* Clean up callbacks when done.
* Stop the threads.

The API of the :class:`Aggregator` is as follows:

.. autoclass:: aggregator.aggregator.Aggregator
    :members: setup, start, stop, register_callback
    :noindex:

Publisher
+++++++++

In order to send data to aggregator, the client needs to interact with the
aggregator's `publisher`. The `publisher` is an instace of the class
:class:`Publisher`.

To send data to the aggregator (and in turn to a data writer), a client code
needs to call the `Publisher`'s `publish` method. The API is as follows:

.. autoclass:: aggregator.aggregator.Publisher
    :members: publish
    :noindex:

There is no need to instantiate its own publisher: The aggregator provides one
for you to use.

Exceptions
==========

The following exceptions are raised as part of the API:

.. autoclass:: aggregator.aggregator.AggregatorNotRunning
    :noindex:

.. autoclass:: aggregator.aggregator.CallbackError
    :noindex:

.. autoclass:: aggregator.aggregator.SetupError
    :noindex:

.. autoclass:: aggregator.aggregator.PublishError
    :noindex:

Example
=======

The following code is an example of a oversimplified *data reader*.
It simply reads from a file and returns one line at a time::

    class FileReader():
        def __init__(self, filename):
            self.filename = filename
            self.file = None

        def setup(self):
            self.file = open(self.filename, 'r')

        def teardown(self):
            self.file.close()

        def read(self):
            return self.file.readline()

A simple *data writer* (also called a *callback*) that writes data to a file is shown below::

    from mconf_aggr.aggregator import AggregatorCallback, CallbackError


    class FileWriter(AggregatorCallback):
        def __init__(self, filename="file_writer.txt"):
            self.filename = filename

        def setup(self):
            pass

        def teardown(self):
            pass

        def run(self, data):
            with open(self.filename, 'a') as f:
                try:
                    f.write(str(data) + "\n")
                except IOError as err:
                    raise CallbackError from err

Note that it inherits (effectively, implements) the :class:`AggregatorCallback`
class. A simple *pass* statement is enough to consider `setup` and `teardown`
as implemented. It also raises a CallbackError signaling to aggregator that
something went wrong while processing the data so the aggregator can handle
the situation.

Consider the following file `data_input.txt`::

    data1
    data2
    data3
    data4
    data5

It all can be put together in the working example below::

    #!/usr/bin/env python3.9


    import sys

    from mconf_aggr.dummy import FileReader, FileWriter
    from mconf_aggr.aggregator import Aggregator, SetupError, \
                                      PublishError, AggregatorNotRunning


    def main():
        # Instantiate a data reader and a data writer.
        reader = FileReader("data_input.txt")
        writer = FileWriter("data_output.txt")

        # Instantiate a new aggregator.
        aggregator = Aggregator()

        # Register the data writer as a new callback
        # on the channel 'example'.
        aggregator.register_callback(writer, channel='example')

        try:
            # Set callbacks up, prepare and start threads for callbacks.
            aggregator.setup()
        except SetupError:
            print("An error occurred while setting the aggregator up.")
            sys.exit(1)

        # Set data reader up.
        reader.setup()

        # Get the publisher.
        publisher = aggregator.publisher

        # Start the aggregator.
        aggregator.start()

        while True:
            try:
                # Receives data from external source. In this case,
                # the file data_input.txt
                data = reader.read()

                # This data reader sends None when done.
                if data:
                    try:
                        # Publish data to the channel 'example'.
                        publisher.publish(data, channel='example')
                    except PublishError:
                        print("An error occurred while publishing data.")

                        continue
                    except AggregatorNotRunning:
                        print("The aggregator stopped.")
                        reader.stop()

                        sys.exit(1)

                time.sleep(10)
            except:
                break

        # Tear callbacks down and exit from threads.
        aggregator.stop()

        # Stop data reader.
        reader.teardown()

    if __name__ == '__main__':
        main()

The result is the file `data_output.txt`::

    data1
    data2
    data3
    data4
    data5

Note that in this example two threads were executed: The main thread and
the thread for the callback.
