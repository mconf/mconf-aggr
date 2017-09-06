#!/usr/bin/env python3.6


import json


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


config = Config()
