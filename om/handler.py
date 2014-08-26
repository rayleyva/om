# -*- coding: utf-8 -*-

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from om.utils.logger import get_logger


class Handler(object):
    '''Base class for handlers
    '''
    def __init__(self):
        self._enabled = True

    @classmethod
    def _handles(cls, result):
        return lambda handler: handler.handles(result)

    @classmethod
    def _handle(cls, result):
        return lambda handler: handler.handle(result)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        return self._enabled

    def handles(self, metric):
        '''Returns True if this handler handles this result
        '''
        return False

    def handle(self, metric):
        raise NotImplementedError

    def __repr__(self):
        return "<Handler:%s>" % type(self).__name__


class StdoutHandler(Handler):
    '''Outputs all metrics to stdout
    '''

    def handles(self, metric):
        return True

    def handle(self, metric):
        log = get_logger("metric:%s:%s:%s" % (metric.host, metric.plugin.name, metric.state))
        if metric.state == 'critical':
            log.error("%s" % (metric.values))
        else:
            log.debug("%s" % (metric.values))


class MailHandler(Handler):
    '''Mails the plugin result if metric value is considered abnormal.
    '''
    def __init__(self, **kwargs):
        self.config = kwargs

    def handles(self, metric):
        return True

    def handle(self, metric):
        if metric.state != 'normal': self.send_alert(metric)

    def send_alert(self, metric):
        server = smtplib.SMTP(self.config['smtp'], self.config['port'])
        if self.config.get('security', '') == 'starttls':
            server.starttls()
        server.login(self.config['login'], self.config['password'])

        body = "%s.%s: %s (%s)" % (metric.host, metric.plugin.name, metric.values, metric.state)

        fromaddr = self.config['from']
        toaddr = ', '.join(self.config['to'])

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = self.config.get('subject', 'Overseer-Mini Alert')
        msg.attach(MIMEText(body, "plain"))

        server.sendmail(fromaddr, toaddr, msg.as_string())
