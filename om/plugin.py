# -*- coding: utf-8 -*-

from datetime import datetime

from om.thresholds import NumericThresholdCreatorMixin, EnumThresholdCreatorMixin
from om.metric import Metric

class Plugin(object):
    '''Base class for all metrics
    '''
    PLUGIN_STATES = ['normal', 'critical']
    name = ''
    metric_descriptions = {}

    def __init__(self, *args, **kwargs):
        super(Plugin,self).__init__() #swallow arguments

    def execute(self, executor):
        raise NotImplementedError('Execute method must be implemented')

    def __repr__(self):
        return "<Plugin name='%s'>" % (self.name)

class NativeReachablePlugin(Plugin, EnumThresholdCreatorMixin):
    name = 'native_reachable'
    metric_descriptions = {'reachable': 'string(32)'}
    default_thresholds = {'reachable': {'good': ['online'],
                                        'bad': ['unreachable', 'autherror']}}

    def __init__(self, **kwargs):
        super(NativeReachablePlugin, self).__init__(**kwargs)
        self.create_thresholds(kwargs.get('thresholds', self.default_thresholds))

class ShellPlugin(Plugin):
    default_thresholds = {}

    def __init__(self, **kwargs):
        super(ShellPlugin, self).__init__(**kwargs)
        self.create_thresholds(kwargs.get('thresholds', self.default_thresholds))

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

        return Metric(executor.host, self, datetime.now(), output, self.thresholds)


class DiskUsage(ShellPlugin, NumericThresholdCreatorMixin):
    '''Verifies disk usage
    '''
    name = 'disk_usage'
    default_thresholds = {'usage': 80}
    metric_descriptions = {'usage': 'int'}

    @property
    def command(self):
        return u'df -PT'

    def _output_parse(self, output, status):
        values = {}

        for line in output[1:]:
            name, fstype, blocks, used, avail, usage, mnt = line.split()
            usage = int(usage.replace('%', ''))

            if name == 'none': continue

            values[name] = {'usage' : usage}

        return values


class MemoryUsage(ShellPlugin, NumericThresholdCreatorMixin):
    '''Verifies memory usage
    '''
    name = 'memory_usage'
    default_thresholds = {'usage': 70}
    metric_descriptions = {'usage': 'int'}

    @property
    def command(self):
        return u'free -m | grep buffers/cache'

    def _output_parse(self, output, status):
        _, _, used, free = output[0].split()
        used, free = int(used), int(free)
        total = used + free
        usage = 100 * used/float(total)
        return {'system' : {'used': used, 'free': free, 'total': total, 'usage': usage}}


class CPULoad(ShellPlugin, NumericThresholdCreatorMixin):
    '''Verifies CPU load
    '''
    name = 'cpu_load'
    default_thresholds = {'avg_1min': 25, 'avg_5min': 50, 'avg_15min': 75}
    metric_descriptions = {'avg_1min': 'int', 'avg_5min' : 'int', 'avg_15min' : 'int'}

    @property
    def command(self):
        return u'cat /proc/loadavg'

    def _output_parse(self, output, status):
        return {'system' : dict(zip(['avg_1min', 'avg_5min', 'avg_15min'], [float(avg) for avg in output[0].split()[:3]]))}


class ProcessState(ShellPlugin, EnumThresholdCreatorMixin):
    '''Verifies if a process is running
    '''
    name = 'process_state'
    default_thresholds = {'status' : {'good' : ['running'],
                                      'bad' : ['not-running']}}
    metric_descriptions = {'status': 'string(12)'}

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
                    return {self.process_name : {'status' : 'running'}}

        return {self.process_name : {'status' : 'not-running'}}


PLUGINS_LIST = [DiskUsage, CPULoad, MemoryUsage, ProcessState]
def list_plugins():
    return PLUGINS_LIST

DEFAULT_PLUGINS = [CPULoad, DiskUsage, MemoryUsage]
def list_default_plugins():
    return DEFAULT_PLUGINS

NATIVE_PLUGINS_LIST = [NativeReachablePlugin]
def list_native_plugins():
    return NATIVE_PLUGINS_LIST
