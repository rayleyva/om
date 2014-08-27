# -*- coding: utf-8 -*-

class Metric(object):

    def __init__(self, host, plugin, values={}, thresholds={}):
        self.host = host
        self.plugin = plugin
        self.values = values
        self.thresholds = thresholds

    @property
    def state(self):
        for key, metrics in self.values.iteritems():
            for m, value in metrics.iteritems():
                if self.thresholds.get(m) is None: continue
                if not self.thresholds.get(m).check_value (value):
                    return 'critical'
        return 'normal'