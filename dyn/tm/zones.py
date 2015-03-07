# -*- coding: utf-8 -*-
"""This module contains all Zone related API objects."""
import os
from time import sleep
from datetime import datetime

from .utils import unix_date
from .errors import DynectCreateError, DynectGetError
from .records import RECORD_TYPES
from .session import DynectSession, DNSAPIObject
from .services import (ActiveFailover, DynamicDNS, DNSSEC, TrafficDirector,
                       GSLB, ReverseDNS, RTTM, HTTPRedirect)
from ..core import (IntegerAttribute, StringAttribute, ListAttribute,
                    ImmutableAttribute, ValidatedAttribute)
from ..compat import force_unicode

__author__ = 'jnappi'
__all__ = ['get_all_zones', 'Zone', 'SecondaryZone', 'Node']


def get_all_zones():
    """Accessor function to retrieve a *list* of all
    :class:`~dyn.tm.zones.Zone`'s accessible to a user

    :return: a *list* of :class:`~dyn.tm.zones.Zone`'s
    """
    uri = '/Zone/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get(uri, api_args)
    zones = []
    for zone in response['data']:
        zones.append(Zone(zone['zone'], api=False, **zone))
    return zones


def get_all_secondary_zones():
    """Accessor function to retrieve a *list* of all :class:`SecondaryZone`'s
    accessible to a user

    :return: a *list* of :class:`~dyn.tm.zones.SecondaryZone`'s
    """
    uri = '/Secondary/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get(uri, api_args)
    zones = []
    for zone in response['data']:
        zones.append(SecondaryZone(zone.pop('zone'), api=False, **zone))
    return zones


# noinspection PyUnresolvedReferences
class Zone(DNSAPIObject):
    """A class representing a DynECT Primary Zone"""
    #: Primary Zone URI
    uri = '/Zone/{zone_name}/'

    #: The name of this Zone
    zone = ImmutableAttribute('zone')

    #: Alias to zone
    name = ImmutableAttribute('zone')

    #: The fully qualified domain name of this Zone
    fqdn = ImmutableAttribute('fqdn')

    #: The style of this zone's serial. Valid values are increment, epoch, day,
    #: and minute
    serial_style = ValidatedAttribute('serial_style',
                                      validator=('increment', 'epoch', 'day',
                                                 'minute'))

    #: The current serial of this zone, the format of the serial will be
    #: dependent on the value of serial_style
    serial = IntegerAttribute('serial')

    #: Convenience property for this :class:`Zone`. If a :class:`Zone` is
    #: frozen, the status will read as `'frozen'`, if the :class:`Zones` is not
    #: frozen the status will read as `'active'`. Because the API does not
    #: return information about whether or not a :class:`Zones` is frozen there
    #: will be a few cases where this status will be `None` in order to avoid
    #: guessing what the current status actually is.
    status = StringAttribute('status')

    def __init__(self, name, *args, **kwargs):
        """Create a :class:`Zone` object. Note: When creating a new
            :class:`Zone` if no contact is specified the path to a local zone
            file must be passed to the ``file_name`` param.

        :param name: the name of the zone to create
        :param contact: Administrative contact for this zone
        :param ttl: TTL (in seconds) for records in the zone
        :param serial_style: The style of the zone's serial. Valid values:
            increment, epoch, day, minute
        :param file_name: The path to a valid RFC1035, BIND, or tinydns style
            Master file. Note: this file must be under 1mb in size.
        :param master_ip: The IP of the master server from which to fetch zone
            data for Transferring this :class:`Zone`. Note: This argument is
            required for performing a valid ZoneTransfer operation.
        :param timeout: The time, in minutes, to wait for a zone xfer to
            complete
        """
        self.uri = self.uri.format(zone_name=name)
        self.records, self.services = dict(), dict()
        self._contact = self._ttl = None
        super(Zone, self).__init__(*args, **kwargs)
        self._fqdn = name if name.endswith('.') else '{0}.'.format(name)

    def _post(self, contact=None, ttl=60, serial_style='increment',
              file_name=None, master_ip=None, timeout=None):
        """Create a new :class:`Zone` object on the DynECT System"""
        if contact is None and file_name is None and master_ip is None:
            raise DynectInvalidArgumentError('contact', None)
        if file_name is not None:
            self._post_with_file(file_name)
        elif master_ip is not None:
            self._xfer(master_ip, timeout)
        else:
            # Assign serial style here to force pre-api validation
            self._serial_style = serial_style

            api_args = {'zone': self.name, 'rname': contact, 'ttl': ttl,
                        'serial_style': serial_style}
            response = DynectSession.post(self.uri, api_args)
            self._build(response['data'])
        self._status = 'active'

    def _post_with_file(self, file_name):
        """Create a :class:`Zone` from a RFC1035 style Master file. A ZoneFile
        for BIND or tinydns will also be accepted

        :param file_name: The path to a valid ZoneFile
        """
        full_path = os.path.abspath(file_name)
        file_size = os.path.getsize(full_path)
        if file_size > 1048576:
            raise DynectInvalidArgumentError('Zone File Size', file_size,
                                             'Under 1MB')
        else:
            uri = '/ZoneFile/{0}/'.format(self.name)
            f = open(full_path, 'r')
            content = f.read()
            f.close()
            api_args = {'file': content}
            DynectSession.post(uri, api_args)
            self.__poll_for_get()

    def _xfer(self, master_ip, timeout=None):
        """Create a :class:`Zone` by ZoneTransfer by providing an optional
        master_ip argument.
        """
        uri = '/ZoneTransfer/{0}/'.format(self.name)
        api_args = {'master_ip': master_ip}
        DynectSession.post(uri, api_args)
        time_out = timeout or 10
        count = 0
        while count < time_out:
            response = DynectSession.get(uri)
            if response['status'] == 'running' and response['message'] == '':
                sleep(60)
                count += 1
            else:
                break
        self._get()

    def __poll_for_get(self, n_loops=10, xfer=False, xfer_master_ip=None):
        """For use ONLY by _post_with_file and _xfer. Will wait at MOST
        ``n_loops * 2`` seconds for a successfull GET API response. If no
        successfull get is recieved no error will be raised.
        """
        count = 0
        got = False
        while count < n_loops:
            try:
                self._get()
                got = True
                break
            except DynectGetError:
                sleep(2)
                count += 1
        if not got and xfer:
            uri = '/ZoneTransfer/{0}/'.format(self.name)
            api_args = {}
            if xfer_master_ip is not None:
                api_args['master_ip'] = xfer_master_ip
            response = DynectSession.get(uri, api_args)
            error_labels = ['running', 'waiting', 'failed', 'canceled']
            ok_labels = ['ready', 'unpublished', 'ok']
            if response['data']['status'] in error_labels:
                raise DynectCreateError(response['msgs'])
            elif response['data']['status'] in ok_labels:
                self._get()

    @property
    def __root_soa(self):
        """Return the SOA record associated with this Zone"""
        return self.get_all_records_by_type('SOA')[0]

    @property
    def contact(self):
        """The email address of the primary :class:`Contact` associated with
        this :class:`Zone`
        """
        if self._contact is None:
            self._contact = self.__root_soa.rname
        return self._contact
    @contact.setter
    def contact(self, value):
        self.__root_soa.rname = value

    @property
    def ttl(self):
        """This :class:`Zone`'s default TTL"""
        if self._ttl is None:
            self._ttl = self.__root_soa.ttl
        return self._ttl
    @ttl.setter
    def ttl(self, value):
        self.__root_soa.ttl = value

    def freeze(self):
        """Causes the zone to become frozen. Freezing a zone prevents changes
        to the zone until it is thawed.
        """
        self._update(freeze=True)
        self._status = 'frozen'

    def thaw(self):
        """Causes the zone to become thawed. Thawing a frozen zone allows
        changes to again be made to the zone.
        """
        self._update(thaw=True)
        self._status = 'active'

    def publish(self):
        """Causes all pending changes to become part of the zone. The serial
        number increments based on its serial style and the data is pushed out 
        to the nameservers.
        """
        self._update(publish=True)

    def get_notes(self, offset=None, limit=None):
        """Generates a report containing the Zone Notes for this :class:`Zone`

        :param offset: The starting point at which to retrieve the notes
        :param limit: The maximum number of notes to be retrieved
        :return: A :class:`list` of :class:`dict` containing :class:`Zone`
        Notes
        """
        uri = '/ZoneNoteReport/'
        api_args = {'zone': self.name}
        if offset:
            api_args['offset'] = offset
        if limit:
            api_args['limit'] = limit
        response = DynectSession.post(uri, api_args)
        return response['data']

    def add_record(self, name=None, record_type='A', *args, **kwargs):
        """Adds an a record with the provided name and data to this
        :class:`Zone`

        :param name: The name of the node where this record will be added
        :param record_type: The type of record you would like to add.
            Valid record_type arguments are: 'A', 'AAAA', 'CERT', 'CNAME',
            'DHCID', 'DNAME', 'DNSKEY', 'DS', 'KEY', 'KX', 'LOC', 'IPSECKEY',
            'MX', 'NAPTR', 'PTR', 'PX', 'NSAP', 'RP', 'NS', 'SOA', 'SPF',
            'SRV', and 'TXT'.
        :param args: Non-keyword arguments to pass to the Record constructor
        :param kwargs: Keyword arguments to pass to the Record constructor
        """
        fqdn = name + '.' + self.name + '.' if name else self.name + '.'
        # noinspection PyCallingNonCallable
        rec = RECORD_TYPES[record_type](self.name, fqdn, *args, **kwargs)
        if record_type in self.records:
            self.records[record_type].append(rec)
        else:
            self.records[record_type] = [rec]
        return rec

    def add_service(self, name=None, service_type=None, *args, **kwargs):
        """Add the specified service type to this zone, or to a node under this
        zone

        :param name: The name of the :class:`Node` where this service will be
            attached to or `None` to attach it to the root :class:`Node` of
            this :class:`Zone`
        :param service_type: The type of the service you would like to create.
            Valid service_type arguments are: 'ActiveFailover', 'DDNS',
            'DNSSEC', 'DSF', 'GSLB', 'RDNS', 'RTTM', 'HTTPRedirect'
        :param args: Non-keyword arguments to pass to the Record constructor
        :param kwargs: Keyword arguments to pass to the Record constructor
        """
        constructors = {'ActiveFailover': ActiveFailover,
                        'DDNS': DynamicDNS,
                        'DNSSEC': DNSSEC,
                        'DSF': TrafficDirector,
                        'GSLB': GSLB,
                        'RDNS': ReverseDNS,
                        'RTTM': RTTM,
                        'HTTPRedirect': HTTPRedirect}
        fqdn = self.name + '.'
        if name:
            fqdn = name + '.' + fqdn
        if service_type == 'DNSSEC':
            # noinspection PyCallingNonCallable
            service = constructors[service_type](self.name, *args, **kwargs)
        else:
            # noinspection PyCallingNonCallable
            service = constructors[service_type](self.name, fqdn, *args,
                                                 **kwargs)
        if service_type in self.services:
            self.services[service_type].append(service)
        else:
            self.services[service_type] = [service]
        return service

    def get_node(self, node=None):
        """Returns all DNS Records for that particular node

        :param node: The name of the Node you wish to access, or `None` to get
            the root :class:`Node` of this :class:`Zone`
        """
        if node:
            fqdn = node + '.' + self.name + '.'
        else:
            fqdn = self.name + '.'
        return Node(self.name, fqdn)

    def get_all_records(self):
        """Retrieve a list of all record resources for the specified node and
        zone combination as well as all records from any Base_Record below that
        point on the zone hierarchy

        :return: A :class:`List` of all the :class:`DNSRecord`'s under this
            :class:`Zone`
        """
        self.records = {}
        uri = '/AllRecord/{0}/'.format(self.name)
        if self.fqdn is not None:
            uri += '{0}/'.format(self.fqdn)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        # Strip out empty record_type lists
        record_lists = {label: rec_list for label, rec_list in
                        response['data'].items() if rec_list != []}
        records = {}
        for key, record_list in record_lists.items():
            search = key.split('_')[0].upper()
            constructor = RECORD_TYPES[search]
            list_records = []
            for record in record_list:
                del record['zone']
                del record['fqdn']
                # Unpack rdata
                for r_key, r_val in record['rdata'].items():
                    record[r_key] = r_val
                list_records.append(constructor(self.name, self.fqdn,
                                                api=False, **record))
            records[key] = list_records
        return records

    def get_all_records_by_type(self, record_type):
        """Get a list of all :class:`DNSRecord` of type ``record_type`` which
        are owned by this node.

        :param record_type: The type of :class:`DNSRecord` you wish returned.
            Valid record_type arguments are: 'A', 'AAAA', 'CERT', 'CNAME',
            'DHCID', 'DNAME', 'DNSKEY', 'DS', 'KEY', 'KX', 'LOC', 'IPSECKEY',
            'MX', 'NAPTR', 'PTR', 'PX', 'NSAP', 'RP', 'NS', 'SOA', 'SPF',
            'SRV', and 'TXT'.
        :return: A :class:`List` of :class:`DNSRecord`'s
        """
        names = {'A': 'ARecord', 'AAAA': 'AAAARecord', 'CERT': 'CERTRecord',
                 'CNAME': 'CNAMERecord', 'DHCID': 'DHCIDRecord',
                 'DNAME': 'DNAMERecord', 'DNSKEY': 'DNSKEYRecord',
                 'DS': 'DSRecord', 'KEY': 'KEYRecord', 'KX': 'KXRecord',
                 'LOC': 'LOCRecord', 'IPSECKEY': 'IPSECKEYRecord',
                 'MX': 'MXRecord', 'NAPTR': 'NAPTRRecord', 'PTR': 'PTRRecord',
                 'PX': 'PXRecord', 'NSAP': 'NSAPRecord', 'RP': 'RPRecord',
                 'NS': 'NSRecord', 'SOA': 'SOARecord', 'SPF': 'SPFRecord',
                 'SRV': 'SRVRecord', 'TLSA': 'TLSARecord', 'TXT': 'TXTRecord'}
        constructor = RECORD_TYPES[record_type]
        uri = '/{0}/{1}/{2}/'.format(names[record_type], self.name, self.fqdn)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        records = []
        for record in response['data']:
            del record['fqdn']
            del record['zone']
            # Unpack rdata
            for key, val in record['rdata'].items():
                record[key] = val
            del record['rdata']
            records.append(constructor(self.name, self.fqdn, api=False,
                                       **record))
        return records

    def get_any_records(self):
        """Retrieve a list of all :class:`DNSRecord`'s associated with this
        :class:`Zone`
        """
        if self.fqdn is None:
            return
        api_args = {'detail': 'Y'}
        uri = '/ANYRecord/{0}/{1}/'.format(self.name, self.fqdn)
        response = DynectSession.get(uri, api_args)
        # Strip out empty record_type lists
        record_lists = {label: rec_list for label, rec_list in
                        response['data'].items() if rec_list != []}
        records = {}
        for key, record_list in record_lists.items():
            search = key.split('_')[0].upper()
            constructor = RECORD_TYPES[search]
            list_records = []
            for record in record_list:
                del record['zone']
                del record['fqdn']
                # Unpack rdata
                for r_key, r_val in record['rdata'].items():
                    record[r_key] = r_val
                list_records.append(constructor(self.name, self.fqdn,
                                                api=False, **record))
            records[key] = list_records
        return records

    def get_all_active_failovers(self):
        """Retrieve a list of all :class:`ActiveFailover` services associated
        with this :class:`Zone`

        :return: A :class:`List` of :class:`ActiveFailover` Services
        """
        uri = '/Failover/{0}/'.format(self.name)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        afos = []
        for failover in response['data']:
            del failover['zone']
            del failover['fqdn']
            afos.append(ActiveFailover(self.name, self.fqdn, api=False,
                                       **failover))
        return afos

    def get_all_ddns(self):
        """Retrieve a list of all :class:`DDNS` services associated with this
        :class:`Zone`

        :return: A :class:`List` of :class:`DDNS` Services
        """
        uri = '/DDNS/{0}/'.format(self.name)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        ddnses = []
        for ddns in response['data']:
            del ddns['zone']
            del ddns['fqdn']
            ddnses.append(
                DynamicDNS(self.name, self._fqdn, api=False, **ddns))
        return ddnses

    def get_all_httpredirect(self):
        """Retrieve a list of all :class:`HTTPRedirect` services associated with this
        :class:`Zone`

        :return: A :class:`List` of :class:`HTTPRedirect` Services
        """
        uri = '/HTTPRedirect/{0}/'.format(self._name)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        httpredirs = []
        for httpredir in response['data']:
            del httpredir['zone']
            del httpredir['fqdn']
            httpredirs.append(HTTPRedirect(self._name, self._fqdn, api=False, **httpredir))
        return httpredirs

    def get_all_gslb(self):
        """Retrieve a list of all :class:`GSLB` services associated with this
        :class:`Zone`

        :return: A :class:`List` of :class:`GSLB` Services
        """
        uri = '/GSLB/{0}/'.format(self.name)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        gslbs = []
        for gslb_svc in response['data']:
            del gslb_svc['zone']
            del gslb_svc['fqdn']
            gslbs.append(GSLB(self.name, self._fqdn, api=False, **gslb_svc))
        return gslbs

    def get_all_rdns(self):
        """Retrieve a list of all :class:`ReverseDNS` services associated with
        this :class:`Zone`

        :return: A :class:`List` of :class:`ReverseDNS` Services
        """
        uri = '/IPTrack/{0}/'.format(self.name)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        rdnses = []
        for rdns in response['data']:
            del rdns['zone']
            del rdns['fqdn']
            rdnses.append(
                ReverseDNS(self.name, self._fqdn, api=False, **rdns))
        return rdnses

    def get_all_rttm(self):
        """Retrieve a list of all :class:`RTTM` services associated with this
        :class:`Zone`

        :return: A :class:`List` of :class:`RTTM` Services
        """
        uri = '/RTTM/{0}/'.format(self.name)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        rttms = []
        for rttm_svc in response['data']:
            del rttm_svc['zone']
            del rttm_svc['fqdn']
            rttms.append(RTTM(self.name, self.fqdn, api=False, **rttm_svc))
        return rttms

    def get_qps(self, start_ts, end_ts=None, breakdown=None, hosts=None,
                rrecs=None):
        """Generates a report with information about Queries Per Second (QPS)
        for this zone

        :param start_ts: datetime.datetime instance identifying point in time
            for the QPS report
        :param end_ts: datetime.datetime instance indicating the end of the
            data range for the report. Defaults to datetime.datetime.now()
        :param breakdown: By default, most data is aggregated together.
            Valid values ('hosts', 'rrecs', 'zones').
        :param hosts: List of hosts to include in the report.
        :param rrecs: List of record types to include in report.
        :return: A :class:`str` with CSV data
        """
        end_ts = end_ts or datetime.now()
        api_args = {'start_ts': unix_date(start_ts),
                    'end_ts': unix_date(end_ts),
                    'zones': [self.name]}
        if breakdown is not None:
            api_args['breakdown'] = breakdown
        if hosts is not None:
            api_args['hosts'] = hosts
        if rrecs is not None:
            api_args['rrecs'] = rrecs
        response = DynectSession.post('/QPSReport/', api_args)
        return response['data']

    def __str__(self):
        return force_unicode('<Zone>: {0}').format(self.name)


class SecondaryZone(DNSAPIObject):
    """A class representing DynECT Secondary zones"""
    # Secondary Zone URI
    uri = '/Secondary/{zone_name}/'

    #: The name of this secondary zone
    zone = StringAttribute('zone')

    #: Alias to zone
    name = StringAttribute('zone')

    #: A list of IPv4 or IPv6 addresses of the master nameserver(s) for this
    #: zone
    masters = ListAttribute('masters')

    #: Name of the :class:`~dyn.tm.accounts.Contact` that will receive
    #: notifications for this :class:`~dyn.tm.zones.SecondaryZone`
    contact_nickname = StringAttribute('contact_nickname')

    #: Name of the TSIG key that will be used to sign transfer requests to this
    #: zone's master
    tsig_key_name = StringAttribute('tsig_key_name')

    def __init__(self, zone, *args, **kwargs):
        """Create a :class:`SecondaryZone` object

        :param zone: The name of this secondary zone
        :param masters: A list of IPv4 or IPv6 addresses of the master
            nameserver(s) for this zone.
        :param contact_nickname: Name of the :class:`Contact` that will receive
            notifications for this zone
        :param tsig_key_name: Name of the TSIG key that will be used to sign
            transfer requests to this zone's master
        """
        self.uri = self.uri.format(zone_name=zone)
        self._zone = zone
        super(SecondaryZone, self).__init__(*args, **kwargs)

    def _post(self, masters, contact_nickname=None, tsig_key_name=None):
        """Create a new :class:`SecondaryZone` object on the DynECT System"""
        self._masters = masters
        self._contact_nickname = contact_nickname
        self._tsig_key_name = tsig_key_name
        api_args = {'masters': self._masters}
        if contact_nickname:
            api_args['contact_nickname'] = self._contact_nickname
        if tsig_key_name:
            api_args['tsig_key_name'] = self._tsig_key_name
        response = DynectSession.post(self.uri, api_args)
        self._build(response['data'])

    def activate(self):
        """Activates this secondary zone"""
        self._update(activate=True)

    def deactivate(self):
        """Deactivates this secondary zone"""
        self._update(deactivate=True)

    def retransfer(self):
        """Retransfers this secondary zone from its original provider into
        Dyn's Managed DNS
        """
        self._update(retransfer=True)

    def __str__(self):
        return force_unicode('<SecondaryZone>: {0}').format(self.zone)


class Node(object):
    """Node object. Represents a valid fqdn node within a zone. It should be
    noted that simply creating a :class:`Node` object does not actually create
    anything on the DynECT System. The only way to really create a
    :class:`Node` on the DynECT System is by attaching either a record or a
    service to it.
    """

    def __init__(self, zone, fqdn=None):
        """Create a :class:`Node` object

        :param zone: name of the zone that this Node belongs to
        :param fqdn: the fully qualified domain name of this zone
        """
        super(Node, self).__init__()
        self.zone = zone
        self.fqdn = fqdn or self.zone + '.'
        self.records = self.my_records = {}
        self.services = []

    def add_record(self, record_type='A', *args, **kwargs):
        """Adds an a record with the provided data to this :class:`Node`

        :param record_type: The type of record you would like to add.
            Valid record_type arguments are: 'A', 'AAAA', 'CERT', 'CNAME',
            'DHCID', 'DNAME', 'DNSKEY', 'DS', 'KEY', 'KX', 'LOC', 'IPSECKEY',
            'MX', 'NAPTR', 'PTR', 'PX', 'NSAP', 'RP', 'NS', 'SOA', 'SPF',
            'SRV', and 'TXT'.
        :param args: Non-keyword arguments to pass to the Record constructor
        :param kwargs: Keyword arguments to pass to the Record constructor
        """
        # noinspection PyCallingNonCallable
        rec = RECORD_TYPES[record_type](self.zone, self.fqdn, *args, **kwargs)
        if record_type in self.records:
            self.records[record_type].append(rec)
        else:
            self.records[record_type] = [rec]
        return rec

    def add_service(self, service_type=None, *args, **kwargs):
        """Add the specified service type to this :class:`Node`

        :param service_type: The type of the service you would like to create.
            Valid service_type arguments are: 'ActiveFailover', 'DDNS',
            'DNSSEC', 'DSF', 'GSLB', 'RDNS', 'RTTM', 'HTTPRedirect'
        :param args: Non-keyword arguments to pass to the Record constructor
        :param kwargs: Keyword arguments to pass to the Record constructor
        """
        objects = {'ActiveFailover': ActiveFailover,
                   'DDNS': DynamicDNS,
                   'DNSSEC': DNSSEC,
                   'DSF': TrafficDirector,
                   'GSLB': GSLB,
                   'RDNS': ReverseDNS,
                   'RTTM': RTTM,
                   'HTTPRedirect': HTTPRedirect}

        # noinspection PyCallingNonCallable
        service = objects[service_type](self.zone, self.fqdn, *args, **kwargs)
        self.services.append(service)
        return service

    def get_all_records(self):
        """Retrieve a list of all record resources for the specified node and
        zone combination as well as all records from any Base_Record below that
        point on the zone hierarchy
        """
        self.records = {}
        uri = '/AllRecord/{0}/'.format(self.zone)
        if self.fqdn is not None:
            uri += '{0}/'.format(self.fqdn)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        # Strip out empty record_type lists
        record_lists = {label: rec_list for label, rec_list in
                        response['data'].items() if rec_list != []}
        records = {}
        for key, record_list in record_lists.items():
            search = key.split('_')[0].upper()
            constructor = RECORD_TYPES[search]
            list_records = []
            for record in record_list:
                del record['zone']
                del record['fqdn']
                # Unpack rdata
                for r_key, r_val in record['rdata'].items():
                    record[r_key] = r_val
                list_records.append(
                    constructor(self.zone, self.fqdn, api=False, **record))
            records[key] = list_records
        return records

    def get_all_records_by_type(self, record_type):
        """Get a list of all :class:`DNSRecord` of type ``record_type`` which
        are owned by this node.

        :param record_type: The type of :class:`DNSRecord` you wish returned.
            Valid record_type arguments are: 'A', 'AAAA', 'CERT', 'CNAME',
            'DHCID', 'DNAME', 'DNSKEY', 'DS', 'KEY', 'KX', 'LOC', 'IPSECKEY',
            'MX', 'NAPTR', 'PTR', 'PX', 'NSAP', 'RP', 'NS', 'SOA', 'SPF',
            'SRV', and 'TXT'.
        :return: A list of :class:`DNSRecord`'s
        """
        names = {'A': 'ARecord', 'AAAA': 'AAAARecord', 'CERT': 'CERTRecord',
                 'CNAME': 'CNAMERecord', 'DHCID': 'DHCIDRecord',
                 'DNAME': 'DNAMERecord', 'DNSKEY': 'DNSKEYRecord',
                 'DS': 'DSRecord', 'KEY': 'KEYRecord', 'KX': 'KXRecord',
                 'LOC': 'LOCRecord', 'IPSECKEY': 'IPSECKEYRecord',
                 'MX': 'MXRecord', 'NAPTR': 'NAPTRRecord', 'PTR': 'PTRRecord',
                 'PX': 'PXRecord', 'NSAP': 'NSAPRecord', 'RP': 'RPRecord',
                 'NS': 'NSRecord', 'SOA': 'SOARecord', 'SPF': 'SPFRecord',
                 'SRV': 'SRVRecord', 'TLSA': 'TLSARecord', 'TXT': 'TXTRecord'}
        constructor = RECORD_TYPES[record_type]
        uri = '/{0}/{1}/{2}/'.format(names[record_type], self.zone, self.fqdn)
        api_args = {'detail': 'Y'}
        response = DynectSession.get(uri, api_args)
        records = []
        for record in response['data']:
            del record['fqdn']
            del record['zone']
            # Unpack rdata
            for key, val in record['rdata'].items():
                record[key] = val
            del record['rdata']
            records.append(constructor(self.zone, self.fqdn, **record))
        return records

    def get_any_records(self):
        """Retrieve a list of all recs"""
        if self.fqdn is None:
            return
        api_args = {'detail': 'Y'}
        uri = '/ANYRecord/{0}/{1}/'.format(self.zone, self.fqdn)
        response = DynectSession.get(uri, api_args)
        # Strip out empty record_type lists
        record_lists = {label: rec_list for label, rec_list in
                        response['data'].items() if rec_list != []}
        records = {}
        for key, record_list in record_lists.items():
            search = key.split('_')[0].upper()
            constructor = RECORD_TYPES[search]
            list_records = []
            for record in record_list:
                del record['zone']
                del record['fqdn']
                # Unpack rdata
                for r_key, r_val in record['rdata'].items():
                    record[r_key] = r_val
                list_records.append(
                    constructor(self.zone, self.fqdn, **record))
            records[key] = list_records
        return records

    def delete(self):
        """Delete this node, any records within this node, and any nodes
        underneath this node
        """
        uri = '/Node/{0}/{1}'.format(self.zone, self.fqdn)
        DynectSession.delete(uri)

    def __str__(self):
        return force_unicode('<Node>: {0}').format(self.fqdn)
