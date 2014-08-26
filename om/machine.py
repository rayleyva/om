# -*- coding: utf-8 -*-

from om.metrics import CPULoad, DiskUsage, MemoryUsage
from om.executor import Executor
from om.utils.logger import get_logger

log = get_logger("machine")


class Machine(object):
    DEFAULT_PLUGINS = [CPULoad, DiskUsage, MemoryUsage]

    def __init__(self, host, machine_ssh, machine_metrics):
        self.executor = Executor(host, **machine_ssh)
        self.plugins = self._load_plugins(machine_metrics)

    def run_plugins(self):
        return [plugin.execute(self) for plugin in self.plugins]

    def _load_plugins(self, machine_metrics):
        plugin_classes = self.DEFAULT_PLUGINS
        plugin_instances = []

        for plugin_class in plugin_classes:
            plugin_name = plugin_class.name_on_config
            overrides = machine_metrics.get(plugin_name, {})
            plugin_instances.append(plugin_class(**overrides))

        log.debug('loaded plugins %s' % plugin_instances)
        return plugin_instances

    def __repr__(self):
        return "<Machine executor='%s' plugins=%s>" % \
               (self.executor, self.plugins)