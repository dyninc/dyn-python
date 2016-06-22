# -*- coding: utf-8 -*-
from dyn.compat import force_unicode
from dyn.tm.utils import Active
from dyn.tm.session import DynectSession

__author__ = 'jnappi'
__all__ = ['ReverseDNS']


class ReverseDNS(object):
    """A DynECT ReverseDNS service"""
    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an new :class:`ReverseDNS` object instance

        :param zone: The zone under which this service will be attached
        :param fqdn: The fqdn where this service will be located
        :param hosts: A list of Hostnames of the zones where you want to track
            records
        :param netmask: A netmask to match A/AAAA rdata against. Matched
            records will get PTR records, any others won't
        :param ttl: TTL for the created PTR records. May be omitted, explicitly
            specified, set to 'default', or 'match'
        :param record_types: A list of which type of records this service will
            track. Note: Both A and AAAA can not be monitored by the same
            service
        """
        super(ReverseDNS, self).__init__()
        self._zone = zone
        self._fqdn = fqdn
        self.valid_record_types = ('A', 'AAAA', 'DynA', 'DynAAAA')
        self._hosts = self._netmask = self._ttl = self._record_types = None
        self._iptrack_id = self.uri = self._active = None
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) + len(kwargs) == 1:
            self._get(*args, **kwargs)
        else:
            self._post(*args, **kwargs)

    def _post(self, hosts, netmask, ttl='default', record_types=None):
        """Create a new ReverseDNS Service on the DynECT System"""
        self._hosts = hosts
        self._netmask = netmask
        self._ttl = ttl
        self._record_types = []
        if record_types is None:
            record_types = ['A']
        for record_type in record_types:
            if record_type in self.valid_record_types:
                self._record_types.append(record_type)
        api_args = {'record_types': self._record_types,
                    'hosts': self._hosts,
                    'netmask': self._netmask}
        if ttl is not None:
            api_args['ttl'] = self._ttl
        uri = '/IPTrack/{}/{}/'.format(self._zone, self._fqdn)
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])
        self.uri = '/IPTrack/{}/{}/{}/'.format(self._zone, self._fqdn,
                                               self._iptrack_id)

    def _get(self, service_id):
        """Build an object around an existing DynECT ReverseDNS Service"""
        self._iptrack_id = service_id
        uri = '/IPTrack/{}/{}/{}/'.format(self._zone, self._fqdn,
                                          self._iptrack_id)
        api_args = {}
        response = DynectSession.get_session().execute(uri, 'GET', api_args)
        self._build(response['data'])
        self.uri = '/IPTrack/{}/{}/{}/'.format(self._zone, self._fqdn,
                                               self._iptrack_id)

    def _update(self, api_args):
        """Update this object by making a PUT API call with the provided
        api_args
        """
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Build this object based on the data contained in an API response"""
        for key, val in data.items():
            if key == 'active':
                self._active = Active(val)
            else:
                setattr(self, '_' + key, val)

    @property
    def zone(self):
        """The zone that this ReverseDNS Service is attached to is a read-only
        attribute
        """
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """The fqdn that this ReverseDNS Service is attached to is a read-only
        attribute
        """
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def active(self):
        """Indicates whether or not the service is active. When setting
        directly, rather than using activate/deactivate valid arguments are 'Y'
        or True to activate, or 'N' or False to deactivate. Note: If your
        service is already active and you try to activate it, nothing will
        happen. And vice versa for deactivation.

        :returns: An :class:`Active` object representing the current state of
            this :class:`ReverseDNS` Service
        """
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
    def iptrack_id(self):
        """The unique System id for this service. This is a read-only property.
        """
        return self._iptrack_id

    @iptrack_id.setter
    def iptrack_id(self, value):
        pass

    @property
    def record_types(self):
        """Types of records to track"""
        return self._record_types

    @record_types.setter
    def record_types(self, value):
        self._record_types = value
        api_args = {'record_types': self._record_types,
                    'hosts': self._hosts}
        self._update(api_args)

    @property
    def hosts(self):
        """Hostnames of zones in your account where you want to track
        records
        """
        return self._hosts

    @hosts.setter
    def hosts(self, value):
        self._hosts = value
        api_args = {'record_types': self._record_types,
                    'hosts': self._hosts}
        self._update(api_args)

    @property
    def ttl(self):
        """TTL for the created PTR records. Omit to use zone default"""
        return int(self._ttl)

    @ttl.setter
    def ttl(self, value):
        self._ttl = value
        api_args = {'record_types': self._record_types,
                    'hosts': self._hosts,
                    'ttl': self._ttl}
        self._update(api_args)

    @property
    def netmask(self):
        """A netmask to match A/AAAA rdata against. Matched records will get
        PTR records, any others won't
        """
        return self._netmask

    @netmask.setter
    def netmask(self, value):
        self._netmask = value
        api_args = {'record_types': self._record_types,
                    'hosts': self._hosts,
                    'netmask': self._netmask}
        self._update(api_args)

    def activate(self):
        """Activate this ReverseDNS service"""
        api_args = {'activate': True}
        self._update(api_args)

    def deactivate(self):
        """Deactivate this ReverseDNS service"""
        api_args = {'deactivate': True}
        self._update(api_args)

    def delete(self):
        """Delete this ReverseDNS service from the DynECT System"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<ReverseDNS>: {}').format(self._fqdn)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
