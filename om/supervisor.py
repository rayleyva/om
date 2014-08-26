# -*- coding: utf-8 -*-
import time

from om.config import Config
from om.machine import Machine
from om.handler import Handler
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
        self._load_machines()

    def run(self):
        self.running = True

        while self.running:
            map(self.collect_metrics, self.machines)
            time.sleep(self.POLL_FREQUENCY_MINUTES * 60)

    def collect_metrics(self, machine):
        log.info("collecting metrics for machine=%s" % machine)
        self.handle_results(machine.run_plugins())

    def handle_results(self, results=[]):
        [map(Handler._handle(result), self.derive_handlers(result)) for result in results]

    def derive_handlers(self, result):
        '''Return a list of handlers interested on this plugin result
        '''
        return filter(Handler._handles(result), self.config.handlers)

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
