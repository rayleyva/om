# -*- coding: utf-8 -*-

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from om.metrics import PLUGIN_STATES
from om.utils.logger import get_logger


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

    def __repr__(self):
        return "<Handler:%s>" % type(self).__name__


class StdoutHandler(Handler):
    '''Outputs all metrics to stdout
    '''

    def handles(self, plugin_result):
        return True

    def handle(self, plugin_result):
        log = get_logger("metric:%s:%s:%s" % (plugin_result.host, plugin_result.plugin.name_on_config, plugin_result.state))
        if plugin_result.state == 'critical':
            log.error("%s" % (plugin_result.value))
        else:
            log.debug("%s" % (plugin_result.value))


class MailHandler(Handler):
    '''Mails the plugin result if metric value is considered abnormal.
    '''
    def __init__(self, **kwargs):
        self.config = kwargs

    def handles(self, plugin_result):
        return True

    def handle(self, plugin_result):
        if plugin_result.state != 'normal': self.send_alert(plugin_result)

    def send_alert(self, plugin_result):
        server = smtplib.SMTP(self.config['smtp'], self.config['port'])
        if self.config.get('security', '') == 'starttls':
            server.starttls()
        server.login(self.config['login'], self.config['password'])

        body = "%s.%s: %s (%s)" % (plugin_result.host, plugin_result.plugin.name, plugin_result.value, plugin_result.state)

        fromaddr = self.config['from']
        toaddr = ', '.join(self.config['to'])

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = self.config.get('subject', 'Overseer-Mini Alert')
        msg.attach(MIMEText(body, "plain"))

        server.sendmail(fromaddr, toaddr, msg.as_string())
