# -*- coding: utf-8 -*-
import time

from om.config import Config
from om.handler import StdoutHandler, MailHandler
from om.metrics import DiskUsage, MemoryUsage
from om.executor import Executor
from om.utils.logger import get_logger

log = get_logger("supervisor")


class Supervisor(object):
    '''Schedules the remote metrics calls for monitored machines. Delegates handling of
    results.
    '''
    DEFAULT_PLUGINS = [DiskUsage, MemoryUsage]
    POLL_FREQUENCY_MINUTES = 1

    def __init__(self, config_file=None):
        self.running = False
        self.config = Config(config_file)
        self.host_plugins = self._load_plugins()
        self.executors = self._load_executors()
        self.handlers = self._load_handlers()

    def run(self):
        self.running = True

        while self.running:
            map(self.collect_metrics, self.config['machines'])
            time.sleep(self.POLL_FREQUENCY_MINUTES * 60)

    def collect_metrics(self, machine):
        log.info("collecting metrics for machine=%s" % machine)
        results = []

        for plugin in self.host_plugins[machine]:
            results.append(plugin.execute(self.executors[machine], machine))

        self.handle_results(results)

    def handle_results(self, results=[]):
        for result in results:
            interested_handlers = self.get_handlers(result)
            for handler in interested_handlers:
                handler.handle(result)

    def get_handlers(self, plugin_result):
        '''Return a list of handlers interested on this plugin result
        '''
        return [handler for handler in self.handlers if handler.handles(plugin_result)]

    def _load_plugins(self):
        plugins = self.DEFAULT_PLUGINS
        plugins_per_host = {}

        global_metrics = self.config.get('metrics', {})

        for machine, config in self.config['machines'].iteritems():
            plugin_instances = []
            machine_metrics = config.get('metrics', {})

            for plugin_class in plugins:
                plugin_name = plugin_class.name_on_config
                overrides = machine_metrics.get(plugin_name) or global_metrics.get(plugin_name)
                overrides = overrides or {}
                plugin_instances.append(plugin_class(**overrides))

            plugins_per_host[machine] = plugin_instances

        log.debug('loaded plugins %s' % plugins_per_host)
        return plugins_per_host

    def _load_executors(self):
        global_ssh = self.config.get('ssh', {})
        executors = {}

        for machine, config in self.config['machines'].iteritems():
            host = config.get('host')
            machine_ssh = config.get('ssh', global_ssh)

            if host is None:
                raise Exception('Machine host must be present')

            executors[machine] = Executor(host, **machine_ssh)

        log.debug('loaded host connections %s' % executors)
        return executors

    def _load_handlers(self):
        handlers = [StdoutHandler()]
        for handler, config in self.config.get('handlers', {}).iteritems():
            if handler == 'email':
                handlers.append(MailHandler(**config))

        log.debug('loaded handlers %s' % handlers)
        return handlers
