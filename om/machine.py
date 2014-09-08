# -*- coding: utf-8 -*-

import paramiko
import socket

from datetime import datetime

from om.plugin import create_plugin, list_plugins, list_default_plugins, NativeReachablePlugin
from om.executor import Executor
from om.metric import Metric
from om.utils.logger import get_logger

log = get_logger("machine")

class Machine(object):

    def __init__(self, host, machine_ssh, machine_metrics):
        self.host = host
        self.machine_ssh = machine_ssh
        self.plugins = Machine.load_plugins(machine_metrics)

    def run_plugins(self):
        machine_reachable_status = 'online'
        res = []

        try:
            executor = Executor(self.host, **self.machine_ssh)
            executor.start()
            for plugin in self.plugins:
                res.append(plugin.execute(executor))
            executor.stop()

        except paramiko.ssh_exception.AuthenticationException: #TODO machine should know nothing about paramiko
            machine_reachable_status = 'authfailed'
        except socket.error: #TODO machine should know nothing about sockets
            machine_reachable_status = 'unreachable'

        #Create metric for 'native' plugins that collect 'meta-metrics', such as if the machine was reachable
        reachable_plugin = NativeReachablePlugin()
        native_res = [Metric(self.host, reachable_plugin, datetime.now(), {'machine': {'reachable': machine_reachable_status}}, reachable_plugin.thresholds)]

        return native_res + res

    def __repr__(self):
        return "<Machine host='%s'>" % self.host

    @staticmethod
    def load_plugins(configs):
        instances = []
        if not configs:
            plugins = list_default_plugins()
            for p_klass in plugins:
                for name, c in configs.get(p_klass.name, {'default': {}}).iteritems():
                    instances.append(p_klass(**c))
        else:
            for c in configs:
                instances.append(create_plugin(c))

        return instances
