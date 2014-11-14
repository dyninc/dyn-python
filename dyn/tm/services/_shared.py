# -*- coding: utf-8 -*-
from ..session import DynectSession
from ...core import (APIObject, StringAttribute, ValidatedAttribute,
                     IntegerAttribute)
from ...compat import force_unicode

__author__ = 'jnappi'


class BaseMonitor(APIObject):
    """A :class:`Monitor` for a GSLB Service"""
    session_type = DynectSession
    protocol = ValidatedAttribute('protocol',
                                  validator=('HTTP', 'HTTPS', 'PING', 'SMTP',
                                             'TCP'))
    interval = ValidatedAttribute('interval', validator=(1, 5, 10, 15))
    retries = IntegerAttribute('retries')
    timeout = ValidatedAttribute('timeout', validator=(10, 15, 25, 30))
    port = IntegerAttribute('port')
    path = StringAttribute('path')
    host = StringAttribute('host')
    header = StringAttribute('header')
    expected = StringAttribute('expected')

    def __init__(self, protocol, interval, retries=None, timeout=None,
                 port=None, path=None, host=None, header=None, expected=None):
        """Create a :class:`Monitor` object

        :param protocol: The protocol to monitor. Must be either HTTP, HTTPS,
            PING, SMTP, or TCP
        :param interval: How often (in minutes) to run the monitor. Must be 1,
            5, 10, or 15,
        :param retries: The number of retries the monitor attempts on failure
            before giving up
        :param timeout: The amount of time in seconds before the connection
            attempt times out
        :param port: For HTTP(S)/SMTP/TCP probes, an alternate connection port
        :param path: For HTTP(S) probes, a specific path to request
        :param host: For HTTP(S) probes, a value to pass in to the Host
        :param header: For HTTP(S) probes, additional header fields/values to
            pass in, separated by a newline character.
        :param expected: For HTTP(S) probes, a string to search for in the
            response. For SMTP probes, a string to compare the banner against.
            Failure to find this string means the monitor will report a down
            status.
        """
        super(BaseMonitor, self).__init__()
        self._protocol = protocol
        self._interval = interval
        self._retries = retries
        self._timeout = timeout
        self._port = port
        self._path = path
        self._host = host
        self._header = header
        self._expected = expected
        self.zone = None
        self.fqdn = None

    def _post(self, *args, **kwargs):
        """You can't create a HealthMonitor on it's own, so force _post and
        _get to be no-ops
        """
        pass
    _get = _post

    def _update(self, **api_args):
        mon_args = {'monitor': api_args}
        super(BaseMonitor, self)._update(**mon_args)

    def _build(self, data):
        super(BaseMonitor, self)._build(data.pop('monitor'))

    def to_json(self):
        """Convert this :class:`HealthMonitor` object to a JSON blob"""
        json_blob = {'protocol': self.protocol,
                     'interval': self.interval}
        for key, val in self.__dict__.items():
            if val is not None and not hasattr(val, '__call__') and \
                    key.startswith('_'):
                json_blob[key[1:]] = val
        return json_blob

    @property
    def uri(self):
        if self.zone is not None and self.fqdn is not None:
            return '/GSLB/{0}/{1}/'.format(self.zone, self.fqdn)
        raise ValueError

    @property
    def status(self):
        """Get the current status of this :class:`Monitor` from the
        DynECT System
        """
        respnose = DynectSession.get_session().execute(self.uri, 'GET')
        return respnose['data']['status']

    def __str__(self):
        """str override"""
        return force_unicode('<{0}>: {1}').format(self.__class__.__name__,
                                                  self.protocol)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
