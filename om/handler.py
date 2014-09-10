# -*- coding: utf-8 -*-

import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import sqlite3
import redis

from om.utils.logger import get_logger

log = get_logger("metrics")


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

    def setup(self):
        pass

    def teardown(self):
        pass

    def setup_for_plugin(self, p):
        pass

    def __repr__(self):
        return "<Handler:%s>" % type(self).__name__


class StdoutHandler(Handler):
    '''Outputs all metrics to stdout.
    '''

    def handles(self, metric):
        return True

    def handle(self, metric):
        print "%s:%s:%s %s" % (metric.host, metric.plugin.name, metric.state, metric.values)


import json

class JSONStdoutHandler(Handler):
    '''Outputs metrics in JSON format to stdout
    '''

    def handles(self, metric):
        return True

    def handle(self, metric):
        print json.dumps(metric.values)


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

class Sqlite3Handler(Handler):
    '''Stores the metrics in a sqlite3 database
    '''

    table_metric_prefix = 'om_metric_'

    def __init__(self, **kwargs):
        super(Sqlite3Handler,self).__init__()
        self.path = kwargs['path']
        self.expiration_days = kwargs['expiration_days']

    def handles(self, metric):
        return True

    def _get_table_name(self, plugin):
        return '%s%s' % (self.table_metric_prefix, plugin.name)

    def _type_for_description(self, desc):
        if desc == 'int': return 'INTEGER'
        if desc.startswith('string'):
            return desc.replace('string', 'VARCHAR')

        return ''

    def _gen_values(self, datadict):
        return ','.join([u"'%s'" % unicode(datadict[k]) for k in sorted(datadict.keys())])

    def setup_for_plugin(self, p):
        table_name = self._get_table_name (p)
        columns = ['host TEXT NOT NULL', 'timestamp DATETIME NOT NULL', 'instance TEXT']
        for name in sorted(p.metric_descriptions.keys()):
            description = p.metric_descriptions[name]
            columns.append(u'%s %s' % (name, self._type_for_description(description)))
        columns = ','.join(columns)

        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute(u'CREATE TABLE IF NOT EXISTS %s (%s)' % (table_name, columns))
        conn.commit()
        conn.close()

    def teardown(self):
        if self.expiration_days is None: return

        conn = sqlite3.connect(self.path)
        c = conn.cursor()

        c.execute('SELECT NAME FROM sqlite_master WHERE type=\'table\'')
        for table in filter(lambda x: x[0].startswith(self.table_metric_prefix), c):
            table_c = conn.cursor()
            table_c.execute("DELETE FROM %s WHERE "
                            "date('now') > datetime(timestamp,'+%s day')" %
                            (table[0], str(self.expiration_days)))
        conn.commit()
        conn.close()

    def handle(self, metric):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        for instance,datadict in metric.values.iteritems():
            c.execute("INSERT INTO %s VALUES ('%s', '%s', '%s', %s)" % (self._get_table_name(metric.plugin),
                                                                        metric.host, metric.timestamp, instance,
                                                                        self._gen_values(datadict)))

        conn.commit()
        conn.close()


class RedisHandler(Handler):
    '''Stores the metrics in a Redis database
    '''

    def __init__(self, **kwargs):
        super(RedisHandler, self).__init__()
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', 6379)
        self.max_list_length = kwargs.get('max_list_length', 0)
        self.keys_prefix = ''
        self.redis = redis.StrictRedis(host=host, port=port, db=0)

    def handles(self, metric):
        return True

    def handle(self, metric):
        pipeline = self.redis.pipeline()
        host_plugin = u'%s%s:%s' % (self.keys_prefix, metric.host, metric.plugin.name)
        for instance, datadict in metric.values.iteritems():
            host_plugin_instance = u'%s:%s' % (host_plugin, instance)
            for k,v in datadict.iteritems():
                pipeline.lpush(u'%s:%s' % (host_plugin_instance, k), "[%d,%s]" % (time.time(), v))
        pipeline.execute()

    def teardown(self):
        if self.max_list_length == 0: return
        for k in self.redis.keys('%s*' % self.keys_prefix):
            self.redis.ltrim(k, 0, self.max_list_length-1)

HANDLERS = [MailHandler, JSONStdoutHandler, StdoutHandler, Sqlite3Handler, RedisHandler]
def list_handlers():
    return HANDLERS
