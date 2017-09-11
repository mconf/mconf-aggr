#!/usr/bin/env python3.6


import json
import logging
import logging.config
import os


class Config:
    def __init__(self, custom_config=None):
        self.custom_config = custom_config
        self._config = {}

        self.load_config("default.json")
        if custom_config: self.load_config(self.custom_config)

    def load_config(self, config_file):
        config = self.read_config(config_file)
        if self._config is None:
            self._config = config
        else:
            self._config.update(config)

    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)

        return config

    def __getitem__(self, key):
        try:
            value = self._config[key]
        except KeyError as e:
            # Log it.
            value = None
            print("Invalid key: {}".format(key))
        finally:
            return value


def setup_logging(default_path='logging.json',
                  default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


config = Config()
