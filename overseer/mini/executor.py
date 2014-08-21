# -*- coding: utf-8 -*-

import paramiko
import getpass

class Executor(object):
    '''Responsible for connecting and executing tasks remotely

    Connects to the remote computer and executes a list of overseer.mini.Task.
    The results are gathered and available to the caller
    '''

    def __init__(self, host, port=22, username=getpass.getuser(),
                 password=None, use_local_keys=True,
                 autoadd_unknown_hosts=True, **options):
        self.host = host
        self.options = options

    def run(self, tasks):
        '''Connects to remote computer and execute the tasks
        '''
        client = self.client
        client.connect(self.host, port=self.options['port'],
                            username=self.options['username'],
                            password=self.options['password'])
        for t in tasks:
            t.run(client)
        client.close()
        client = None

    @property
    def client(self):
        '''Returns a client on demand.
        '''
        client = paramiko.client.SSHClient()
        if self.options.use_local_keys:
            client.load_system_host_keys()
        if self.options.autoadd_unknown_hosts:
            client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        return client

    def execute(self, plugin):
        stdin, stdout, stderr = self.client.exec_command(plugin.command)
        output = stdout.readlines()
        stderr = stderr.readlines()
        status = stdout.channel.recv_exit_status()
        return output, status
