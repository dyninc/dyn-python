# -*- coding: utf-8 -*-
from ._shared import BaseMonitor
from ..utils import Active, APIList
from ..session import DynectSession
from ...core import (APIService, ImmutableAttribute, StringAttribute,
                     ClassAttribute, IntegerAttribute, ValidatedListAttribute)
from ...compat import force_unicode

__author__ = 'jnappi'
__all__ = ['AFOMonitor', 'ActiveFailover']


class AFOMonitor(BaseMonitor):
    """A health monitor for an :class:`ActiveFailover` service"""

    @property
    def uri(self):
        if self.zone is not None and self.fqdn is not None:
            return '/Failover/{0}/{1}/'.format(self.zone, self.fqdn)
        raise ValueError


class ActiveFailover(APIService):
    """With Active Failover, we monitor your Primary IP.  If a failover event
    is detected, our system auto switches (hot swaps) to your dedicated back-up
    IP
    """
    uri = '/Failover/{zone}/{fqdn}/'
    session_type = DynectSession

    #: The zone that this :class:`ActiveFailover` service is attached to
    zone = ImmutableAttribute('zone')

    #: The fqdn of this :class:`ActiveFailover` service is attached to
    fqdn = ImmutableAttribute('fqdn')

    #: IPv4 Address or FQDN being monitored by this :class:`ActiveFailover`
    address = StringAttribute('address')

    #: The target failover resource type.
    failover_mode = StringAttribute('failover_mode')

    #: The IPv4 Address or CNAME data for the failover target
    failover_data = StringAttribute('failover_data')

    #: The :class:`AFOMonitor` for this :class:`ActiveFailover` service
    monitor = ClassAttribute('monitor', AFOMonitor)

    #: Name of contact to receive notifications for this service
    contact_nickname = StringAttribute('contact_nickname')

    #: Indicates whether this service should restore its original state when
    #: the source IPs resume online status
    auto_recover = StringAttribute('auto_recover')

    #: A comma separated list of what events trigger notifications. Must be one
    #: of 'ip', 'svc', or 'nosrv'
    notify_events = ValidatedListAttribute('notify_events',
                                           validator=('ip', 'svc', 'nosrv'))

    #: The Hostname or IP address of a server to receive syslog notifications
    #: on monitoring events
    syslog_server = StringAttribute('syslog_server')

    #: The port where the remote syslog server listens
    syslog_port = IntegerAttribute('syslog_port')

    #: The ident to use when sending syslog notifications
    syslog_ident = StringAttribute('syslog_ident')

    #: The syslog facility to use when sending syslog notifications
    syslog_facility = StringAttribute('syslog_facility')

    #: TTL in seconds of records in the service. Must be less than 1/2 of the
    #: :class:`AFOMonitor`'s monitoring interval
    ttl = IntegerAttribute('ttl')

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
        :param monitor: The :class:`AFOMonitor` for this
            :class:`ActiveFailover` service
        :param contact_nickname: Name of contact to receive notifications from
            this :class:`ActiveFailover` service
        :param ttl: Time To Live in seconds of records in the service. Must be
            less than 1/2 of the Health Probe's monitoring interval
        """
        self._zone, self._fqdn = zone, fqdn
        self.uri = self.uri.format(zone=zone, fqdn=fqdn)
        super(ActiveFailover, self).__init__(*args, **kwargs)

    def _post(self, address, failover_mode, failover_data, monitor,
              contact_nickname, auto_recover=None, notify_events=None,
              syslog_server=None, syslog_port=None, syslog_ident=None,
              syslog_facility=None, ttl=None):
        """Create a new Active Failover Service on the DynECT System"""
        self._address = address
        self._failover_mode = failover_mode
        self._failover_data = failover_data
        self._monitor = monitor
        self._monitor.zone = self.zone
        self._monitor.fqdn = self.fqdn
        self._contact_nickname = contact_nickname
        self._auto_recover = auto_recover
        self._notify_events = notify_events
        self._syslog_server = syslog_server
        self._syslog_port = syslog_port
        self._syslog_ident = syslog_ident
        self._syslog_facility = syslog_facility
        self._ttl = ttl

        response = DynectSession.post(self.uri, self.api_args)
        self._build(response['data'])

    def _update(self, **api_args):
        if 'monitor' in api_args:
            api_args['monitor'] = api_args['monitor'].to_json()
        if 'notify_events' in api_args:
            api_args['notify_events'] = ', '.join(api_args['notify_events'])
        if 'activate' not in api_args and 'deactivate' not in api_args:
            for key, val in self.api_args.items():
                if key not in api_args:
                    api_args[key] = val
        super(ActiveFailover, self)._update(**api_args)

    def _build(self, data):
        """Build this object from the data returned in an API response"""
        if 'monitor' in data:
            self._monitor = AFOMonitor(**data.pop('monitor'))
        if 'active' in data:
            self._active = Active(data.pop('active'))
        if 'notify_events' in data:
            events = data.pop('notify_events').split(',')
            filtered = [event.strip() for event in events if event.strip()]
            self._notify_events = APIList(DynectSession, 'notify_events',
                                          self.uri, filtered)
        super(ActiveFailover, self)._build(data)

    @property
    def api_args(self):
        """AFO's required API fields are pretty excessive per call, so use a
        property to dynamically generate them on access
        """
        return {'address': self.address, 'failover_mode': self.failover_mode,
                'failover_data': self.failover_data,
                'monitor': self.monitor.to_json(),
                'contact_nickname': self.contact_nickname}

    def __str__(self):
        return force_unicode('<ActiveFailover>: {0}').format(self.fqdn)
