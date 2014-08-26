# -*- coding: utf-8 -*-

import json

from om.handler import StdoutHandler, MailHandler
from om.utils.logger import get_logger

log = get_logger("config")


class Config(object):

    def __init__(self, path):
        self._config = {}
        self._load_config(path)
        self._handlers = []

    def __getitem__(self, key):
        return self._config.__getitem__(key)

    def get(self, key, default_val):
        return self._config.get(key, default_val)

    def _load_config(self, path):
        if path is not None:
            with open(path) as config_file:
                self._config = json.load(config_file)

    @property
    def handlers(self):
        if not self._handlers:
            self._handlers = [StdoutHandler()]
            for handler, config in self.get('handlers', {}).iteritems():
                if handler == 'email':
                    self.handlers.append(MailHandler(**config))

            log.debug('loaded handlers %s' % self.handlers)

        return self._handlers