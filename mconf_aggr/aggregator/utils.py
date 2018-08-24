import time
from contextlib import contextmanager


@contextmanager
def time_logger(logger_func, msg, **kw_format):
    """Provide a log for the elapsed time in the context block.
    """
    start_time = time.time()
    yield None
    end_time = time.time()

    elapsed_time = round(end_time - start_time, 4)
    kw_format.update({'elapsed': elapsed_time})

    try:
        logger_func(msg.format(**kw_format))
    except Exception as err:
        kw = ", ".join(["{}: {}".format(k, v) for k, v in kw_format.items()])
        print("Error while logging elapsed time: {} ({})."
              .format(err, kw))


# @contextmanager
# def session_scope(raise_exception=True):
#     """Provide a transactional scope around a series of operations.
#     """
#     session = Session()
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         if raise_exception:
#             raise
#     finally:
#         session.close()


def create_session_scope(Session):
    @contextmanager
    def session_scope(raise_exception=True):
        """Provide a transactional scope around a series of operations.
        """
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            if raise_exception:
                raise
        finally:
            session.close()

    return session_scope
