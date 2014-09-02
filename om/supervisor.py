# -*- coding: utf-8 -*-
import time

from om.config import Config
from om.handler import Handler
from om.plugin import list_native_plugins
from om.utils.logger import get_logger

log = get_logger("supervisor")


class Supervisor(object):
    '''Schedules the remote metrics calls for monitored hosts. Delegates handling of
    results.
    '''
    POLL_FREQUENCY_MINUTES = 5

    def __init__(self, config_file=None):
        self.running = False
        self.config = Config(config_file)
        self.poll_frequency = self.config.get('poll_frequency', self.POLL_FREQUENCY_MINUTES)

    def run(self):
        self.running = True
        while self.running:
            self.init_handlers()
            map(self.collect_metrics, self.config.hosts)
            self.finalize_handlers()

            time.sleep(self.poll_frequency * 60)

    def init_handlers(self):
        plugins = set(list_native_plugins())
        for machine in self.config.hosts:
            for p in machine.plugins:
                plugins.add(p)

        for h in self.config.handlers:
            h.setup()
            for p in plugins:
                h.setup_for_plugin(p)



    def finalize_handlers(self):
        for h in self.config.handlers:
            h.teardown()

    def collect_metrics(self, machine):
        log.debug("collecting for %s" % machine.host)
        self.handle_results(machine.run_plugins())

    def handle_results(self, results=[]):
        [map(Handler._handle(result), self.derive_handlers(result)) for result in results]

    def derive_handlers(self, result):
        return filter(Handler._handles(result), self.config.handlers)
