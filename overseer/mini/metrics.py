# -*- coding: utf-8 -*-

from collections import namedtuple

MetricPluginResult = namedtuple('MetricPluginResult', 'plugin host state value')
PLUGIN_STATES = ['normal', 'critical']


class MetricPlugin(object):
    '''Base class for all metrics
    '''

    def __init__(self, **kwargs):
        pass

    @property
    def name(self):
        return type(self).__name__

    def execute(self, remote, host):
        raise NotImplementedError('Run method not implemented in class %s' %
                                  self.get_name())

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<Metric name='%s'>" % (self.name_on_config)


class ShellMetricPlugin(MetricPlugin):

    @property
    def command(self):
        raise NotImplementedError()

    def _status_check(self, output, status):
        if status != 0: raise Exception
        return output

    def _output_parse(self, output, status):
        return output

    def execute(self, remote, host):
        output, status = remote.execute(self)

        # Middleware-like processing
        for processor in [self._status_check, self._output_parse]:
            output = processor(output, status)

        return MetricPluginResult(self, host, self.state, output)


class DiskUsage(ShellMetricPlugin):
    '''Verifies the amount of disk available on a given partition
    '''
    name_on_config = 'disk_usage'
    critical_usage = 80

    def __init__(self, critical_usage=critical_usage):
        if isinstance(critical_usage, unicode):
            critical_usage = int(critical_usage.replace('%', ''))
        self.critical_usage = critical_usage

    @property
    def command(self):
        return u'df -PT'

    def _output_parse(self, output, status):
        message = ''
        status = 'normal'

        for line in output[1:]:
            name, fstype, blocks, used, avail, usage, mnt = line.split()
            usage = int(usage.replace('%', ''))

            if usage >= self.critical_usage:
                message += "disk %s usage has reached critical: %d%% (over %d%%)." % (name, usage, self.critical_usage)
                self.state = 'critical'

        return message
