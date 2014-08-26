# -*- coding: utf-8 -*-

from collections import namedtuple

class Metric(object):

    def __init__(self, host, plugin, values={}, thresholds={}):
        self.host = host
        self.plugin = plugin
        self.values = values
        self.thresholds = thresholds

    @property
    def state(self):
        for key, value in self.values.iteritems():
            if self.thresholds.get(key): continue
            if value > self.thresholds.get(key):
                return 'critical'
        return 'normal'

class Plugin(object):
    '''Base class for all metrics
    '''
    PLUGIN_STATES = ['normal', 'critical']
    name = ''

    def __init__(self, *args, **kwargs):
        super(Plugin,self).__init__() #swallow arguments

    def execute(self, executor):
        raise NotImplementedError('Execute method must be implemented')

    def __repr__(self):
        return "<Plugin name='%s'>" % (self.name)


class ShellPlugin(Plugin):
    thresholds = {}

    @property
    def command(self):
        raise NotImplementedError()

    def _status_check(self, output, status):
        if status != 0: raise Exception
        return output

    def _output_parse(self, output, status):
        return output

    def execute(self, executor):
        output, status = executor.execute(self)

        # Middleware-like processing
        for processor in [self._status_check, self._output_parse]:
            output = processor(output, status)

        return Metric(executor.host, self, output, self.thresholds)


class DiskUsage(ShellPlugin):
    '''Verifies disk usage
    '''
    name = 'disk_usage'
    thresholds = {'usage': 80}

    @property
    def command(self):
        return u'df -PT'

    def _output_parse(self, output, status):
        values = {}

        for line in output[1:]:
            name, fstype, blocks, used, avail, usage, mnt = line.split()
            usage = int(usage.replace('%', ''))

            if name == 'none': continue

            values[name] = usage

        return values


class MemoryUsage(ShellPlugin):
    '''Verifies memory usage
    '''
    name = 'memory_usage'
    thresholds = {'usage': 70}

    @property
    def command(self):
        return u'free -m | grep buffers/cache'

    def _output_parse(self, output, status):
        _, _, used, free = output[0].split()
        used, free = int(used), int(free)
        total = used + free
        usage = 100 * used/float(total)
        return {'used': used, 'free': free, 'total': total, 'usage': usage}


class CPULoad(ShellPlugin):
    '''Verifies CPU load
    '''
    name = 'cpu_load'
    thresholds = {'avg_1min': 25, 'avg_5min': 50, 'avg_15min': 75}

    @property
    def command(self):
        return u'cat /proc/loadavg'

    def _output_parse(self, output, status):
        return dict(zip(['avg_1min', 'avg_5min', 'avg_15min'], [float(avg) for avg in output[0].split()[:3]]))

class ProcessState(ShellPlugin):
    '''Verifies if a process is running
    '''
    name = 'process_state'

    def __init__(self, **kwargs):
        super(ProcessState, self).__init__(**kwargs)
        self.process_name = kwargs.get('process_name', '')
        if not self.process_name:
            pass #TODO raise exception

    def _status_check(self, output, status):
        return output #ignore status

    @property
    def command(self):
        return u'ps cax | grep %s' % (self.process_name)

    def _output_parse(self, output, status):
        if output:
            for line in output:
                tokens = line.strip().split()
                if tokens[-1] == self.process_name:
                    return {'status' : 'running'}

        return {'status' : 'not-running'}

PLUGINS_LIST = [DiskUsage, CPULoad, MemoryUsage, ProcessState]
def list_plugins():
    return PLUGINS_LIST

DEFAULT_PLUGINS = [CPULoad, DiskUsage, MemoryUsage]
def list_default_plugins():
    return DEFAULT_PLUGINS