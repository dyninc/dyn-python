# -*- coding: utf-8 -*-
"""This module contains class objects for all supported DynDNS Record types

These DNS_Records should really only need to be created via a zone instance but
could also be created independently if passed valid zone, fqdn data
"""
from .session import DynectSession
from ..core import (APIObject, ImmutableAttribute, IntegerAttribute,
                    StringAttribute, ValidatedAttribute)
from ..compat import force_unicode

__author__ = 'jnappi'
__all__ = ['DNSRecord', 'ARecord', 'AAAARecord', 'CERTRecord', 'CNAMERecord',
           'DHCIDRecord', 'DNAMERecord', 'DNSKEYRecord', 'DSRecord',
           'KEYRecord', 'KXRecord', 'LOCRecord', 'IPSECKEYRecord', 'MXRecord',
           'NAPTRRecord', 'PTRRecord', 'PXRecord', 'NSAPRecord', 'RPRecord',
           'NSRecord', 'SOARecord', 'SPFRecord', 'SRVRecord', 'TLSARecord',
           'TXTRecord', 'RECORD_TYPES']


# noinspection PyMissingConstructor
class DNSRecord(APIObject):
    """Base record object contains functionality to be used across all other
    record type objects
    """
    session_type = DynectSession
    zone = ImmutableAttribute('zone')
    fqdn = ImmutableAttribute('fqdn')
    record_id = ImmutableAttribute('record_id')
    ttl = IntegerAttribute('ttl')
    record_type = ''

    def __init__(self, zone, fqdn, record_id=None, *args, **kwargs):
        self._zone, self._fqdn, self._record_id = zone, fqdn, record_id
        self.uri = '/{0}/{1}/{2}/'.format(self.record_type, zone, fqdn)
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif record_id:
            self._get(record_id)
        else:
            self._post(*args, **kwargs)
        self.uri += '{0}/'.format(self.record_id)

    def _post(self, *args, **api_args):
        """Make the API call to create the current record type

        :param api_args: arguments to be pased to the API call
        """
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _get(self, record_id):
        """Get an existing record object from the DynECT System

        :param record_id: The id of the record you would like to get
        """
        uri = self.uri + '{}/'.format(record_id)
        response = DynectSession.get_session().execute(uri, 'GET')
        self._build(response['data'])

    def _update(self, **api_args):
        """Build our records rdata api_argument attribute, and ship that off to
        the API
        """
        rdata = DNSRecord.rdata(self)
        for key, val in api_args.items():
            if key in rdata:
                rdata[key] = val
        api_args['rdata'] = rdata
        super(DNSRecord, self)._update(**api_args)

    def _build(self, data):
        """Flatten the inner rdata dict for convenience and ship that data off
        to be built
        """
        if 'rdata' in data:
            for r_key, r_val in data.pop('rdata').items():
                data[r_key] = r_val
        super(DNSRecord, self)._build(data)

    def rdata(self):
        """Return a records rdata"""
        rdata = {}
        for key, val in self.__dict__.items():
            if key.startswith('_') and not hasattr(val, '__call__') \
                    and key != '_record_type' and key != '_record_id':
                if 'ttl' not in key and 'zone' not in key \
                        and 'fqdn' not in key:
                    rdata[key[1:]] = val
        return rdata

    @property
    def geo_node(self):
        return {'zone': self._zone, 'fqdn': self._fqdn}

    @property
    def geo_rdata(self):
        data = DNSRecord.rdata(self)
        return {x: data[x] for x in data if data[x] is not None}

    @property
    def rec_name(self):
        """Convenience property to access the name of this record type"""
        return self.record_type.replace('Record', '').lower()

    def __str__(self):
        return force_unicode('<{0}>: {1}').format(self.record_type, self.fqdn)


class ARecord(DNSRecord):
    """The IPv4 Address (A) Record forward maps a host name to an IPv4 address.
    """
    record_type = 'ARecord'
    address = StringAttribute('address')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.ARecord`'s rdata as a JSON blob
        """
        guts = super(ARecord, self).rdata()
        shell = {'a_rdata': guts}
        return shell

    def __str__(self):
        """str override"""
        return '<ARecord>: {0}'.format(self.address)
    __repr__ = __str__


class AAAARecord(DNSRecord):
    """The IPv6 Address (AAAA) Record is used to forward map hosts to IPv6
    addresses and is the current IETF recommendation for this purpose.
    """
    record_type = 'AAAARecord'
    address = StringAttribute('address')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.AAAARecord`'s rdata as a JSON
        blob
        """
        guts = super(AAAARecord, self).rdata()
        shell = {'aaaa_rdata': guts}
        return shell

    def __str__(self):
        """str override"""
        return '<AAAARecord>: {0}'.format(self.address)
    __repr__ = __str__


class CERTRecord(DNSRecord):
    """The Certificate (CERT) Record may be used to store either public key
    certificates or Certificate Revocation Lists (CRL) in the zone file.
    """
    record_type = 'CERTRecord'
    format = IntegerAttribute('format')
    tag = IntegerAttribute('tag')
    algorithm = StringAttribute('algorithm')
    certificate = StringAttribute('certificate')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.CERTRecord`'s rdata as a JSON
        blob
        """
        guts = super(CERTRecord, self).rdata()
        shell = {'cert_rdata': guts}
        return shell


class CNAMERecord(DNSRecord):
    """The Canonical Name (CNAME) Records map an alias to the real or canonical
    name that may lie inside or outside the current zone.
    """
    record_type = 'CNAMERecord'
    cname = StringAttribute('cname')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.CNAMERecord`'s rdata as a JSON
        blob
        """
        guts = super(CNAMERecord, self).rdata()
        shell = {'cname_rdata': guts}
        return shell


class DHCIDRecord(DNSRecord):
    """The :class:`~dyn.tm.records.DHCIDRecord` provides a means by which DHCP
    clients or servers can associate a DHCP client's identity with a DNS name,
    so that multiple DHCP clients and servers may deterministically perform
    dynamic DNS updates to the same zone.
    """
    record_type = 'DHCIDRecord'
    digest = StringAttribute('digest')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DHCIDRecord`'s rdata as a JSON
        blob
        """
        guts = super(DHCIDRecord, self).rdata()
        shell = {'dhcid_rdata': guts}
        return shell


class DNAMERecord(DNSRecord):
    """The Delegation of Reverse Name (DNAME) Record is designed to assist the
    delegation of reverse mapping by reducing the size of the data that must be
    entered. DNAME's are designed to be used in conjunction with a bit label
    but do not strictly require one. However, do note that without a bit label
    a DNAME is equivalent to a CNAME when used in a reverse-map zone file.
    """
    record_type = 'DNAMERecord'
    dname = StringAttribute('dname')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DNAMERecord`'s rdata as a JSON
        blob
        """
        guts = super(DNAMERecord, self).rdata()
        shell = {'dname_rdata': guts}
        return shell


class DNSKEYRecord(DNSRecord):
    """The DNSKEY Record describes the public key of a public key (asymmetric)
    cryptographic algorithm used with DNSSEC.nis. It is typically used to
    authenticate signed keys or zones.
    """
    record_type = 'DNSKEYRecord'
    protocol = IntegerAttribute('protocol')
    public_key = StringAttribute('public_key')
    algorithm = ValidatedAttribute('algorithm', validator=range(1, 6))
    flags = IntegerAttribute('flags')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DNSKEYRecord`'s rdata as a JSON
        blob
        """
        guts = super(DNSKEYRecord, self).rdata()
        shell = {'dnskey_rdata': guts}
        return shell


class DSRecord(DNSRecord):
    """The Delegation Signer (DS) record type is used in DNSSEC to create the
    chain of trust or authority from a signed parent zone to a signed child
    zone.
    """
    record_type = 'DSRecord'
    digest = StringAttribute('digest')
    keytag = IntegerAttribute('keytag')
    algorithm = ValidatedAttribute('algorithm', validator=range(1, 6))
    digtype = ValidatedAttribute('digtype', validator=('SHA1', 'SHA256'))

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DSRecord`'s rdata as a JSON blob
        """
        guts = super(DSRecord, self).rdata()
        shell = {'ds_rdata': guts}
        return shell


class KEYRecord(DNSRecord):
    """"Public Key" (KEY) Records are used for the storage of public keys for
    use by multiple applications such as IPSec, SSH, etc..., as well as for use
    by DNS security methods including the original DNSSEC protocol. However,
    as of RFC3445 the use of :class:`~dyn.tm.records.KEYRecord`'s have been
    limited to use in DNS Security operations such as DDNS and zone transfer
    due to the difficulty of querying for specific uses.
    """
    record_type = 'KEYRecord'
    algorithm = ValidatedAttribute('algorithm', validator=range(1, 6))
    flags = IntegerAttribute('flags')
    protocol = IntegerAttribute('protocol')
    public_key = StringAttribute('public_key')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.KEYRecord`'s rdata as a JSON
        blob
        """
        guts = super(KEYRecord, self).rdata()
        shell = {'key_rdata': guts}
        return shell


class KXRecord(DNSRecord):
    """The "Key Exchanger" (KX) Record type is provided with one or more
    alternative hosts.
    """
    record_type = 'KXRecord'
    exchange = StringAttribute('exchange')
    preference = IntegerAttribute('preference')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.KXRecord`'s rdata as a JSON blob
        """
        guts = super(KXRecord, self).rdata()
        shell = {'kx_rdata': guts}
        return shell


class LOCRecord(DNSRecord):
    """:class:`~dyn.tm.records.LOCRecord`'s allow for the definition of
    geographic positioning information associated with a host or service name.
    """
    record_type = 'LOCRecord'
    altitude = IntegerAttribute('altitude')
    horiz_pre = StringAttribute('horiz_pre')
    latitude = IntegerAttribute('latitude')
    longitude = IntegerAttribute('longitude')
    size = IntegerAttribute('size')
    version = ValidatedAttribute('version', validator=(0,))
    vert_pre = StringAttribute('vert_pre')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.LOCRecord`'s rdata as a JSON
        blob
        """
        guts = super(LOCRecord, self).rdata()
        shell = {'loc_rdata': guts}
        return shell


class IPSECKEYRecord(DNSRecord):
    """The IPSECKEY is used for storage of keys used specifically for IPSec
    oerations
    """
    record_type = 'IPSECKEYRecord'
    precedence = IntegerAttribute('precedence')
    gatetype = ValidatedAttribute('gatetype', validator=range(0, 4))
    algorithm = ValidatedAttribute('algorithm', validator=range(0, 3))
    gateway = IntegerAttribute('gateway')
    public_key = StringAttribute('public_key')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.IPSECKEYRecord`'s rdata as a
        JSON blob
        """
        guts = super(IPSECKEYRecord, self).rdata()
        shell = {'ipseckey_rdata': guts}
        return shell


class MXRecord(DNSRecord):
    """The "Mail Exchanger" record type specifies the name and relative
    preference of mail servers for a Zone. Defined in RFC 1035
    """
    record_type = 'MXRecord'
    exchange = StringAttribute('exchange')
    preference = IntegerAttribute('preference')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.MXRecord`'s rdata as a JSON blob
        """
        guts = super(MXRecord, self).rdata()
        shell = {'mx_rdata': guts}
        return shell


class NAPTRRecord(DNSRecord):
    """Naming Authority Pointer Records are a part of the Dynamic Delegation
    Discovery System (DDDS). The NAPTR is a generic record that defines a
    `rule` that may be applied to private data owned by a client application.
    """
    record_type = 'NAPTRRecord'
    order = IntegerAttribute('order')
    preference = IntegerAttribute('preference')
    services = StringAttribute('services')
    regexp = StringAttribute('regexp')
    replacement = StringAttribute('replacement')
    flags = StringAttribute('flags')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NAPTRRecord`'s rdata as a JSON
        blob
        """
        guts = super(NAPTRRecord, self).rdata()
        shell = {'naptr_rdata': guts}
        return shell


class PTRRecord(DNSRecord):
    """Pointer Records are used to reverse map an IPv4 or IPv6 IP address to a
    host name
    """
    record_type = 'PTRRecord'
    ptrdname = StringAttribute('ptrdname')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.PTRRecord`'s rdata as a JSON
        blob
        """
        guts = super(PTRRecord, self).rdata()
        shell = {'ptr_rdata': guts}
        return shell


class PXRecord(DNSRecord):
    """The X.400 to RFC 822 E-mail RR allows mapping of ITU X.400 format e-mail
    addresses to RFC 822 format e-mail addresses using a MIXER-conformant
    gateway.
    """
    record_type = 'PXRecord'
    preference = StringAttribute('preference')
    map822 = StringAttribute('map822')
    mapx400 = StringAttribute('mapx400')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.PXRRecord`'s rdata as a JSON
        blob
        """
        guts = super(PXRecord, self).rdata()
        shell = {'pxr_rdata': guts}
        return shell


class NSAPRecord(DNSRecord):
    """The Network Services Access Point record is the equivalent of an RR for
    ISO's Open Systems Interconnect (OSI) system in that it maps a host name to
    an endpoint address.
    """
    record_type = 'NSAPRecord'
    nsap = StringAttribute('nsap')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NSAPRecord`'s rdata as a JSON
        blob
        """
        guts = super(NSAPRecord, self).rdata()
        shell = {'nsap_rdata': guts}
        return shell


class RPRecord(DNSRecord):
    """The Respnosible Person record allows an email address and some optional
    human readable text to be associated with a host. Due to privacy and spam
    considerations, :class:`~dyn.tm.records.RPRecords` are not widely used on
    public servers but can provide very useful contact data during diagnosis
    and debugging network problems.
    """
    record_type = 'RPRecord'
    mbox = StringAttribute('mbox')
    txtdname = StringAttribute('txtdname')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.RPRecord`'s rdata as a JSON blob
        """
        guts = super(RPRecord, self).rdata()
        shell = {'rp_rdata': guts}
        return shell


class NSRecord(DNSRecord):
    """Nameserver Records are used to list all the nameservers that will
    respond authoritatively for a domain.
    """
    record_type = 'NSRecord'
    nsdname = StringAttribute('nsdname')
    service_class = StringAttribute('service_class')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NSRecord`'s rdata as a JSON blob
        """
        guts = super(NSRecord, self).rdata()
        shell = {'ns_rdata': guts}
        return shell


class SOARecord(DNSRecord):
    """The Start of Authority Record describes the global properties for the
    Zone (or domain). Only one SOA Record is allowed under a zone at any given
    time. NOTE: Dynect users do not have the permissions required to create or
    delete SOA records on the Dynect System.
    """
    record_type = 'SOARecord'
    rname = StringAttribute('rname')
    serial_style = StringAttribute('serial_style')
    minimum = IntegerAttribute('minimum')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.SOARecord`'s rdata as a JSON
        blob
        """
        guts = super(SOARecord, self).rdata()
        shell = {'soa_rdata': guts}
        return shell

    def delete(self):
        """Users can not POST or DELETE SOA Records"""
        pass


class SPFRecord(DNSRecord):
    """Sender Policy Framework Records are used to allow a recieving Message
    Transfer Agent (MTA) to verify that the originating IP of an email from a
    sender is authorized to send main for the sender's domain.
    """
    record_type = 'SPFRecord'
    txtdata = StringAttribute('txtdata')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.SPFRecord`'s rdata as a JSON
        blob
        """
        guts = super(SPFRecord, self).rdata()
        shell = {'spf_rdata': guts}
        return shell


class SRVRecord(DNSRecord):
    """The Services Record type allow a service to be associated with a host
    name. A user or application that wishes to discover where a service is
    located can interrogate for the relevant SRV that describes the service.
    """
    record_type = 'SRVRecord'
    txtdata = StringAttribute('txtdata')
    port = IntegerAttribute('port')
    priority = IntegerAttribute('priority')
    target = StringAttribute('target')
    weight = IntegerAttribute('weight')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.SRVRecord`'s rdata as JSON"""
        guts = super(SRVRecord, self).rdata()
        shell = {'srv_rdata': guts}
        return shell


class TLSARecord(DNSRecord):
    """The TLSA record is used to associate a TLS server
    certificate or public key with the domain name where the record is
    found, thus forming a "TLSA certificate association". Defined in RFC 6698
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.TLSARecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param cert_usage: Specifies the provided association that will be used
            to match the certificate presented in the TLS handshake. Example
            values: 0 (CA constraint), 1 (Service certificate constraint),
            2 (Trust anchor assertion ), 3 (Domain-issued certificate)
        :param selector: Specifies which part of the TLS certificate presented
            by the server will be matched against the association data. Example
            values: 0 (Full certificate), 1 (SubjectPublicKeyInfo)
        :param match_type: Specifies how the certificate association is
            presented. Example values: 0 (No hash used), 1 (SHA-256),
            2 (SHA-512)
        :param certificate: Full certificate or its SubjectPublicKeyInfo, or
            hash based on the matching type.
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(TLSARecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'TLSARecord'
        else:
            super(TLSARecord, self).__init__(zone, fqdn)
            self._record_type = 'TLSARecord'
            self._cert_usage = self._selector = None
            self._mathc_type = self._certificate = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) + len(kwargs) == 1:
                self._get_record(*args, **kwargs)
            elif 'cert_usage' in kwargs or 'selector' in \
                    kwargs or 'match_type' in kwargs or \
                    'certificate' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) >= 1:
                self._post(*args, **kwargs)

    def _post(self, cert_usage, selector, match_type, certificate, ttl=0):
        """Create a new :class:`~dyn.tm.records.TLSARecord` on the DynECT System
        """
        self._ttl = ttl
        self._cert_usage = cert_usage
        self._selector = selector
        self._match_type = match_type
        self._certificate = certificate
        self.api_args = {'rdata': {'cert_usage': self._cert_usage,
                                   'selector': self._selector,
                                   'match_type': self._match_type,
                                   'certificate': self._certificate},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.TLSARecord`'s rdata as a JSON blob
        """
        guts = super(TLSARecord, self).rdata()
        shell = {'tlsa_rdata': guts}
        return shell

    @property
    def cert_usage(self):
        """Specifies the provided association that will be used
        to match the certificate presented in the TLS handshake
        """
        return self._cert_usage

    @cert_usage.setter
    def cert_usage(self, value):
        self._cert_usage = value
        self.api_args['rdata']['cert_usage'] = self._cert_usage
        self._update_record(self.api_args)
        
    @property
    def selector(self):
        """Specifies which part of the TLS certificate presented
        by the server will be matched against the association data.
        """
        return self._selector

    @selector.setter
    def selector(self, value):
        self._selector = value
        self.api_args['rdata']['selector'] = self._selector
        self._update_record(self.api_args)

    @property
    def match_type(self):
        """Specifies how the certificate association is presented.
        """
        return self._match_type

    @match_type.setter
    def match_type(self, value):
        self._match_type = value
        self.api_args['rdata']['match_type'] = self._match_type
        self._update_record(self.api_args)
        
    @property
    def certificate(self):
        """Full certificate or its SubjectPublicKeyInfo, or
        hash based on the matching type
        """
        return self._certificate

    @certificate.setter
    def certificate(self, value):
        self._certificate = value
        self.api_args['rdata']['certificate'] = self._certificate
        self._update_record(self.api_args)
 

class TXTRecord(DNSRecord):
    """The Text record type provides the ability to associate arbitrary text
    with a name. For example, it can be used to provide a description of the
    host, service contacts, or any other required system information.
    """
    record_type = 'TXTRecord'
    txtdata = StringAttribute('txtdata')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.TXTRecord`'s rdata as a JSON
        blob
        """
        guts = super(TXTRecord, self).rdata()
        shell = {'txt_rdata': guts}
        return shell

RECORD_TYPES = {
    'A': ARecord, 'AAAA': AAAARecord, 'CERT': CERTRecord, 'CNAME': CNAMERecord,
    'DHCID': DHCIDRecord, 'DNAME': DNAMERecord, 'DNSKEY': DNSKEYRecord,
    'DS': DSRecord, 'KEY': KEYRecord, 'KX': KXRecord, 'LOC': LOCRecord,
    'IPSECKEY': IPSECKEYRecord, 'MX': MXRecord, 'NAPTR': NAPTRRecord,
    'PTR': PTRRecord, 'PX': PXRecord, 'NSAP': NSAPRecord, 'RP': RPRecord,
    'NS': NSRecord, 'SOA': SOARecord, 'SPF': SPFRecord, 'SRV': SRVRecord,
    'TXT': TXTRecord
}
