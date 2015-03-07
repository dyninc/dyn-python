# -*- coding: utf-8 -*-
from datetime import datetime

from ._shared import BaseMonitor
from ..utils import APIList, Active, unix_date
from ..session import DynectSession
from ...core import (APIObject, APIService, ImmutableAttribute,
                     StringAttribute, ValidatedAttribute, IntegerAttribute,
                     ClassAttribute, ValidatedListAttribute, ListAttribute)
from ...compat import force_unicode

__author__ = 'jnappi'
__all__ = ['RTTMMonitor', 'RTTMPerformanceMonitor', 'RegionPoolEntry',
           'RTTMRegion', 'RTTM']


class RTTMMonitor(BaseMonitor):
    """A :class:`RTTMMonitor` for RTTM Service."""

    @property
    def uri(self):
        if self.zone is not None and self.fqdn is not None:
            return '/RTTM/{0}/{1}/'.format(self.zone, self.fqdn)
        raise ValueError


class RTTMPerformanceMonitor(RTTMMonitor):
    """A :class:`RTTMPerformanceMonitor` for RTTM Service."""
    def __init__(self, *args, **kwargs):
        super(RTTMPerformanceMonitor, self).__init__(*args, **kwargs)
        self.valid_intervals = (10, 20, 30, 60)

    def _build(self, data):
        super(BaseMonitor, self)._build(data.pop('performance_monitor'))


class RegionPoolEntry(APIObject):
    """Creates a new RTTM service region pool entry in the zone/node
    indicated
    """
    session_type = DynectSession

    zone = ImmutableAttribute('zone')
    fqdn = ImmutableAttribute('fqdn')
    region_code = ImmutableAttribute('region_code')
    address = StringAttribute('address')
    label = StringAttribute('label')
    weight = ValidatedAttribute('weight', validator=range(1, 16))
    serve_mode = ValidatedAttribute('serve_mode',
                                    validator=('always', 'obey', 'remove',
                                               'no'))
    logs = ImmutableAttribute('log')

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
        self._address = address
        super(RegionPoolEntry, self).__init__(address, label, weight,
                                              serve_mode, **kwargs)

    @property
    def uri(self):
        uri = '/RTTMRegionPoolEntry/{zone}/{fqdn}/{region}/{address}/'
        return uri.format(zone=self.zone, fqdn=self.fqdn,
                          region=self.region_code, address=self.address)

    def _get(self):
        args = {'detail': 'Y'}
        response = DynectSession.get(self.uri, args)
        self._build(response['data'])

    def to_json(self):
        """Return a JSON representation of this RegionPoolEntry"""
        json_blob = {'address': self.address, 'label': self.label,
                     'weight': self.weight, 'serve_mode': self.serve_mode}
        return json_blob

    def __str__(self):
        return force_unicode('<RTTMRegionPoolEntry>: {0}').format(self.address)


class RTTMRegion(APIObject):
    """docstring for RTTMRegion"""
    uri = '/RTTMRegion/{zone}/{fqdn}/{region}/'
    session_type = DynectSession
    zone = ImmutableAttribute('zone')
    fqdn = ImmutableAttribute('fqdn')
    region_code = ValidatedAttribute('region_code',
                                     validator=('US West', 'US Central',
                                                'US East', 'Asia', 'EU West',
                                                'EU Central', 'EU East',
                                                'global'))
    autopopulate = StringAttribute('autopopulate')
    ep = IntegerAttribute('ep')
    apmc = IntegerAttribute('apmc')
    epmc = IntegerAttribute('epmc')
    serve_count = IntegerAttribute('serve_count')
    failover_mode = ValidatedAttribute('failover_mode',
                                       validator=('ip', 'cname', 'region',
                                                  'global'))
    failover_data = ValidatedAttribute('failover_data',
                                       validator=('ip', 'cname', 'region',
                                                  'global'))
    pool = ListAttribute('pool')

    def __init__(self, zone, fqdn, region_code, pool, autopopulate=None,
                 ep=None, apmc=None, epmc=None, serve_count=None,
                 failover_mode=None, failover_data=None):
        """Create a :class:`RTTMRegion` object

        :param region_code: Name of the region
        :param pool: The IP Pool list for this region
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
        self.uri = self.uri.format(zone=zone, fqdn=fqdn, region=region_code)
        if len(pool) > 0 and isinstance(pool[0], dict):
            self.pool = []
            for item in pool:
                rpe = RegionPoolEntry(api=False, **item)
                rpe.zone = self.zone
                rpe.fqdn = self.fqdn
                rpe.region_code = self.region_code
                self.pool.append(rpe)
        super(RTTMRegion, self).__init__(zone, fqdn, region_code, pool,
                                         autopopulate, ep, apmc, epmc,
                                         serve_count, failover_mode,
                                         failover_data)

    def _post(self):
        """Create a new :class:`RTTMRegion` on the DynECT System"""
        uri = '/RTTMRegion/{0}/{1}/'.format(self.zone, self.fqdn)
        api_args = {'region_code': self.region_code,
                    'pool': self.pool.to_json()}
        if self.autopopulate:
            api_args['autopopulate'] = self.autopopulate
        if self.ep:
            api_args['ep'] = self.ep
        if self.apmc:
            api_args['apmc'] = self.apmc
        if self.epmc:
            api_args['epmc'] = self.epmc
        if self.serve_count:
            api_args['serve_count'] = self.serve_count
        if self.failover_mode:
            api_args['failover_mode'] = self.failover_mode
        if self.failover_data:
            api_args['failover_data'] = self.failover_data
        response = DynectSession.post(uri, api_args)
        self._build(response['data'])

    def _update(self, api_args):
        """Private Update method to cut back on redundant code"""
        response = DynectSession.put(self.uri, api_args)
        self._build(response['data'])

    def _build(self, data):
        data.pop('pool', None)
        super(RTTMRegion, self)._build(data)

    def to_json(self):
        """Unpack this object and return it as a JSON blob"""
        json_blob = {'region_code': self.region_code,
                     'pool': [entry.to_json() for entry in self.pool]}
        if self.autopopulate:
            json_blob['autopopulate'] = self.autopopulate
        if self.ep:
            json_blob['ep'] = self.ep
        if self.apmc:
            json_blob['apmc'] = self.apmc
        if self.epmc:
            json_blob['epmc'] = self.epmc
        if self.serve_count:
            json_blob['serve_count'] = self.serve_count
        if self.failover_mode:
            json_blob['failover_mode'] = self.failover_mode
        if self.failover_data:
            json_blob['failover_data'] = self.failover_data
        return json_blob

    def __str__(self):
        return force_unicode('<RTTMRegion>: {0}').format(self.region_code)


class RTTM(APIService):
    """Real Time Traffic Management (RTTM) is a DynECT Managed DNS service,
    which monitors all of your endpoints to detect the best-performing ones and
    also auto-populates your regional pools using that information to provide
    you with the lowest latency possible. Differing from GSLB, RTTM collects
    real-time performance data on the load time of each of your endpoints,
    rather than just routing your traffic to manually entered, static
    configurations.
    """
    uri = '/RTTM/{zone}/{fqdn}/'
    session_type = DynectSession

    #: The zone that this :class:`RTTM` service is attached to
    zone = ImmutableAttribute('zone')

    #: The FQDN of the node that this :class:`RTTM` service is attached to
    fqdn = ImmutableAttribute('fqdn')

    #: Indicates whether or not the service should automatically come out of
    #: failover when the IP addresses resume active status or if the service
    #: should remain in failover until manually reset. Must be one of
    #: :const:`True`, :const:`False`, 'Y', or 'N'
    auto_recover = ValidatedAttribute('auto_recover', validator=('Y', 'N'))

    #: Time To Live in seconds of records in the service. Must be less than
    #: 1/2 of the :class:`RTTMMonitor`'s monitoring interval. Must be one of
    #: 30, 60, 150, 300, or 450.
    ttl = ValidatedAttribute('ttl', validator=(30, 60, 150, 300, 450))

    #: A list of the events which trigger notifications. Must be one of 'ip',
    #: 'svc', or 'nosrv'
    notify_events = ValidatedListAttribute('notify_events',
                                           validator=('ip', 'svc', 'nosrv'))

    #: The Hostname or IP address of a server to receive syslog notifications
    #: on monitoring events
    syslog_server = StringAttribute('syslog_server')

    #: The port where the remote syslog server listens for notifications
    syslog_port = IntegerAttribute('syslog_port')

    #: The ident to use when sending syslog notifications
    syslog_ident = StringAttribute('syslog_ident')

    #: The syslog facility to use when sending syslog notifications. Must be
    #: one of kern, user, mail, daemon, auth, syslog, lpr, news, uucp, cron,
    #: authpriv, ftp, ntp, security, console, local0, local1, local2, local3,
    #: local4, local5, local6, or local7
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

    #: The :class:`RTTMMonitor` for this service
    monitor = ClassAttribute('monitor', class_type=RTTMMonitor)

    #: The :class:`RTTMPerformanceMonitor` for this service
    performance_monitor = ClassAttribute('performance_monitor',
                                         class_type=RTTMPerformanceMonitor)

    #: Name of contact to receive notifications
    contact_nickname = StringAttribute('contact_nickname')

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
        :param region: A list of :class:`RTTMRegion`'s
        :param monitor: The :class:`RTTMMonitor` for this service
        :param performance_monitor: The performance monitor for the service
        :param contact_nickname: Name of contact to receive notifications
        """
        self.uri = self.uri.format(zone=zone, fqdn=fqdn)
        self._zone, self._fqdn = zone, fqdn
        super(RTTM, self).__init__(*args, **kwargs)
        self.region.uri = self.uri

    def _post(self, contact_nickname, performance_monitor, region, ttl=None,
              auto_recover=None, notify_events=None, syslog_server=None,
              syslog_port=514, syslog_ident='dynect', syslog_facility='daemon',
              monitor=None):
        """Create a new RTTM Service on the DynECT System"""
        api_args = {'contact_nickname': contact_nickname,
                    'performance_monitor': performance_monitor.to_json(),
                    'region': [reg.to_json() for reg in region], 'ttl': ttl,
                    'auto_recover': auto_recover,
                    'notify_events': notify_events,
                    'syslog_server': syslog_server, 'syslog_port': syslog_port,
                    'syslog_ident': syslog_ident,
                    'syslog_facility': syslog_facility}
        if monitor:
            api_args['monitor'] = monitor.to_json()
        if performance_monitor:
            api_args['performance_monitor'] = performance_monitor.to_json()

        # API expects a CSV string, not a list
        if isinstance(self.notify_events, list):
            api_args['notify_events'] = ', '.join(notify_events)

        api_args = {api_args[k] for k in api_args if api_args[k] is not None}
        resp = DynectSession.post(self.uri, api_args)
        self._build(resp['data'])

    def _build(self, data):
        """Build the neccesary substructures under this :class:`RTTM`"""
        if 'region' in data:
            self.region = APIList(DynectSession.get_session, 'region')
            for region in data.pop('region'):
                code = region.pop('region_code', None)
                pool = region.pop('pool', None)
                status = region.pop('status', None)
                r = RTTMRegion(self.zone, self.fqdn, code, pool, **region)
                r._status = status
                self.region.append(r)
            self.region.uri = self.uri
        if 'monitor' in data:
            if self.monitor is not None:
                self.monitor.zone = self.zone
                self.monitor.fqdn = self.fqdn
            else:
                monitor = data.pop('monitor')
                proto = monitor.pop('protocol', None)
                inter = monitor.pop('interval', None)
                self.monitor = RTTMMonitor(proto, inter, **monitor)
        if 'performance_monitor' in data:
            if self.performance_monitor is not None:
                self.performance_monitor.zone = self.zone
                self.performance_monitor.fqdn = self.fqdn
            else:
                monitor = data.pop('performance_monitor')
                proto = monitor.pop('protocol', None)
                inter = monitor.pop('interval', None)
                self.performance_monitor = RTTMPerformanceMonitor(proto, inter,
                                                                  **monitor)
        if 'notify_events' in data:
            self._notify_events = [item.strip() for item in
                                   data.pop('notify_events').split(',')]
        if 'active' in data:
            self._active = Active(data.pop('active'))
        super(RTTM, self)._build(data)

    def _update(self, **api_args):
        if 'monitor' in api_args:
            api_args['monitor'] = api_args['monitor'].to_json()
        if 'performance_monitor' in api_args:
            pm = api_args['performance_monitor']
            api_args['performance_monitor'] = pm.to_json()
        super(RTTM, self)._update(**api_args)

    def get_rrset_report(self, ts):
        """Generates a report of regional response sets for this RTTM service
        at a given point in time

        :param ts: UNIX timestamp identifying point in time for the log report
        :return: dictionary containing rrset report data
        """
        api_args = {'zone': self.zone, 'fqdn': self.fqdn, 'ts': ts}
        response = DynectSession.post('/RTTMRRSetReport/', api_args)
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
        api_args = {'zone': self.zone, 'fqdn': self.fqdn,
                    'start_ts': unix_date(start_ts),
                    'end_ts': unix_date(end_ts)}
        response = DynectSession.post('/RTTMLogReport/', api_args)
        return response['data']

    def recover(self, recoverip=None, address=None):
        """Recovers the RTTM service or a specific node IP within the service
        """
        api_args = {'recover': True}
        if recoverip:
            api_args['recoverip'] = recoverip
            api_args['address'] = address
        resp = DynectSession.put(self.uri, api_args)
        self._build(resp['data'])

    def __str__(self):
        return force_unicode('<RTTM>: {0}').format(self.fqdn)
