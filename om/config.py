# -*- coding: utf-8 -*-

import json

from om.handler import StdoutHandler, MailHandler
from om.machine import Machine
from om.utils.logger import get_logger

log = get_logger("config")


class Config(object):

    def __init__(self, path):
        self._config = {}
        self._load_config(path)
        self._handlers = []
        self._machines = []

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

    @property
    def machines(self):
        if not self._machines:
            self._machines = []
            global_metrics = self.get('metrics', {})
            global_ssh = self.get('ssh', {})

            for machine, config in self.get('machines', {}).iteritems():
                machine_host = config.get('host')
                machine_ssh = config.get('ssh', global_ssh)
                machine_metrics = global_metrics.copy()
                machine_metrics.update(config.get('metrics', {}))

                self._machines.append(Machine(machine_host, machine_ssh, machine_metrics))

        return self._machines