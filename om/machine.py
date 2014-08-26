# -*- coding: utf-8 -*-

from om.metrics import list_plugins, list_default_plugins
from om.executor import Executor
from om.utils.logger import get_logger

log = get_logger("machine")


class Machine(object):

    def __init__(self, host, machine_ssh, machine_metrics):
        self.host = host
        self.machine_ssh = machine_ssh
        self.plugins = Machine.load_plugins(machine_metrics)

    def run_plugins(self):
        executor = Executor(self.host, **self.machine_ssh)
        executor.start()
        res = [plugin.execute(executor) for plugin in self.plugins]
        executor.stop()
        return res

    def __repr__(self):
        return "<Machine executor='%s' plugins=%s>" % \
               (self.executor, self.plugins)

    @staticmethod
    def load_plugins(configs):
        if not configs:
            plugins = list_default_plugins()
        else:
            pnames = configs.keys()
            plugins = [p for p in list_plugins() if p.name in pnames]
        load = lambda plugin: plugin(**configs.get(plugin.name, {}))
        return map(load, plugins)

