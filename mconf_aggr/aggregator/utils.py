import time
from contextlib import contextmanager


@contextmanager
def time_logger(logger_func, msg, **kw_format):
    """Provide a log for the elapsed time in the context block."""
    start_time = time.time()
    yield None
    end_time = time.time()

    elapsed_time = round(end_time - start_time, 4)
    kw_format.update({"elapsed": elapsed_time})

    try:
        logger_func(msg.format(**kw_format))
    except Exception as err:
        kw = ", ".join(["{}: {}".format(k, v) for k, v in kw_format.items()])
        print("Error while logging elapsed time: {} ({}).".format(err, kw))


def create_session_scope(Session):
    @contextmanager
    def session_scope(raise_exception=True):
        """Provide a transactional scope around a series of operations."""
        session = Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            if raise_exception:
                raise
        finally:
            session.close()

    return session_scope


class RequestTimeLogger:
    """Logger the request and also update management variables."""

    """ How many requests are being handled
    """
    current_requests_count = 0

    @staticmethod
    @contextmanager
    def time_logger_requests(logger_func, msg, extra=dict(), **kw_format):
        """Provide a log for the elapsed time in the context block and handle
        statistics of requests."""
        RequestTimeLogger.current_requests_count += 1

        start_time = time.time()
        yield None
        end_time = time.time()

        elapsed_time = round(end_time - start_time, 4)
        kw_format.update({"elapsed": elapsed_time})

        try:
            logger_func(msg.format(**kw_format), extra=extra)
        except Exception as err:
            kw = ", ".join(["{}: {}".format(k, v) for k, v in kw_format.items()])
            print("Error while logging elapsed time: {} ({}).".format(err, kw))

        RequestTimeLogger.current_requests_count -= 1


def signal_handler(aggregator, liveness_probe, signal):
    """Unix signals handler.

    Handle signals, closing the application gracefully if the signal is a SIGTERM.

    Parameters
    ----------
    aggregator : Aggregator
        The aggregator object which this thread monitors errors for.
    liveness_probe : LivenessProbeListener
        The probe listener which handles the /health route.
    signal : signal
        The signal which was spawned in the main thread.
    """

    if signal == signal.SIGTERM:
        liveness_probe.close()

        # Wait aggregator handle with all the received events before close it
        while (
            any([not x.channel.empty() for x in aggregator.subscribers])
            or RequestTimeLogger.current_requests_count > 0
        ):
            print("There are events to handle yet.")

        aggregator.stop()
        exit(0)
