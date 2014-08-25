# -*- coding: utf-8 -*-
import time

from om.config import Config
from om.handler import StdoutHandler, MailHandler
from om.machine import Machine
from om.utils.logger import get_logger

log = get_logger("supervisor")


class Supervisor(object):
    '''Schedules the remote metrics calls for monitored machines. Delegates handling of
    results.
    '''
    POLL_FREQUENCY_MINUTES = 1

    def __init__(self, config_file=None):
        self.running = False
        self.config = Config(config_file)
        self._load_handlers()
        self._load_machines()

    def run(self):
        self.running = True

        while self.running:
            map(self.collect_metrics, self.machines)
            time.sleep(self.POLL_FREQUENCY_MINUTES * 60)

    def collect_metrics(self, machine):
        log.info("collecting metrics for machine=%s" % machine)
        results = machine.run_plugins()
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

    def _load_handlers(self):
        self.handlers = [StdoutHandler()]
        for handler, config in self.config.get('handlers', {}).iteritems():
            if handler == 'email':
                self.handlers.append(MailHandler(**config))

        log.debug('loaded handlers %s' % self.handlers)

    def _load_machines(self):
        self.machines = []
        global_metrics = self.config.get('metrics', {})
        global_ssh = self.config.get('ssh', {})

        for machine, config in self.config.get('machines', {}).iteritems():
            machine_host = config.get('host')
            machine_ssh = config.get('ssh', global_ssh)
            machine_metrics = global_metrics.copy()
            machine_metrics.update(config.get('metrics', {}))

            self.machines.append(Machine(machine_host, machine_ssh, machine_metrics))
