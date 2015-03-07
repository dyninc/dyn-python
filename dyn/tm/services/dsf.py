# -*- coding: utf-8 -*-
"""This module contains wrappers for interfacing with every element of a
Traffic Director (DSF) service.
"""
from ..utils import APIList, Active
from ..errors import DynectInvalidArgumentError
from ..records import *
from ..session import DynectSession, DNSAPIObject
from ...core import (ImmutableAttribute, StringAttribute, IntegerAttribute,
                     ValidatedAttribute, APIDescriptor, BooleanAttribute,
                     ListAttribute)
from ...compat import force_unicode

__author__ = 'jnappi'
__all__ = ['get_all_dsf_services', 'get_all_dsf_monitors', 'DSFARecord',
           'DSFAAAARecord', 'DSFCERTRecord', 'DSFCNAMERecord',
           'DSFDHCIDRecord', 'DSFDNAMERecord', 'DSFDNSKEYRecord',
           'DSFDSRecord', 'DSFKEYRecord', 'DSFKXRecord', 'DSFLOCRecord',
           'DSFIPSECKEYRecord', 'DSFMXRecord', 'DSFNAPTRRecord',
           'DSFPTRRecord', 'DSFPXRecord', 'DSFNSAPRecord', 'DSFRPRecord',
           'DSFNSRecord', 'DSFSPFRecord', 'DSFSRVRecord', 'DSFTXTRecord',
           'DSFRecordSet', 'DSFFailoverChain', 'DSFResponsePool', 'DSFRuleset',
           'DSFMonitorEndpoint', 'DSFMonitor', 'TrafficDirector']


def get_all_dsf_services():
    """:return: A ``list`` of :class:`TrafficDirector` Services"""
    uri = '/DSF/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get(uri, api_args)
    directors = []
    for dsf in response['data']:
        directors.append(TrafficDirector(None, api=False, **dsf))
    return directors


def get_all_dsf_monitors():
    """:return: A ``list`` of :class:`DSFMonitor` Services"""
    uri = '/DSFMonitor/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get(uri, api_args)
    mons = []
    for dsf in response['data']:
        mons.append(DSFMonitor(api=False, **dsf))
    return mons


class _DSFRecord(DNSAPIObject):
    """Base type for all DSF Records"""
    uri = ''
    label = StringAttribute('label')
    weight = IntegerAttribute('weight')
    automation = ValidatedAttribute('automation',
                                    validator=('auto', 'auto_down', 'manual'))
    endpoints = APIDescriptor('endpoints')
    endpoint_up_count = IntegerAttribute('endpoint_up_count')
    eligible = BooleanAttribute('eligible')

    dsf_id = ImmutableAttribute('dsf_id')
    record_set_id = ImmutableAttribute('record_set_id')

    def __init__(self, label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`_DSFRecord` object.

        :param label: A unique label for this :class:`DSFRecord`
        :param weight: Weight for this :class:`DSFRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        if 'api' not in kwargs:
            kwargs['api'] = False
        DNSAPIObject.__init__(self, label=label, weight=weight,
                              automation=automation, endpoints=endpoints,
                              endpoint_up_count=endpoint_up_count,
                              eligible=eligible, **kwargs)

    def _post(self, dsf_id, record_set_id):
        """Create a new :class:`DSFRecord` on the DynECT System

        :param dsf_id: The unique system id for the DSF service associated with
            this :class:`DSFRecord`
        :param record_set_id: The unique system id for the record set
            associated with this :class:`DSFRecord`
        """
        self.uri = '/DSFRecord/{0}/{1}/'.format(dsf_id, record_set_id)
        api_args = {}
        for key, val in self.__dict__.items():
            if val is not None and not hasattr(val, '__call__') and \
                    key.startswith('_'):
                if key != '_dsf_id' and key != '_record_set_id':
                    api_args[key[1:]] = val
        resp = DynectSession.post(self.uri, api_args)
        self._build(resp['data'])

    def _get(self, dsf_id, record_set_id):
        """Get an existing :class:`DSFRecord` from the DynECT System

        :param dsf_id: The unique system id for the DSF service associated with
            this :class:`DSFRecord`
        :param record_set_id: The unique system id for the record set
            associated with this :class:`DSFRecord`
        """
        self.uri = '/DSFRecord/{0}/{1}/'.format(dsf_id, record_set_id)
        response = DynectSession.get(self.uri)
        self._build(response['data'])

    def _build(self, data):
        """Private build method

        :param data: API Response data
        """
        for key, val in data.items():
            if key == 'rdata':
                pass
            else:
                setattr(self, '_' + key, val)

    def to_json(self):
        """Convert this DSFRecord to a json blob"""
        json = {'label': self.label, 'weight': self.weight,
                'automation': self.automation, 'endpoints': self.endpoints,
                'eligible': self.eligible,
                'endpoint_up_count': self.endpoint_up_count}
        json_blob = {x: json[x] for x in json if json[x] is not None}

        if hasattr(self, 'rdata'):
            # We don't need to worry about rdata() throwing an error since if
            # we have a record type, then we know we're a subclass of a
            # DNSRecord
            rdata = self.rdata()
            outer_key = list(rdata.keys())[0]
            inner_data = rdata[outer_key]
            real_data = {x: inner_data[x] for x in inner_data
                         if x not in json_blob and x not in self.__dict__ and
                         x[1:] not in self.__dict__ and
                         inner_data[x] is not None}
            json_blob['rdata'] = {outer_key: real_data}
        return json_blob

    def delete(self):
        """Delete this :class:`DSFRecord`"""
        api_args = {'publish': 'Y'}
        DynectSession.delete(self.uri, api_args)


class DSFARecord(_DSFRecord, ARecord):
    """An :class:`ARecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, address, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFARecord` object

        :param address: IPv4 address for the record
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFARecord`
        :param weight: Weight for this :class:`DSFARecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        ARecord.__init__(self, None, None, address=address, ttl=ttl, api=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFAAAARecord(_DSFRecord, AAAARecord):
    """An :class:`AAAARecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, address, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFAAAARecord` object

        :param address: IPv6 address for the record
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFAAAARecord`
        :param weight: Weight for this :class:`DSFAAAARecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        AAAARecord.__init__(self, None, None, address=address, ttl=ttl,
                            create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFCERTRecord(_DSFRecord, CERTRecord):
    """An :class:`CERTRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, format, tag, algorithm, certificate, ttl=0, label=None,
                 weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFCERTRecord` object

        :param format: Numeric value for the certificate type
        :param tag: Numeric value for the public key certificate
        :param algorithm: Public key algorithm number used to generate the
            certificate
        :param certificate: The public key certificate
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFCERTRecord`
        :param weight: Weight for this :class:`DSFCERTRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        CERTRecord.__init__(self, None, None, format=format, tag=tag,
                            algorithm=algorithm, certificate=certificate,
                            ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFCNAMERecord(_DSFRecord, CNAMERecord):
    """An :class:`CNAMERecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, cname, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFCNAMERecord` object

        :param cname: Hostname
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFCNAMERecord`
        :param weight: Weight for this :class:`DSFCNAMERecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        CNAMERecord.__init__(self, None, None, cname=cname, ttl=ttl,
                             create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFDHCIDRecord(_DSFRecord, DHCIDRecord):
    """An :class:`DHCIDRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, digest, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFDHCIDRecord` object

        :param digest: Base-64 encoded digest of DHCP data
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFDHCIDRecord`
        :param weight: Weight for this :class:`DSFDHCIDRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        DHCIDRecord.__init__(self, None, None, digest=digest, ttl=ttl,
                             create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFDNAMERecord(_DSFRecord, DNAMERecord):
    """An :class:`DNAMERecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, dname, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFDNAMERecord` object

        :param dname: Target Hostname
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFDNAMERecord`
        :param weight: Weight for this :class:`DSFDNAMERecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        DNAMERecord.__init__(self, None, None, dname=dname, ttl=ttl,
                             create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFDNSKEYRecord(_DSFRecord, DNSKEYRecord):
    """An :class:`DNSKEYRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, protocol, public_key, algorithm=5, flags=256, ttl=0,
                 label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFDNSKEYRecord` object

        :param protocol: Numeric value for protocol
        :param public_key: The public key for the DNSSEC signed zone
        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param flags: Numeric value confirming this is the zone's DNSKEY
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFDNSKEYRecord`
        :param weight: Weight for this :class:`DSFDNSKEYRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        DNSKEYRecord.__init__(self, None, None, protocol=protocol,
                              public_key=public_key, algorithm=algorithm,
                              flags=flags, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFDSRecord(_DSFRecord, DSRecord):
    """An :class:`DSRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, digest, keytag, algorithm=5, digtype=1, ttl=0,
                 label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFDSRecord` object

        :param digest: The digest in hexadecimal form. 20-byte,
            hexadecimal-encoded, one-way hash of the DNSKEY record surrounded
            by parenthesis characters '(' & ')'
        :param keytag: The digest mechanism to use to verify the digest
        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param digtype: the digest mechanism to use to verify the digest. Valid
            values are SHA1, SHA256
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFDSRecord`
        :param weight: Weight for this :class:`DSFDSRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        DSRecord.__init__(self, None, None, digest=digest, keytag=keytag,
                          algorithm=algorithm, digtype=digtype, ttl=ttl,
                          create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFKEYRecord(_DSFRecord, KEYRecord):
    """An :class:`KEYRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, algorithm, flags, protocol, public_key, ttl=0,
                 label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFKEYRecord` object

        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param flags: See RFC 2535 for information on KEY record flags
        :param protocol: Numeric identifier of the protocol for this KEY record
        :param public_key: The public key for this record
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFKEYRecord`
        :param weight: Weight for this :class:`DSFKEYRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        KEYRecord.__init__(self, None, None, algorithm=algorithm, flags=flags,
                           protocol=protocol, public_key=public_key, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFKXRecord(_DSFRecord, KXRecord):
    """An :class:`KXRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, exchange, preference, ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFKXRecord` object

        :param exchange: Hostname that will act as the Key Exchanger. The
            hostname must have a :class:`CNAMERecord`, an :class:`ARecord`
            and/or an :class:`AAAARecord` associated with it
        :param preference: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFKXRecord`
        :param weight: Weight for this :class:`DSFKXRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        KXRecord.__init__(self, None, None, exchange=exchange,
                          preference=preference, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFLOCRecord(_DSFRecord, LOCRecord):
    """An :class:`LOCRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, altitude, latitude, longitude, horiz_pre=10000, size=1,
                 vert_pre=10, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFLOCRecord` object

        :param altitude: Measured in meters above sea level
        :param horiz_pre:
        :param latitude: Measured in degrees, minutes, and seconds with N/S
            indicator for North and South
        :param longitude: Measured in degrees, minutes, and seconds with E/W
            indicator for East and West
        :param size:
        :param version:
        :param vert_pre:
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFLOCRecord`
        :param weight: Weight for this :class:`DSFLOCRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        LOCRecord.__init__(self, None, None, altitude=altitude,
                           latitude=latitude, longitude=longitude,
                           horiz_pre=horiz_pre, size=size, vert_pre=vert_pre,
                           ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFIPSECKEYRecord(_DSFRecord, IPSECKEYRecord):
    """An :class:`IPSECKEYRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, precedence, gatetype, algorithm, gateway, public_key,
                 ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFIPSECKEYRecord` object

        :param precedence: Indicates priority among multiple IPSECKEYS. Lower
            numbers are higher priority
        :param gatetype: Gateway type. Must be one of 0, 1, 2, or 3
        :param algorithm: Public key's cryptographic algorithm and format. Must
            be one of 0, 1, or 2
        :param gateway: Gateway used to create IPsec tunnel. Based on Gateway
            type
        :param public_key: Base64 encoding of the public key. Whitespace is
            allowed
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFIPSECKEYRecord`
        :param weight: Weight for this :class:`DSFIPSECKEYRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        IPSECKEYRecord.__init__(self, None, None, precedence=precedence,
                                gatetype=gatetype, algorithm=algorithm,
                                gateway=gateway, public_key=public_key,
                                ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFMXRecord(_DSFRecord, MXRecord):
    """An :class:`MXRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, exchange, preference=10, ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFMXRecord` object

        :param exchange: Hostname of the server responsible for accepting mail
            messages in the zone
        :param preference: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node.
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFMXRecord`
        :param weight: Weight for this :class:`DSFMXRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        MXRecord.__init__(self, None, None, exchange=exchange,
                          preference=preference, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFNAPTRRecord(_DSFRecord, NAPTRRecord):
    """An :class:`NAPTRRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, order, preference, services, regexp, replacement,
                 flags='U', ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFNAPTRRecord` object

        :param order: Indicates the required priority for processing NAPTR
            records. Lowest value is used first.
        :param preference: Indicates priority where two or more NAPTR records
            have identical order values. Lowest value is used first.
        :param services: Always starts with "e2u+" (E.164 to URI). After the
            e2u+ there is a string that defines the type and optionally the
            subtype of the URI where this :class:`NAPTRRecord` points.
        :param regexp: The NAPTR record accepts regular expressions
        :param replacement: The next domain name to find. Only applies if this
            :class:`NAPTRRecord` is non-terminal.
        :param flags: Should be the letter "U". This indicates that this NAPTR
            record terminal
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFNAPTRRecord`
        :param weight: Weight for this :class:`DSFNAPTRRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        NAPTRRecord.__init__(self, None, None, order=order,
                             preference=preference, services=services,
                             regexp=regexp, replacement=replacement,
                             flags=flags, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFPTRRecord(_DSFRecord, PTRRecord):
    """An :class:`PTRRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, ptrdname, ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFPTRRecord` object

        :param ptrdname: The hostname where the IP address should be directed
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFPTRRecord`
        :param weight: Weight for this :class:`DSFPTRRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        PTRRecord.__init__(self, None, None, ptrdname=ptrdname, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFPXRecord(_DSFRecord, PXRecord):
    """An :class:`PXRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, preference, map822, mapx400, ttl=0, label=None,
                 weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFPXRecord` object

        :param preference: Sets priority for processing records of the same
            type. Lowest value is processed first.
        :param map822: mail hostname
        :param mapx400: The domain name derived from the X.400 part of MCGAM
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFPXRecord`
        :param weight: Weight for this :class:`DSFPXRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        PXRecord.__init__(self, None, None, preference=preference,
                          map822=map822, mapx400=mapx400, ttl=ttl,
                          create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFNSAPRecord(_DSFRecord, NSAPRecord):
    """An :class:`NSAPRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, nsap, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFNSAPRecord` object

        :param nsap: Hex-encoded NSAP identifier
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFNSAPRecord`
        :param weight: Weight for this :class:`DSFNSAPRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        NSAPRecord.__init__(self, None, None, nsap=nsap, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFRPRecord(_DSFRecord, RPRecord):
    """An :class:`RPRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, mbox, txtdname, ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFRPRecord` object

        :param mbox: Email address of the Responsible Person.
        :param txtdname: Hostname where a TXT record exists with more
            information on the responsible person.
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFRPRecord`
        :param weight: Weight for this :class:`DSFRPRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        RPRecord.__init__(self, None, None, mbox=mbox, txtdname=txtdname,
                          ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFNSRecord(_DSFRecord, NSRecord):
    """An :class:`NSRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, nsdname, service_class='', ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFNSRecord` object

        :param nsdname: Hostname of the authoritative Nameserver for the zone
        :param service_class: Hostname of the authoritative Nameserver for the
            zone
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFNSRecord`
        :param weight: Weight for this :class:`DSFNSRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        NSRecord.__init__(self, None, None, nsdname=nsdname,
                          service_class=service_class, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFSPFRecord(_DSFRecord, SPFRecord):
    """An :class:`SPFRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, txtdata, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFSPFRecord` object

        :param txtdata: Free text containing SPF record information
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFSPFRecord`
        :param weight: Weight for this :class:`DSFSPFRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        SPFRecord.__init__(self, None, None, txtdata=txtdata, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFSRVRecord(_DSFRecord, SRVRecord):
    """An :class:`SRVRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, port, priority, target, rr_weight, ttl=0, label=None,
                 weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFSRVRecord` object

        :param port: Indicates the port where the service is running
        :param priority: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node
        :param target: The domain name of a host where the service is running
            on the specified port
        :param rr_weight: Secondary prioritizing of records to serve. Records
            of equal priority should be served based on their weight. Higher
            values are served more often
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFSRVRecord`
        :param weight: Weight for this :class:`DSFSRVRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        SRVRecord.__init__(self, None, None, port=port, priority=priority,
                           target=target, weight=rr_weight, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFTXTRecord(_DSFRecord, TXTRecord):
    """An :class:`TXTRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, txtdata, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFTXTRecord` object

        :param txtdata: Plain text data to be served by this
            :class:`DSFTXTRecord`
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFTXTRecord`
        :param weight: Weight for this :class:`DSFTXTRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        TXTRecord.__init__(self, None, None, txtdata=txtdata, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)


class DSFRecordSet(DNSAPIObject):
    """A Collection of DSFRecord Type objects belonging to a
    :class:`DSFFailoverChain`
    """
    records = ListAttribute('records')
    status = ImmutableAttribute('status')

    #: A unique label for this DSF Record Set
    label = StringAttribute('label')

    #: The type of rdata represented by this DFS Record Set
    rdata_class = StringAttribute('rdata_class')

    #: Default TTL for all DSF Record's within this DSF Record SEt
    ttl = IntegerAttribute('ttl')

    #: Defines how eligibility can be changed in response to monitoring. Must
    #: be one of 'auto', 'auto_down', or 'manual'
    automation = ValidatedAttribute('automation',
                                    validator=('auto', 'auto_down', 'manual'))

    #: How many records to serve out of this DSF Record Set
    serve_count = IntegerAttribute('serve_count')

    #: The number of records that must be failing before this DSF Record Set
    #: becomes ineligible
    fail_count = IntegerAttribute('fail_count')

    #: The number of Records that must not be okay before this DSFRecordSet
    #: becomes in trouble.
    trouble_count = IntegerAttribute('trouble_count')

    #: Indicates whether or not this DSFRecordSet can be served.
    eligible = BooleanAttribute('eligible')

    #: The unique DynECT system id of the DSF Monitor attached to this
    #: DSFRecordSet
    dsf_monitor_id = ImmutableAttribute('dsf_monitor_id')

    def __init__(self, rdata_class, label=None, ttl=None, automation=None,
                 serve_count=None, fail_count=None, trouble_count=None,
                 eligible=None, dsf_monitor_id=None, records=None, **kwargs):
        """Create a new :class:`DSFRecordSet` object

        :param rdata_class: The type of rdata represented by this
            :class:`DSFRecordSet`
        :param label: A unique label for this :class:`DSFRecordSet`
        :param ttl: Default TTL for :class:`DSFRecord`'s within this
            :class:`DSFRecordSet`
        :param automation: Defines how eligible can be changed in response to
            monitoring
        :param serve_count: How many Records to serve out of this
            :class:`DSFRecordSet`
        :param fail_count: The number of Records that must not be okay before
            this :class:`DSFRecordSet` becomes ineligible.
        :param trouble_count: The number of Records that must not be okay
            before this :class:`DSFRecordSet` becomes in trouble.
        :param eligible: Indicates whether or not this :class:`DSFRecordSet`
            can be served.
        :param dsf_monitor_id: The unique system id of the DSF Monitor attached
            to this :class:`DSFRecordSet`
        :param records: A list of :class:`DSFRecord`'s within this
            :class:`DSFRecordSet`
        :param kwargs: Used for manipulating additional data to be speicified
            by the creation of other system objects.
        """
        self._rdata_class = rdata_class
        super(DSFRecordSet, self).__init__(rdata_class, label=label, ttl=ttl,
                                           automation=automation,
                                           serve_count=serve_count,
                                           fail_count=fail_count,
                                           trouble_count=trouble_count,
                                           eligible=eligible,
                                           dsf_monitor_id=dsf_monitor_id,
                                           records=records, **kwargs)
        if records is not None and len(records) > 0 and isinstance(records[0],
                                                                   dict):
            self._records = []
            for record in records:
                constructors = {'a': DSFARecord, 'aaaa': DSFAAAARecord,
                                'cert': DSFCERTRecord, 'cname': DSFCNAMERecord,
                                'dhcid': DSFDHCIDRecord,
                                'dname': DSFDNAMERecord,
                                'dnskey': DSFDNSKEYRecord, 'ds': DSFDSRecord,
                                'key': DSFKEYRecord, 'kx': DSFKXRecord,
                                'loc': DSFLOCRecord,
                                'ipseckey': DSFIPSECKEYRecord,
                                'mx': DSFMXRecord, 'naptr': DSFNAPTRRecord,
                                'ptr': DSFPTRRecord, 'px': DSFPXRecord,
                                'nsap': DSFNSAPRecord, 'rp': DSFRPRecord,
                                'ns': DSFNSRecord, 'spf': DSFSPFRecord,
                                'srv': DSFSRVRecord, 'txt': DSFTXTRecord}
                rec_type = record['rdata_class'].lower()
                constructor = constructors[rec_type]
                rdata_key = 'rdata_{0}'.format(rec_type)
                kws = ('ttl', 'label', 'weight', 'automation', 'endpoints',
                       'endpoint_up_count', 'eligible', 'dsf_record_id',
                       'dsf_record_set_id', 'status', 'torpidity')
                for data in record['rdata']:
                    record_data = data['data'][rdata_key]
                    for kw in kws:
                        record_data[kw] = record[kw]
                    if constructor is DSFSRVRecord:
                        record_data['rr_weight'] = record_data.pop('weight')
                    self._records.append(constructor(**record_data))
        else:
            self._records = records or []
        self.uri = self._master_line = self._rdata = self._status = None
        self._service_id = self._dsf_record_set_id = None
        for key, val in kwargs.items():
            if key != 'records':
                setattr(self, '_' + key, val)
        # If dsf_id and dsf_response_pool_id were specified in kwargs
        if self._service_id is not None \
                and self._dsf_record_set_id is not None:
            self.uri = '/DSFRecordSet/{0}/{1}/'.format(self._service_id,
                                                       self._dsf_record_set_id)

    def _post(self, dsf_id):
        """Create a new :class:`DSFRecordSet` on the DynECT System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFRecordSet` is attached to
        """
        self._service_id = dsf_id
        uri = '/DSFRecordSet/{0}/'.format(self._service_id)
        api_args = {}
        for key, val in self.__dict__.items():
            if key == 'records':
                api_args['records'] = [record.to_json() for record in val]
            elif val is not None and not hasattr(val, '__call__') and \
                    key.startswith('_'):
                api_args[key[1:]] = val
        response = DynectSession.post(uri, api_args)
        self._build(response['data'])
        self.uri = '/DSFRecordSet/{0}/{1}/'.format(self._service_id,
                                                   self._dsf_record_set_id)

    def _get(self, dsf_id, dsf_record_set_id):
        """Get an existing :class:`DSFRecordSet` from the DynECT System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFRecordSet` is attached to
        :param dsf_record_set_id: The unique system id of the DSF Record Set
            this :class:`DSFRecordSet` is attached to
        """
        self._service_id = dsf_id
        self._dsf_record_set_id = dsf_record_set_id
        self.uri = '/DSFRecordSet/{0}/{1}/'.format(self._service_id,
                                                   self._dsf_record_set_id)
        response = DynectSession.get(self.uri)
        self._build(response['data'])

    def _build(self, data):
        """Private build method"""
        for key, val in data.items():
            if key != 'records':
                setattr(self, '_' + key, val)

    def to_json(self):
        """Convert this :class:`DSFRecordSet` to a JSON blob"""
        json_blob = {'rdata_class': self._rdata_class,
                     'label': self.label, 'ttl': self.ttl,
                     'automation': self.automation,
                     'serve_count': self.serve_count,
                     'fail_count': self.fail_count,
                     'trouble_count': self.trouble_count,
                     'eligible': self.eligible,
                     'dsf_monitor_id': self.dsf_monitor_id,
                     'records': [rec.to_json() for rec in self.records]}
        return {key: json_blob[key] for key in json_blob if json_blob[key]}

    def delete(self):
        """Delete this :class:`DSFRecordSet` from the Dynect System"""
        api_args = {'publish': 'Y'}
        DynectSession.delete(self.uri, api_args)

    def __str__(self):
        return '<DSFRecordSet ({0})>: {1}'.format(self.rdata_class, self.label)


class DSFFailoverChain(DNSAPIObject):
    uri = '/DSFRecordSetFailoverChain/{0}/{1}/'

    #: A unique label for this DSF Failover Chain
    label = StringAttribute('label')

    #: Indicates whether or not the contained DSF Record Sets are core record
    #: sets
    core = BooleanAttribute('core')

    #: A :const:`list` of :class:`DSFRecordSet`'s for this DSF Failover Chain
    record_sets = ListAttribute('record_sets')

    #: The unique DynECT system id for the response pool that this DSF Failover
    #: Chain belongs to
    dsf_response_pool_id = ImmutableAttribute('dsf_response_pool_id')

    #: The unique system id for the Traffic Director service that this failover
    #: chain belongs to
    dsf_id = ImmutableAttribute('dsf_id')

    def __init__(self, label=None, core=None, record_sets=None, **kwargs):
        """Create a :class:`DSFFailoverChain` object

        :param label: A unique label for this :class:`DSFFailoverChain`
        :param core: Indicates whether or not the contained
            :class:`DSFRecordSets` are core record sets
        :param record_sets: A list of :class:`DSFRecordSet`'s for this
            :class:`DSFFailoverChain`
        """
        self._label = label
        self._core = core
        if isinstance(record_sets, list) and len(record_sets) > 0 and \
                isinstance(record_sets[0], dict):
            # Clear record sets
            self._record_sets = []
            # Create new record set objects
            for record_set in record_sets:
                if 'service_id' in record_set \
                        and record_set['service_id'] == '':
                    record_set['service_id'] = kwargs['service_id']
                self._record_sets.append(DSFRecordSet(api=False, **record_set))
        else:
            self._record_sets = record_sets
        super(DSFFailoverChain, self).__init__(**kwargs)

    def _post(self, dsf_id, dsf_response_pool_id):
        """Create a new :class:`DSFFailoverChain` on the Dynect System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFFailoverChain` is attached to
        :param dsf_response_pool_id: The unique system is of the DSF response
            pool this :class:`DSFFailoverChain` is attached to
        """
        self._dsf_id = dsf_id
        self._dsf_response_pool_id = dsf_response_pool_id
        self.uri = self.uri.format(self.dsf_id, self.dsf_response_pool_id)
        api_args = {'publish': 'Y'}
        if self._label:
            api_args['label'] = self._label
        if self._core:
            api_args['core'] = self._core
        if self._record_sets:
            api_args['record_sets'] = self._record_sets.to_json()
        resp = DynectSession.post(self.uri, api_args)
        self._build(resp['data'])

    def _get(self, dsf_id, dsf_response_pool_id):
        """Retrieve an existing :class:`DSFFailoverChain` from the Dynect
        System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFFailoverChain` is attached to
        :param dsf_response_pool_id: The unique system is of the DSF response
            pool this :class:`DSFFailoverChain` is attached to
        """
        self._dsf_id = dsf_id
        self._dsf_response_pool_id = dsf_response_pool_id
        self.uri = self.uri.format(self.dsf_id, self.dsf_response_pool_id)
        super(DSFFailoverChain, self)._get()

    def _build(self, data):
        if 'record_sets' in data:
            data.pop('record_sets')
        super(DSFFailoverChain, self)._build(data)

    def to_json(self):
        """Convert this :class:`DSFFailoverChain` to JSON"""
        json_blob = {}
        if self._label:
            json_blob['label'] = self._label
        if self._core:
            json_blob['core'] = self._core
        if self.record_sets:
            json_blob['record_sets'] = [rs.to_json() for rs in
                                        self.record_sets]
        return json_blob

    def delete(self):
        """Delete this :class:`DSFFailoverChain` from the Dynect System"""
        api_args = {'publish': 'Y'}
        DynectSession.delete(self.uri, api_args)

    def __str__(self):
        return '<DSFFailoverChain>: {0}'.format(self.label)


class DSFResponsePool(DNSAPIObject):
    uri = '/DSFResponsePool/{0}/{1}/'
    _get_length = 1

    #: A unique label for this DSF Response Pool
    label = StringAttribute('label')

    #: If fewer than this number of core record sets are eligible, status will
    #: be set to 'fail'
    core_set_count = IntegerAttribute('core_set_count')

    #: Indicates whether or not this DSF Response Pool can be served
    eligible = BooleanAttribute('eligible')

    #: Defines how eligibility can be changed in response to monitoring
    automation = StringAttribute('automation')

    #: The unique DynECT system id for the :class:`DSFRuleset` that this
    #: response pool belongs to
    dsf_ruleset_id = ImmutableAttribute('dsf_ruleset_id')

    #: The unique DynECT system id for this DSF Response Pool
    dsf_response_pool_id = ImmutableAttribute('dsf_response_pool_id')

    #: When specified with `dsf_ruleset_id`, indicates the position of the
    #: DSF Response Pool
    index = IntegerAttribute('index')

    #: A :const:`list` of :class:`DSFFailoverChain`'s that are defined for this
    #: DSF Response Pool
    rs_chains = ImmutableAttribute('rs_chains')

    #: The unique DynECT system id for the Traffic Director service that this
    #: DFS Response Pool belongs to
    dsf_id = ImmutableAttribute('dsf_id')

    def __init__(self, label, dsf_id=None, core_set_count=1, eligible=True,
                 automation='auto', dsf_ruleset_id=None, index=None,
                 rs_chains=None, **kwargs):
        """Create a :class:`DSFResponsePool` object

        :param label: A unique label for this :class:`DSFResponsePool`
        :param core_set_count: If fewer than this number of core record sets
            are eligible, status will be set to fail
        :param eligible: Indicates whether or not the :class:`DSFResponsePool`
            can be served
        :param automation: Defines how eligible can be changed in response to
            monitoring
        :param dsf_ruleset_id: Unique system id of the Ruleset this
            :class:`DSFResponsePool` is attached to
        :param index: When specified with dsf_ruleset_id, indicates the
            position of the :class:`DSFResponsePool`
        :param rs_chains: A list of :class:`DSFFailoverChain` that are defined
            for this :class:`DSFResponsePool`
        """
        self._label, self._dsf_id = label, dsf_id
        if dsf_id is None:
            kwargs['api'] = False

        if isinstance(rs_chains, list) and len(rs_chains) > 0 and \
                isinstance(rs_chains[0], dict):
            # Clear Failover Chains
            self._rs_chains = []
            # Create a new FO Chain for each entry returned from API
            for chain in rs_chains:
                self._rs_chains.append(DSFFailoverChain(api=False, **chain))
        else:
            self._rs_chains = rs_chains

        super(DSFResponsePool, self).__init__(core_set_count=core_set_count,
                                              eligible=eligible,
                                              automation=automation,
                                              dsf_ruleset_id=dsf_ruleset_id,
                                              index=index, **kwargs)

    def _post(self):
        """Create a new :class:`DSFResponsePool` on the DynECT System"""
        api_args = {'publish': 'Y', 'label': self._label,
                    'core_set_count': self.core_set_count,
                    'eligible': self.eligible, 'automation': self.automation}
        if self.dsf_ruleset_id:
            api_args['dsf_ruleset_id'] = self.dsf_ruleset_id
        if self.index:
            api_args['index'] = self.index
        if self._rs_chains:
            api_args['rs_chains'] = self._rs_chains
        resp = DynectSession.post(self.uri, api_args)
        self._build(resp['data'])

    def _get(self, dsf_response_pool_id):
        """Get an existing :class:`DSFResponsePool` from the DynECT System

        :param dsf_response_pool_id: the id of this :class:`DSFResponsePool`
        """
        self.uri = self.uri.format(self.dsf_id, dsf_response_pool_id)
        response = DynectSession.get(self.uri)
        self._build(response['data'])

    def _build(self, data):
        if 'rs_chains' in data:
            data.pop('rs_chains')
        super(DSFResponsePool, self)._build(data)
        self.uri = self.uri.format(self.dsf_id, self.dsf_response_pool_id)

    def to_json(self):
        """Convert this :class:`DSFResponsePool` to a JSON blob"""
        rs_json = [rs.to_json() for rs in self._rs_chains]
        json_blob = {'label': self.label, 'eligible': self.eligible,
                     'core_set_count': self.core_set_count,
                     'automation': self.automation, 'rs_chains': rs_json}
        if self.index:
            json_blob['index'] = self.index
        if self.dsf_ruleset_id:
            json_blob['dsf_ruleset_id'] = self.dsf_ruleset_id
        return json_blob

    def delete(self):
        """Delete this :class:`DSFResponsePool` from the DynECT System"""
        api_args = {'publish': 'Y'}
        DynectSession.delete(self.uri, api_args)

    def __str__(self):
        return '<DSFResponsePool>: {0}'.format(self.dsf_response_pool_id)


class DSFRuleset(DNSAPIObject):
    #: A unique label for this DSF Ruleset
    label = StringAttribute('label')

    #: A set of rules describing what traffic is applied to this DSF Ruleset.
    #: Must be one of 'always' or 'geoip'
    criteria_type = ValidatedAttribute('criteria_type',
                                       validator=('always', 'geoip'))

    #: Varied depending on this specified `criteria_type`
    criteria = ListAttribute('criteria')

    #: A :const:`list` of :class:`DSFResponsePool`'s for this DSF Ruleset
    response_pools = ImmutableAttribute('response_pools')

    def __init__(self, label, criteria_type, response_pools, criteria=None,
                 **kwargs):
        """Create a :class:`DSFRuleset` object

        :param label: A unique label for this :class:`DSFRuleset`
        :param criteria_type: A set of rules describing what traffic is applied
            to the :class:`DSFRuleset`
        :param criteria: Varied depending on the specified criteria_type
        :param response_pools: A list of :class:`DSFResponsePool`'s for this
            :class:`DSFRuleset`
        """
        self._label, self._criteria_type = label, criteria_type
        self._criteria = criteria
        if isinstance(response_pools, list) and len(response_pools) > 0 and \
                isinstance(response_pools[0], dict):
            self._response_pools = []
            for pool in response_pools:
                pool = {x: pool[x] for x in pool if x != 'rulesets'}
                self._response_pools.append(DSFResponsePool(api=False, **pool))
            kwargs['api'] = False
        else:
            self._response_pools = response_pools
        self._service_id = self._dsf_ruleset_id = self.uri = None
        super(DSFRuleset, self).__init__(**kwargs)

    def _post(self, dsf_id):
        """Create a new :class:`DSFRuleset` on the DynECT System

        :param dsf_id: the id of the DSF service this :class:`DSFRuleset` is
            attached to
        """
        self._service_id = dsf_id
        uri = '/DSFRuleset/{0}/'.format(self._service_id)
        api_args = {'publish': 'Y', 'label': self._label,
                    'criteria_type': self._criteria_type,
                    'criteria': self._criteria}
        response = DynectSession.post(uri, api_args)
        self._build(response['data'])
        self.uri = '/DSFRuleset/{0}/{1}/'.format(self._service_id,
                                                 self._dsf_ruleset_id)

    def _get(self, dsf_id, dsf_ruleset_id):
        """Get an existing :class:`DSFRuleset` from the DynECT System

        :param dsf_id: the id of the DSF service this :class:`DSFRuleset` is
            attached to
        :param dsf_ruleset_id: The unique system id of this :class:`DSFRuleset`
        """
        self.uri = '/DSFRuleset/{0}/{1}/'.format(dsf_id, dsf_ruleset_id)
        super(DSFRuleset, self)._get()

    def _build(self, data):
        """Pop out unused rs_chains data"""
        if 'rs_chains' in data:
            data.pop('rs_chains')
        super(DSFRuleset, self)._build(data)

    def to_json(self):
        """JSON-ified version of this DSFRuleset Object"""
        pool_json = [pool.to_json() for pool in self._response_pools]
        json_blob = {'label': self._label,
                     'criteria_type': self._criteria_type,
                     'criteria': self._criteria,
                     'response_pools': pool_json}
        return json_blob

    def delete(self):
        """Remove this :class:`DSFRuleset` from it's associated
        :class:`TrafficDirector` Service
        """
        api_args = {'publish': 'Y'}
        DynectSession.delete(self.uri, api_args)

    def __str__(self):
        return '<DSFRuleset>: {0}'.format(self.label)


class DSFMonitorEndpoint(object):
    """An Endpoint object to be passed to a :class:`DSFMonitor`"""

    def __init__(self, address, label, active='Y', site_prefs=None):
        """Create a :class:`DSFMonitorEndpoint` object

        :param address: The address to monitor.
        :param label: A label to identify this :class:`DSFMonitorEndpoint`.
        :param active: Indicates whether or not this
            :class:`DSFMonitorEndpoint` endpoint is active. Must be one of
            True, False, 'Y', or 'N'
        :param site_prefs: A ``list`` of site codes from which this
            :class:`DSFMonitorEndpoint` will be monitored
        """
        self._address = address
        self._label = label
        self._active = Active(active)
        self._site_prefs = site_prefs
        self._monitor = None

    def _update(self, api_args):
        """Update this :class:`DSFMonitorEndpoint` with the provided api_args

        :param api_args: arguments to pass to the API via PUT
        """
        if self._monitor is not None:
            full_list = self._monitor.endpoints
            args_list = []
            for endpoint in full_list:
                if id(endpoint) == id(self):
                    args_list.append(api_args)
                else:
                    args_list.append(endpoint.to_json())
            self._monitor._update(endpoints=args_list)

    def to_json(self):
        """Get the JSON representation of this :class:`DSFMonitorEndpoint`
        object
        """
        json_blob = {'address': self._address, 'label': self._label,
                     'active': str(self._active),
                     'site_prefs': self._site_prefs}
        return {x: json_blob[x] for x in json_blob if json_blob[x] is not None}

    @property
    def active(self):
        """Indicates if this :class:`DSFMonitorEndpoint` is active. When
        updating valid arguments are 'Y' or True to activate, or 'N' or False
        to deactivate.

        :returns: An :class:`Active` object representing the current state of
            this :class:`DSFMonitorEndpoint`
        """
        return self._active

    @active.setter
    def active(self, value):
        valid_input = ('Y', 'N', True, False)
        if value not in valid_input:
            raise DynectInvalidArgumentError('active', value, valid_input)
        api_args = self.to_json()
        api_args['active'] = value
        self._update(api_args)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        api_args = self.to_json()
        api_args['label'] = value
        self._update(api_args)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        api_args = self.to_json()
        api_args['address'] = value
        self._update(api_args)

    @property
    def site_prefs(self):
        return self._site_prefs

    @site_prefs.setter
    def site_prefs(self, value):
        api_args = self.to_json()
        api_args['site_prefs'] = value
        self._update(api_args)


class DSFMonitor(DNSAPIObject):
    """A Monitor for a :class:`TrafficDirector` Service"""
    uri = '/DSFMonitor/'
    _get_length = 1

    #: The unique DynECT system id for this DSF Monitor
    dsf_monitor_id = ImmutableAttribute('dsf_monitor_id')

    #: A unique label used to describe this DSF Monitor
    label = StringAttribute('label')

    #: The protocol for this monitor to use while monitoring. Must be one of
    #: 'HTTP', 'HTTPS', 'PING', 'SMTP', or 'TCP'
    protocol = ValidatedAttribute('protocol',
                                  validator=('HTTP', 'HTTPS', 'PING', 'SMTP',
                                             'TCP'))

    #: The number of responses to determine whether or not the endpoint is
    #: 'up' or 'down'
    response_count = IntegerAttribute('response_count')

    #: How often to this DSF Monitor should monitor
    probe_interval = IntegerAttribute('probe_interval')

    #: How many retries this :class:`DSFMonitor` should attempt on failure
    #: before giving up.
    retries = IntegerAttribute('retries')

    #: Indicates whether or not this DSFMonitor is active
    active = StringAttribute('active')

    #: Additional options pertaining to this DSF Monitor
    options = APIDescriptor('options')

    #: A List of :class:`DSFMonitorEndpoint`'s that are associated with this
    #: DSFMonitor
    endpoints = ListAttribute('endpoints')

    def __init__(self, label=None, monitor_id=None, protocol=None,
                 response_count=None, probe_interval=None, retries=None,
                 active='Y', timeout=None, port=None, path=None, host=None,
                 header=None, expected=None, endpoints=None):
        """

        :param label:
        :param monitor_id:
        :param protocol:
        :param response_count:
        :param probe_interval:
        :param retries:
        :param active:
        :param timeout:
        :param port:
        :param path:
        :param host:
        :param header:
        :param expected:
        :param endpoints:
        :return:
        """
        if monitor_id is not None:
            super(DSFMonitor, self).__init__(monitor_id=monitor_id)
        else:
            self._monitor_id = None
            super(DSFMonitor, self).__init__(label=label, protocol=protocol,
                                             response_count=response_count,
                                             probe_interval=probe_interval,
                                             retries=retries, active=active,
                                             timeout=timeout, port=port,
                                             path=path,
                                             host=host, header=header,
                                             expected=expected,
                                             endpoints=endpoints)

    def _get(self, monitor_id):
        """Get an existing :class:`DSFMonitor` from the DynECT System"""
        self.uri = '/DSFMonitor/{0}/'.format(monitor_id)
        super(DSFMonitor, self)._get()

    def _post(self, label, protocol, response_count, probe_interval, retries,
              active='Y', timeout=None, port=None, path=None, host=None,
              header=None, expected=None, endpoints=None):
        """Create a new :class:`DSFMonitor` on the DynECT System"""
        self._active = Active(active)
        self._options = {}
        if timeout:
            self._options['timeout'] = timeout
        if port:
            self._options['port'] = port
        if path:
            self._options['path'] = path
        if host:
            self._options['host'] = host
        if header:
            self._options['header'] = header
        if expected:
            self._options['expected'] = expected
        api_args = {'label': label, 'protocol': protocol,
                    'response_count': response_count,
                    'probe_interval': probe_interval,
                    'retries': retries, 'active': str(self._active),
                    'options': self._options}

        if self.endpoints is None and endpoints is not None:
            self._endpoints = endpoints

        if self.endpoints is not None:
            api_args['endpoints'] = [x.to_json() for x in self.endpoints]

        response = DynectSession.post(self.uri, api_args)
        self._build(response['data'])

    def _build(self, data):
        """Update this object based on the information passed in via data

        :param data: The ``['data']`` field from an API JSON response
        """
        if 'endpoints' in data:
            endpoints = data.pop('endpoints')
            self._endpoints = []
            for endpoint in endpoints:
                ep = DSFMonitorEndpoint(**endpoint)
                ep._monitor = self
                self._endpoints.append(ep)
        if 'options' in data:
            options = data.pop('options')
            for key, val in options.items():
                data[key] = val
        if 'active' in data:
            self._active = Active(data.pop('active'))
        super(DSFMonitor, self)._build(data)
        self.uri = '/DSFMonitor/{0}/'.format(self.dsf_monitor_id)

    def __str__(self):
        return '<DSFMonitor>: {0}'.format(self.dsf_monitor_id)


class TrafficDirector(DNSAPIObject):
    """Traffic Director is a DNS based traffic routing and load balancing
    service that is Geolocation aware and can support failover by monitoring
    endpoints.
    """
    uri = '/DSF/'
    _get_length = 1

    #: The unique DynECT system id for this Traffic Director service
    service_id = ImmutableAttribute('service_id')

    #: A unique label describing this Traffic Director service
    label = StringAttribute('label')

    #: The default TTL to be used across this service
    ttl = IntegerAttribute('ttl')

    #: A list of :class:`DSFRulesets` that are defined for this service
    rulesets = ListAttribute('rulesets')

    def __init__(self, *args, **kwargs):
        """Create a :class:`TrafficDirector` object

        :param label: A unique label for this :class:`TrafficDirector` service
        :param ttl: The default TTL to be used across this service
        :param publish: If Y, service will be published on creation
        :param nodes: A list of zone, FQDN pairs in a hash that are to be
            linked to this :class:`TrafficDirector` service:
        :param notifiers: A list of names of notifiers associated with this
            :class:`TrafficDirector` service
        :param rulesets: A list of :class:`DSFRulesets` that are defined for
            this :class:`TrafficDirector` service
        """
        self._notifiers = APIList(DynectSession.get_session, 'notifiers')
        self._nodes = APIList(DynectSession.get_session, 'nodes')
        self._rulesets = APIList(DynectSession.get_session, 'rulesets')
        self._notifiers.uri = self._nodes.uri = self._rulesets.uri = self.uri
        super(TrafficDirector, self).__init__(*args, **kwargs)

        self.uri = '/DSF/{service_id}'.format(service_id=self.service_id)
        self._notifiers.uri = self._nodes.uri = self._rulesets.uri = self.uri

    def _post(self, label, ttl=None, publish='Y', nodes=None, notifiers=None,
              rulesets=None):
        """Create a new :class:`TrafficDirector` on the DynECT System"""
        uri = '/DSF/'
        api_args = {'label': label, 'publish': publish}
        if ttl:
            api_args['ttl'] = ttl
        if nodes:
            api_args['nodes'] = nodes
        if notifiers:
            if isinstance(notifiers[0], dict):
                api_args['notifiers'] = notifiers
            else:  # notifiers is a list of Notifier objects
                api_args['notifiers'] = [{'notifier_id': n.notifier_id} for n
                                         in notifiers]
        if rulesets:
            api_args['rulesets'] = [rule.to_json() for rule in rulesets]
        response = DynectSession.post(uri, api_args)
        self.uri = '/DSF/{0}/'.format(response['data']['service_id'])
        self._build(response['data'])

    def _build(self, data):
        if 'notifiers' in data:
            self._notifiers = APIList(DynectSession.get_session, 'notifiers',
                                      None, data.pop('notifiers'))
        if 'rulesets' in data:
            self._rulesets = APIList(DynectSession.get_session, 'rulesets')
            self._rulesets.uri = None
            # For each Ruleset returned, create a new DSFRuleset object
            for ruleset in data.pop('rulesets'):
                for pool in ruleset.get('response_pools', []):
                    pool['dsf_id'] = self.service_id
                self._rulesets.append(DSFRuleset(**ruleset))
        if 'nodes' in data:
            self._nodes = APIList(DynectSession.get_session, 'nodes', None,
                                  data.pop('nodes'))
        self._notifiers.uri = self._nodes.uri = self._rulesets.uri = self.uri
        super(TrafficDirector, self)._build(data)

    def _get(self, service_id):
        """Get an existing :class:`TrafficDirector` from the DynECT System"""
        self.uri = '/DSF/{0}/'.format(service_id)
        api_args = {'pending_changes': 'Y'}
        resp = DynectSession.get(self.uri, api_args)
        self._build(resp['data'])

    def revert_changes(self):
        """Clears the changeset for this service and reverts all non-published
        changes to their original state
        """
        self._update(revert=True)

    def add_notifier(self, notifier_id, publish='Y'):
        """Links the Notifier with the specified id to this Traffic Director
        service
        """
        self._update(add_notifier=True, notifier_id=notifier_id,
                     publish=publish)

    def remove_orphans(self):
        """Remove Record Set Chains which are no longer referenced by a
        :class:`DSFResponsePool`
        """
        self._update(remove_orphans='Y')

    def publish(self):
        """Publish any pending changesets for this service"""
        self._update(publish='Y')

    @property
    def records(self):
        """A list of this :class:`TrafficDirector` Services' DSFRecords"""
        return [record for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains
                for record_set in rs_chains.record_sets
                for record in record_set.records]

    @property
    def record_sets(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFRecordSet`'s
        """
        return [record_set for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains
                for record_set in rs_chains.record_sets]

    @property
    def response_pools(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFResponsePool`'s
        """
        return [response_pool for ruleset in self._rulesets
                for response_pool in ruleset.response_pools]

    @property
    def rs_chains(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFFailoverChain`'s
        """
        return [rs_chains for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains]

    def __str__(self):
        return force_unicode('<TrafficDirector>: {0}').format(self.service_id)
