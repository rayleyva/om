# -*- coding: utf-8 -*-

import json

from overseer.mini import executor, tasks

class ConfigLoader(object):
    '''Loads a config file into a executor and task objects

       TODO Document config parameters
    '''

    def __init__(self, path):
        self.path = path
        self.config = {}

    def load(self):
        with open(self.path) as filedata:
            self.config = json.load(filedata)

    def create_task(self, data):
        if data['type'] == 'diskusage':
            return tasks.DiskUsageTask()
        return None #TODO

    def get_executors(self):
        self.load()

        global_tasks = [self.create_task(t) for t in self.config.get('tasks', [])]

        for machine in self.config['machines']:
            re = executor.RemoteExecutor(machine['host'], machine.get('username', self.config['username']))

            for task in global_tasks:
                re.add_task(task)

            for task_data in machine.get('tasks', []):
                re.add_task(self.create_task(task_data))

            yield re
