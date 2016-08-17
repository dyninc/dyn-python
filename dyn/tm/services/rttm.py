# -*- coding: utf-8 -*-
import warnings
from datetime import datetime

from dyn.compat import force_unicode
from dyn.tm.utils import APIList, Active, unix_date
from dyn.tm.errors import DynectInvalidArgumentError
from dyn.tm.session import DynectSession
from dyn.tm.task import Task

__author__ = 'jnappi'
__all__ = ['Monitor', 'PerformanceMonitor', 'RegionPoolEntry', 'RTTMRegion',
           'RTTM']


class Monitor(object):
    """A :class:`Monitor` for RTTM Service. May be used as a HealthMonitor"""

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
        self.zone = self.fqdn = self._status = None
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
        response hashes or other :class:`DNSSECKey` instances

        :param other: the value to compare this :class:`HealthMonitor` to.
            Valid input types: `dict`, :class:`HealthMonitor`
        """
        if isinstance(other, dict):
            return False
        elif isinstance(other, Monitor):
            return False
        return False

    def _get(self):
        """Update this :class:`Monitor` with data from the Dyn System"""
        uri = '/RTTM/{}/{}/'.format(self.zone, self.fqdn)
        api_args = {}
        response = DynectSession.get_session().execute(uri, 'GET', api_args)
        self._build(response['data']['monitor'])

    def _update(self, api_args):
        """Update the Dyn System with data from this :class:`Monitor`"""
        uri = '/RTTM/{}/{}/'.format(self.zone, self.fqdn)
        response = DynectSession.get_session().execute(uri, 'PUT', api_args)
        self._build(response['data']['monitor'])

    def _build(self, data):
        """Update the fields in this :class:`PerformanceMonitor` with the data
        from API calls.

        :param data: The 'data' field of API responses
        """
        for key, val in data.items():
            setattr(self, '_' + key, val)

    @property
    def status(self):
        """Get the current status of this :class:`HealthMonitor` from the
        DynECT System
        """
        self._get()
        return self._status

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
        self._update(api_args)

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
        self._update(api_args)

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
        self._update(api_args)

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
        self._update(api_args)

    @property
    def port(self):
        """For HTTP(S)/SMTP/TCP probes, an alternate connection port"""
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        api_args = {'monitor': {'port': self._port}}
        self._update(api_args)

    @property
    def path(self):
        """For HTTP(S) probes, a specific path to request"""
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        api_args = {'monitor': {'path': self._path}}
        self._update(api_args)

    @property
    def host(self):
        """For HTTP(S) probes, a value to pass in to the Host"""
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        api_args = {'monitor': {'host': self._host}}
        self._update(api_args)

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
        self._update(api_args)

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
        self._update(api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<HealthMonitor>: {}').format(self._protocol)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class PerformanceMonitor(Monitor):
    """A :class:`PerformanceMonitor` for RTTM Service."""

    def __init__(self, *args, **kwargs):
        super(PerformanceMonitor, self).__init__(*args, **kwargs)
        self.valid_intervals = (10, 20, 30, 60)

    def _get(self):
        """Update this :class:`PerformanceMonitor` with data from the Dyn
        System
        """
        uri = '/RTTM/{}/{}/'.format(self.zone, self.fqdn)
        api_args = {}
        response = DynectSession.get_session().execute(uri, 'GET', api_args)
        self._build(response['data']['performance_monitor'])

    def _update(self, api_args):
        """Update the Dyn System with data from this
        :class:`PerformanceMonitor`
        """
        uri = '/RTTM/{}/{}/'.format(self.zone, self.fqdn)
        response = DynectSession.get_session().execute(uri, 'PUT', api_args)
        self._build(response['data']['performance_monitor'])

    def __str__(self):
        """str override"""
        return force_unicode('<PerformanceMonitor>: {}').format(self._protocol)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class RegionPoolEntry(object):
    """Creates a new RTTM service region pool entry in the zone/node
    indicated
    """

    def __init__(self, address, label, weight, serve_mode, **kwargs):
        """Create a :class:`RegionPoolEntry` object

        :param address: The IPv4 address or FQDN of this Node IP
        :param label: A descriptive string identifying this IP
        :param weight:  A number from 1-15 describing how often this record
            should be served. The higher the number, the more often the address
            is served
        :param serve_mode: Sets the behavior of this particular record. Must be
            one of 'always', 'obey', 'remove', or 'no'
        """
        super(RegionPoolEntry, self).__init__()
        self.valid_modes = ('always', 'obey', 'remove', 'no')
        self._address = address
        self._label = label
        self._task_id = None
        self._zone = kwargs.get('zone')
        self._fqdn = kwargs.get('fqdn')
        self._region_code = kwargs.get('region_code')
        if weight not in range(1, 16):
            raise DynectInvalidArgumentError('weight', weight, '1-15')
        self._weight = weight
        if serve_mode not in self.valid_modes:
            raise DynectInvalidArgumentError('serve_mode', serve_mode,
                                             self.valid_modes)
        self._serve_mode = serve_mode
        self._log = []
        self._build(kwargs)

    def _update(self, args):
        """Private method for processing various updates"""
        uri = '/RTTMRegionPoolEntry/{}/{}/{}/{}/'.format(self._zone,
                                                         self._fqdn,
                                                         self._region_code,
                                                         self._address)
        response = DynectSession.get_session().execute(uri, 'PUT', args)
        self._build(response['data'])

    def _get(self):
        uri = '/RTTMRegionPoolEntry/{}/{}/{}/{}/'.format(self._zone,
                                                         self._fqdn,
                                                         self._region_code,
                                                         self._address)
        args = {'detail': 'Y'}
        response = DynectSession.get_session().execute(uri, 'GET', args)
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
        action on this :class:`RegionPoolEntry`."""
        if self._task_id:
            self._task_id.refresh()
        return self._task_id

    @property
    def logs(self):
        self._get()
        return self._log

    @logs.setter
    def logs(self, value):
        pass

    @property
    def address(self):
        """The IPv4 address or FQDN of this Node IP"""
        return self._address

    @address.setter
    def address(self, new_address):
        api_args = {'new_address': new_address}
        self._update(api_args)

    @property
    def zone(self):
        """Zone for this :class:`RegionPoolEntry`,
         this is stored locally for REST command completion"""
        return self._zone

    @zone.setter
    def zone(self, zone):
        self._zone = zone

    @property
    def fqdn(self):
        """FQDN for this :class:`RegionPoolEntry`,
         this is stored locally for REST command completion"""
        return self._fqdn

    @fqdn.setter
    def fqdn(self, fqdn):
        self._fqdn = fqdn

    @property
    def region_code(self):
        """region_code for this :class:`RegionPoolEntry`,
         this is stored locally for REST command completion"""
        return self._region_code

    @region_code.setter
    def region_code(self, region_code):
        self._region_code = region_code

    @property
    def label(self):
        """A descriptive string identifying this IP"""
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        self._update(api_args)

    @property
    def weight(self):
        """A number from 1-15 describing how often this record should be
        served. The higher the number, the more often the address is served
        """
        return self._weight

    @weight.setter
    def weight(self, new_weight):
        if new_weight < 1 or new_weight > 15:
            raise DynectInvalidArgumentError('weight', new_weight, '1-15')
        self._weight = new_weight
        api_args = {'weight': self._weight}
        self._update(api_args)

    @property
    def serve_mode(self):
        """Sets the behavior of this particular record"""
        return self._serve_mode

    @serve_mode.setter
    def serve_mode(self, serve_mode):
        if serve_mode not in self.valid_modes:
            raise DynectInvalidArgumentError('serve_mode', serve_mode,
                                             self.valid_modes)
        self._serve_mode = serve_mode
        api_args = {'serve_mode': self._serve_mode}
        self._update(api_args)

    def to_json(self):
        """Return a JSON representation of this RegionPoolEntry"""
        json_blob = {'address': self._address, 'label': self._label,
                     'weight': self._weight, 'serve_mode': self._serve_mode}
        return json_blob

    def delete(self):
        """Delete this :class:`RegionPoolEntry`"""
        uri = '/RTTMRegionPoolEntry/{}/{}/{}/{}/'.format(self._zone,
                                                         self._fqdn,
                                                         self._region_code,
                                                         self._address)
        DynectSession.get_session().execute(uri, 'DELETE', {})

    def __str__(self):
        """str override"""
        return force_unicode('<RTTMRegionPoolEntry>: {}').format(self._address)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class RTTMRegion(object):
    """docstring for RTTMRegion"""

    def __init__(self, zone, fqdn, region_code, *args, **kwargs):
        """Create a :class:`RTTMRegion` object

        :param region_code: Name of the region
        :param pool: (*arg) The IP Pool list for this region
        :param autopopulate: If set to Y, this region will automatically be
            filled in from the global pool, and any other options passed in for
            this region will be ignored
        :param ep: Eligibility Pool - How many records will make it into the
            eligibility pool. The addresses that get chosen will be those that
            respond the fastest
        :param apmc: The minimum amount of IPs that must be in the up state,
            otherwise the region will be in failover
        :param epmc: The minimum amount of IPs that must be populated in the
            EP, otherwise the region will be in failover
        :param serve_count: How many records will be returned in each DNS
            response
        :param failover_mode: How the region should failover. Must be one of
            'ip', 'cname', 'region', or 'global'
        :param failover_data: Dependent upon failover_mode. Must be one of ip',
            'cname', 'region', or 'global'
        """
        super(RTTMRegion, self).__init__()
        self.valid_region_codes = ('US West', 'US Central', 'US East', 'Asia',
                                   'EU West', 'EU Central', 'EU East',
                                   'global')
        self.valid_modes = ('ip', 'cname', 'region', 'global')
        self._task_id = None
        self._zone = zone
        self._fqdn = fqdn
        self._autopopulate = self._ep = self._apmc = None
        self._epmc = self._serve_count = self._failover_mode = None
        self._failover_data = None
        if len(args) != 0:
            pool = args[0]
        else:
            pool = None
        if region_code not in self.valid_region_codes:
            raise DynectInvalidArgumentError('region_code', region_code,
                                             self.valid_region_codes)
        self._region_code = region_code
        self._pool = []
        self.uri = '/RTTMRegion/{}/{}/{}/'.format(self._zone, self._fqdn,
                                                  self._region_code)
        # Backwards Compatability, since we changed the structure of this
        # Class:
        if kwargs.get('pool'):
            warnings.warn("passing pool as keyword argument is\
                          depreciated! please pass in as 4th argument",
                          DeprecationWarning)
            pool = kwargs.pop('pool')

        if not pool and len(kwargs) == 0:
            self._get()
        if len(kwargs) > 0:
            self._build(kwargs)
        if pool:
            for poole in pool:
                if isinstance(poole, dict):
                    rpe = RegionPoolEntry(zone=self._zone,
                                          fqdn=self._fqdn,
                                          region_code=self._region_code,
                                          **poole)
                    self._pool.append(rpe)
                else:
                    if not poole.zone:
                        poole.zone = self._zone
                    if not poole.fqdn:
                        poole.fqdn = self._fqdn
                    if not poole.region_code:
                        poole.region_code = self._region_code
                    self._pool.append(poole)
        self._status = None

    def _post(self):
        """Create a new :class:`RTTMRegion` on the DynECT System"""
        uri = '/RTTMRegion/{}/{}/'.format(self._zone, self._fqdn)
        api_args = {'region_code': self._region_code,
                    'pool': [poole.to_json() for poole in self._pool]}
        if self._autopopulate:
            if self._autopopulate not in ('Y', 'N'):
                raise DynectInvalidArgumentError('autopopulate',
                                                 self._autopopulate,
                                                 ('Y', 'N'))
            api_args['autopopulate'] = self._autopopulate
        if self._ep:
            api_args['ep'] = self._ep
        if self._apmc:
            api_args['apmc'] = self._apmc
        if self._epmc:
            api_args['epmc'] = self._epmc
        if self._serve_count:
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
        """Get an existing :class:`RTTMRegion` object from the DynECT System"""
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args):
        """Private Update method to cut back on redundant code"""
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        for key, val in data.items():
            if key == 'pool':
                pass
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

    @property
    def autopopulate(self):
        """If set to Y, this region will automatically be filled in from the
        global pool, and any other options passed in for this region will be
        ignored. Must be either 'Y' or 'N'.
        """
        return self._autopopulate

    @autopopulate.setter
    def autopopulate(self, value):
        self._autopopulate = value
        api_args = {'autopopulate': self._autopopulate}
        self._update(api_args)

    @property
    def ep(self):
        """Eligibility Pool - How many records will make it into the
        eligibility pool. The addresses that get chosen will be those that
        respond the fastest
        """
        return self._ep

    @ep.setter
    def ep(self, value):
        self._ep = value
        api_args = {'ep': self._ep}
        self._update(api_args)

    @property
    def apmc(self):
        """The minimum amount of IPs that must be in the up state, otherwise
        the region will be in failover.
        """
        return self._apmc

    @apmc.setter
    def apmc(self, value):
        self._apmc = value
        api_args = {'apmc': self._apmc}
        self._update(api_args)

    @property
    def epmc(self):
        """The minimum amount of IPs that must be populated in the EP,
        otherwise the region will be in failover
        """
        return self._epmc

    @epmc.setter
    def epmc(self, value):
        self._epmc = value
        api_args = {'epmc': self._epmc}
        self._update(api_args)

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
        """How the region should failover. Must be one of 'ip', 'cname',
        'region', or 'global'
        """
        return self._failover_mode

    @failover_mode.setter
    def failover_mode(self, value):
        self._failover_mode = value
        api_args = {'failover_mode': self._failover_mode}
        self._update(api_args)

    @property
    def failover_data(self):
        """Dependent upon failover_mode. Must be one of ip', 'cname', 'region',
        or 'global'
        """

        return self._failover_data

    @failover_data.setter
    def failover_data(self, value):
        if value not in self.valid_modes:
            raise DynectInvalidArgumentError('failover_data', value,
                                             self.valid_modes)
        api_args = {'failover_data': value}
        self._update(api_args)

    @property
    def pool(self):
        """The IP Pool list for this :class:`RTTMRegion`"""
        return self._pool

    @pool.setter
    def pool(self, value):
        self._pool = value
        api_args = {'pool': self._pool}
        self._update(api_args)

    @property
    def status(self):
        """The current state of the region."""
        self._get()
        return self._status

    @status.setter
    def status(self, value):
        pass

    @property
    def _json(self):
        """Unpack this object and return it as a JSON blob"""
        json_blob = {'region_code': self._region_code,
                     'pool': [entry.to_json() for entry in self._pool]}
        if self._autopopulate:
            json_blob['autopopulate'] = self._autopopulate
        if self._ep:
            json_blob['ep'] = self._ep
        if self._apmc:
            json_blob['apmc'] = self._apmc
        if self._epmc:
            json_blob['epmc'] = self._epmc
        if self._serve_count:
            json_blob['serve_count'] = self._serve_count
        if self._failover_mode:
            json_blob['failover_mode'] = self._failover_mode
        if self._failover_data:
            json_blob['failover_data'] = self._failover_data
        return json_blob

    def delete(self):
        """Delete an existing :class:`RTTMRegion` object from the DynECT
        System
        """
        DynectSession.get_session().execute(self.uri, 'DELETE')

    def __str__(self):
        """str override"""
        return force_unicode('<RTTMRegion>: {}').format(self._region_code)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class RTTM(object):
    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`RTTM` object

        :param auto_recover:  Indicates whether or not the service should
            automatically come out of failover when the IP addresses resume
            active status or if the service should remain in failover until
            manually reset. Must be one of 'Y' or 'N'
        :param ttl: Time To Live in seconds of records in the service. Must be
            less than 1/2 of the Health Probe's monitoring interval. Must be
            one of 30, 60, 150, 300, or 450.
        :param notify_events: A list of the events which trigger notifications.
            Must be one of 'ip', 'svc', or 'nosrv'
        :param syslog_server: The Hostname or IP address of a server to receive
            syslog notifications on monitoring events
        :param syslog_port: The port where the remote syslog server listens for
            notifications
        :param syslog_ident: The ident to use when sending syslog notifications
        :param syslog_facility: The syslog facility to use when sending syslog
            notifications. Must be one of kern, user, mail, daemon, auth,
            syslog, lpr, news, uucp, cron, authpriv, ftp, ntp, security,
            console, local0, local1, local2, local3, local4, local5, local6, or
            local7
        :param syslog_delivery: The syslog delivery action type. 'all' will
            deliver notifications no matter what the endpoint state. 'change'
            (default) will deliver only on change in the detected endpoint
            state
        :param region: A list of :class:`RTTMRegion`'s
        :param monitor: The :class:`Monitor` for this service
        :param performance_monitor: The performance monitor for the service
        :param contact_nickname: Name of contact to receive notifications
        :param syslog_probe_fmt: see below for format:
        :param syslog_status_fmt: see below for format:
        :param syslog_rttm_fmt: see below for format:
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
        super(RTTM, self).__init__()
        self.valid_ttls = (30, 60, 150, 300, 450)
        self.valid_notify_events = ('ip', 'svc', 'nosrv')
        self.valid_syslog_facilities = ('kern', 'user', 'mail', 'daemon',
                                        'auth', 'syslog', 'lpr', 'news',
                                        'uucp', 'cron', 'authpriv', 'ftp',
                                        'ntp', 'security', 'console', 'local0',
                                        'local1', 'local2', 'local3', 'local4',
                                        'local5', 'local6', 'local7')
        self._zone = zone
        self._fqdn = fqdn
        self.uri = '/RTTM/{}/{}/'.format(self._zone, self._fqdn)
        self._auto_recover = self._ttl = self._notify_events = None
        self._syslog_server = self._syslog_port = self._syslog_ident = None
        self._syslog_facility = self._monitor = None
        self._performance_monitor = self._contact_nickname = None
        self._active = self._syslog_delivery = self._syslog_probe_fmt = None
        self._syslog_status_fmt = self._syslog_rttm_fmt = None
        self._recovery_delay = None
        self._region = APIList(DynectSession.get_session, 'region')
        self._task_id = None
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)
        self._region.uri = self.uri

    def _post(self, contact_nickname, performance_monitor, region, ttl=None,
              auto_recover=None, notify_events=None, syslog_server=None,
              syslog_port=514, syslog_ident='dynect', syslog_facility='daemon',
              syslog_delivery='change', syslog_probe_fmt=None,
              syslog_status_fmt=None, syslog_rttm_fmt=None,
              recovery_delay=None, monitor=None):
        """Create a new RTTM Service on the DynECT System"""
        self._auto_recover = auto_recover
        self._ttl = ttl
        self._notify_events = notify_events
        self._syslog_server = syslog_server
        self._syslog_port = syslog_port
        self._syslog_ident = syslog_ident
        self._syslog_facility = syslog_facility
        self._syslog_delivery = syslog_delivery
        self._region += region
        self._monitor = monitor
        self._performance_monitor = performance_monitor
        self._contact_nickname = contact_nickname
        self._syslog_probe_fmt = syslog_probe_fmt
        self._syslog_status_fmt = syslog_status_fmt
        self._syslog_rttm_fmt = syslog_rttm_fmt
        self._recovery_delay = recovery_delay
        api_args = {}
        if auto_recover:
            if auto_recover not in ('Y', 'N'):
                raise DynectInvalidArgumentError('auto_recover', auto_recover,
                                                 ('Y', 'N'))
            api_args['auto_recover'] = self._auto_recover
        if ttl:
            if ttl not in self.valid_ttls:
                raise DynectInvalidArgumentError('ttl', ttl, self.valid_ttls)
            api_args['ttl'] = self._ttl
        if notify_events:
            for event in notify_events:
                if event not in self.valid_notify_events:
                    raise DynectInvalidArgumentError('notify_events', event,
                                                     self.valid_notify_events)
            api_args['notify_events'] = self._notify_events
        if syslog_server:
            api_args['syslog_server'] = self._syslog_server
        if syslog_port:
            api_args['syslog_port'] = self._syslog_port
        if syslog_ident:
            api_args['syslog_ident'] = self._syslog_ident
        if syslog_facility:
            if syslog_facility not in self.valid_syslog_facilities:
                raise DynectInvalidArgumentError('syslog_facility',
                                                 syslog_facility,
                                                 self.valid_syslog_facilities)
            api_args['syslog_facility'] = self._syslog_facility
        if syslog_delivery:
            api_args['syslog_delivery'] = self._syslog_delivery
        if syslog_probe_fmt:
            api_args['syslog_probe_fmt'] = self._syslog_probe_fmt
        if syslog_status_fmt:
            api_args['syslog_status_fmt'] = self._syslog_status_fmt
        if syslog_rttm_fmt:
            api_args['syslog_rttm_fmt'] = self._syslog_rttm_fmt
        if recovery_delay:
            api_args['recovery_delay'] = self._recovery_delay
        if region:
            api_args['region'] = [reg._json for reg in self._region]
        if monitor:
            api_args['monitor'] = self._monitor.to_json()
        if performance_monitor:
            mon_args = self._performance_monitor.to_json()
            api_args['performance_monitor'] = mon_args
        if contact_nickname:
            api_args['contact_nickname'] = self._contact_nickname

        # API expects a CSV string, not a list
        if isinstance(self.notify_events, list):
            api_args['notify_events'] = ','.join(self.notify_events)

        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _get(self):
        """Build an object around an existing DynECT RTTM Service"""
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args):
        """Perform a PUT api call using this objects data"""
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Build the neccesary substructures under this :class:`RTTM`"""
        for key, val in data.items():
            if key == 'region':
                self._region = APIList(DynectSession.get_session, 'region')
                for region in val:
                    code = region.pop('region_code', None)
                    pool = region.pop('pool', None)
                    status = region.pop('status', None)

                    r = RTTMRegion(self._zone, self._fqdn, code, pool,
                                   **region)
                    r._status = status
                    self._region.append(r)
            elif key == 'monitor':
                if self._monitor is not None:
                    self._monitor.zone = self._zone
                    self._monitor.fqdn = self._fqdn
                else:
                    proto = val.pop('protocol', None)
                    inter = val.pop('interval', None)
                    self._monitor = Monitor(proto, inter, **val)
            elif key == 'performance_monitor':
                if self._performance_monitor is not None:
                    self._performance_monitor.zone = self._zone
                    self._performance_monitor.fqdn = self._fqdn
                else:
                    proto = val.pop('protocol', None)
                    inter = val.pop('interval', None)
                    self._performance_monitor = PerformanceMonitor(proto,
                                                                   inter,
                                                                   **val)
            elif key == 'notify_events':
                self._notify_events = [item.strip() for item in val.split(',')]
            elif key == 'active':
                self._active = Active(val)
            elif key == "task_id" and not val:
                self._task_id = None
            elif key == "task_id":
                self._task_id = Task(val)
            else:
                setattr(self, '_' + key, val)
        self._region.uri = self.uri

    @property
    def task(self):
        """:class:`Task` for most recent system
         action on this :class:`ActiveFailover`."""
        if self._task_id:
            self._task_id.refresh()
        return self._task_id

    def get_rrset_report(self, ts):
        """Generates a report of regional response sets for this RTTM service
        at a given point in time

        :param ts: UNIX timestamp identifying point in time for the log report
        :return: dictionary containing rrset report data
        """
        api_args = {'zone': self._zone,
                    'fqdn': self._fqdn,
                    'ts': ts}
        response = DynectSession.get_session().execute('/RTTMRRSetReport/',
                                                       'POST', api_args)
        return response['data']

    def get_log_report(self, start_ts, end_ts=None):
        """Generates a report with information about changes to an existing
        RTTM service

        :param start_ts: datetime.datetime instance identifying point in time
            for the start of the log report
        :param end_ts: datetime.datetime instance identifying point in time
            for the end of the log report. Defaults to datetime.datetime.now()
        :return: dictionary containing log report data
        """
        end_ts = end_ts or datetime.now()
        api_args = {'zone': self._zone,
                    'fqdn': self._fqdn,
                    'start_ts': unix_date(start_ts),
                    'end_ts': unix_date(end_ts)}
        response = DynectSession.get_session().execute('/RTTMLogReport/',
                                                       'POST', api_args)
        return response['data']

    def activate(self):
        """Activate this RTTM Service"""
        api_args = {'activate': True}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def deactivate(self):
        """Deactivate this RTTM Service"""
        api_args = {'deactivate': True}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def recover(self, recoverip=None, address=None):
        """Recovers the RTTM service or a specific node IP within the service
        """
        api_args = {'recover': True}
        if recoverip:
            api_args['recoverip'] = recoverip
            api_args['address'] = address
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def active(self):
        """Returns whether or not this :class:`RTTM` Service is currently
        active. When setting directly, rather than using activate/deactivate
        valid arguments are 'Y' or True to activate, or 'N' or False to
        deactivate. Note: If your service is already active and you try to
        activate it, nothing will happen. And vice versa for deactivation.

        :returns: An :class:`Active` object representing the current state of
            this :class:`ReverseDNS` Service
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
    def auto_recover(self):
        """Indicates whether or not the service should automatically come out
        of failover when the IP addresses resume active status or if the
        service should remain in failover until manually reset. Must be one of
        'Y' or 'N'
        """
        return self._auto_recover

    @auto_recover.setter
    def auto_recover(self, value):
        if value not in ('Y', 'N'):
            raise DynectInvalidArgumentError('auto_recover', value,
                                             ('Y', 'N'))
        api_args = {'auto_recover': value}
        self._update(api_args)

    @property
    def ttl(self):
        """Time To Live in seconds of records in the service. Must be less than
        1/2 of the Health Probe's monitoring interval. Must be one of 30, 60,
        150, 300, or 450.
        """
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        if value not in self.valid_ttls:
            raise DynectInvalidArgumentError('ttl', value, self.valid_ttls)
        api_args = {'ttl': value}
        self._update(api_args)

    @property
    def notify_events(self):
        """A list of events which trigger notifications. Valid values are:
        'ip', 'svc', and 'nosrv'
        """
        return self._notify_events

    @notify_events.setter
    def notify_events(self, value):
        for val in value:
            if val not in self.valid_notify_events:
                raise DynectInvalidArgumentError('notify_events', val,
                                                 self.valid_notify_events)
        value = ','.join(value)
        api_args = {'notify_events': value}
        self._update(api_args)

    @property
    def status(self):
        """Status"""
        self._get()
        return self._status

    @property
    def syslog_server(self):
        """The Hostname or IP address of a server to receive syslog
        notifications on monitoring events
        """
        self._get()
        return self._syslog_server

    @syslog_server.setter
    def syslog_server(self, value):
        api_args = {'syslog_server': value}
        self._update(api_args)

    @property
    def syslog_port(self):
        """The port where the remote syslog server listens for notifications"""
        self._get()
        return self._syslog_port

    @syslog_port.setter
    def syslog_port(self, value):
        api_args = {'syslog_port': value}
        self._update(api_args)

    @property
    def syslog_ident(self):
        """The ident to use when sending syslog notifications"""
        self._get()
        return self._syslog_ident

    @syslog_ident.setter
    def syslog_ident(self, value):
        api_args = {'syslog_ident': value}
        self._update(api_args)

    @property
    def syslog_facility(self):
        """The syslog facility to use when sending syslog notifications. Must
        be one of kern, user, mail, daemon, auth, syslog, lpr, news, uucp,
        cron, authpriv, ftp, ntp, security, console, local0, local1, local2,
        local3, local4, local5, local6, or local7
        """
        self._get()
        return self._syslog_facility

    @syslog_facility.setter
    def syslog_facility(self, value):
        if value not in self.valid_syslog_facilities:
            raise DynectInvalidArgumentError('syslog_facility', value,
                                             self.valid_syslog_facilities)
        api_args = {'syslog_facility': value}
        self._update(api_args)

    @property
    def syslog_delivery(self):
        self._get()
        return self._syslog_delivery

    @syslog_delivery.setter
    def syslog_delivery(self, value):
        api_args = {'syslog_delivery': value}
        self._update(api_args)

    @property
    def syslog_probe_format(self):
        self._get()
        return self._syslog_probe_fmt

    @syslog_probe_format.setter
    def syslog_probe_format(self, value):
        api_args = {'syslog_probe_fmt': value}
        self._update(api_args)

    @property
    def syslog_status_format(self):
        self._get()
        return self._syslog_status_fmt

    @syslog_status_format.setter
    def syslog_status_format(self, value):
        api_args = {'syslog_status_fmt': value}
        self._update(api_args)

    @property
    def syslog_rttm_format(self):
        self._get()
        return self._syslog_rttm_fmt

    @syslog_rttm_format.setter
    def syslog_rttm_format(self, value):
        api_args = {'syslog_rttm_fmt': value}
        self._update(api_args)

    @property
    def recovery_delay(self):
        self._get()
        return self._recovery_delay

    @recovery_delay.setter
    def recovery_delay(self, value):
        api_args = {'recovery_delay': value}
        self._update(api_args)

    @property
    def region(self):
        """A list of :class:`RTTMRegion`'s"""
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
        """The :class:`Monitor` for this service"""
        return self._monitor

    @monitor.setter
    def monitor(self, value):
        if isinstance(value, Monitor):
            self._monitor = value
            api_args = {'monitor': self._monitor.to_json()}
            self._update(api_args)

    @property
    def performance_monitor(self):
        """The Performance :class:`Monitor` for this service"""
        return self._performance_monitor

    @performance_monitor.setter
    def performance_monitor(self, value):
        if isinstance(value, Monitor):
            self._performance_monitor = value
            api_args = {'performance_monitor':
                        self._performance_monitor.to_json()}
            self._update(api_args)

    @property
    def contact_nickname(self):
        """The name of contact to receive notifications from this service"""
        return self._contact_nickname

    @contact_nickname.setter
    def contact_nickname(self, value):
        api_args = {'contact_nickname': value}
        self._update(api_args)

    def delete(self):
        """Delete this RTTM Service"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<RTTM>: {}').format(self._fqdn)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
