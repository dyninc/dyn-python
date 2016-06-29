# -*- coding: utf-8 -*-
from dyn.compat import force_unicode
from dyn.tm.utils import APIList
from dyn.tm.errors import DynectInvalidArgumentError
from dyn.tm.session import DynectSession
from dyn.tm.task import Task

__author__ = 'jnappi'
__all__ = ['Monitor', 'GSLBRegionPoolEntry', 'GSLBRegion', 'GSLB']


class Monitor(object):
    """A :class:`Monitor` for a GSLB Service"""

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
        self.valid_protocols = ('HTTP', 'HTTPS', 'PING', 'SMTP', 'TCP')
        self.valid_intervals = (1, 5, 10, 15)
        self.valid_timeouts = (10, 15, 25, 30)

    def to_json(self):
        """Convert this :class:`HealthMonitor` object to a JSON blob"""
        json_blob = {'protocol': self._protocol,
                     'interval': self._interval}
        for key, val in self.__dict__.items():
            if val is not None and not hasattr(val, '__call__') and \
                    key.startswith('_'):
                json_blob[key[1:]] = val
        return json_blob

    def __eq__(self, other):
        """eq override for comparing :class:`HealthMonitor` objects to JSON
        response hashes or other :class:`HealthMonitor` instances

        :param other: the value to compare this :class:`HealthMonitor` to.
            Valid input types: `dict`, :class:`HealthMonitor`
        """
        if isinstance(other, dict):
            return False
        elif isinstance(other, Monitor):
            return False
        else:
            return False

    @property
    def status(self):
        """Get the current status of this :class:`HealthMonitor` from the
        DynECT System
        """
        api_args = {}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        respnose = DynectSession.get_session().execute(uri, 'GET', api_args)
        return respnose['data']['status']

    @property
    def protocol(self):
        """The protocol to monitor"""
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if value not in self.valid_protocols:
            raise Exception
        self._protocol = value
        api_args = {'monitor': {'protocol': self._protocol}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    @property
    def interval(self):
        """How often to run this monitor"""
        return self._interval

    @interval.setter
    def interval(self, value):
        if value not in self.valid_intervals:
            raise Exception
        self._interval = value
        api_args = {'monitor': {'interval': self._interval}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    @property
    def retries(self):
        """The number of retries the monitor attempts on failure before giving
        up
        """
        return self._retries

    @retries.setter
    def retries(self, value):
        self._retries = value
        api_args = {'monitor': {'retries': self._retries}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    @property
    def timeout(self):
        """The amount of time in seconds before the connection attempt times
        out
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value
        api_args = {'monitor': {'timeout': self._timeout}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    @property
    def port(self):
        """For HTTP(S)/SMTP/TCP probes, an alternate connection port"""
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        api_args = {'monitor': {'port': self._port}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    @property
    def path(self):
        """For HTTP(S) probes, a specific path to request"""
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        api_args = {'monitor': {'path': self._path}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    @property
    def host(self):
        """For HTTP(S) probes, a value to pass in to the Host"""
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        api_args = {'monitor': {'host': self._host}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    @property
    def header(self):
        """For HTTP(S) probes, additional header fields/values to pass in,
        separated by a newline character
        """
        return self._header

    @header.setter
    def header(self, value):
        self._header = value
        api_args = {'monitor': {'header': self._header}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    @property
    def expected(self):
        """For HTTP(S) probes, a string to search for in the response. For
        SMTP probes, a string to compare the banner against. Failure to find
        this string means the monitor will report a down status
        """
        return self._expected

    @expected.setter
    def expected(self, value):
        self._expected = value
        api_args = {'monitor': {'expected': self._expected}}
        uri = '/Failover/{}/{}/'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<GSLBMonitor>: {}').format(self._protocol)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class GSLBRegionPoolEntry(object):
    """:class:`GSLBRegionPoolEntry`"""

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
        super(GSLBRegionPoolEntry, self).__init__()
        self.valid_serve_modes = ('always', 'obey', 'remove', 'no')
        self.valid_weight = range(1, 15)
        self._zone = zone
        self._fqdn = fqdn
        self._region_code = region_code
        self._address = address
        self._label = self._weight = self._serve_mode = None
        self._task_id = None

        uri = '/GSLBRegionPoolEntry/{}/{}/{}/{}/'
        self.uri = uri.format(self._zone, self._fqdn, self._region_code,
                              self._address)
        if len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._build(kwargs)

    def _post(self, label=None, weight=None, serve_mode=None):
        """Create a new :class:`GSLBRegionPoolEntry` on the DynECT System"""
        self._label = label
        self._weight = weight
        self._serve_mode = serve_mode
        uri = '/GSLBRegionPoolEntry/{}/{}/{}/'.format(self._zone, self._fqdn,
                                                      self._region_code)
        api_args = {'address': self._address}
        if label:
            api_args['label'] = self._label
        if weight:
            if weight not in self.valid_weight:
                raise DynectInvalidArgumentError('weight', weight,
                                                 self.valid_weight)
            api_args['weight'] = self._weight
        if serve_mode:
            if serve_mode not in self.valid_serve_modes:
                raise DynectInvalidArgumentError('serve_mode', serve_mode,
                                                 self.valid_serve_modes)
            api_args['serve_mode'] = self._serve_mode
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])

    def _get(self):
        """Get an existing :class:`GSLBRegionPoolEntry` object from the DynECT
        System
        """
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args):
        """Private update method"""
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Build the variables in this object by pulling out the data from data
        """
        for key, val in data.items():
            if key == "task_id" and not val:
                self._task_id = None
            elif key == "task_id":
                self._task_id = Task(val)
            else:
                setattr(self, '_' + key, val)

    @property
    def task(self):
        """:class:`Task` for most recent system
        action on this :class:`ActiveFailover`."""
        if self._task_id:
            self._task_id.refresh()
        return self._task_id

    def sync(self):
        """Sync this :class:`GSLBRegionPoolEntry` object with the DynECT System
        """
        self._get()

    @property
    def zone(self):
        """Zone monitored by this :class:`GSLBRegionPoolEntry`"""
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """The fqdn of the specific node which will be monitored by this
        :class:`GSLBRegionPoolEntry`
        """
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def region_code(self):
        """ISO Region Code for this :class:`GSLBRegionPoolEntry`"""
        return self._region_code

    @region_code.setter
    def region_code(self, value):
        pass

    @property
    def address(self):
        """The IP address or FQDN of this Node IP"""
        return self._address

    @address.setter
    def address(self, value):
        self._address = value
        api_args = {'new_address': self._address}
        self._update(api_args)

    @property
    def label(self):
        """Identifying descriptive information for this
        :class:`GSLBRegionPoolEntry`
        """
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        self._update(api_args)

    @property
    def weight(self):
        """A number in the range of 1-14 controlling the order in which this
        :class:`GSLBRegionPoolEntry` will be served.
        """
        return self._weight

    @weight.setter
    def weight(self, new_weight):
        if new_weight not in self.valid_weight:
            raise DynectInvalidArgumentError(new_weight,
                                             self.valid_weight)
        self._weight = new_weight
        api_args = {'weight': self._weight}
        self._update(api_args)

    @property
    def serve_mode(self):
        """Sets the behavior of this particular record. Must be one of 'always',
        'obey', 'remove', or 'no'
        """
        return self._serve_mode

    @serve_mode.setter
    def serve_mode(self, new_serve_mode):
        if new_serve_mode not in self.valid_serve_modes:
            raise DynectInvalidArgumentError('serve_mode', new_serve_mode,
                                             self.valid_serve_modes)
        self._serve_mode = new_serve_mode
        api_args = {'serve_mode': self._serve_mode}
        self._update(api_args)

    def to_json(self):
        """Convert this object into a json blob"""
        output = {'address': self._address}
        if self._label:
            output['label'] = self._label
        if self._weight:
            output['weight'] = self._weight
        if self._serve_mode:
            output['serve_mode'] = self._serve_mode
        return output

    def delete(self):
        """Delete this :class:`GSLBRegionPoolEntry` from the DynECT System"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        s = force_unicode('<GSLBRegionPoolEntry>: {}')
        return s.format(self._region_code)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class GSLBRegion(object):
    """docstring for GSLBRegion"""

    def __init__(self, zone, fqdn, region_code, *args, **kwargs):
        """Create a :class:`GSLBRegion` object

        :param zone: Zone monitored by this :class:`GSLBRegion`
        :param fqdn: The fqdn of the specific node which will be monitored by
            this :class:`GSLBRegion`
        :param region_code: ISO region code of this :class:`GSLBRegion`
        :param pool: (*arg) The IP Pool list for this :class:`GSLBRegion`
        :param serve_count: How many records will be returned in each DNS
            response
        :param failover_mode: How the :class:`GSLBRegion` should failover. Must
            be one of 'ip', 'cname', 'region', 'global'
        :param failover_data: Dependent upon failover_mode. Must be one of
            'ip', 'cname', 'region', 'global'
        """
        super(GSLBRegion, self).__init__()
        self.valid_region_codes = ('US West', 'US Central', 'US East', 'Asia',
                                   'EU West', 'EU Central', 'EU East',
                                   'global')

        self.valid_modes = ('ip', 'cname', 'region', 'global')
        self._zone = zone
        self._fqdn = fqdn
        self._pool = self._serve_count = self._failover_mode = None
        self._failover_data = None
        self._task_id = None
        if region_code not in self.valid_region_codes:
            raise DynectInvalidArgumentError('region_code', region_code,
                                             self.valid_region_codes)
        self._region_code = region_code
        self.uri = '/GSLBRegion/{}/{}/{}/'.format(self._zone, self._fqdn,
                                                  self._region_code)
        self._pool = []
        if len(args) == 0 and len(kwargs) == 0:
            self._get()
        if len(kwargs) > 0:
            self._build(kwargs)
        elif len(args) > 0:
            for pool in args[0]:
                if isinstance(pool, dict):
                    self._pool.append(GSLBRegionPoolEntry(self._zone,
                                                          self._fqdn,
                                                          self._region_code,
                                                          **pool))
                else:
                    self._pool.append(pool)

    def _post(self, pool, serve_count=None, failover_mode=None,
              failover_data=None):
        """Create a new :class:`GSLBRegion` on the DynECT System"""
        self._pool = pool
        self._serve_count = serve_count
        self._failover_mode = failover_mode
        self._failover_data = failover_data
        uri = '/GSLBRegion/{}/{}/'.format(self._zone, self._fqdn)
        api_args = {'pool': self._pool.to_json(),
                    'region_code': self._region_code}
        if serve_count:
            api_args['serve_count'] = self._serve_count
        if self._failover_mode:
            if self._failover_mode not in self.valid_modes:
                raise DynectInvalidArgumentError('failover_mode',
                                                 self._failover_mode,
                                                 self.valid_modes)
            api_args['failover_mode'] = self._failover_mode
        if self._failover_data:
            if self._failover_data not in self.valid_modes:
                raise DynectInvalidArgumentError('failover_data',
                                                 self._failover_data,
                                                 self.valid_modes)
            api_args['failover_data'] = self._failover_data
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])

    def _get(self):
        """Get an existing :class:`GSLBRegion` object"""
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args):
        """Private udpate method for PUT commands"""
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        self._pool = []
        for key, val in data.items():
            if key == 'pool':
                for pool in val:
                    if isinstance(pool, dict):
                        self._pool.append(GSLBRegionPoolEntry(
                            self._zone, self._fqdn, self._region_code,
                            **pool)
                        )
                    else:
                        self._pool.append(pool)
            elif key == "task_id" and not val:
                self._task_id = None
            elif key == "task_id":
                self._task_id = Task(val)
            else:
                setattr(self, '_' + key, val)

    @property
    def task(self):
        """:class:`Task` for most recent system
        action on this :class:`ActiveFailover`."""
        if self._task_id:
            self._task_id.refresh()
        return self._task_id

    def sync(self):
        """Sync this :class:`GSLBRegion` object with the DynECT System"""
        self._get()

    @property
    def zone(self):
        """Zone monitored by this :class:`GSLBRegion`"""
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """The fqdn of the specific node which will be monitored by this
        :class:`GSLBRegion`
        """
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def region_code(self):
        """ISO region code of this :class:`GSLBRegion`"""
        return self._region_code

    @region_code.setter
    def region_code(self, value):
        pass

    @property
    def serve_count(self):
        """How many records will be returned in each DNS response"""
        return self._serve_count

    @serve_count.setter
    def serve_count(self, value):
        self._serve_count = value
        api_args = {'serve_count': self._serve_count}
        self._update(api_args)

    @property
    def failover_mode(self):
        """How the :class:`GSLBRegion` should failover. Must be one of 'ip',
        'cname', 'region', 'global'
        """
        return self._failover_mode

    @failover_mode.setter
    def failover_mode(self, value):
        self._failover_mode = value
        api_args = {'failover_mode': self._failover_mode}
        self._update(api_args)

    @property
    def failover_data(self):
        """Dependent upon failover_mode. Must be one of 'ip', 'cname',
        'region', 'global'
        """
        return self._failover_data

    @failover_data.setter
    def failover_data(self, value):
        self._failover_data = value
        api_args = {'failover_data': self._failover_data}
        self._update(api_args)

    @property
    def pool(self):
        """The IP Pool list for this :class:`GSLBRegion`"""
        return self._pool

    @pool.setter
    def pool(self, value):
        self._pool = value
        api_args = {'pool': self._pool.to_json()}
        self._update(api_args)

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

    def delete(self):
        """Delete this :class:`GSLBRegion`"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<GSLBRegion>: {}').format(self._region_code)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class GSLB(object):
    """A Global Server Load Balancing (GSLB) service"""

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`GSLB` object

        :param auto_recover: Indicates whether or not the service should
            automatically come out of failover when the IP addresses resume
            active status or if the service should remain in failover until
            manually reset. Must be 'Y' or 'N'
        :param ttl: Time To Live in seconds of records in the service. Must be
            less than 1/2 of the Health Probe's monitoring interval. Must be
            one of 30, 60, 150, 300, or 450
        :param notify_events: A comma separated list of the events which
            trigger notifications. Must be one of 'ip', 'svc', or 'nosrv'
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
        :param syslog_delivery: The syslog delivery action type. 'all' will
            deliver notifications no matter what the endpoint state. 'change'
            (default) will deliver only on change in the detected endpoint
            state
        :param region: A list of :class:`GSLBRegion`'s
        :param monitor: The health :class:`Monitor` for this service
        :param contact_nickname: Name of contact to receive notifications
        :param syslog_probe_fmt: see below for format:
        :param syslog_status_fmt: see below for format:
            Use the following format for syslog_xxxx_fmt paramaters.
            %hos	hostname
            %tim	current timestamp or monitored interval
            %reg	region code
            %sta	status
            %ser	record serial
            %rda	rdata
            %sit	monitoring site
            %rti	response time
            %msg	message from monitoring
            %adr	address of monitored node
            %med	median value
            %rts	response times (RTTM)
        :param recovery_delay: number of up status polling intervals to
            consider service up
        """

        super(GSLB, self).__init__()
        self.valid_auto_recover = ('Y', 'N')
        self.valid_ttls = (30, 60, 150, 300, 450)
        self.valid_notify_events = ('ip', 'svc', 'nosrv')
        self.valid_syslog_facility = ('kern', 'user', 'mail', 'daemon', 'auth',
                                      'syslog', 'lpr', 'news', 'uucp', 'cron',
                                      'authpriv', 'ftp', 'ntp', 'security',
                                      'console', 'local0', 'local1', 'local2',
                                      'local3', 'local4', 'local5', 'local6',
                                      'local7')
        self._zone = zone
        self._fqdn = fqdn
        self.uri = '/GSLB/{}/{}/'.format(self._zone, self._fqdn)
        self._auto_recover = self._ttl = self._notify_events = None
        self._syslog_server = self._syslog_port = self._syslog_ident = None
        self._syslog_facility = self._monitor = self._contact_nickname = None
        self._syslog_probe_fmt = self._syslog_status_fmt = None
        self._active = self._status = self._syslog_delivery = None
        self._task_id = None
        self._recovery_delay = None
        self._region = APIList(DynectSession.get_session, 'region')
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)
        self._region.uri = self.uri

    def _post(self, contact_nickname, region, auto_recover=None, ttl=None,
              notify_events=None, syslog_server=None, syslog_port=514,
              syslog_ident='dynect', syslog_facility='daemon',
              syslog_probe_fmt=None, syslog_status_fmt=None, monitor=None,
              syslog_delivery='change', recovery_delay=None):
        """Create a new :class:`GSLB` service object on the DynECT System"""
        self._auto_recover = auto_recover
        self._ttl = ttl
        self._notify_events = notify_events
        self._syslog_server = syslog_server
        self._syslog_port = syslog_port
        self._syslog_ident = syslog_ident
        self._syslog_facility = syslog_facility
        self._syslog_delivery = syslog_delivery
        self._syslog_probe_fmt = syslog_probe_fmt
        self._syslog_status_fmt = syslog_status_fmt
        self._recovery_delay = recovery_delay
        self._region += region
        self._monitor = monitor
        self._contact_nickname = contact_nickname
        api_args = {'contact_nickname': self._contact_nickname,
                    'region': [r._json for r in self._region]}
        if auto_recover:
            api_args['auto_recover'] = self._auto_recover
        if ttl:
            api_args['ttl'] = self._ttl
        if notify_events:
            api_args['notify_events'] = self._notify_events
        if syslog_server:
            api_args['syslog_server'] = self._syslog_server
        if syslog_port:
            api_args['syslog_port'] = self._syslog_port
        if syslog_ident:
            api_args['syslog_ident'] = self._syslog_ident
        if syslog_facility:
            api_args['syslog_facility'] = self._syslog_facility
        if syslog_delivery:
            api_args['syslog_delivery'] = self._syslog_delivery
        if syslog_probe_fmt:
            api_args['syslog_probe_fmt'] = self._syslog_probe_fmt
        if syslog_status_fmt:
            api_args['syslog_status_fmt'] = self._syslog_status_fmt
        if recovery_delay:
            api_args['recovery_delay'] = self._recovery_delay
        if monitor:
            api_args['monitor'] = self._monitor.to_json()
            self._monitor.zone = self._zone
            self._monitor.fqdn = self._fqdn
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _get(self):
        """Get an existing :class:`GSLB` service object"""
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data, region=True):
        """Private method which builds the objects fields based on the data
        returned by an API call

        :param data: the data from the JSON respnose
        :param region: Boolean flag specifying whether to rebuild the region
            objects or not
        """
        for key, val in data.items():
            if key == 'region':
                if region:
                    self._region = APIList(DynectSession.get_session, 'region')
                    for region in val:
                        region_code = region.pop('region_code', None)
                        self._region.append(GSLBRegion(self._zone, self._fqdn,
                                                       region_code, **region))
            elif key == 'monitor':
                # We already have the monitor object, no need to rebuild it
                pass
            elif key == "task_id" and not val:
                self._task_id = None
            elif key == "task_id":
                self._task_id = Task(val)
            else:
                setattr(self, '_' + key, val)
        self._region.uri = self.uri

    @property
    def task(self):
        """:class:`Task` for most recent system action on this :class:`GSLB`.
        """
        if self._task_id:
            self._task_id.refresh()
        return self._task_id

    def sync(self):
        """Sync this :class:`GSLB` object with the DynECT System"""
        self._get()

    def activate(self):
        """Activate this :class:`GSLB` service on the DynECT System"""
        api_args = {'activate': True}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    def deactivate(self):
        """Deactivate this :class:`GSLB` service on the DynECT System"""
        api_args = {'deactivate': True}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

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
        self._build(response['data'], region=False)

    @property
    def auto_recover(self):
        """Indicates whether or not the service should automatically come out
        of failover when the IP addresses resume active status or if the
        service should remain in failover until manually reset. Must be 'Y' or
        'N'
        """
        return self._auto_recover

    @auto_recover.setter
    def auto_recover(self, value):
        if value not in self.valid_auto_recover:
            raise DynectInvalidArgumentError('auto_recover', value,
                                             self.valid_auto_recover)
        self._auto_recover = value
        api_args = {'auto_recover': self._auto_recover}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def status(self):
        """The current state of the service. Will be one of 'unk', 'ok',
        'trouble', or 'failover'
        """
        api_args = {}
        respnose = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._status = respnose['data']['status']
        return self._status

    @status.setter
    def status(self, value):
        pass

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

    @property
    def ttl(self):
        """Time To Live in seconds of records in the service. Must be less than
        1/2 of the Health Probe's monitoring interval. Must be one of 30, 60,
        150, 300, or 450
        """
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        if value not in self.valid_ttls:
            raise DynectInvalidArgumentError('ttl', value, self.valid_ttls)
        self._ttl = value
        api_args = {'ttl': self._ttl}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def notify_events(self):
        """A comma separated list of the events which trigger notifications.
        Must be one of 'ip', 'svc', or 'nosrv'
        """
        return self._notify_events

    @notify_events.setter
    def notify_events(self, value):
        if value not in self.valid_notify_events:
            raise DynectInvalidArgumentError('notify_events', value,
                                             self.valid_notify_events)
        self._notify_events = value
        api_args = {'notify_events': self._notify_events}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def syslog_server(self):
        """The Hostname or IP address of a server to receive syslog
        notifications on monitoring events
        """
        self._get()
        return self._syslog_server

    @syslog_server.setter
    def syslog_server(self, value):
        self._syslog_server = value
        api_args = {'syslog_server': self._syslog_server}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def syslog_port(self):
        """The port where the remote syslog server listens for notifications"""
        self._get()
        return self._syslog_port

    @syslog_port.setter
    def syslog_port(self, value):
        self._syslog_port = value
        api_args = {'syslog_port': self._syslog_port}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def syslog_ident(self):
        """The ident to use when sending syslog notifications"""
        self._get()
        return self._syslog_ident

    @syslog_ident.setter
    def syslog_ident(self, value):
        self._syslog_ident = value
        api_args = {'syslog_ident': self._syslog_ident}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def syslog_facility(self):
        """The syslog facility to use when sending syslog notifications. Must
        be one of 'kern', 'user', 'mail', 'daemon', 'auth', 'syslog', 'lpr',
        'news', 'uucp', 'cron', 'authpriv', 'ftp', 'ntp', 'security',
        'console', 'local0', 'local1', 'local2', 'local3', 'local4', 'local5',
        'local6', or 'local7'
        """
        self._get()
        return self._syslog_facility

    @syslog_facility.setter
    def syslog_facility(self, value):
        if value not in self.valid_syslog_facility:
            raise DynectInvalidArgumentError('syslog_facility', value,
                                             self.valid_syslog_facility)
        self._syslog_facility = value
        api_args = {'syslog_facility': self._syslog_facility}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def syslog_delivery(self):
        self._get()
        return self._syslog_delivery

    @syslog_delivery.setter
    def syslog_delivery(self, value):
        api_args = {'syslog_delivery': value}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def syslog_probe_format(self):
        self._get()
        return self._syslog_probe_fmt

    @syslog_probe_format.setter
    def syslog_probe_format(self, value):
        api_args = {'syslog_probe_fmt': value}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def syslog_status_format(self):
        self._get()
        return self._syslog_status_fmt

    @syslog_status_format.setter
    def syslog_status_format(self, value):
        api_args = {'syslog_status_fmt': value}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def recovery_delay(self):
        self._get()
        return self._recovery_delay

    @recovery_delay.setter
    def recovery_delay(self, value):
        api_args = {'recovery_delay': value}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    @property
    def region(self):
        """A list of :class:`GSLBRegion`'s"""
        return self._region

    @region.setter
    def region(self, value):
        if isinstance(value, list) and not isinstance(value, APIList):
            self._region = APIList(DynectSession.get_session, 'region', None,
                                   value)
        elif isinstance(value, APIList):
            self._region = value
        self._region.uri = self.uri

    @property
    def monitor(self):
        """The health :class:`Monitor` for this service"""
        return self._monitor

    @monitor.setter
    def monitor(self, value):
        # We're only going accept new monitors of type Monitor
        if isinstance(value, Monitor):
            api_args = {'monitor': value.to_json()}
            response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                           api_args)
            self._build(response['data'], region=False)
            self._monitor = value

    @property
    def contact_nickname(self):
        """Name of contact to receive notifications from this :class:`GSLB`
        service
        """
        return self._contact_nickname

    @contact_nickname.setter
    def contact_nickname(self, value):
        self._contact_nickname = value
        api_args = {'contact_nickname': self._contact_nickname}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'], region=False)

    def delete(self):
        """Delete this :class:`GSLB` service from the DynECT System"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<GSLB>: {}').format(self._fqdn)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
