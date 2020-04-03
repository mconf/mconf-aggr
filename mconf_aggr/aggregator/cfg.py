#!/usr/bin/env python3.6

"""This module provides a configuration class for aggregator.

In order to be able to share configurations across the different components of
the aggregator, we provide a ``Config`` class. This class encapsulates all
external information we need to adjust the aggregator functioning.
A global object `config` is available for use in other modules.
"""
import configparser
import distutils.util
import json
import logging
import logging.config
import os


class EnvConfig:
    def __init__(self):
        self._config = {}

    def load(self):
        self._load_env()

        return self

    def _load_env(self):
        # Default values.
        self._config["MCONF_WEBHOOK_CALLBACK_URL"] = os.getenv("MCONF_WEBHOOK_CALLBACK_URL")
        self._config["MCONF_WEBHOOK_SHOULD_REGISTER"] = to_bool(os.getenv("MCONF_WEBHOOK_SHOULD_REGISTER", "True"))
        self._config["MCONF_WEBHOOK_DATABASE_HOST"] = os.getenv("MCONF_WEBHOOK_DATABASE_HOST")
        self._config["MCONF_WEBHOOK_DATABASE_USER"] = os.getenv("MCONF_WEBHOOK_DATABASE_USER")
        self._config["MCONF_WEBHOOK_DATABASE_PASSWORD"] = os.getenv("MCONF_WEBHOOK_DATABASE_PASSWORD")
        self._config["MCONF_WEBHOOK_DATABASE_DATABASE"] = os.getenv("MCONF_WEBHOOK_DATABASE_DATABASE")
        self._config["MCONF_WEBHOOK_DATABASE_PORT"] = os.getenv("MCONF_WEBHOOK_DATABASE_PORT") or "5432"
        self._config["MCONF_KAFKA_HOST"] = os.getenv("MCONF_KAFKA_HOST") or "localhost:9092"
        self._config["MCONF_KAFKA_TOPIC"] = os.getenv("MCONF_KAFKA_TOPIC")
        self._config["MCONF_KAFKA_GROUP_ID"] = os.getenv("MCONF_KAFKA_GROUP_ID")
        self._config["MCONF_WEBHOOK_ROUTE"] = os.getenv("MCONF_WEBHOOK_ROUTE") or "/"
        self._config["MCONF_WEBHOOK_AUTH_REQUIRED"] = to_bool(os.getenv("MCONF_WEBHOOK_AUTH_REQUIRED", "True"))
        self._config["MCONF_WEBHOOK_LOG_LEVEL"] = os.getenv("MCONF_WEBHOOK_LOG_LEVEL")
        self._config["MCONF_KAFKA_SASL_USERNAME"] = os.getenv("MCONF_KAFKA_SASL_USERNAME")
        self._config["MCONF_KAFKA_SASL_PASSWORD"] = os.getenv("MCONF_KAFKA_SASL_PASSWORD")
        self._config["MCONF_KAFKA_SECURITY_PROTOCOL"] = os.getenv("MCONF_KAFKA_SECURITY_PROTOCOL")
        self._config["MCONF_KAFKA_SASL_MECHANISM"] = os.getenv("MCONF_KAFKA_SASL_MECHANISM")

    def __getitem__(self, key):
        """Make accessing configurations easier."""
        try:
            value = self._config[key]
        except KeyError as e:
            value = None
            print("Invalid key: {}".format(key))  # Logger is not ready yet.
        finally:
            return value


def setup_logging(log_level, logging_config_file=None):
    """Load logging configuration from JSON file.

    It loads configurations to be used by the `logging` module.

    Parameters
    ----------
    log_level : str
        Log level required ("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL").
    logging_config_file: str
        Path to the logging JSON configuration file.

    References
    ----------
    Logging documentation for Python 3.

    `Logging library
    <https://docs.python.org/3/library/logging.html>`_

    `Logging basic tutorial
    <lhttps://docs.python.org/3/howto/logging.html#logging-basic-tutorial>`_

    `Logging advanced tutorial
    <https://docs.python.org/3/howto/logging.html#logging-advanced-tutorial>`_

    `Logging cookbook
    <https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook>`_
    """
    path = logging_config_file or _get_config_path("logging.json")
    if os.path.exists(path):
        with open(path, 'rt') as f:
            log_config = json.load(f)

        if log_level: log_config["root"]["level"] = log_level.upper()
        logging.config.dictConfig(log_config)
    else:
        print(f"WARN: Check the logging filepath: {path}")
        logging.basicConfig(level=logging.INFO)


def _get_config_path(config_file):
    module_path = os.path.dirname(__file__)
    config_dir = os.path.join(module_path, os.pardir)

    return os.path.join(config_dir, config_file)


def to_bool(s):
    return bool(distutils.util.strtobool(s))


"""Singleton ``Config`` instance. Intended to be used outside this module."""
config = EnvConfig().load()

# Load logging settings.
setup_logging(log_level=config["MCONF_WEBHOOK_LOG_LEVEL"])
