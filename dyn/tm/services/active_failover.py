# -*- coding: utf-8 -*-
from dyn.compat import force_unicode
from dyn.tm.utils import Active
from dyn.tm.errors import DynectInvalidArgumentError
from dyn.tm.session import DynectSession
from dyn.tm.task import Task

__author__ = 'jnappi'
__all__ = ['HealthMonitor', 'ActiveFailover']


class HealthMonitor(object):
    """A health monitor for an :class:`ActiveFailover` service"""

    def __init__(self, protocol, interval, retries=None, timeout=None,
                 port=None, path=None, host=None, header=None, expected=None):
        """Create a :class:`HealthMonitor` object

        :param protocol: The protocol to monitor. Must be either HTTP, HTTPS,
            PING, SMTP, or TCP
        :param interval: How often (in minutes) to run this
            :class:`HealthMonitor`. Must be 1, 5, 10, or 15,
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
        super(HealthMonitor, self).__init__()
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
        json_blob = {'protocol': self.protocol,
                     'interval': self.interval}
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
        elif isinstance(other, HealthMonitor):
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
        return force_unicode('<HealthMonitor>: {}').format(self._protocol)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class ActiveFailover(object):
    """With Active Failover, we monitor your Primary IP.  If a failover event
    is detected, our system auto switches (hot swaps) to your dedicated back-up
    IP
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a new :class:`ActiveFailover` object

        :param zone: The zone to attach this :class:`ActiveFailover` service to
        :param fqdn: The FQDN where this :class:`ActiveFailover` service will
            be attached
        :param address: IPv4 Address or FQDN being monitored by this
            :class:`ActiveFailover` service
        :param failover_mode: Indicates the target failover resource type.
        :param failover_data: The IPv4 Address or CNAME data for the failover
            target
        :param auto_recover: Indicates whether this service should restore its
            original state when the source IPs resume online status
        :param notify_events: A comma separated list of what events trigger
            notifications
        :param syslog_server: The Hostname or IP address of a server to receive
            syslog notifications on monitoring events
        :param syslog_port: The port where the remote syslog server listens
        :param syslog_ident: The ident to use when sending syslog notifications
        :param syslog_facility: The syslog facility to use when sending syslog
            notifications
        :param syslog_delivery: The syslog delivery action type. 'all' will
            deliver notifications no matter what the endpoint state. 'change'
            (default) will deliver only on change in the detected endpoint
            state
        :param monitor: The :class:`HealthMonitor` for this
            :class:`ActiveFailover` service
        :param contact_nickname: Name of contact to receive notifications from
            this :class:`ActiveFailover` service
        :param ttl: Time To Live in seconds of records in the service. Must be
            less than 1/2 of the Health Probe's monitoring interval
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
        super(ActiveFailover, self).__init__()
        self.valid_notify_events = ('ip', 'svc', 'nosrv')
        self._zone = zone
        self._fqdn = fqdn
        self._address = self._failover_mode = self._failover_data = None
        self._monitor = self._active = None
        self._contact_nickname = self._auto_recover = None
        self._notify_events = self._syslog_server = self._syslog_port = None
        self._syslog_ident = self._syslog_probe_fmt = None
        self._syslog_status_fmt = self._syslog_facility = self._ttl = None
        self._syslog_delivery = self._recovery_delay = None
        self.uri = '/Failover/{}/{}/'.format(self._zone, self._fqdn)
        self.api_args = {}
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)

    def _get(self):
        """Build an object around an existing DynECT Active Failover Service"""
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _post(self, address, failover_mode, failover_data, monitor,
              contact_nickname, auto_recover=None, notify_events=None,
              syslog_server=None, syslog_port=None, syslog_ident=None,
              syslog_facility=None, ttl=None, syslog_probe_fmt=None,
              syslog_status_fmt=None, syslog_delivery=None,
              recovery_delay=None):
        """Create a new Active Failover Service on the DynECT System"""
        self._address = address
        self._failover_mode = failover_mode
        self._failover_data = failover_data
        self._monitor = monitor
        self._monitor.zone = self._zone
        self._monitor.fqdn = self._fqdn
        self._contact_nickname = contact_nickname
        self._auto_recover = auto_recover
        self._notify_events = notify_events
        self._syslog_server = syslog_server
        self._syslog_port = syslog_port
        self._syslog_ident = syslog_ident
        self._syslog_facility = syslog_facility
        self._syslog_delivery = syslog_delivery
        self._syslog_probe_fmt = syslog_probe_fmt
        self._syslog_status_fmt = syslog_status_fmt
        self._recovery_delay = recovery_delay
        self._ttl = ttl
        self.api_args = {'address': self._address,
                         'failover_mode': self._failover_mode,
                         'failover_data': self._failover_data,
                         'monitor': self.monitor.to_json(),
                         'contact_nickname': self._contact_nickname}
        if syslog_probe_fmt:
            self.api_args['syslog_probe_fmt'] = self._syslog_probe_fmt
        if syslog_status_fmt:
            self.api_args['syslog_status_fmt'] = self._syslog_status_fmt
        if recovery_delay:
            self.api_args['recovery_delay'] = self._recovery_delay
        if syslog_facility:
            self.api_args['syslog_facility'] = self._syslog_facility
        if syslog_delivery:
            self.api_args['syslog_delivery'] = self._syslog_delivery
        if syslog_ident:
            self.api_args['syslog_ident'] = self._syslog_ident
        if notify_events:
            self.api_args['notify_events'] = self._notify_events
        if syslog_server:
            self.api_args['syslog_server'] = self._syslog_server
        if syslog_port:
            self.api_args['syslog_port'] = self._syslog_port

        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       self.api_args)
        self._build(response['data'])

    def _build(self, data):
        """Build this object from the data returned in an API response"""
        self._task_id = None
        for key, val in data.items():
            if key == 'monitor':
                self._monitor = HealthMonitor(**val)
            elif key == 'active':
                self._active = Active(val)
            elif key == "task_id" and not val:
                self._task_id = None
            elif key == "task_id":
                self._task_id = Task(val)
            else:
                setattr(self, '_' + key, val)

    def _update(self, api_args):
        """Update this :class:`ActiveFailover`, via the API, with the args in
        api_args
        """
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def task(self):
        """:class:`Task` for most recent system action
        on this :class:`ActiveFailover`."""
        if self._task_id:
            self._task_id.refresh()
        return self._task_id

    @property
    def zone(self):
        """The zone to attach this :class:`ActiveFailover` service to"""
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """The FQDN where this :class:`ActiveFailover` service will be attached
        """
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def active(self):
        """Return whether or not this :class:`ActiveFailover` service is
        active. When setting directly, rather than using activate/deactivate
        valid arguments are 'Y' or True to activate, or 'N' or False to
        deactivate.

        Note: If your service is already active and you try to activate it,
        nothing will happen. And vice versa for deactivation.

        :returns: An :class:`Active` object representing the current state of
            this :class:`ActiveFailover` Service
        """
        self._get()
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
    def address(self):
        """IPv4 Address or FQDN being monitored by this :class:`ActiveFailover`
        service
        """
        return self._address

    @address.setter
    def address(self, value):
        self._address = value
        api_args = {'address': self._address,
                    'failover_mode': self._failover_mode,
                    'failover_data': self._failover_data,
                    'monitor': self.monitor.to_json(),
                    'contact_nickname': self._contact_nickname}
        self._update(api_args)

    @property
    def failover_mode(self):
        """Indicates the target failover resource type."""
        return self._failover_mode

    @failover_mode.setter
    def failover_mode(self, value):
        self._failover_mode = value
        self.api_args['failover_mode'] = self._failover_mode
        self._update(self.api_args)

    @property
    def failover_data(self):
        """The IPv4 Address or CNAME data for the failover target"""
        return self._failover_data

    @failover_data.setter
    def failover_data(self, value):
        self._failover_data = value
        self.api_args['failover_data'] = self._failover_data
        self._update(self.api_args)

    @property
    def monitor(self):
        """The :class:`HealthMonitor` for this :class:`ActiveFailover` service
        """
        return self._monitor

    @monitor.setter
    def monitor(self, value):
        self._monitor = value
        self.api_args['monitor'] = self._monitor.to_json()
        self._update(self.api_args)

    @property
    def contact_nickname(self):
        """Name of contact to receive notifications from this
        :class:`ActiveFailover` service
        """
        return self._contact_nickname

    @contact_nickname.setter
    def contact_nickname(self, value):
        self._contact_nickname = value
        self.api_args['contact_nickname'] = self._contact_nickname
        self._update(self.api_args)

    @property
    def auto_recover(self):
        """Indicates whether this service should restore its original state
        when the source IPs resume online status
        """
        return self._auto_recover

    @auto_recover.setter
    def auto_recover(self, value):
        self._auto_recover = value
        api_args = self.api_args
        api_args['auto_recover'] = self._auto_recover
        self._update(api_args)

    @property
    def notify_events(self):
        """A comma separated list of what events trigger notifications"""
        return self._notify_events

    @notify_events.setter
    def notify_events(self, value):
        for val in value:
            if val not in self.valid_notify_events:
                raise DynectInvalidArgumentError('notify_events', val,
                                                 self.valid_notify_events)
        value = ','.join(value)
        api_args = self.api_args
        api_args['notify_events'] = value
        self._update(api_args)

    def recover(self):
        """Recover this :class:`ActiveFailover` service"""
        api_args = {'recover': 'Y'}
        self._update(api_args)

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
        api_args = self.api_args
        api_args['syslog_server'] = self._syslog_server
        self._update(api_args)

    @property
    def syslog_port(self):
        """The port where the remote syslog server listens"""
        self._get()
        return self._syslog_port

    @syslog_port.setter
    def syslog_port(self, value):
        self._syslog_port = value
        api_args = self.api_args
        api_args['syslog_port'] = self._syslog_port
        self._update(api_args)

    @property
    def syslog_ident(self):
        """The ident to use when sending syslog notifications"""
        self._get()
        return self._syslog_ident

    @syslog_ident.setter
    def syslog_ident(self, value):
        self._syslog_ident = value
        api_args = self.api_args
        api_args['syslog_ident'] = self._syslog_ident
        self._update(api_args)

    @property
    def syslog_facility(self):
        """The syslog facility to use when sending syslog notifications"""
        self._get()
        return self._syslog_facility

    @syslog_facility.setter
    def syslog_facility(self, value):
        self._syslog_facility = value
        api_args = self.api_args
        api_args['syslog_facility'] = self._syslog_facility
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
    def recovery_delay(self):
        self._get()
        return self._recovery_delay

    @recovery_delay.setter
    def recovery_delay(self, value):
        api_args = {'recovery_delay': value}
        self._update(api_args)

    @property
    def ttl(self):
        """Time To Live in seconds of records in the service. Must be less than
        1/2 of the Health Probe's monitoring interval
        """
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        self._ttl = value
        api_args = self.api_args
        api_args['ttl'] = self._ttl
        self._update(api_args)

    def activate(self):
        """Activate this :class:`ActiveFailover` service"""
        api_args = {'activate': True}
        self._update(api_args)

    def deactivate(self):
        """Deactivate this :class:`ActiveFailover` service"""
        api_args = {'deactivate': True}
        self._update(api_args)

    def delete(self):
        """Delete this :class:`ActiveFailover` service from the Dynect System
        """
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<ActiveFailover>: {}').format(self._fqdn)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
