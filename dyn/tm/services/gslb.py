# -*- coding: utf-8 -*-
from ._shared import BaseMonitor
from ..utils import APIList
from ..session import DynectSession, DNSAPIObject
from ...core import (APIService, ImmutableAttribute, StringAttribute,
                     ValidatedAttribute, IntegerAttribute, ClassAttribute,
                     ListAttribute)
from ...compat import force_unicode

__author__ = 'jnappi'
__all__ = ['GSLBMonitor', 'GSLBRegionPoolEntry', 'GSLBRegion', 'GSLB']


class GSLBMonitor(BaseMonitor):
    """A :class:`GSLBMonitor` for a GSLB Service"""

    @property
    def uri(self):
        if self.zone is not None and self.fqdn is not None:
            return '/GSLB/{0}/{1}/'.format(self.zone, self.fqdn)
        raise ValueError


class GSLBRegionPoolEntry(DNSAPIObject):
    uri = '/GSLBRegionPoolEntry/{zone}/{fqdn}/{region}/{address}/'
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
        api_args = {'address': self.address, 'label': label, 'weight': weight,
                    'serve_mode': serve_mode}
        api_args = {api_args[k] for k in api_args if api_args[k] is not None}
        response = DynectSession.post(uri, api_args)
        self._build(response['data'])

    def _update(self, **api_args):
        if 'address' in api_args:
            api_args['new_address'] = api_args.pop('address')
        super(GSLBRegionPoolEntry, self)._update(**api_args)

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
        return force_unicode('<GSLBRegionPoolEntry>: {0}'.format(
            self.region_code)
        )


class GSLBRegion(DNSAPIObject):
    uri = '/GSLBRegion/{zone}/{fqdn}/{region}/'
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

    def add_entry(self, address, label=None, weight=None, serve_mode=None):
        """Create a new :class:`GSLBRegionPoolEntry` with the provided
        parameters and add it to this :class:`GSLBRegion`

        :param address: The IP address or FQDN of this Node IP
        :param label: Identifying descriptive information for this
        :param weight: A number in the range of 1-14 controlling the order in
            which this :class:`GSLBRegionPoolEntry` will be served
        :param serve_mode: Sets the behavior of this particular record. Must be
            one of 'always', 'obey', 'remove', 'no'
        :return: The newly created :class:`GSLBRegionPoolEntry`
        """
        new_entry = GSLBRegionPoolEntry(self.zone, self.fqdn, self.region_code,
                                        address, label, weight, serve_mode)
        self._pool.append(new_entry)
        return new_entry

    def _post(self, pool, serve_count=None, failover_mode=None,
              failover_data=None):
        """Create a new :class:`GSLBRegion` on the DynECT System"""
        uri = '/GSLBRegion/{0}/{1}/'.format(self.zone, self.fqdn)
        api_args = {'pool': pool.to_json(), 'serve_count': serve_count,
                    'failover_mode': failover_mode,
                    'failover_data': failover_data}
        api_args = {api_args[k] for k in api_args if api_args[k] is not None}
        response = DynectSession.post(uri, api_args)
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

    @property
    def to_json(self):
        """Convert this :class:`GSLBRegion` to a json blob"""
        output = {'region_code': self.region_code,
                  'pool': [pool.to_json() for pool in self._pool]}
        if self.serve_count:
            output['serve_count'] = self.serve_count
        if self.failover_mode:
            output['failover_mode'] = self.failover_mode
        if self.failover_data:
            output['failover_data'] = self.failover_data
        return output

    def __str__(self):
        return force_unicode('<GSLBRegion>: {0}').format(self.region_code)


class GSLB(APIService, DNSAPIObject):
    """A Global Server Load Balancing (GSLB) service"""
    uri = '/GSLB/{zone}/{fqdn}/'
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
    monitor = ClassAttribute('monitor', class_type=GSLBMonitor)
    contact_nickname = StringAttribute('contact_nickname')

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
                    'region': [r.to_json() for r in region],
                    'auto_recover': auto_recover, 'ttl': ttl,
                    'notify_events': notify_events,
                    'syslog_server': syslog_server, 'syslog_port': syslog_port,
                    'syslog_ident': syslog_ident,
                    'syslog_facility': syslog_facility,
                    'monitor': monitor.to_json()}
        api_args = {api_args[k] for k in api_args if api_args[k] is not None}
        response = DynectSession.post(self.uri, api_args)
        self._build(response['data'])

    def _build(self, data):
        """Private method which builds the objects fields based on the data
        returned by an API call

        :param data: the data from the JSON respnose
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
            if isinstance(monitor, GSLBMonitor):
                api_args['monitor'] = monitor.to_json()
        super(GSLB, self)._update(**api_args)

    def recover(self, address=None):
        """Recover the GSLB service on the designated zone node or a specific
        node IP within the service
        """
        if address:
            api_args = {'recoverip': True, 'address': address}
        else:
            api_args = {'recover': True}
        response = DynectSession.put(self.uri, api_args)
        self._build(response['data'])

    def add_region(self, region_code, pool, serve_count=None,
                   failover_mode=None, failover_data=None):
        """Add a new :class:`GSLBRegion` to this :class:`GSLB` service

        :param region_code: ISO region code of this :class:`GSLBRegion`
        :param pool: The IP Pool list for this :class:`GSLBRegion`
        :param serve_count: How many records will be returned in each DNS
            response
        :param failover_mode: How the :class:`GSLBRegion` should failover. Must
            be one of 'ip', 'cname', 'region', 'global'
        :param failover_data: Dependent upon failover_mode. Must be one of
            'ip', 'cname', 'region', 'global'
        :return: The newly created :class:`GSLBRegion` object
        """
        new_region = GSLBRegion(self.zone, self.fqdn, region_code, pool,
                                serve_count, failover_mode, failover_data)
        self._region.append(new_region)
        return new_region

    def __str__(self):
        return force_unicode('<GSLB>: {0}').format(self.fqdn)
