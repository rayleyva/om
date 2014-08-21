# -*- coding: utf-8 -*-
import time

from overseer.mini.config import Config
from overseer.mini.handler import StdoutHandler
from overseer.mini.metrics import DiskUsage
from overseer.mini.executor import Executor


class Supervisor(object):
    '''Schedules the remote metrics calls for monitored machines. Delegates handling of
    results.
    '''

    def __init__(self, config_file=None):
        self.metric_plugins = [DiskUsage()]
        self.handlers = [StdoutHandler()]
        self.running = False
        self.config = Config(config_file)
        self.executors = {}

        global_ssh = self.config.get('ssh', {})

        for machine, config in self.config['machines'].iteritems():
            print "Creating executor for %s (extra vars: %s)" % (machine, config)

            host = config.get('host')
            machine_ssh = config['ssh'] or global_ssh

            if host is None:
                raise Exception('Machine host must be present')

            self.executors[machine] = Executor(host, **machine_ssh)

    def run(self):
        self.running = True

        while self.running:
            map(self.collect_metrics, self.config['machines'])
            time.sleep(15)

    def collect_metrics(self, machine):
        print "Collecting metrics for machine=%s" % machine
        results = []

        for plugin in self.metric_plugins:
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