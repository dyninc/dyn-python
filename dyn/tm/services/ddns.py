# -*- coding: utf-8 -*-
"""This module contains API Wrapper implementations of the Dynamic DNS service
"""
from ..utils import Active
from ..session import DynectSession, DNSAPIObject
from ..accounts import User
from ...core import APIService, ImmutableAttribute, StringAttribute
from ...compat import force_unicode

__author__ = 'jnappi'
__all__ = ['DynamicDNS']


class DynamicDNS(APIService, DNSAPIObject):
    """DynamicDNS is a service which aliases a dynamic IP Address to a static
    hostname
    """
    uri = '/DDNS/{zone}/{fqdn}/{rr_type}/'

    #: The zone to attach this :class:`DynamicDNS` Service to
    zone = ImmutableAttribute('zone')

    #: The FQDN of the node where this service will be attached
    fqdn = ImmutableAttribute('fqdn')

    #: Either A, for IPv4, or AAAA, for IPv6
    record_type = ImmutableAttribute('record_type')

    #: IPv4 (if `record_type` is A) or IPv6 (if `record_type` is AAAA) address
    #: for the service
    address = StringAttribute('address')

    #: Name of the user to create, or the name of an existing update user to
    #: allow access to this service
    user = ImmutableAttribute('user')

    def __init__(self, zone, fqdn, record_type, *args, **kwargs):
        """Create a new :class:`DynamicDNS` service object

        :param zone: The zone to attach this DDNS Service to
        :param fqdn: The FQDN of the node where this service will be attached
        :param record_type: Either A, for IPv4, or AAAA, for IPv6
        :param address: IPv4 or IPv6 address for the service
        :param full_setup: Flag to indicate a user is specified
        :param user: Name of the user to create, or the name of an existing
            update user to allow access to this service
        """
        self._active = None
        self.uri = self.uri.format(zone=zone, fqdn=fqdn, rr_type=record_type)
        self.zone = zone
        self.fqdn = fqdn
        super(DynamicDNS, self).__init__(*args, **kwargs)

    def _build(self, data):
        if 'active' in data:
            self._active = Active(data.pop('active'))
        if 'ddns' in data and 'new_user' in data:
            for ddns_key, ddns_val in data.pop('ddns'):
                setattr(self, '_' + ddns_key, ddns_val)
            user_data = data.pop('new_user')
            username = user_data.pop('user_name')
            self._user = User(data.pop(username, api=False, **user_data))
        super(DynamicDNS, self)._build(data)

    def _post(self, address, user=None):
        """Create a new DynamicDNS Service on the DynECT System"""
        api_args = {'address': address}
        if user:
            api_args['user'] = user
            api_args['full_setup'] = True
        resp = DynectSession.post(self.uri, api_args)
        self._build(resp['data'])

    def reset(self):
        """Resets the abuse count on this Dynamic DNS service"""
        self._update(reset=True)

    def __str__(self):
        return force_unicode('<DynamicDNS>: {0}').format(self.fqdn)
