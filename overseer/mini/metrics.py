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
        return self.get_name()


class ShellMetricPlugin(MetricPlugin):

    @property
    def command(self):
        raise NotImplementedError()

    def _status_check(self, output, status):
        if status != 0: raise Exception
        return output

    def _output_parse(self, output, status):
        return output

    def _get_state(self, output, status):
        if status != 0:
            return 'critical'
        else:
            return 'normal'

    def execute(self, remote, host):
        output, status = remote.execute(self)

        # Middleware-like processing
        for processor in [self._status_check, self._output_parse]:
            output = processor(output, status)

        return MetricPluginResult(self, host, self._get_state(output, status), output)


class DiskUsage(ShellMetricPlugin):
    '''Verifies the amount of disk available on a given partition
    '''
    name_on_config = 'disk_usage'
    critical_usage = 80

    def __init__(self, critical_usage=critical_usage):
        if isinstance(critical_usage, unicode):
            critical_usage = int(critical_usage.replace('%', ''))
        self.critical_usage = critical_usage
        self.parsed = {}

    @property
    def command(self):
        return u'df -PT'

    def _get_state(self, output, status):
        if any([disk['capacity'] >= self.critical_usage for name, disk in self.parsed.iteritems()]):
            return 'critical'
        else:
            return 'normal'

    def _output_parse(self, output, status):
        for line in output[1:]:
            name, fstype, blocks, used, avail, capacity, mnt = line.split()
            capacity = int(capacity.replace('%', ''))
            self.parsed[name] = { 'fs': fstype, 'capacity': capacity }
        return self.parsed
