# -*- coding: utf-8 -*-

class RemoteExecutor(object):
    '''Responsible for connecting and executing tasks remotely

    Connects to the remote computer and executes a list of overseer.mini.Task.
    The results are gathered and available to the caller
    '''

    def __init__(self, host, username):
        self.tasks = []
        self.host = host
        self.username = username

    def add_task(self, t):
        self.tasks.append(t)

    def run(self):
        for t in self.tasks:
            print t
