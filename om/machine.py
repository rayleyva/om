# -*- coding: utf-8 -*-

from om.metrics import CPULoad, DiskUsage, MemoryUsage
from om.executor import Executor
from om.utils.logger import get_logger

log = get_logger("machine")


class Machine(object):
    DEFAULT_PLUGINS = [CPULoad, DiskUsage, MemoryUsage]

    def __init__(self, host, machine_ssh, machine_metrics):
        self.executor = Executor(host, **machine_ssh)
        self.plugins = Machine.load_plugins(machine_metrics)

    def run_plugins(self):
        return [plugin.execute(self) for plugin in self.plugins]

    def __repr__(self):
        return "<Machine executor='%s' plugins=%s>" % \
               (self.executor, self.plugins)

    @staticmethod
    def load_plugins(configs, plugins=DEFAULT_PLUGINS):
        load = lambda plugin: plugin(**configs.get(plugin.name_on_config, {}))
        return map(load, plugins)

