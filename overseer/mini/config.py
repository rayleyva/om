# -*- coding: utf-8 -*-

import json

class Config(object):
    '''Loads a config file into a executor and task objects

       TODO Document config parameters
    '''

    def __init__(self, path):
        self._config = {}
        self._load_config(path)

    def __getitem__(self, key):
        return self._config.__getitem__(key)

    def get(self, key, default_val):
        return self._config.get(key, default_val)

    def _load_config(self, path):
        with open(path) as config_file:
            self._config = json.load(config_file)

    # DEPRECATED
    # def create_task(self, name, data):
    #     if name == 'diskusage':
    #         return tasks.DiskUsageTask()
    #     return None #TODO

    # def get_executors(self):
    #     # DEPRECATED
    #     self.load()

    #     global_ssh = self.config.get('ssh', {})
    #     global_tasks = [self.create_task(n,t) for n,t in self.config.get('metrics', {}).items()]

    #     for machine, m_data in self.config['machines'].items():
    #         ssh = global_ssh.copy()
    #         ssh.update(m_data.get('ssh', {}))

    #         re = executor.Executor(m_data['host'], ssh['user'],
    #                                ssh.get('port', None))

    #         tasks = global_tasks[:]

    #         for task_name, task_data in m_data.get('metrics', []):
    #             tasks.append(self.create_task(task_name, task_data))

    #         yield re, tasks
