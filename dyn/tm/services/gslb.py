# -*- coding: utf-8 -*-
from ..utils import APIList
from ..session import DynectSession
from ...core import (APIObject, ImmutableAttribute, StringAttribute,
                     ValidatedAttribute, IntegerAttribute, ClassAttribute,
                     ListAttribute)
from ...compat import force_unicode

__author__ = 'jnappi'
__all__ = ['Monitor', 'GSLBRegionPoolEntry', 'GSLBRegion', 'GSLB']


class Monitor(APIObject):
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
        super(Monitor, self).__init__()
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
        super(Monitor, self)._update(**mon_args)

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
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        respnose = DynectSession.get_session().execute(uri, 'GET')
        return respnose['data']['status']

    def __str__(self):
        """str override"""
        return force_unicode('<GSLBMonitor>: {0}').format(self.protocol)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class GSLBRegionPoolEntry(APIObject):
    """:class:`GSLBRegionPoolEntry`"""
    uri = '/GSLBRegionPoolEntry/{zone}/{fqdn}/{region}/{address}/'
    session_type = DynectSession
    zone = ImmutableAttribute('zone')
    fqdn = ImmutableAttribute('fqdn')
    region_code = ImmutableAttribute('region_code')
    label = StringAttribute('label')
    weight = ValidatedAttribute('weight', validator=range(1, 15))
    serve_mode = ValidatedAttribute('serve_mode', validator=('always', 'obey',
                                                             'remove', 'no'))

    def __init__(self, zone, fqdn, region_code, address, *args, **kwargs):
        """Create a :class:`GSLBRegionPoolEntry` object

        :param zone: Zone monitored by this :class:`GSLBRegionPoolEntry`
        :param fqdn: The fqdn of the specific node which will be monitored by
            this :class:`GSLBRegionPoolEntry`
        :param region_code: ISO Region Code for this
            :class:`GSLBRegionPoolEntry`
        :param address: The IP address or FQDN of this Node IP
        :param label: Identifying descriptive information for this
            :class:`GSLBRegionPoolEntry`
        :param weight: A number in the range of 1-14 controlling the order in
            which this :class:`GSLBRegionPoolEntry` will be served
        :param serve_mode: Sets the behavior of this particular record. Must be
            one of 'always', 'obey', 'remove', 'no'
        """
        self.zone, self.fqdn, = zone, fqdn
        self.region_code, self.address = region_code, address
        self.uri = self.uri.format(zone=zone, fqdn=fqdn, region=region_code,
                                   address=address)
        super(GSLBRegionPoolEntry, self).__init__(*args, **kwargs)

    def _post(self, label=None, weight=None, serve_mode=None):
        """Create a new :class:`GSLBRegionPoolEntry` on the DynECT System"""
        uri = '/GSLBRegionPoolEntry/{0}/{1}/{2}/'.format(self.zone, self.fqdn,
                                                         self.region_code)
        api_args = {'address': self.address}
        if label:
            api_args['label'] = label
        if weight:
            api_args['weight'] = weight
        if serve_mode:
            api_args['serve_mode'] = serve_mode
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])

    def _update(self, **api_args):
        if 'address' in api_args:
            api_args['new_address'] = api_args.pop('address')
        super(GSLBRegionPoolEntry, self)._update(**api_args)

    def sync(self):
        """Sync this :class:`GSLBRegionPoolEntry` object with the DynECT System
        """
        self._get()

    def to_json(self):
        """Convert this object into a json blob"""
        output = {'address': self.address}
        if self.label:
            output['label'] = self.label
        if self.weight:
            output['weight'] = self.weight
        if self.serve_mode:
            output['serve_mode'] = self.serve_mode
        return output

    def __str__(self):
        """str override"""
        return force_unicode('<GSLBRegionPoolEntry>: {0}'.format(
            self.region_code)
        )
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class GSLBRegion(APIObject):
    """docstring for GSLBRegion"""
    uri = '/GSLBRegion/{zone}/{fqdn}/{region}/'
    session_type = DynectSession
    zone = ImmutableAttribute('zone')
    fqdn = ImmutableAttribute('fqdn')
    region_code = ImmutableAttribute('region_code')
    pool = ListAttribute('pool')
    serve_count = IntegerAttribute('serve_count')
    failover_mode = ValidatedAttribute('failover_mode',
                                       validator=('ip', 'cname', 'region',
                                                  'global'))
    failover_data = ValidatedAttribute('failover_data',
                                       validator=('ip', 'cname', 'region',
                                                  'global'))

    def __init__(self, zone, fqdn, region_code, *args, **kwargs):
        """Create a :class:`GSLBRegion` object

        :param zone: Zone monitored by this :class:`GSLBRegion`
        :param fqdn: The fqdn of the specific node which will be monitored by
            this :class:`GSLBRegion`
        :param region_code: ISO region code of this :class:`GSLBRegion`
        :param pool: The IP Pool list for this :class:`GSLBRegion`
        :param serve_count: How many records will be returned in each DNS
            response
        :param failover_mode: How the :class:`GSLBRegion` should failover. Must
            be one of 'ip', 'cname', 'region', 'global'
        :param failover_data: Dependent upon failover_mode. Must be one of
            'ip', 'cname', 'region', 'global'
        """
        self._pool = []
        self.uri = self.uri.format(zone=zone, fqdn=fqdn, region=region_code)
        super(GSLBRegion, self).__init__(*args, **kwargs)

    def _post(self, pool, serve_count=None, failover_mode=None,
              failover_data=None):
        """Create a new :class:`GSLBRegion` on the DynECT System"""
        self._pool = pool
        self._serve_count = serve_count
        self._failover_mode = failover_mode
        self._failover_data = failover_data
        uri = '/GSLBRegion/{0}/{1}/'.format(self.zone, self.fqdn)
        api_args = {'pool': self._pool.to_json()}
        if serve_count:
            api_args['serve_count'] = self._serve_count
        if failover_mode:
            api_args['failover_mode'] = self._failover_mode
        if failover_data:
            api_args['failover_data'] = self._failover_data
        response = DynectSession.get_session()(uri, 'POST', api_args)
        self._build(response['data'])

    def _build(self, data):
        if 'pool' in data:
            pools = data.pop('pool')
            for pool in pools:
                if isinstance(pool, dict):
                    self._pool.append(GSLBRegionPoolEntry(self.zone, self.fqdn,
                                                          self.region_code,
                                                          method=None, **pool))
                else:
                    self._pool.append(pool)
        super(GSLBRegion, self)._build(data)

    def _update(self, **api_args):
        if 'pool' in api_args:
            api_args['pool'] = api_args['pool'].to_json()
        super(GSLBRegion, self)._update(**api_args)

    def sync(self):
        """Sync this :class:`GSLBRegion` object with the DynECT System"""
        self._get()

    @property
    def _json(self):
        """Convert this :class:`GSLBRegion` to a json blob"""
        output = {'region_code': self.region_code,
                  'pool': [pool.to_json() for pool in self._pool]}
        if self._serve_count:
            output['serve_count'] = self._serve_count
        if self._failover_mode:
            output['failover_mode'] = self._failover_mode
        if self._failover_data:
            output['failover_data'] = self._failover_data
        return output

    def __str__(self):
        """str override"""
        return force_unicode('<GSLBRegion>: {0}').format(self.region_code)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class GSLB(APIObject):
    """A Global Server Load Balancing (GSLB) service"""
    uri = '/GSLB/{zone}/{fqdn}/'
    session_type = DynectSession
    zone = ImmutableAttribute('zone')
    fqdn = ImmutableAttribute('fqdn')
    auto_recover = ValidatedAttribute('auto_recover', validator=('Y', 'N'))
    ttl = ValidatedAttribute('ttl', validator=(30, 60, 150, 300, 450))
    notify_events = ValidatedAttribute('notify_events',
                                       validator=('ip', 'svc', 'nosrv'))
    syslog_server = StringAttribute('syslog_server')
    syslog_port = IntegerAttribute('syslog_port')
    syslog_ident = StringAttribute('syslog_ident')
    syslog_facility = ValidatedAttribute('syslog_facility',
                                         validator=(
                                             'kern', 'user', 'mail', 'daemon',
                                             'auth', 'syslog', 'lpr', 'news',
                                             'uucp', 'cron', 'authpriv', 'ftp',
                                             'ntp', 'security', 'console',
                                             'local0', 'local1', 'local2',
                                             'local3', 'local4', 'local5',
                                             'local6', 'local7'
                                         ))
    monitor = ClassAttribute('monitor', class_type=Monitor)
    contact_nickname = StringAttribute('contact_nickname')

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`GSLB` object

        :param auto_recover: Indicates whether or not the service should
            automatically come out of failover when the IP addresses resume
            active status or if the service should remain in failover until
            manually reset. Must be 'Y' or 'N'
        :param ttl: Time To Live in seconds of records in the service. Must be
            less than 1/2 of the Health Probe's monitoring interval. Must be one
            of 30, 60, 150, 300, or 450
        :param notify_events: A comma separated list of the events which trigger
            notifications. Must be one of 'ip', 'svc', or 'nosrv'
        :param syslog_server: The Hostname or IP address of a server to receive
            syslog notifications on monitoring events
        :param syslog_port: The port where the remote syslog server listens for
            notifications
        :param syslog_ident: The ident to use when sending syslog notifications
        :param syslog_facility: The syslog facility to use when sending syslog
            notifications. Must be one of 'kern', 'user', 'mail', 'daemon',
            'auth', 'syslog', 'lpr', 'news', 'uucp', 'cron', 'authpriv', 'ftp',
            'ntp', 'security', 'console', 'local0', 'local1', 'local2',
            'local3', 'local4', 'local5', 'local6', or 'local7'
        :param region: A list of :class:`GSLBRegion`'s
        :param monitor: The health :class:`Monitor` for this service
        :param contact_nickname: Name of contact to receive notifications
        """
        self.uri = self.uri.format(zone=zone, fqdn=fqdn)

        super(GSLB, self).__init__(*args, **kwargs)

        self._active = self._status = self.active = None
        self._region = APIList(DynectSession.get_session, 'region')

        self._region.uri = self.uri

    def _post(self, contact_nickname, region, auto_recover=None, ttl=None,
              notify_events=None, syslog_server=None, syslog_port=514,
              syslog_ident='dynect', syslog_facility='daemon', monitor=None):
        """Create a new :class:`GSLB` service object on the DynECT System"""
        api_args = {'contact_nickname': contact_nickname,
                    'region': [r._json for r in region]}
        if auto_recover:
            api_args['auto_recover'] = auto_recover
        if ttl:
            api_args['ttl'] = ttl
        if notify_events:
            api_args['notify_events'] = notify_events
        if syslog_server:
            api_args['syslog_server'] = syslog_server
        if syslog_port:
            api_args['syslog_port'] = syslog_port
        if syslog_ident:
            api_args['syslog_ident'] = syslog_ident
        if syslog_facility:
            api_args['syslog_facility'] = syslog_facility
        if monitor:
            api_args['monitor'] = monitor.to_json()
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Private method which builds the objects fields based on the data
        returned by an API call

        :param data: the data from the JSON respnose
        :param region: Boolean flag specifying whether to rebuild the region
            objects or not
        """
        if 'region' in data:
            self._region = APIList(DynectSession.get_session, 'region')
            for region in data.pop('region'):
                region_code = region.pop('region_code', None)
                self._region.append(GSLBRegion(self.zone, self.fqdn,
                                               region_code, **region))
            self._region.uri = self.uri
        if 'monitor' in data:
            if getattr(self, '_monitor', None) is not None:
                # We already have the monitor object, no need to rebuild it
                data.pop('monitor')
            else:
                self._monitor = data.pop('monitor')
                self._monitor.zone = self.zone
                self._monitor.fqdn = self.fqdn
        super(GSLB, self)._build(data)

    def _update(self, **api_args):
        if 'region' in api_args:
            region = api_args.pop('region')
            if isinstance(region, list) and not isinstance(region, APIList):
                self._region = APIList(DynectSession.get_session, 'region',
                                       None, region)
            elif isinstance(region, APIList):
                self._region = region
            self._region.uri = self.uri
        if 'monitor' in api_args:
            monitor = api_args.pop('monitor')
                # We're only going accept new monitors of type Monitor
            if isinstance(monitor, Monitor):
                api_args['monitor'] = monitor.to_json()
        super(GSLB, self)._update(**api_args)

    def sync(self):
        """Sync this :class:`GSLB` object with the DynECT System"""
        self._get()

    def activate(self):
        """Activate this :class:`GSLB` service on the DynECT System"""
        self._update(activate=True)

    def deactivate(self):
        """Deactivate this :class:`GSLB` service on the DynECT System"""
        self._update(deactivate=True)

    def recover(self, address=None):
        """Recover the GSLB service on the designated zone node or a specific
        node IP within the service
        """
        api_args = {}
        if address:
            api_args['recoverip'] = True
            api_args['address'] = address
        else:
            api_args['recover'] = True
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def active(self):
        """Indicates if the service is active. When setting directly, rather
        than using activate/deactivate valid arguments are 'Y' or True to
        activate, or 'N' or False to deactivate. Note: If your service is
        already active and you try to activate it, nothing will happen. And
        vice versa for deactivation.

        :returns: An :class:`Active` object representing the current state of
            this :class:`GSLB` Service
        """
        return self._active
    @active.setter
    def active(self, value):
        deactivate = ('N', False)
        activate = ('Y', True)
        if value in deactivate and self.active:
            self.deactivate()
        elif value in activate and not self.active:
            self.activate()

    def __str__(self):
        """str override"""
        return force_unicode('<GSLB>: {0}').format(self.fqdn)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
