# -*- coding: utf-8 -*-

from collections import namedtuple

MetricPluginResult = namedtuple('MetricPluginResult', 'plugin host state value')
PLUGIN_STATES = ['normal', 'critical']


class MetricPlugin(object):
    '''Base class for all metrics
    '''
    @property
    def name(self):
        return type(self).__name__

    def execute(self, executor):
        raise NotImplementedError('Run method not implemented in class %s' %
                                  self.get_name())

    def __unicode__(self):
        return self.get_name()


class ShellMetricPlugin(MetricPlugin):

    @property
    def command(self):
        raise NotImplementedError()

    def _status_check(self, output, status):
        raise Exception if status != 0
        return output

    def _output_parse(self, output, status):
        return output

    def _get_state(self, output, status):
        if status != 0:
            return 'critical'
        else:
            return 'normal'

    def execute(self, remote, host):
        output, status = remote.execute(self.command)

        # Middleware-like processing
        for processor in [self._status_check, self._output_parse]:
            output = processor(output, status)

        return MetricPluginResult(self, host, self._get_state(output, status), output)


class DiskUsage(ShellMetricPlugin):
    '''Verifies the amount of disk available on a given partition
    '''

    @property
    def command(self):
        return u'df -h'

    def _output_parse(self, output, status):
        #TODO implement
        print ''.join(output)
