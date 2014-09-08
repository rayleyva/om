# -*- coding: utf-8 -*-

import os, errno
import json
import getpass

from om.handler import JSONStdoutHandler, StdoutHandler, MailHandler, RedisHandler, Sqlite3Handler
from om.machine import Machine
from om.utils.logger import get_logger

log = get_logger("config")



def mkdir_p(path):
    try:
        os.makedirs(path)
    except os.error, e:
        if e.errno != errno.EEXIST:
            raise

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
        if path is not None and os.path.exists(path):
            with open(path) as config_file:
                self._config = json.load(config_file)
        else:
            self._bootstrap_config(path)

    def _bootstrap_config(self, path):
        log.info("Creating %s" % path)
        self._config = {'hosts': {}, 'handlers': {'stdout': {}}}

        try:
            mkdir_p('/etc/om')
            with open(path, 'w') as config_file:
                json.dump(self._config, config_file)
        except OSError as ose:
            log.error('Insufficient permissions at /etc/om. Please "sudo mkdir /etc/om" and "sudo chown %s /etc/om"' % getpass.getuser())
            raise ose

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
            global_metrics = self.get('plugins', [])
            global_ssh = self.get('ssh', {})

            for machine, config in self.get('hosts', {}).iteritems():
                machine_host = config.get('host')
                machine_ssh = config.get('ssh', global_ssh)
                machine_metrics = global_metrics[:]
                machine_metrics.extend(config.get('plugins', []))
                self._hosts.append(Machine(machine_host, machine_ssh, machine_metrics))
            log.debug('loaded hosts %s' % self._hosts)

        return self._hosts
