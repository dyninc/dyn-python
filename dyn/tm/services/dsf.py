# -*- coding: utf-8 -*-
"""This module contains wrappers for interfacing with every element of a Traffic
Director (DSF) service.
"""
import dyn.tm.zones
from ..utils import APIList, Active
from ..errors import DynectInvalidArgumentError
from ..records import *
from ..session import DynectSession
from ...compat import force_unicode


__author__ = 'jnappi'
__all__ = ['get_all_dsf_services', 'get_all_dsf_monitors', 'DSFARecord',
           'DSFAAAARecord', 'DSFALIASRecord', 'DSFCERTRecord', 'DSFCNAMERecord',
           'DSFDHCIDRecord', 'DSFDNAMERecord', 'DSFDNSKEYRecord', 'DSFDSRecord',
           'DSFKEYRecord', 'DSFKXRecord', 'DSFLOCRecord', 'DSFIPSECKEYRecord',
           'DSFMXRecord', 'DSFNAPTRRecord', 'DSFPTRRecord', 'DSFPXRecord',
           'DSFNSAPRecord', 'DSFRPRecord', 'DSFNSRecord', 'DSFSPFRecord',
           'DSFSRVRecord', 'DSFTXTRecord', 'DSFRecordSet', 'DSFFailoverChain',
           'DSFResponsePool', 'DSFRuleset', 'DSFMonitorEndpoint', 'DSFMonitor',
           'TrafficDirector']


def get_all_dsf_services():
    """:return: A ``list`` of :class:`TrafficDirector` Services"""
    uri = '/DSF/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    directors = []
    for dsf in response['data']:
        directors.append(TrafficDirector(None, api=False, **dsf))
    return directors


def get_all_dsf_monitors():
    """:return: A ``list`` of :class:`DSFMonitor` Services"""
    uri = '/DSFMonitor/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    mons = []
    for dsf in response['data']:
        mons.append(DSFMonitor(api=False, **dsf))
    return mons


class _DSFRecord(object):
    """docstring for _DSFRecord"""
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
        self.valid_automation = ('auto', 'auto_down', 'manual')
        self._label = label
        self._weight = weight
        if automation not in self.valid_automation:
            raise DynectInvalidArgumentError('automation', automation,
                                             self.valid_automation)
        self._automation = automation
        self._endpoints = endpoints
        self._endpoint_up_count = endpoint_up_count
        self._eligible = eligible
        self._dsf_id = self._record_set_id = self.uri = None
        for key, val in kwargs.items():
            setattr(self, '_' + key, val)

    def _post(self, dsf_id, record_set_id):
        """Create a new :class:`DSFRecord` on the DynECT System

        :param dsf_id: The unique system id for the DSF service associated with
            this :class:`DSFRecord`
        :param record_set_id: The unique system id for the record set associated
            with this :class:`DSFRecord`
        """
        self._dsf_id = dsf_id
        self._record_set_id = record_set_id
        self.uri = '/DSFRecord/{}/{}/'.format(self._dsf_id, self._record_set_id)
        api_args = {}
        for key, val in self.__dict__.items():
            if val is not None and not hasattr(val, '__call__') and \
                    key.startswith('_'):
                if key != '_dsf_id' and key != '_record_set_id':
                    api_args[key[1:]] = val
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _get(self, dsf_id, record_set_id):
        """Get an existing :class:`DSFRecord` from the DynECT System

        :param dsf_id: The unique system id for the DSF service associated with
            this :class:`DSFRecord`
        :param record_set_id: The unique system id for the record set associated
            with this :class:`DSFRecord`
        """
        self._dsf_id = dsf_id
        self._record_set_id = record_set_id
        self.uri = '/DSFRecord/{}/{}/'.format(self._dsf_id, self._record_set_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
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

    @property
    def dsf_id(self):
        """The unique system id for the DSF service associated with this
        :class:`DSFRecord`
        """
        return self._dsf_id
    @dsf_id.setter
    def dsf_id(self, value):
        pass

    @property
    def record_set_id(self):
        """The unique system id for the record set associated with this
        :class:`DSFRecord`
        """
        return self._record_set_id
    @record_set_id.setter
    def record_set_id(self, value):
        pass

    @property
    def label(self):
        """A unique label for this :class:`DSFRecord`"""
        return self._label
    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def weight(self):
        """Weight for this :class:`DSFRecord`"""
        return self._weight
    @weight.setter
    def weight(self, value):
        self._weight = value
        api_args = {'weight': self._weight}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def automation(self):
        """Defines how eligible can be changed in response to monitoring. Must
        be one of 'auto', 'auto_down', or 'manual'
        """
        return self._automation
    @automation.setter
    def automation(self, value):
        self._automation = value
        api_args = {'automation': self._automation}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def endpoints(self):
        """Endpoints are used to determine status, torpidity, and eligible in
        response to monitor data
        """
        return self._endpoints
    @endpoints.setter
    def endpoints(self, value):
        self._endpoints = value
        api_args = {'endpoints': self._endpoints}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def endpoint_up_count(self):
        """Number of endpoints that must be up for the Record status to be 'up'
        """
        return self._endpoint_up_count
    @endpoint_up_count.setter
    def endpoint_up_count(self, value):
        self._endpoint_up_count = value
        api_args = {'endpoint_up_count': self._endpoint_up_count}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def eligible(self):
        """Indicates whether or not the Record can be served"""
        return self._eligible
    @eligible.setter
    def eligible(self, value):
        self._eligible = value
        api_args = {'eligible': self._eligible}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def to_json(self):
        """Convert this DSFRecord to a json blob"""
        json = {'label': self._label, 'weight': self._weight,
                'automation': self._automation, 'endpoints': self._endpoints,
                'eligible': self._eligible,
                'endpoint_up_count': self._endpoint_up_count}
        json_blob = {x: json[x] for x in json if json[x] is not None}
        if hasattr(self, '_record_type'):
            # label = self._record_type.split('Record')[0].lower() + '_rdata'
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
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


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
        ARecord.__init__(self, None, None, address=address, ttl=ttl,
                         create=False)
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


class DSFALIASRecord(_DSFRecord, ALIASRecord):
    """An :class:`AliasRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """
    def __init__(self, alias, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFALIASRecord` object

        :param alias: alias target name
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFALIASRecord`
        :param weight: Weight for this :class:`DSFALIASRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        ALIASRecord.__init__(self, None, None, alias=alias, ttl=ttl,
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
    """An :class:`CNAMERecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
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
    """An :class:`DHCIDRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
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
    """An :class:`DNAMERecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
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
                 ttl=0, label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
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
                                gateway=gateway, public_key=public_key, ttl=ttl,
                                create=False)
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
    def __init__(self, ptrdname, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
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
    def __init__(self, preference, map822, mapx400, ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
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
                          map822=map822, mapx400=mapx400, ttl=ttl, create=False)
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
        :param rr_weight: Secondary prioritizing of records to serve. Records of
            equal priority should be served based on their weight. Higher values
            are served more often
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


class DSFRecordSet(object):
    """A Collection of DSFRecord Type objects belonging to a
    :class:`DSFFailoverChain`
    """
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
        :param trouble_count: The number of Records that must not be okay before
            this :class:`DSFRecordSet` becomes in trouble.
        :param eligible: Indicates whether or not this :class:`DSFRecordSet` can
            be served.
        :param dsf_monitor_id: The unique system id of the DSF Monitor attached
            to this :class:`DSFRecordSet`
        :param records: A list of :class:`DSFRecord`'s within this
            :class:`DSFRecordSet`
        :param kwargs: Used for manipulating additional data to be speicified
            by the creation of other system objects.
        """
        super(DSFRecordSet, self).__init__()
        self._label = label
        self._rdata_class = rdata_class
        self._ttl = ttl
        self._automation = automation
        self._serve_count = serve_count
        self._fail_count = fail_count
        self._trouble_count = trouble_count
        self._eligible = eligible
        self._dsf_monitor_id = dsf_monitor_id
        if records is not None and len(records) > 0 and isinstance(records[0],
                                                                   dict):
            self._records = []
            for record in records:
                constructors = {'a': DSFARecord, 'aaaa': DSFAAAARecord,
                                'alias': DSFALIASRecord, 'cert': DSFCERTRecord,
                                'cname': DSFCNAMERecord, 'dhcid': DSFDHCIDRecord,
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
                rdata_key = 'rdata_{}'.format(rec_type)
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
        if self._service_id is not None and self._dsf_record_set_id is not None:
            self.uri = '/DSFRecordSet/{}/{}/'.format(self._service_id,
                                                     self._dsf_record_set_id)

    def _post(self, dsf_id):
        """Create a new :class:`DSFRecordSet` on the DynECT System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFRecordSet` is attached to
        """
        self._service_id = dsf_id
        uri = '/DSFRecordSet/{}/'.format(self._service_id)
        api_args = {}
        for key, val in self.__dict__.items():
            if key == 'records':
                api_args['records'] = [record.to_json() for record in val]
            elif val is not None and not hasattr(val, '__call__') and \
                    key.startswith('_'):
                api_args[key[1:]] = val
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])
        self.uri = '/DSFRecordSet/{}/{}/'.format(self._service_id,
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
        self.uri = '/DSFRecordSet/{}/{}/'.format(self._service_id,
                                                 self._dsf_record_set_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Private build method"""
        for key, val in data.items():
            if key != 'records':
                setattr(self, '_' + key, val)

    @property
    def records(self):
        """The list of DSFRecord types that are stored in this
        :class:`DSFRecordSet`
        """
        return self._records
    @records.setter
    def records(self, value):
        pass

    @property
    def status(self):
        """The current status of this :class:`DSFRecordSet`"""
        self._get(self._service_id, self._dsf_record_set_id)
        return self._status
    @status.setter
    def status(self, value):
        pass

    @property
    def label(self):
        """A unique label for this :class:`DSFRecordSet`"""
        return self._label
    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def rdata_class(self):
        """The rdata property is a read-only attribute"""
        return self._rdata_class
    @rdata_class.setter
    def rdata_class(self, value):
        pass

    @property
    def ttl(self):
        """Default TTL for :class:`DSFRecord`'s within this
            :class:`DSFRecordSet`"""
        return self._ttl
    @ttl.setter
    def ttl(self, value):
        self._ttl = value
        api_args = {'ttl': self._ttl}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def automation(self):
        """Defines how eligible can be changed in response to monitoring"""
        return self._automation
    @automation.setter
    def automation(self, value):
        self._automation = value
        api_args = {'automation': self._automation}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def serve_count(self):
        """How many Records to serve out of this :class:`DSFRecordSet`"""
        return self._serve_count
    @serve_count.setter
    def serve_count(self, value):
        self._serve_count = value
        api_args = {'serve_count': self._serve_count}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def fail_count(self):
        """The number of Records that must not be okay before this
        :class:`DSFRecordSet` becomes ineligible.
        """
        return self._fail_count
    @fail_count.setter
    def fail_count(self, value):
        self._fail_count = value
        api_args = {'fail_count': self._fail_count}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def trouble_count(self):
        """The number of Records that must not be okay before this
        :class:`DSFRecordSet` becomes in trouble.
        """
        return self._trouble_count
    @trouble_count.setter
    def trouble_count(self, value):
        self._trouble_count = value
        api_args = {'trouble_count': self._trouble_count}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def eligible(self):
        """Indicates whether or not this :class:`DSFRecordSet` can be served."""
        return self._eligible
    @eligible.setter
    def eligible(self, value):
        self._eligible = value
        api_args = {'eligible': self._eligible}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def dsf_monitor_id(self):
        """The unique system id of the DSF Monitor attached to this
        :class:`DSFRecordSet`
        """
        return self._dsf_monitor_id
    @dsf_monitor_id.setter
    def dsf_monitor_id(self, value):
        self._dsf_monitor_id = value
        api_args = {'dsf_monitor_id': self._dsf_monitor_id}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def to_json(self):
        """Convert this :class:`DSFRecordSet` to a JSON blob"""
        json_blob = {'rdata_class': self._rdata_class}
        if self._label:
            json_blob['label'] = self._label
        if self._ttl:
            json_blob['ttl'] = self._ttl
        if self._automation:
            json_blob['automation'] = self._automation
        if self._serve_count:
            json_blob['serve_count'] = self._serve_count
        if self._fail_count:
            json_blob['fail_count'] = self._fail_count
        if self._trouble_count:
            json_blob['trouble_count'] = self._trouble_count
        if self._eligible:
            json_blob['eligible'] = self._eligible
        if self._dsf_monitor_id:
            json_blob['dsf_monitor_id'] = self._dsf_monitor_id
        if self._records:
            json_blob['records'] = [rec.to_json() for rec in self._records]
        else:
            json_blob['records'] = []
        return json_blob

    def delete(self):
        """Delete this :class:`DSFRecordSet` from the Dynect System"""
        api_args = {'publish': 'Y'}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFFailoverChain(object):
    """docstring for DSFFailoverChain"""
    def __init__(self, label=None, core=None, record_sets=None, **kwargs):
        """Create a :class:`DSFFailoverChain` object

        :param label: A unique label for this :class:`DSFFailoverChain`
        :param core: Indicates whether or not the contained
            :class:`DSFRecordSets` are core record sets
        :param record_sets: A list of :class:`DSFRecordSet`'s for this
            :class:`DSFFailoverChain`
        """
        super(DSFFailoverChain, self).__init__()
        self._label = label
        self._core = core
        if isinstance(record_sets, list) and len(record_sets) > 0 and \
                isinstance(record_sets[0], dict):
            # Clear record sets
            self._record_sets = []
            # Create new record set objects
            for record_set in record_sets:
                if 'service_id' in record_set and \
                                record_set['service_id'] == '':
                    record_set['service_id'] = kwargs['service_id']
                self._record_sets.append(DSFRecordSet(**record_set))
        else:
            self._record_sets = record_sets
        self._dsf_id = self._dsf_response_pool_id = self.uri = None
        for key, val in kwargs.items():
            setattr(self, '_' + key, val)
        # If dsf_id and dsf_response_pool_id were specified in kwargs
        if self._dsf_id is not None and self._dsf_response_pool_id is not None:
            r_pid = self._dsf_response_pool_id
            self.uri = '/DSFRecordSetFailoverChain/{}/{}/'.format(self._dsf_id,
                                                                  r_pid)

    def _post(self, dsf_id, dsf_response_pool_id):
        """Create a new :class:`DSFFailoverChain` on the Dynect System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFFailoverChain` is attached to
        :param dsf_response_pool_id: The unique system is of the DSF response
            pool this :class:`DSFFailoverChain` is attached to
        """
        self._dsf_id = dsf_id
        self._dsf_response_pool_id = dsf_response_pool_id
        self.uri = '/DSFRecordSetFailoverChain/{}/{}/'.format(self._dsf_id,
                                                              self._dsf_response_pool_id)
        api_args = {'publish': 'Y'}
        if self._label:
            api_args['label'] = self._label
        if self._core:
            api_args['core'] = self._core
        if self._record_sets:
            api_args['record_sets'] = self._record_sets.to_json()
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    def _get(self, dsf_id, dsf_response_pool_id):
        """Retrieve an existing :class:`DSFFailoverChain` from the Dynect System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFFailoverChain` is attached to
        :param dsf_response_pool_id: The unique system is of the DSF response
            pool this :class:`DSFFailoverChain` is attached to
        """
        self._dsf_id = dsf_id
        self._dsf_response_pool_id = dsf_response_pool_id
        self.uri = '/DSFRecordSetFailoverChain/{}/{}/'.format(self._dsf_id,
                                                              self._dsf_response_pool_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def label(self):
        """A unique label for this :class:`DSFFailoverChain`"""
        return self._label
    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def core(self):
        """Indicates whether or not the contained :class:`DSFRecordSet`'s are
        core record sets.
        """
        return self._core
    @core.setter
    def core(self, value):
        self._core = value
        api_args = {'core': self._core}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def record_sets(self):
        """A list of hashes to create a new :class:`DSFRecordSet` or
        specify/update an existing :class:`DSFRecordSet`
        """
        return self._record_sets
    @record_sets.setter
    def record_sets(self, value):
        pass

    def to_json(self):
        """Convert this :class:`DSFFailoverChain` to a JSON blob"""
        json_blob = {}
        if self._label:
            json_blob['label'] = self._label
        if self._core:
            json_blob['core'] = self._core
        if self.record_sets:
            json_blob['record_sets'] = [rs.to_json() for rs in self.record_sets]
        return json_blob

    def delete(self):
        """Delete this :class:`DSFFailoverChain` from the Dynect System"""
        api_args = {'publish': 'Y'}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFResponsePool(object):
    """docstring for DSFResponsePool"""
    def __init__(self, label, core_set_count=1, eligible=True,
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
        super(DSFResponsePool, self).__init__()
        self._label = label
        self._core_set_count = core_set_count
        self._eligible = eligible
        self._automation = automation
        self._dsf_ruleset_id = dsf_ruleset_id
        self._index = index
        if isinstance(rs_chains, list) and len(rs_chains) > 0 and \
                isinstance(rs_chains[0], dict):
            # Clear Failover Chains
            self._rs_chains = []
            # Create a new FO Chain for each entry returned from API
            for chain in rs_chains:
                self._rs_chains.append(DSFFailoverChain(**chain))
        else:
            self._rs_chains = rs_chains
        self._service_id = self._dsf_response_pool_id = self.uri = None
        for key, val in kwargs.items():
            setattr(self, '_' + key, val)
        # If dsf_id and dsf_response_pool_id were specified in kwargs
        if self._service_id is not None and self._dsf_response_pool_id is not None:
            r_pid = self._dsf_response_pool_id
            self.uri = '/DSFResponsePool/{}/{}/'.format(self._service_id,
                                                        r_pid)

    def _post(self, service_id):
        """Create a new :class:`DSFResponsePool` on the DynECT System

        :param dsf_id: the id of the DSF service this :class:`DSFResponsePool`
            is attached to
        """
        self.service_id = service_id
        uri = '/DSFResponsePool/{}/'.format(self.service_id)
        api_args = {'publish': 'Y', 'label': self._label,
                    'core_set_count': self._core_set_count,
                    'eligible': self._eligible, 'automation': self._automation}
        if self._dsf_ruleset_id:
            api_args['dsf_ruleset_id'] = self._dsf_ruleset_id
        if self._index:
            api_args['index'] = self._index
        if self._rs_chains:
            api_args['rs_chains'] = self._rs_chains
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        for key, val in response['data'].items():
            if key != 'rs_chains':
                setattr(self, '_' + key, val)
        self.uri = '/DSFResponsePool/{}/{}/'.format(self.service_id,
                                                    self._dsf_response_pool_id)

    def _get(self, service_id, dsf_response_pool_id):
        """Get an existing :class:`DSFResponsePool` from the DynECT System

        :param dsf_id: the id of the DSF service this :class:`DSFResponsePool`
            is attached to
        :param dsf_response_pool_id: the id of this :class:`DSFResponsePool`
        """
        self.service_id = service_id
        self._dsf_response_pool_id = dsf_response_pool_id
        self.uri = '/DSFResponsePool/{}/{}/'.format(self.service_id,
                                                    self._dsf_response_pool_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'rs_chains':
                setattr(self, '_' + key, val)

    @property
    def label(self):
        """A unique label for this :class:`DSFResponsePool`"""
        return self._label
    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def core_set_count(self):
        """If fewer than this number of core record sets are eligible, status
        will be set to fail
        """
        return self._core_set_count
    @core_set_count.setter
    def core_set_count(self, value):
        self._core_set_count = value
        api_args = {'core_set_count': self._core_set_count}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def eligible(self):
        """Indicates whether or not the :class:`DSFResponsePool` can be served
        """
        return self._eligible
    @eligible.setter
    def eligible(self, value):
        self._eligible = value
        api_args = {'eligible': self._eligible}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def automation(self):
        """Defines how eligible can be changed in response to monitoring"""
        return self._automation
    @automation.setter
    def automation(self, value):
        self._automation = value
        api_args = {'automation': self._automation}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def dsf_ruleset_ids(self):
        """List of Unique system ids of the Rulesets this :class:`DSFResponsePool` is
        attached to
        """
        self._get(self._service_id, self._dsf_response_pool_id)
        return [ruleset['dsf_ruleset_id'] for ruleset in self._rulesets]

    @dsf_ruleset_ids.setter
    def dsf_ruleset_ids(self, value):
        #self._dsf_ruleset_id = value
        #api_args = {'dsf_ruleset_id': self._dsf_ruleset_id}
        #response = DynectSession.get_session().execute(self.uri, 'PUT',
        #                                               api_args)
        #for key, val in response['data'].items():
        #    if key != 'record_sets':
        #        setattr(self, '_' + key, val)
        pass

    @property
    def rs_chains(self):
        """A list of :class:`DSFFailoverChain` that are defined for this
        :class:`DSFResponsePool`
        """
        return self._rs_chains
    @rs_chains.setter
    def rs_chains(self, value):
        pass

    def to_json(self):
        """Convert this :class:`DSFResponsePool` to a JSON blob"""
        rs_json = [rs.to_json() for rs in self._rs_chains]
        json_blob = {'label': self._label, 'eligible': self._eligible,
                     'core_set_count': self._core_set_count,
                     'automation': self._automation, 'rs_chains': rs_json}
        if self._index:
            json_blob['index'] = self._index
        if self._dsf_ruleset_id:
            json_blob['dsf_ruleset_id'] = self._dsf_ruleset_id
        return json_blob

    def delete(self):
        """Delete this :class:`DSFResponsePool` from the DynECT System"""
        api_args = {'publish': 'Y'}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFRuleset(object):
    """docstring for DSFRuleset"""
    def __init__(self, label, criteria_type, response_pools, criteria=None, failover=None,
                **kwargs):
        """Create a :class:`DSFRuleset` object

        :param label: A unique label for this :class:`DSFRuleset`
        :param criteria_type: A set of rules describing what traffic is applied
            to the :class:`DSFRuleset`
        :param criteria: Varied depending on the specified criteria_type
        :param failover: IP address or Hostname for a last resort failover.
        :param response_pools: A list of :class:`DSFResponsePool`'s for this
            :class:`DSFRuleset`
        """
        super(DSFRuleset, self).__init__()
        self.valid_criteria_types = ('always', 'geoip')
        self.valid_criteria = {'always': (),
                               'geoip': ()}
        self._label = label
        self._criteria_type = criteria_type
        self._criteria = criteria
        self._failover = failover
        if isinstance(response_pools, list) and len(response_pools) > 0 and \
                isinstance(response_pools[0], dict):
            self._response_pools = []
            for pool in response_pools:
                pool = {x: pool[x] for x in pool if x != 'rulesets'}
                self._response_pools.append(DSFResponsePool(**pool))
        else:
            self._response_pools = response_pools
        self._service_id = self._dsf_ruleset_id = self.uri = None
        for key, val in kwargs.items():
            setattr(self, '_' + key, val)
        # If dsf_id and dsf_ruleset_id were specified in kwargs
        if self._service_id is not None and self._dsf_ruleset_id is not None:
            self.uri = '/DSFRuleset/{}/{}/'.format(self._service_id,
                                                   self._dsf_ruleset_id)

    def _post(self, dsf_id):
        """Create a new :class:`DSFRuleset` on the DynECT System

        :param dsf_id: the id of the DSF service this :class:`DSFRuleset` is
            attached to
        """
        self._service_id = dsf_id
        uri = '/DSFRuleset/{}/'.format(self._service_id)
        api_args = {'publish': 'Y', 'label': self._label,
                    'criteria_type': self._criteria_type,
                    'criteria': self._criteria}
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        for key, val in response['data'].items():
            if key != 'rs_chains':
                setattr(self, '_' + key, val)
        self.uri = '/DSFRuleset/{}/{}/'.format(self._service_id,
                                               self._dsf_ruleset_id)

    def _get(self, dsf_id, dsf_ruleset_id):
        """Get an existing :class:`DSFRuleset` from the DynECT System

        :param dsf_id: the id of the DSF service this :class:`DSFRuleset` is
            attached to
        :param dsf_ruleset_id: The unique system id of this :class:`DSFRuleset`
        """
        self._service_id = dsf_id
        self._dsf_ruleset_id = dsf_ruleset_id
        self.uri = '/DSFRuleset/{}/{}/'.format(self._service_id,
                                               self._dsf_ruleset_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'rs_chains':
                setattr(self, '_' + key, val)

    @property
    def label(self):
        """A unique label for this :class:`DSFRuleset`"""
        return self._label
    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def criteria_type(self):
        """A set of rules describing what traffic is applied to the
        :class:`DSFRuleset`
        """
        return self._criteria_type
    @criteria_type.setter
    def criteria_type(self, value):
        self._criteria_type = value
        api_args = {'criteria_type': self._criteria_type}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def criteria(self):
        """The criteria rules, will be varied depending on the specified
        criteria_type
        """
        return self._criteria
    @criteria.setter
    def criteria(self, value):
        self._criteria = value
        api_args = {'criteria': self._criteria}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)

    @property
    def response_pools(self):
        """A list of :class:`DSFResponsePool`'s for this :class:`DSFRuleset`"""
        return self._response_pools
    @response_pools.setter
    def response_pools(self, value):
        pass

    @property
    def _json(self):
        """JSON-ified version of this DSFRuleset Object"""
        pool_json = [pool.to_json() for pool in self._response_pools]
        if self._failover:
            pool_json.append({'failover': self._failover})
        json_blob = {'label': self._label, 'criteria_type': self._criteria_type,
                     'criteria': self._criteria,
                     'response_pools': pool_json}
        return json_blob

    def delete(self):
        """Remove this :class:`DSFRuleset` from it's associated
        :class:`TrafficDirector` Service
        """
        api_args = {'publish': 'Y'}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFMonitorEndpoint(object):
    """An Endpoint object to be passed to a :class:`DSFMonitor`"""
    def __init__(self, address, label, active='Y', site_prefs=None):
        """Create a :class:`DSFMonitorEndpoint` object

        :param address: The address to monitor.
        :param label: A label to identify this :class:`DSFMonitorEndpoint`.
        :param active: Indicates whether or not this :class:`DSFMonitorEndpoint`
            endpoint is active. Must be one of True, False, 'Y', or 'N'
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
                    args_list.append(endpoint._json)
            api_args = {'endpoints': args_list}
            self._monitor._update(api_args)

    @property
    def _json(self):
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
        api_args = self._json
        api_args['active'] = value
        self._update(api_args)

    @property
    def label(self):
        return self._label
    @label.setter
    def label(self, value):
        api_args = self._json
        api_args['label'] = value
        self._update(api_args)

    @property
    def address(self):
        return self._address
    @address.setter
    def address(self, value):
        api_args = self._json
        api_args['address'] = value
        self._update(api_args)

    @property
    def site_prefs(self):
        return self._site_prefs
    @site_prefs.setter
    def site_prefs(self, value):
        api_args = self._json
        api_args['site_prefs'] = value
        self._update(api_args)


class DSFMonitor(object):
    """A Monitor for a :class:`TrafficDirector` Service"""
    def __init__(self, *args, **kwargs):
        """Create a new :class:`DSFMonitor` object

        :param label: A unique label to identify this :class:`DSFMonitor`
        :param protocol: The protocol to monitor. Must be one of 'HTTP',
            'HTTPS', 'PING', 'SMTP', or 'TCP'
        :param response_count: The number of responses to determine whether or
            not the endpoint is 'up' or 'down'
        :param probe_interval: How often to run this :class:`DSFMonitor`
        :param retries: How many retries this :class:`DSFMonitor` should attempt
            on failure before giving up.
        :param active: Indicates if this :class:`DSFMonitor` is active
        :param options: Additional options pertaining to this
            :class:`DSFMonitor`
        :param endpoints: A List of :class:`DSFMonitorEndpoint`'s that are
            associated with this :class:`DSFMonitor`
        """
        super(DSFMonitor, self).__init__()
        self.uri = None
        self._monitor_id = None
        self._label = self._protocol = self._response_count = None
        self._probe_interval = self._retries = self._active = None
        self._options = self._dsf_monitor_id = self._timeout = self._port = None
        self._path = self._host = self._header = self._expected = None
        self._endpoints = []
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
            self.uri = '/DSFMonitor/{}/'.format(self._dsf_monitor_id)
        elif len(args) + len(kwargs) == 1:
            self._get(*args, **kwargs)
        else:
            self._post(*args, **kwargs)

    def _get(self, monitor_id):
        """Get an existing :class:`DSFMonitor` from the DynECT System"""
        self._monitor_id = monitor_id
        self.uri = '/DSFMonitor/{}/'.format(self._monitor_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _post(self, label, protocol, response_count, probe_interval, retries,
              active='Y', timeout=None, port=None, path=None, host=None,
              header=None, expected=None, endpoints=None):
        """Create a new :class:`DSFMonitor` on the DynECT System"""
        uri = '/DSFMonitor/'
        self._label = label
        self._protocol = protocol
        self._response_count = response_count
        self._probe_interval = probe_interval
        self._retries = retries
        self._active = Active(active)
        self._options = {}
        if timeout:
            self._timeout = timeout
            self._options['timeout'] = timeout
        if port:
            self._port = port
            self._options['port'] = port
        if path:
            self._path = path
            self._options['path'] = path
        if host:
            self._host = host
            self._options['host'] = host
        if header:
            self._header = header
            self._options['header'] = header
        if expected:
            self._expected = expected
            self._options['expected'] = expected
        self._endpoints = endpoints
        api_args = {'label': self._label,
                    'protocol': self._protocol,
                    'response_count': self._response_count,
                    'probe_interval': self._probe_interval,
                    'retries': self._retries,
                    'active': str(self._active),
                    'options': self._options}
        if self._endpoints is not None:
            api_args['endpoints'] = [x._json for x in self._endpoints]
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])
        self.uri = '/DSFMonitor/{}/'.format(self._dsf_monitor_id)

    def _update(self, api_args):
        """Private Update method"""
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Update this object based on the information passed in via data

        :param data: The ``['data']`` field from an API JSON response
        """
        for key, val in data.items():
            if key == 'endpoints':
                self._endpoints = []
                for endpoint in val:
                    ep = DSFMonitorEndpoint(**endpoint)
                    ep._monitor = self
                    self._endpoints.append(ep)
            elif key == 'options':
                for opt_key, opt_val in val.items():
                    setattr(self, '_' + opt_key, opt_val)
            elif key == 'active':
                self._active = Active(val)
            else:
                setattr(self, '_' + key, val)

    @property
    def dsf_monitor_id(self):
        """The unique system id of this :class:`DSFMonitor`"""
        return self._dsf_monitor_id
    @dsf_monitor_id.setter
    def dsf_monitor_id(self, value):
        pass

    @property
    def label(self):
        """A unique label to identify this :class:`DSFMonitor`"""
        return self._label
    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        self._update(api_args)

    @property
    def protocol(self):
        """The protocol to monitor. Must be one of 'HTTP', 'HTTPS', 'PING',
        'SMTP', or 'TCP'
        """
        return self._protocol
    @protocol.setter
    def protocol(self, value):
        self._protocol = value
        api_args = {'protocol': self._protocol}
        self._update(api_args)

    @property
    def response_count(self):
        """The minimum number of agents reporting the host as up for failover not to occur. Must be 0, 1 or 2
        """
        return self._response_count
    @response_count.setter
    def response_count(self, value):
        self._response_count = value
        api_args = {'response_count': self._response_count}
        self._update(api_args)

    @property
    def probe_interval(self):
        """How often to run this :class:`DSFMonitor`"""
        return self._probe_interval
    @probe_interval.setter
    def probe_interval(self, value):
        self._probe_interval = value
        api_args = {'probe_interval': self._probe_interval}
        self._update(api_args)

    @property
    def retries(self):
        """How many retries this :class:`DSFMonitor` should attempt on failure
        before giving up.
        """
        return self._retries
    @retries.setter
    def retries(self, value):
        self._retries = value
        api_args = {'retries': self._retries}
        self._update(api_args)

    @property
    def active(self):
        """Returns whether or not this :class:`DSFMonitor` is active. Will
        return either 'Y' or 'N'
        """
        return self._active
    @active.setter
    def active(self, value):
        self._active = value
        api_args = {'active': self._active}
        self._update(api_args)

    @property
    def endpoints(self):
        """A list of the endpoints (and their statuses) that this
        :class:`DSFMonitor` is currently monitoring.
        """
        self._get(self.dsf_monitor_id)
        return self._endpoints
    @endpoints.setter
    def endpoints(self, value):
        pass

    @property
    def options(self):
        """Additional options pertaining to this :class:`DSFMonitor`"""
        return self._options
    @options.setter
    def options(self, value):
        self._options = value
        api_args = {'options': self._options}
        self._update(api_args)

    def delete(self):
        """Delete an existing :class:`DSFMonitor` from the DynECT System"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class TrafficDirector(object):
    """Traffic Director is a DNS based traffic routing and load balancing
    service that is Geolocation aware and can support failover by monitoring
    endpoints.
    """
    def __init__(self, *args, **kwargs):
        """Create a :class:`TrafficDirector` object

        :param label: A unique label for this :class:`TrafficDirector` service
        :param ttl: The default TTL to be used across this service
        :param publish: If Y, service will be published on creation
        :param nodes: A Node Object, a zone, FQDN pair in a hash, or a list
            containing those two things (can be mixed) that are to be
            linked to this :class:`TrafficDirector` service:
        :param notifiers: A list of names of notifiers associated with this
            :class:`TrafficDirector` service
        :param rulesets: A list of :class:`DSFRulesets` that are defined for
            this :class:`TrafficDirector` service
        """
        super(TrafficDirector, self).__init__()
        self._label = self._ttl = self._publish = self._response_pools = None
        self._record_sets = self.uri = self._service_id = None
        self._notifiers = APIList(DynectSession.get_session, 'notifiers')
        self._nodes = APIList(DynectSession.get_session, 'nodes')
        self._rulesets = APIList(DynectSession.get_session, 'rulesets')
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif len(args) + len(kwargs) == 1:
            self._get(*args, **kwargs)
        else:
            self._post(*args, **kwargs)
        self.uri = '/DSF/{}/'.format(self._service_id)
        self._notifiers.uri = self._rulesets.uri = self.uri

    def _post(self, label, ttl=None, publish='Y', nodes=None, notifiers=None,
              rulesets=None):
        """Create a new :class:`TrafficDirector` on the DynECT System"""
        uri = '/DSF/'
        self._label = label
        self._ttl = ttl
        self._nodes = nodes
        self._notifiers = notifiers
        self._rulesets = rulesets
        api_args = {'label': self._label,
                    'publish': publish}
        if ttl:
            api_args['ttl'] = self._ttl
        if nodes:
            _nodeList=[]
            if isinstance(nodes, list):
                for node in nodes:
                    if isinstance(node, dyn.tm.zones.Node):
                        _nodeList.append({'zone':node.zone, 'fqdn':node.fqdn})
                    elif isinstance(node, dict):
                        _nodeList.append(node)
            elif isinstance(nodes,dict):
                _nodeList.append(nodes)
            elif isinstance(nodes, dyn.tm.zones.Node):
                _nodeList.append({'zone':nodes.zone, 'fqdn':nodes.fqdn})
            self._nodes=_nodeList
            api_args['nodes'] = self._nodes
        if notifiers:
            if isinstance(notifiers[0], dict):
                api_args['notifiers'] = notifiers
            else:  # notifiers is a list of Notifier objects
                api_args['notifiers'] = [{'notifier_id': x.notifier_id} for x
                                          in self._notifiers]
        if rulesets:
            api_args['rulesets'] = [rule._json for rule in self._rulesets]
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self.uri = '/DSF/{}/'.format(response['data']['service_id'])
        self._build(response['data'])

    def _build(self, data):
        for key, val in data.items():
            if key == 'notifiers':
                # Don't do anything special with these dicts for now
                self._notifiers = APIList(DynectSession.get_session,
                                          'notifiers', None, val)
            elif key == 'rulesets':
                # Clear Rulesets
                self._rulesets = APIList(DynectSession.get_session, 'rulesets')
                self._rulesets.uri = None
                # For each Ruleset returned, create a new DSFRuleset object
                for ruleset in val:
                    self._rulesets.append(DSFRuleset(**ruleset))
            elif key == 'nodes':
                # nodes are now returned as Node Objects
                self._nodes = [dyn.tm.zones.Node(node['zone'], node['fqdn']) for node in val]
            else:
                setattr(self, '_' + key, val)
        self.uri = '/DSF/{}/'.format(self._service_id)
        self._notifiers.uri = self._rulesets.uri = self.uri

    def _get(self, service_id):
        """Get an existing :class:`TrafficDirector` from the DynECT System"""
        self._service_id = service_id
        self.uri = '/DSF/{}/'.format(self._service_id)
        api_args = {'pending_changes': 'Y'}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args):
        """Private update method"""
        if 'publish' not in api_args:
            api_args['publish'] = 'Y'
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def revert_changes(self):
        """Clears the changeset for this service and reverts all non-published
        changes to their original state
        """
        api_args = {'revert': True}
        self._update(api_args)

    def add_notifier(self, notifier_id, publish='Y'):
        """Links the Notifier with the specified id to this Traffic Director
        service
        """
        api_args = {'add_notifier': True, 'notifier_id': notifier_id,
                    'publish': publish}
        self._update(api_args)

    def remove_orphans(self):
        """Remove Record Set Chains which are no longer referenced by a
        :class:`DSFResponsePool`
        """
        api_args = {'remove_orphans': 'Y'}
        self._update(api_args)

    @property
    def service_id(self):
        """The unique System id of this DSF Service"""
        return self._service_id
    @service_id.setter
    def service_id(self, value):
        pass

    @property
    def records(self):
        """A list of this :class:`TrafficDirector` Services' DSFRecords"""
        return [record for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains
                for record_set in rs_chains.record_sets
                for record in record_set.records]
    @records.setter
    def records(self, value):
        pass

    @property
    def record_sets(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFRecordSet`'s
        """
        return [record_set for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains
                for record_set in rs_chains.record_sets]
    @record_sets.setter
    def record_sets(self, value):
        pass

    @property
    def response_pools(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFResponsePool`'s
        """
        return [response_pool for ruleset in self._rulesets
                for response_pool in ruleset.response_pools]
    @response_pools.setter
    def response_pools(self, value):
        pass

    @property
    def rs_chains(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFFailoverChain`'s
        """
        return [rs_chains for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains]
    @rs_chains.setter
    def rs_chains(self, value):
        pass

    @property
    def notifiers(self):
        """A list of names of notifiers associated with this
        :class:`TrafficDirector` service
        """
        return self._notifiers
    @notifiers.setter
    def notifiers(self, value):
        if isinstance(value, list) and not isinstance(value, APIList):
            self._notifiers = APIList(DynectSession.get_session, 'notifiers',
                                      None, value)
        elif isinstance(value, APIList):
            self._notifiers = value
        self._notifiers.uri = self.uri

    @property
    def rulesets(self):
        """A list of :class:`DSFRulesets` that are defined for this
        :class:`TrafficDirector` service
        """
        return self._rulesets
    @rulesets.setter
    def rulesets(self, value):
        if isinstance(value, list) and not isinstance(value, APIList):
            self._rulesets = APIList(DynectSession.get_session, 'rulesets',
                                     None, value)
        elif isinstance(value, APIList):
            self._rulesets = value
        self._rulesets.uri = self.uri

    @property
    def nodeObjects(self):
        """A list of :class:`Node` Objects that are linked
        to this :class:`TrafficDirector` service"""
        uri = '/DSFNode/{}'.format(self._service_id)
        api_args = {}
        response = DynectSession.get_session().execute(uri, 'GET',
                                                       api_args)
        self._nodes = [dyn.tm.zones.Node(node['zone'], node['fqdn']) for node in response['data']]
        return self._nodes

    @property
    def nodes(self):
        """A list of hashes of zones, fqdn for each DSF node that is linked
        to this :class:`TrafficDirector` service"""
        uri = '/DSFNode/{}'.format(self._service_id)
        api_args = {}
        response = DynectSession.get_session().execute(uri, 'GET',
                                                       api_args)
        self._nodes = [dyn.tm.zones.Node(node['zone'], node['fqdn']) for node in response['data']]
        return [{'zone': node['zone'], 'fqdn': node['fqdn']} for node in response['data']]

    @nodes.setter
    def nodes(self, nodes):
        """A :class:`Node` Object, a zone, FQDN pair in a hash, or a list
        containing those two things (can be mixed) that are to be
        linked to this :class:`TrafficDirector` service. This overwrites
        whatever nodes are already linked to this :class:`TrafficDirector` service ."""
        _nodeList=[]
        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, dyn.tm.zones.Node):
                    _nodeList.append({'zone':node.zone, 'fqdn':node.fqdn})
                elif isinstance(node, dict):
                    _nodeList.append(node)
        elif isinstance(nodes,dict):
            _nodeList.append(nodes)
        elif isinstance(nodes, dyn.tm.zones.Node):
            _nodeList.append({'zone':nodes.zone, 'fqdn':nodes.fqdn})
        uri = '/DSFNode/{}'.format(self._service_id)
        api_args = {'nodes': _nodeList, 'publish': 'Y'}
        response = DynectSession.get_session().execute(uri, 'PUT',
                                                       api_args)
        self._nodes = [dyn.tm.zones.Node(node['zone'], node['fqdn']) for node in response['data']]

    def add_node(self, node):
        """A :class:`Node` object, or a zone, FQDN pair in a hash
        to be added to this :class:`TrafficDirector` service:"""
        if isinstance(node, dyn.tm.zones.Node):
            _node = {'zone':node.zone, 'fqdn':node.fqdn}
        elif isinstance(node, dict):
            _node = node
        uri = '/DSFNode/{}'.format(self._service_id)
        api_args = {'node': _node, 'publish': 'Y'}
        response = DynectSession.get_session().execute(uri, 'POST',
                                                       api_args)
        self._nodes = [dyn.tm.zones.Node(node['zone'], node['fqdn']) for node in response['data']]

    def remove_node(self, node):
        """A :class:`Node` object, or a zone, FQDN pair in a hash
        to be removed to this :class:`TrafficDirector` service:"""
        if isinstance(node, dyn.tm.zones.Node):
            _node = {'zone':node.zone, 'fqdn':node.fqdn}
        elif isinstance(node, dict):
            _node = node
        uri = '/DSFNode/{}'.format(self._service_id)
        api_args = {'node': _node, 'publish': 'Y'}
        response = DynectSession.get_session().execute(uri, 'DELETE',
                                                       api_args)
        self._nodes = [dyn.tm.zones.Node(node['zone'], node['fqdn']) for node in response['data']]

    @property
    def label(self):
        """A unique label for this :class:`TrafficDirector` service"""
        return self._label
    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        self._update(api_args)

    @property
    def ttl(self):
        """The default TTL to be used across this service"""
        if not isinstance(self._ttl, int):
            self._ttl = int(self._ttl)
        return self._ttl
    @ttl.setter
    def ttl(self, value):
        self._ttl = value
        api_args = {'ttl': self._ttl}
        self._update(api_args)

    def delete(self):
        """Delete this :class:`TrafficDirector` from the DynECT System"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<TrafficDirector>: {}').format(self._service_id)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
