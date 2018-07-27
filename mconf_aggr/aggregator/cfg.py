#!/usr/bin/env python3.6

"""This module provides a configuration class for aggregator.

In order to be able to share configurations across the different components of
the aggregator, we provide a ``Config`` class. This class encapsulates all
external information we need to adjust the aggregator functioning.
A global object `config` is available for use in other modules.
"""

import json
import logging
import logging.config
import os


def get_config_path(config_file):
    module_path = os.path.dirname(__file__)
    config_dir = os.path.join(module_path, os.pardir, os.pardir, "config")

    return os.path.join(config_dir, config_file)


class Config:
    """Configuration for aggregator functioning and logging settings.

    This class is not intended to be instantiated outside here. Instead, one
    should use the module-level object `config` as a singleton for this class.
    """
    def __init__(self, custom_config=None):
        """Initialize a `Config` object.

        Parameters
        ----------
        custom_config : str
            Path to the custom JSON configuration file.
        """
        self.custom_config = custom_config
        self._config = {}

        # Load default configurations.
        self.setup_config()
        # Load custom configurations if a config file was provided.
        if custom_config:
            self.setup_config(self.custom_config)

    def setup_config(self, config_file=None):
        """Load general configuration from JSON file.

        It updates the set of configurations with those from the
        `config_file`. Conflicting settings are replaced by new ones.

        Parameters
        ----------
        config_file : str
            Path to the custom JSON configuration file.
            If missing, it defaults to "config/default.json".
        """
        config_file = config_file or get_config_path("default.json")
        config = self.read_config(config_file)
        if self._config is None:
            self._config = config
        else:
            self._config.update(config)

    def setup_logging(self, logging_config_file=None,
                      default_level=logging.INFO, env_key="LOG_CFG"):
        """Load logging configuration from JSON file.

        It loads configurations to be used by the `logging` module.

        Parameters
        ----------
        default_path : str
            Path to the logging JSON configuration file.
            If missing, it defaults to "config/logging.json"
        default_level : int
            Log level required. Defaults to `logging.INFO`.
        env_key : str
            Environment variable used by `logging` module.
            Defaults to "LOG_CFG".

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
        path = logging_config_file or get_config_path("logging.json")
        value = os.getenv(env_key, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)

    def read_config(self, config_file):
        """Read json file and populate dict.

        Parameters
        ----------
        config_file : str
            Path to the JSON configuration file.

        Returns
        -------
        config : dict
            Dictionary with configurations read from `config_file`.
        """
        with open(config_file, 'r') as f:
            config = json.load(f)

        return config

    @property
    def zabbix(self):
        return self['zabbix']

    def __getitem__(self, key):
        """Make accessing configurations easier."""
        try:
            value = self._config[key]
        except KeyError as e:
            value = None
            print("Invalid key: {}".format(key))  # Logger is not ready yet.
        finally:
            return value


"""Singleton ``Config`` instance. Intended to be used outside this module."""
config = Config()
