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
    '''Verifies disk usage
    '''
    name_on_config = 'disk_usage'
    critical = 80

    def __init__(self, critical=critical):
        if isinstance(critical, unicode):
            critical = int(critical.replace('%', ''))
        self.critical = critical

    @property
    def command(self):
        return u'df -PT'

    def _output_parse(self, output, status):
        message = ''
        self.state = 'normal'

        for line in output[1:]:
            name, fstype, blocks, used, avail, usage, mnt = line.split()
            usage = int(usage.replace('%', ''))

            if name == 'none': continue

            if usage >= self.critical:
                message += "disk %s usage has reached critical: %d%% (over %d%%). " % (name, usage, self.critical)
                self.state = 'critical'
            else:
                message += "disk %s usage: %d%% (used=%s, avail=%s). " % (name, usage, used, avail)

        return message


class MemoryUsage(ShellMetricPlugin):
    '''Verifies memory usage
    '''
    name_on_config = 'memory_usage'
    critical = 70

    def __init__(self, critical=critical):
        if isinstance(critical, unicode):
            critical = int(critical.replace('%', ''))
        self.critical = critical

    @property
    def command(self):
        return u'free -m | grep buffers/cache'

    def _output_parse(self, output, status):
        message = ''
        self.state = 'normal'

        _, _, used, free = output[0].split()
        used, free = int(used), int(free)
        total = used + free
        usage = 100 * used/float(total)

        if usage >= self.critical:
            message += "memory usage has reached critical: %d%% (over %d%%)." % (name, usage, self.critical)
            self.state = 'critical'
        else:
            message += "memory usage %.2f%% (used=%d, free=%d)." % (usage, used, free)

        return message
