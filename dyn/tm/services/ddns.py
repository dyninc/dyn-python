# -*- coding: utf-8 -*-
"""This module contains API Wrapper implementations of the Dynamic DNS service
"""
from dyn.compat import force_unicode
from dyn.tm.accounts import User
from dyn.tm.session import DynectSession
from dyn.tm.utils import Active

__author__ = 'jnappi'
__all__ = ['DynamicDNS']


class DynamicDNS(object):
    """DynamicDNS is a service which aliases a dynamic IP Address to a static
    hostname
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a new :class:`DynamicDNS` service object

        :param zone: The zone to attach this DDNS Service to
        :param fqdn: The FQDN of the node where this service will be attached
        :param record_type: Either A, for IPv4, or AAAA, for IPv6
        :param address: IPv4 or IPv6 address for the service
        :param full_setup: Flag to indicate a user is specified
        :param user: Name of the user to create, or the name of an existing
            update user to allow access to this service
        """
        super(DynamicDNS, self).__init__()
        self._zone = zone
        self._fqdn = fqdn
        self._record_type = self._address = self.uri = self._user = None
        self._active = None
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                if key == 'active':
                    self._active = Active(val)
                else:
                    setattr(self, '_' + key, val)
        elif len(args) + len(kwargs) == 1:
            self._get(*args, **kwargs)
        elif 'record_type' in kwargs and len(kwargs) == 1:
            self._get(*args, **kwargs)
        else:
            self._post(*args, **kwargs)

    def _get(self, record_type=None):
        """Build an object around an existing DynECT DynamicDNS Service"""
        self._record_type = record_type
        self.uri = '/DDNS/{}/{}/{}/'.format(self._zone, self._fqdn,
                                            self._record_type)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            if key == 'active':
                self._active = Active(val)
            else:
                setattr(self, '_' + key, val)

    def _post(self, record_type, address, user=None):
        """Create a new DynamicDNS Service on the DynECT System"""
        self._record_type = record_type
        self._address = address
        if user:
            self._user = user
        self.uri = '/DDNS/{}/{}/{}/'.format(self._zone, self._fqdn,
                                            self._record_type)
        api_args = {'address': self._address}
        if user:
            api_args['user'] = self._user
            api_args['full_setup'] = True
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        for key, val in response['data'].items():
            if user:
                if key == 'ddns':
                    for ddns_key, ddns_val in val.items():
                        setattr(self, '_' + ddns_key, ddns_val)
                if key == 'new_user':
                    user_name = val['user_name']
                    del val['user_name']
                    self._user = User(user_name, api=False, **val)
            elif key == 'active':
                self._active = Active(val)
            else:
                setattr(self, '_' + key, val)

    @property
    def zone(self):
        """The zone that this DynamicDNS Service is attached to is a read-only
        attribute
        """
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """The fqdn that this DynamicDNS Service is attached to is a read-only
        attribute
        """
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def active(self):
        """Returns whether or not this :class:`DynamicDNS` Service is currently
        active. When setting directly, rather than using activate/deactivate
        valid arguments are 'Y' or True to activate, or 'N' or False to
        deactivate. Note: If your service is already active and you try to
        activate it, nothing will happen. And vice versa for deactivation.

        :returns: An :class:`Active` object representing the current state of
            this :class:`DynamicDNS` Service
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
    def record_type(self):
        """The record_type of a DDNS Service is a read-only attribute"""
        return self._record_type

    @record_type.setter
    def record_type(self, value):
        pass

    @property
    def user(self):
        """The :class:`User` attribute of a DDNS Service is a read-only
        attribute"""
        return self._user

    @user.setter
    def user(self, value):
        pass

    @property
    def address(self):
        """IPv4 or IPv6 address for this DynamicDNS service"""
        return self._address

    @address.setter
    def address(self, value):
        self._address = value
        api_args = {'address': self._address}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def activate(self):
        """Activate this Dynamic DNS service"""
        api_args = {'activate': True}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def deactivate(self):
        """Deactivate this Dynamic DNS service"""
        api_args = {'deactivate': True}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def reset(self):
        """Resets the abuse count on this Dynamic DNS service"""
        api_args = {'reset': True}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def delete(self):
        """Delete this Dynamic DNS service from the DynECT System"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<DynamicDNS>: {}').format(self._fqdn)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
