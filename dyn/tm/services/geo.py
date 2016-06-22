# -*- coding: utf-8 -*-
"""This module contains API wrappers for the Geo TM service.
NOTE: The Geo Traffic Management Service is deprecated. Legacy users of the
service should contact Concierge for any questions on adding a Geo Traffic
Management  service to your zone. All other users should use Traffic Director
(DSF) instead.
"""
from dyn.tm.records import (ARecord, AAAARecord, CERTRecord,
                            CNAMERecord, DHCIDRecord, DNAMERecord,
                            DNSKEYRecord, DSRecord, KEYRecord, KXRecord,
                            LOCRecord, IPSECKEYRecord, MXRecord, NAPTRRecord,
                            PTRRecord, PXRecord, NSAPRecord, RPRecord,
                            NSRecord, SPFRecord, SRVRecord, TXTRecord)
from dyn.tm.session import DynectSession

__author__ = 'jnappi'
__all__ = ['GeoARecord', 'GeoAAAARecord', 'GeoCERTRecord', 'GeoCNAMERecord',
           'GeoDHCIDRecord', 'GeoDNAMERecord', 'GeoDNSKEYRecord',
           'GeoDSRecord', 'GeoKEYRecord', 'GeoKXRecord', 'GeoLOCRecord',
           'GeoIPSECKEYRecord', 'GeoMXRecord', 'GeoNAPTRRecord',
           'GeoPTRRecord', 'GeoPXRecord', 'GeoNSAPRecord', 'GeoRPRecord',
           'GeoNSRecord', 'GeoSPFRecord', 'GeoSRVRecord', 'GeoTXTRecord',
           'GeoRegionGroup', 'Geo']


class GeoARecord(ARecord):
    """An :class:`ARecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, weight, serve_count, label=None, ttl=None, *args,
                 **kwargs):
        """Create a :class:`GeoARecord` object

        :param weight: The weight for this :class:`GeoARecord`
        :param serve_count: The serve count for this :class:`GeoARecord`
        :param *args: Non keyword args for the associated :class:`ARecord`
        :param label: A unique label for this :class:`GeoARecord`
        :param ttl: TTL for the associated :class:`ARecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`ARecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoARecord, self).__init__(*args, **kwargs)
        self.weight = weight
        self.serve_count = serve_count
        self.label = label
        self._ttl = ttl


class GeoAAAARecord(AAAARecord):
    """An :class:`AAAARecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, weight, serve_count, label=None, ttl=None, *args,
                 **kwargs):
        """Create a :class:`GeoAAAARecord` object

        :param weight: The weight for this :class:`GeoAAAARecord`
        :param serve_count: The serve count for this :class:`GeoAAAARecord`
        :param *args: Non keyword args for the associated :class:`AAAARecord`
        :param label: A unique label for this :class:`GeoAAAARecord`
        :param ttl: TTL for the associated :class:`AAAARecord`
        :param **kwargs: Keyword args for the associated :class:`AAAARecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoAAAARecord, self).__init__(*args, **kwargs)
        self.weight = weight
        self.serve_count = serve_count
        self.label = label
        self._ttl = ttl


class GeoCERTRecord(CERTRecord):
    """An :class:`CERTRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoCERTRecord` object

        :param *args: Non keyword args for the associated :class:`CERTRecord`
        :param label: A unique label for this :class:`GeoCERTRecord`
        :param ttl: TTL for the associated :class:`CERTRecord`
        :param **kwargs: Keyword args for the associated :class:`CERTRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoCERTRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoCNAMERecord(CNAMERecord):
    """An :class:`CNAMERecord` object which is able to store additional data
    for use by a :class:`Geo` service.
    """
    def __init__(self, weight, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoCNAMERecord` object

        :param weight: The weight for this :class:`GeoCNAMERecord`
        :param *args: Non keyword args for the associated :class:`CNAMERecord`
        :param label: A unique label for this :class:`GeoCNAMERecord`
        :param ttl: TTL for the associated :class:`CNAMERecord`
        :param **kwargs: Keyword args for the associated :class:`CNAMERecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoCNAMERecord, self).__init__(*args, **kwargs)
        self.weight = weight
        self.label = label
        self._ttl = ttl


class GeoDHCIDRecord(DHCIDRecord):
    """An :class:`DHCIDRecord` object which is able to store additional data
    for use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoCNAMERecord` object

        :param *args: Non keyword args for the associated :class:`DHCIDRecord`
        :param label: A unique label for this :class:`GeoDHCIDRecord`
        :param ttl: TTL for the associated :class:`DHCIDRecord`
        :param **kwargs: Keyword args for the associated :class:`DHCIDRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoDHCIDRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoDNAMERecord(DNAMERecord):
    """An :class:`DNAMERecord` object which is able to store additional data
    for use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoDNAMERecord` object

        :param *args: Non keyword args for the associated :class:`DNAMERecord`
        :param label: A unique label for this :class:`GeoDNAMERecord`
        :param ttl: TTL for the associated :class:`DNAMERecord`
        :param **kwargs: Keyword args for the associated :class:`DNAMERecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoDNAMERecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoDNSKEYRecord(DNSKEYRecord):
    """An :class:`DNSKEYRecord` object which is able to store additional data
    for use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoDNSKEYRecord` object

        :param *args: Non keyword args for the associated :class:`DNSKEYRecord`
        :param label: A unique label for this :class:`GeoDNSKEYRecord`
        :param ttl: TTL for the associated :class:`DNSKEYRecord`
        :param **kwargs: Keyword args for the associated :class:`DNSKEYRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoDNSKEYRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoDSRecord(DSRecord):
    """An :class:`DSRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoDSRecord` object

        :param *args: Non keyword args for the associated :class:`DSRecord`
        :param label: A unique label for this :class:`GeoDSRecord`
        :param ttl: TTL for the associated :class:`DSRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`DSRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoDSRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoKEYRecord(KEYRecord):
    """An :class:`KEYRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoKEYRecord` object

        :param *args: Non keyword args for the associated :class:`KEYRecord`
        :param label: A unique label for this :class:`GeoKEYRecord`
        :param ttl: TTL for the associated :class:`KEYRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`KEYRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoKEYRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoKXRecord(KXRecord):
    """An :class:`KXRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoKXRecord` object

        :param *args: Non keyword args for the associated :class:`KXRecord`
        :param label: A unique label for this :class:`GeoKXRecord`
        :param ttl: TTL for the associated :class:`KXRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`KXRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoKXRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoLOCRecord(LOCRecord):
    """An :class:`LOCRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoLOCRecord` object

        :param *args: Non keyword args for the associated :class:`LOCRecord`
        :param label: A unique label for this :class:`GeoLOCRecord`
        :param ttl: TTL for the associated :class:`LOCRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`LOCRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoLOCRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoIPSECKEYRecord(IPSECKEYRecord):
    """An :class:`IPSECKEYRecord` object which is able to store additional data
    for use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoIPSECKEYRecord` object

        :param *args: Non keyword args for the associated
            :class:`IPSECKEYRecord`
        :param label: A unique label for this :class:`GeoIPSECKEYRecord`
        :param ttl: TTL for the associated :class:`IPSECKEYRecord`, will
            override a ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated
            :class:`IPSECKEYRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoIPSECKEYRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoMXRecord(MXRecord):
    """An :class:`MXRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoMXRecord` object

        :param *args: Non keyword args for the associated :class:`MXRecord`
        :param label: A unique label for this :class:`GeoMXRecord`
        :param ttl: TTL for the associated :class:`MXRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`MXRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoMXRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoNAPTRRecord(NAPTRRecord):
    """An :class:`NAPTRRecord` object which is able to store additional data
    for use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoNAPTRRecord` object

        :param *args: Non keyword args for the associated :class:`NAPTRRecord`
        :param label: A unique label for this :class:`GeoNAPTRRecord`
        :param ttl: TTL for the associated :class:`NAPTRRecord`, will override
            a ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`NAPTRRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoNAPTRRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoPTRRecord(PTRRecord):
    """An :class:`PTRRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoPTRRecord` object

        :param *args: Non keyword args for the associated :class:`PTRRecord`
        :param label: A unique label for this :class:`GeoPTRRecord`
        :param ttl: TTL for the associated :class:`PTRRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`PTRRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoPTRRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoPXRecord(PXRecord):
    """An :class:`PXRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoPXRecord` object

        :param *args: Non keyword args for the associated :class:`PXRecord`
        :param label: A unique label for this :class:`GeoPXRecord`
        :param ttl: TTL for the associated :class:`PXRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`PXRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoPXRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoNSAPRecord(NSAPRecord):
    """An :class:`NSAPRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoNSAPRecord` object

        :param *args: Non keyword args for the associated :class:`NSAPRecord`
        :param label: A unique label for this :class:`GeoNSAPRecord`
        :param ttl: TTL for the associated :class:`NSAPRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`NSAPRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoNSAPRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoRPRecord(RPRecord):
    """An :class:`RPRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoRPRecord` object

        :param *args: Non keyword args for the associated :class:`RPRecord`
        :param label: A unique label for this :class:`GeoRPRecord`
        :param ttl: TTL for the associated :class:`RPRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`RPRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoRPRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoNSRecord(NSRecord):
    """An :class:`NSRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoNSRecord` object

        :param *args: Non keyword args for the associated :class:`NSRecord`
        :param label: A unique label for this :class:`GeoNSRecord`
        :param ttl: TTL for the associated :class:`NSRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`NSRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoNSRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoSPFRecord(SPFRecord):
    """An :class:`SPFRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoSPFRecord` object

        :param *args: Non keyword args for the associated :class:`SPFRecord`
        :param label: A unique label for this :class:`GeoSPFRecord`
        :param ttl: TTL for the associated :class:`SPFRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`SPFRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoSPFRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoSRVRecord(SRVRecord):
    """An :class:`SRVRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoSRVRecord` object

        :param *args: Non keyword args for the associated :class:`SRVRecord`
        :param label: A unique label for this :class:`GeoSRVRecord`
        :param ttl: TTL for the associated :class:`SRVRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`SRVRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoSRVRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoTXTRecord(TXTRecord):
    """An :class:`TXTRecord` object which is able to store additional data for
    use by a :class:`Geo` service.
    """
    def __init__(self, label=None, ttl=None, *args, **kwargs):
        """Create a :class:`GeoTXTRecord` object

        :param *args: Non keyword args for the associated :class:`TXTRecord`
        :param label: A unique label for this :class:`GeoTXTRecord`
        :param ttl: TTL for the associated :class:`TXTRecord`, will override a
            ttl specified in *args or **kwargs
        :param **kwargs: Keyword args for the associated :class:`TXTRecord`
        """
        # Set api flag so the record isn't really created
        kwargs['create'] = False
        super(GeoTXTRecord, self).__init__(*args, **kwargs)
        self.label = label
        self._ttl = ttl


class GeoRegionGroup(object):
    """docstring for GeoRegionGroup"""
    def __init__(self, countries, name, geo_records, **kwargs):
        """Create a :class:`GeoRegionGroup` object

        :param countries: A list of ISO-3166 two letter codes to represent the
            names of countries and their subdivisions or one of the predefined
            groups.
        :param name: Name of this :class:`GeoRegionGroup`
        :param geo_records: A `list` of custom Geo DNSRecord subclass type
            objects
        """
        super(GeoRegionGroup, self).__init__()
        self.uri = None
        self._service_name = self._group_name = self._countries = None
        self._countries = countries
        self._name = name
        self.geo_records = geo_records
        # TODO: implement return data (GET) object creation
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)

    def _post(self, countries, name, geo_records):
        self._countries = countries
        self._name = name
        self.geo_records = geo_records
        api_args = {'service_name': self._service_name,
                    'group_name': self._group_name,
                    'countries': self._countries, 'name': self._name}
        return api_args

    def _get(self):
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    @property
    def countries(self):
        return self._countries

    def delete(self):
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class Geo(object):
    """docstring for Geo"""
    def __init__(self, service_name, *args, **kwargs):
        """Create a new :class:`Geo` object

        :param service_name: The name of this Geo Service
        :param groups: A list of :class:`GeoRegionGroup`'s
        :param nodes: A list of :class:`GeoNode`'s
        :param ttl: Time to Live for each record in the service
        """
        super(Geo, self).__init__()
        self._service_name = service_name
        self.uri = '/Geo/{}/'.format(self._service_name)
        self._groups = self._nodes = self._ttl = None
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)

    def _post(self, groups, ttl=None):
        """Create a new :class:`Geo` service on the DynECT System"""
        self._groups = groups
        self._ttl = ttl
        api_args = {'groups': []}
        nodes = []
        for group in groups:
            weight = {}
            serve_count = {}
            ttls = {}
            label = {}
            rdata = {}
            for record in group.geo_records:
                weight_name = ''.join([record.rec_name, '_weight'])
                serve_name = ''.join([record.rec_name, '_serve_count'])
                ttl_name = ''.join([record.rec_name, '_ttl'])
                label_name = ''.join([record.rec_name, '_label'])
                rdata_name = ''.join([record.rec_name, '_rdata'])
                # Build weight hash
                if hasattr(record, 'weight'):
                    if weight_name in weight:
                        weight[weight_name].append(record.weight)
                    else:
                        weight[weight_name] = [record.weight]
                # Build serve_count hash
                if hasattr(record, 'serve_count'):
                    serve_count[serve_name] = str(record.serve_count)
                # Build ttl hash
                if ttl_name in serve_count:
                    ttls[ttl_name] = str(record.ttl) or str(self._ttl)
                # Build label hash
                autolabel = ''
                if label_name in label:
                    label[label_name].append(record.label or autolabel)
                else:
                    label[label_name] = [record.label or autolabel]
                # Build rdata hash
                if rdata_name in rdata:
                    rdata[rdata_name].append(record.geo_rdata)
                else:
                    rdata[rdata_name] = [record.geo_rdata]
                nodes.append(record.geo_node)
            group_data = {'weight': weight, 'serve_count': serve_count,
                          'ttl': ttls, 'label': label, 'rdata': rdata,
                          'countries': group.countries, 'name': group._name}
            api_args['groups'].append(group_data)
        if self._ttl:
            api_args['ttl'] = self._ttl
        api_args['nodes'] = nodes
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        for key, val in response['data'].items():
            if key == 'groups':
                pass
            elif key == 'nodes':
                pass
            else:
                setattr(self, '_' + key, val)

    def _get(self):
        """Get an existing :class:`Geo` service from the DynECT System"""
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            if key == 'groups':
                pass
            elif key == 'nodes':
                pass
            else:
                setattr(self, '_' + key, val)

    def _update(self, api_args):
        """Private Update method"""
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key == 'groups':
                pass
            elif key == 'nodes':
                pass
            else:
                setattr(self, '_' + key, val)

    @property
    def service_name(self):
        return self._service_name

    @service_name.setter
    def service_name(self, new_name):
        self._service_name = new_name
        api_args = {'new_name': self._service_name}
        self._update(api_args)
        self.uri = '/Geo/{}/'.format(self._service_name)

    @property
    def groups(self):
        return self._groups

    @groups.setter
    def groups(self, value):
        self._groups = value
        api_args = {'groups': self._groups.to_json()}
        self._update(api_args)

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        self._nodes = value
        api_args = {'nodes': self._nodes.to_json()}
        self._update(api_args)

    def activate(self):
        """Activate this :class:`Geo` service on the DynECT System"""
        api_args = {'activate': True}
        self._update(api_args)

    def deactivate(self):
        """Deactivate this :class:`Geo` service on the DynECT System"""
        api_args = {'deactivate': True}
        self._update(api_args)

    def delete(self):
        """Delete this :class:`Geo` service from the DynECT System"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)
