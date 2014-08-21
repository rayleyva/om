# -*- coding: utf-8 -*-

from overseer.mini.metrics import PLUGIN_STATES

class Handler(object):
    '''Base class for handlers
    '''
    def __init__(self):
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        return self._enabled

    def handles(self, plugin_result):
        '''Returns True if this handler handles this result
        '''
        return False

    def handle(self, plugin_result):
        raise NotImplementedError


class StdoutHandler(Handler):
    '''Outputs all metrics to stdout
    '''

    def handles(self, plugin_result):
        return True

    def handle(self, plugin_result):
        print "[%s]\t[%s]: %s (%s)" % (plugin_result.host, plugin_result.plugin.name, plugin_result.value, plugin_result.state)


class MailHandler(Handler):
    '''Mails the plugin result if metric value is considered abnormal.
    '''

    def handles(self, plugin_result):
        return True

    def handle(self, plugin_result):
        if plugin_result.state != 'normal': send_alert(plugin_result)

    def send_alert(self, plugin_result):
        # TODO implement
        print "Would send alert for %s" % plugin_result