# -*- coding: utf-8 -*-

import paramiko

class RemoteExecutor(object):
    '''Responsible for connecting and executing tasks remotely

    Connects to the remote computer and executes a list of overseer.mini.Task.
    The results are gathered and available to the caller
    '''

    def __init__(self, host, username):
        self.tasks = []
        self.host = host
        self.username = username
        self.client = None

    def add_task(self, t):
        self.tasks.append(t)

    def run(self):
        '''Connects to remote computer and execute the tasks
        '''
        self.client = self._create_client()
        self.client.connect(self.host, username=self.username)
        for t in self.tasks:
            t.run(self.client)
        self.client.close()
        self.client = None

    def _create_client(self):
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()

        #FIXME remove this and expose an option to use it
        client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

        return client
