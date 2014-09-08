# -*- coding: utf-8 -*-
import os
import time

from om.config import Config
from om.handler import Handler
from om.plugin import list_native_plugins
from om.utils.logger import get_logger

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

log = get_logger("supervisor")


class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, supervisor, config_file='config.json'):
        self.supervisor = supervisor
        self.config_file = config_file

    def on_created(self, event):
        if event.src_path.endswith(self.config_file):
            self.supervisor.reload_config()

    def on_modified(self, event):
        if event.src_path.endswith(self.config_file):
            self.supervisor.reload_config()


class Supervisor(object):
    '''Schedules the remote metrics calls for monitored hosts. Delegates handling of
    results.
    '''
    POLL_FREQUENCY_MINUTES = 0.1
    CONFIG_FOLDER = '/etc/om'
    CONFIG_FILE = '/etc/om/config.json'

    def __init__(self, config_file=CONFIG_FILE):
        self.running = False
        self.config_file = config_file
        self._setup_config()
        self._setup_config_monitor()
        self.poll_frequency = self.config.get('poll_frequency', self.POLL_FREQUENCY_MINUTES)

    def _setup_config(self):
        self.config = Config(self.config_file)
        self.config_change_handler = ConfigChangeHandler(self, self.config_file)

    def _setup_config_monitor(self):
        self.observer = Observer()
        dirname = os.path.dirname(self.config_file)
        if not dirname:
            dirname = '.'
        self.observer.schedule(self.config_change_handler, path=dirname, recursive=False)

    def reload_config(self):
        log.info('Config file %s changed, reloading..' % self.CONFIG_FILE)
        try:
            new_config = Config(self.CONFIG_FILE)
            self.config = new_config
        except ValueError as e:
            log.error('There was an error loading the new configuration: %s' % e)

    def run_forever(self):
        self.observer.start()
        self.running = True
        while self.running:
            self.init_handlers()
            map(self.collect_metrics, self.config.hosts)
            self.finalize_handlers()
            time.sleep(self.poll_frequency * 60)
        self.observer.stop()
        self.observer.join()

    def stop(self):
        self.running = False

    def run(self):
        self.init_handlers()
        map(self.collect_metrics, self.config.hosts)
        self.finalize_handlers()

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
