# -*- coding: utf-8 -*-

import json

class Config(object):

    def __init__(self, path):
        self._config = {}
        self._load_config(path)

    def __getitem__(self, key):
        return self._config.__getitem__(key)

    def get(self, key, default_val):
        return self._config.get(key, default_val)

    def _load_config(self, path):
        if path is not None:
            with open(path) as config_file:
                self._config = json.load(config_file)
