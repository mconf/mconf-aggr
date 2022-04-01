from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mconf_aggr.aggregator import cfg


class DatabaseConnector:
    """Wrapper of PostgreSQL connection.

    It encapsulates the inner workings of the SQLAlchemy connection process.

    Before using it, one must call once its method `connect()` to configure and
    create a connection to the database. Then, the `update()` method can be
    called for each metric whenever it is necessary to update the database.
    When finished, one must call `close()` to definitely close the connection
    to the database (currently it does nothing).
    """

    Session = None

    @classmethod
    def connect(cls):
        """Configure and connect the database.

        It is responsible for creating an engine for the URI provided and
        configure the session.
        """
        engine = create_engine(cls._build_uri(), echo=False)
        cls.Session = sessionmaker()
        cls.Session.configure(bind=engine)

    @classmethod
    def close(cls):
        """Close the connection to the database.

        It currently does nothing.
        """
        pass

    @classmethod
    def get_session_scope(cls):
        @contextmanager
        def session_scope(raise_exception=True):
            """Provide a transactional scope around a series of operations."""
            session = cls.Session()
            try:
                yield session
                session.commit()
            except RuntimeError:
                session.rollback()
                if raise_exception:
                    raise
            finally:
                session.close()

        return session_scope

    @classmethod
    def _build_uri(cls):
        user = cfg.config["MCONF_WEBHOOK_DATABASE_USER"]
        password = cfg.config["MCONF_WEBHOOK_DATABASE_PASSWORD"]
        host = cfg.config["MCONF_WEBHOOK_DATABASE_HOST"]
        database = cfg.config["MCONF_WEBHOOK_DATABASE_DATABASE"]
        port = cfg.config["MCONF_WEBHOOK_DATABASE_PORT"]

        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
