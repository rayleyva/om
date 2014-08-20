# -*- coding: utf-8 -*-

class Task(object):
    '''Base class for all tasks from Overseer-mini
    '''

    @property
    def name(self):
        return type(self).__name__

    def __unicode__(self):
        return self.get_name()

    def run(self, remote):
        raise NotImplementedError('Run method not implemented in class %s' %
                                  self.get_name())

class ShellCommandTask(Task):

    def run(self, remote):
        command = self.get_command()
        stdin, stdout, stderr = remote.exec_command(command)
        output = stdout.readlines()
        status = stdout.channel.recv_exit_status()
        self.check_status_code(status)
        self.parse_output(output)

    def check_status_code(self, status):
        #TODO add exception raising or failure reports if status != 0
        pass

    def parse_output(self, output):
        pass

class DiskUsageTask(ShellCommandTask):
    '''Verifies the amount of disk available on a given partition
    '''

    def get_command(self):
        return u'df -h'

    def parse_output(self, output):
        #TODO implement
        print ''.join(output)
