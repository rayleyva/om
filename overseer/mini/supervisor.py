# -*- coding: utf-8 -*-

from overseer.mini.config import ConfigLoader
from overseer.mini.executor import Executor


class Supervisor(object):
    '''Schedules the remote metrics calls for monitored hosts. Delegates handling of
    results.
    '''

    def __init__(self, config_file=None):
        self.metric_plugins = []
        self.handlers = []
        self.config = self.load_config(config_file)
        self.plugin_executor = Executor()
        self.running = False

    def run(self):
        self.running = True

        while self.running:
            map(self.collect_metrics, self.config['hosts'])

    def collect_metrics(self, host):
        results = []

        for plugin in self.metric_plugins:
            results << plugin.execute(self.plugin_executor, host)

        self.handle_results(results)

    def handle_results(self, results=[]):
        for result in results:
            interested_handlers = self.get_handlers(result)
            handler.handle(result) if handler is not None

    def get_handlers(self, plugin_result):
        '''Return a list of handlers interested on this plugin result
        '''
        return [handler for handler in self.handlers if handler.handles(plugin_result)]