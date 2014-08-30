# -*- coding: utf-8 -*-

import json

from om.handler import JSONStdoutHandler, StdoutHandler, MailHandler, RedisHandler, Sqlite3Handler
from om.machine import Machine
from om.utils.logger import get_logger

log = get_logger("config")


class Config(object):

    def __init__(self, path):
        self._config = {}
        self._load_config(path)
        self._handlers = []
        self._hosts = []

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
            for handler, config in self.get('handlers', {}).iteritems():
                if handler == 'email':
                    self._handlers.append(MailHandler(**config))
                elif handler == 'stdout':
                    self._handlers.append(StdoutHandler(**config))
                elif handler == 'json_stdout':
                    self._handlers.append(JSONStdoutHandler(**config))
                elif handler == 'redis':
                    self._handlers.append(RedisHandler(**config))
                elif handler == 'sqlite3':
                    self._handlers.append(Sqlite3Handler(**config))
            log.debug('loaded handlers %s' % self._handlers)

        return self._handlers

    @property
    def hosts(self):
        if not self._hosts:
            global_metrics = self.get('plugins', {})
            global_ssh = self.get('ssh', {})

            for machine, config in self.get('hosts', {}).iteritems():
                machine_host = config.get('host')
                machine_ssh = config.get('ssh', global_ssh)
                machine_metrics = global_metrics.copy()
                machine_metrics.update(config.get('plugins', {}))
                self._hosts.append(Machine(machine_host, machine_ssh, machine_metrics))
            log.debug('loaded hosts %s' % self._hosts)

        return self._hosts