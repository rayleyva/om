# -*- coding: utf-8 -*-

import paramiko
import getpass

class Executor(object):
    '''Responsible for connecting and executing tasks remotely

    Connects to the remote computer and executes a list of overseer.mini.Task.
    The results are gathered and available to the caller
    '''

    def __init__(self, host, username=getpass.getuser(), port=22,
                 password=None, use_local_keys=True,
                 autoadd_unknown_hosts=True, **options):
        self.host = host
        self.port = int(port) if port else 22
        self.username = username
        self.password = password
        self.use_local_keys = use_local_keys
        self.autoadd_unknown_hosts = autoadd_unknown_hosts
        self.options = options

    def _get_connection_optional_args(self):
        args = {}
        if self.password:
            args['password'] = self.password
        return args

    def get_client(self):
        '''Returns a client on demand.
        '''
        client = paramiko.client.SSHClient()
        if self.use_local_keys:
            client.load_system_host_keys()
        if self.autoadd_unknown_hosts:
            client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        return client

    def execute(self, plugin):
        client = self.get_client()
        optional_args = self._get_connection_optional_args()
        client.connect(self.host, port=self.port, username=self.username,
                       **optional_args)

        stdin, stdout, stderr = client.exec_command(plugin.command)
        output = stdout.readlines()
        stderr = stderr.readlines()
        status = stdout.channel.recv_exit_status()
        client.close()
        return output, status

    def __repr__(self):
        return "<Connection " + \
               "host='%s' port=%d username='%s' password='%s'>" \
               % (self.host, self.port, self.username, 'REDACTED' if self.password else '')
