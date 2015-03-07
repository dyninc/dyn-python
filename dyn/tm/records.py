# -*- coding: utf-8 -*-
"""This module contains class objects for all supported DynDNS Record types

These DNS_Records should really only need to be created via a zone instance but
could also be created independently if passed valid zone, fqdn data
"""
from .session import DynectSession, DNSAPIObject
from ..core import (ImmutableAttribute, IntegerAttribute, StringAttribute,
                    ValidatedAttribute)
from ..compat import force_unicode

__author__ = 'jnappi'
__all__ = ['DNSRecord', 'ARecord', 'AAAARecord', 'CERTRecord', 'CNAMERecord',
           'DHCIDRecord', 'DNAMERecord', 'DNSKEYRecord', 'DSRecord',
           'KEYRecord', 'KXRecord', 'LOCRecord', 'IPSECKEYRecord', 'MXRecord',
           'NAPTRRecord', 'PTRRecord', 'PXRecord', 'NSAPRecord', 'RPRecord',
           'NSRecord', 'SOARecord', 'SPFRecord', 'SRVRecord', 'TLSARecord',
           'TXTRecord', 'RECORD_TYPES']


# noinspection PyMissingConstructor
class DNSRecord(DNSAPIObject):
    """Base record object contains functionality to be used across all other
    record type objects
    """
    #: Name of zone that this record belongs to
    zone = ImmutableAttribute('zone')

    #: The fully qualified domain name where this record can be found
    fqdn = ImmutableAttribute('fqdn')

    #: The unique DynECT System id for this record. Note, that this id will
    #: change when a record is updated. Outdated record id's can still be used
    #: to retrieve older versions of records from the DynECT system
    record_id = ImmutableAttribute('record_id')

    #: The time to live for this DNS Record
    ttl = IntegerAttribute('ttl')

    #: A :const:`str` representation of what type this record is
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
        response = DynectSession.post(self.uri, api_args)
        self._build(response['data'])

    def _get(self, record_id):
        """Get an existing record object from the DynECT System

        :param record_id: The id of the record you would like to get
        """
        uri = self.uri + '{0}/'.format(record_id)
        response = DynectSession.get(uri)
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

    #: IPv4 address for the record
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

    #: IPv6 address for the record
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

    #: Numeric value for the certificate type
    format = IntegerAttribute('format')

    #: Numeric value for the public key certificate
    tag = IntegerAttribute('tag')

    #: Public key algorithm number used to generate the certificate
    algorithm = StringAttribute('algorithm')

    #: The public key certificate
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

    #: The hostname that this CNAME Record points to
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

    #: Base-64 encoded digest of DHCP data
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

    #: Target hostname pointed to by this :class:`~dyn.tm.records.DNAMERecord`
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

    #: Numeric value for protocol
    protocol = IntegerAttribute('protocol')

    #: The public key for the DNSSEC signed zone
    public_key = StringAttribute('public_key')

    #: Numeric value representing the public key encryption algorithm which
    #: will sign the zone. Must be one of 1 (RSA-MD5), 2 (Diffie-Hellman),
    #: 3 (DSA/SHA-1), 4 (Elliptic Curve), or 5 (RSA-SHA-1)
    algorithm = ValidatedAttribute('algorithm', validator=range(1, 6))

    #: Numeric value confirming this is the zone's DNSKEY
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

    #: The digest in hexadecimal form. 20-byte, hexadecimal-encoded, one-way
    #: hash of the DNSKEY record surrounded by parenthesis characters '(' & ')'
    digest = StringAttribute('digest')

    #: The digest mechanism to use to verify the digest
    keytag = IntegerAttribute('keytag')

    #: Numeric value representing the public key encryption algorithm which
    #: will sign the zone. Must be one of 1 (RSA-MD5), 2 (Diffie-Hellman),
    #: 3 (DSA/SHA-1), 4 (Elliptic Curve), or 5 (RSA-SHA-1)
    algorithm = ValidatedAttribute('algorithm', validator=range(1, 6))

    #: the digest mechanism to use to verify the digest. Valid values are
    #: 'SHA1' or 'SHA256'
    digtype = ValidatedAttribute('digtype', validator=('SHA1', 'SHA256'))

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DSRecord`'s rdata as a JSON blob
        """
        guts = super(DSRecord, self).rdata()
        shell = {'ds_rdata': guts}
        return shell


class IPSECKEYRecord(DNSRecord):
    """The IPSECKEY is used for storage of keys used specifically for IPSec
    oerations
    """
    record_type = 'IPSECKEYRecord'

    #: Indicates priority among multiple IPSECKEYS. Lower numbers are higher
    #: priority
    precedence = IntegerAttribute('precedence')

    #: Gateway type. Must be one of 0, 1, 2, or 3
    gatetype = ValidatedAttribute('gatetype', validator=range(0, 4))

    #: Public key's cryptographic algorithm and format. Must be one of 0, 1, or
    #: 2
    algorithm = ValidatedAttribute('algorithm', validator=range(0, 3))

    #: Gateway used to create IPsec tunnel. Based on Gateway type
    gateway = IntegerAttribute('gateway')

    #: Base64 encoding of the public key. Whitespace is allowed
    public_key = StringAttribute('public_key')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.IPSECKEYRecord`'s rdata as a
        JSON blob
        """
        guts = super(IPSECKEYRecord, self).rdata()
        shell = {'ipseckey_rdata': guts}
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

    #: Numeric value representing the public key encryption algorithm which
    #: will sign the zone. Must be one of 1 (RSA-MD5), 2 (Diffie-Hellman),
    #: 3 (DSA/SHA-1), 4 (Elliptic Curve), or 5 (RSA-SHA-1)
    algorithm = ValidatedAttribute('algorithm', validator=range(1, 6))

    #: See RFC 2535 for information on valid KEY record flags
    flags = IntegerAttribute('flags')

    #: Numeric identifier of the protocol for this KEY record
    protocol = IntegerAttribute('protocol')

    #: The public key for this record
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

    #: Hostname that will act as the Key Exchanger. The hostname must have a
    #: :class:`~dyn.tm.records.CNAMERecord`, an
    #: :class:`~dyn.tm.records.ARecord` and/or an
    #: :class:`~dyn.tm.records.AAAARecord` associated with it
    exchange = StringAttribute('exchange')

    #: Numeric value for priority usage. Lower value takes precedence over
    #: higher value where two records of the same type exist on the zone/node
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

    #: Measured in meters above sea level
    altitude = IntegerAttribute('altitude')

    #: Measured in degrees, minutes, and seconds with N/S indicator for North
    #: and South
    latitude = IntegerAttribute('latitude')

    #: Measured in degrees, minutes, and seconds with E/W indicator for East
    #: and West
    longitude = IntegerAttribute('longitude')

    horiz_pre = StringAttribute('horiz_pre')
    size = IntegerAttribute('size')
    version = ValidatedAttribute('version', validator=(0,), default=0)
    vert_pre = StringAttribute('vert_pre')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.LOCRecord`'s rdata as a JSON
        blob
        """
        guts = super(LOCRecord, self).rdata()
        shell = {'loc_rdata': guts}
        return shell


class MXRecord(DNSRecord):
    """The "Mail Exchanger" record type specifies the name and relative
    preference of mail servers for a Zone. Defined in RFC 1035
    """
    record_type = 'MXRecord'

    #: Hostname of the server responsible for accepting mail messages in the
    #: zone
    exchange = StringAttribute('exchange')

    #: Numeric value for priority usage. Lower value takes precedence over
    #: higher value where two records of the same type exist on the zone/node.
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

    #: Indicates the required priority for processing NAPTR records. Lowest
    #: value is used first.
    order = IntegerAttribute('order')

    #: Indicates priority where two or more NAPTR records have identical order
    #: values. Lowest value is used first.
    preference = IntegerAttribute('preference')

    #: Always starts with 'e2u+' (E.164 to URI). After the 'e2u+' there is a
    #: string that defines the type and optionally the subtype of the URI where
    #: this :class:`~dyn.tm.records.NAPTRRecord` points.
    services = StringAttribute('services')

    #: The NAPTR record accepts regular expressions
    regexp = StringAttribute('regexp')

    #: The next domain name to find. Only applies if this
    #: :class:`~dyn.tm.records.NAPTRRecord` is non-terminal.
    replacement = StringAttribute('replacement')

    #: Should be the letter 'U'. This indicates that this is a terminal NAPTR
    #: record
    flags = StringAttribute('flags', default='U')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NAPTRRecord`'s rdata as a JSON
        blob
        """
        guts = super(NAPTRRecord, self).rdata()
        shell = {'naptr_rdata': guts}
        return shell


class NSAPRecord(DNSRecord):
    """The Network Services Access Point record is the equivalent of an RR for
    ISO's Open Systems Interconnect (OSI) system in that it maps a host name to
    an endpoint address.
    """
    record_type = 'NSAPRecord'

    #: Hex-encoded NSAP identifier
    nsap = StringAttribute('nsap')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NSAPRecord`'s rdata as a JSON
        blob
        """
        guts = super(NSAPRecord, self).rdata()
        shell = {'nsap_rdata': guts}
        return shell


class NSRecord(DNSRecord):
    """Nameserver Records are used to list all the nameservers that will
    respond authoritatively for a domain.
    """
    record_type = 'NSRecord'

    #: Hostname of the authoritative Nameserver for the zone
    nsdname = StringAttribute('nsdname')

    #: Hostname of the authoritative Nameserver for the zone
    service_class = StringAttribute('service_class')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NSRecord`'s rdata as a JSON blob
        """
        guts = super(NSRecord, self).rdata()
        shell = {'ns_rdata': guts}
        return shell


class PTRRecord(DNSRecord):
    """Pointer Records are used to reverse map an IPv4 or IPv6 IP address to a
    host name
    """
    record_type = 'PTRRecord'

    #: The hostname where the IP address should be directed
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

    #: Sets priority for processing records of the same type. Lowest value is
    #: processed first.
    preference = StringAttribute('preference')

    #: mail hostname
    map822 = StringAttribute('map822')

    #: The domain name derived from the X.400 part of MCGAM
    mapx400 = StringAttribute('mapx400')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.PXRRecord`'s rdata as a JSON
        blob
        """
        guts = super(PXRecord, self).rdata()
        shell = {'pxr_rdata': guts}
        return shell


class RPRecord(DNSRecord):
    """The Respnosible Person record allows an email address and some optional
    human readable text to be associated with a host. Due to privacy and spam
    considerations, :class:`~dyn.tm.records.RPRecords` are not widely used on
    public servers but can provide very useful contact data during diagnosis
    and debugging network problems.
    """
    record_type = 'RPRecord'

    #: Email address of the Responsible Person.
    mbox = StringAttribute('mbox')

    #: Hostname where a TXT record exists with more information on the
    #: responsible person.
    txtdname = StringAttribute('txtdname')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.RPRecord`'s rdata as a JSON blob
        """
        guts = super(RPRecord, self).rdata()
        shell = {'rp_rdata': guts}
        return shell


class SOARecord(DNSRecord):
    """The Start of Authority Record describes the global properties for the
    Zone (or domain). Only one SOA Record is allowed under a zone at any given
    time. NOTE: Dynect users do not have the permissions required to create or
    delete SOA records on the Dynect System.
    """
    record_type = 'SOARecord'

    #: Domain name which specifies the mailbox of the person responsible for
    #: this zone
    rname = StringAttribute('rname')

    #: The style of the zone's serial
    serial_style = StringAttribute('serial_style')

    #: The minimum TTL for this :class:`~dyn.tm.records.SOARecord`'s zone
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

    #: Free text containing SPF record information
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

    #: Indicates the port where the service is running
    port = IntegerAttribute('port')

    #: Numeric value for priority usage. Lower value takes precedence over
    #: higher value where two records of the same type exist on the zone/node
    priority = IntegerAttribute('priority')

    #: The domain name of a host where the service is running on the specified
    #: port
    target = StringAttribute('target')

    #: Secondary prioritizing of records to serve. Records of equal priority
    #: should be served based on their weight. Higher values are served more
    #: often
    weight = IntegerAttribute('weight')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.SRVRecord`'s rdata as JSON"""
        guts = super(SRVRecord, self).rdata()
        shell = {'srv_rdata': guts}
        return shell


class TLSARecord(DNSRecord):
    """The TLSA record is used to associate a TLS server certificate or public
    key with the domain name where the record is found, thus forming a
    "TLSA certificate association". Defined in RFC 6698
    """
    record_type = 'TLSARecord'

    #: Specifies the provided association that will be used to match the
    #: certificate presented in the TLS handshake
    cert_usage = IntegerAttribute('cert_usage')

    #: Specifies which part of the TLS certificate presented by the server will
    #: be matched against the association data.
    selector = IntegerAttribute('selector')

    #: Specifies how the certificate association is presented.
    match_type = IntegerAttribute('match_type')

    #: Full certificate or its SubjectPublicKeyInfo, or hash based on the
    #: matching type
    certificate = StringAttribute('certificate')

    def rdata(self):
        """Return this :class:`~dyn.tm.records.TLSARecord`'s rdata as a JSON
        blob
        """
        guts = super(TLSARecord, self).rdata()
        shell = {'tlsa_rdata': guts}
        return shell
 

class TXTRecord(DNSRecord):
    """The Text record type provides the ability to associate arbitrary text
    with a name. For example, it can be used to provide a description of the
    host, service contacts, or any other required system information.
    """
    record_type = 'TXTRecord'

    #: Free form text
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
    'TLSA': TLSARecord, 'TXT': TXTRecord
}
