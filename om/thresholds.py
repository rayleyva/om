# -*- coding: utf-8 -*-

from collections import namedtuple

class Threshold(object):
    '''Implements a threshold checker
    '''

    def __init__(self, name):
        super(Threshold, self).__init__()
        self.name = name

    def check_value(self, v):
        raise NotImplementedError, "check_value not implemented"

class NumericThreshold(Threshold):

    def __init__(self, name, limit, upper=True):
        super(NumericThreshold, self).__init__(name)
        self.limit = limit
        self.upper = upper

    def check_value(self, v):
        if self.upper:
            return v <= self.limit
        else:
            return v >= self.limit

class EnumThreshold(Threshold):
    def __init__(self, name, good_values, bad_values):
        super(EnumThreshold, self).__init__(name)
        self.good_values = good_values
        self.bad_values = bad_values

    def check_value(self, v):
        if v in self.good_values:
            return True
        if v in self.bad_values:
            return False
        #TODO raise exception if values not found

class NumericThresholdCreatorMixin:
    def create_thresholds(self, data):
        self.thresholds = { k: NumericThreshold(k,v) for k,v in data.iteritems()}

class EnumThresholdCreatorMixin:
    def create_thresholds(self, data):
        self.thresholds = { k: EnumThreshold(k, v['good'], v['bad']) for k,v in data.iteritems()}
