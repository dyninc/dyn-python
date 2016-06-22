# -*- coding: utf-8 -*-
"""This module contains API Wrapper implementations of the HTTP Redirect
service
"""
from dyn.compat import force_unicode
from dyn.tm.session import DynectSession

__author__ = 'xorg'
__all__ = ['HTTPRedirect']


class HTTPRedirect(object):
    """HTTPRedirect is a service which sets up a redirect to the specified
    URL.//
    """
    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a new :class:`HTTPRedirect` service object

        :param zone: The zone to attach this HTTPRedirect Service to
        :param fqdn: The FQDN of the node where this service will be attached
        :param code:  HTTP response code to return for redirection.
        :param url: The target URL where the client is sent. Must begin with
            either http:// or https://
        :param keep_uri: A flag indicating whether the redirection should
            include the originally requested URI.
        """
        super(HTTPRedirect, self).__init__()
        self._zone = zone
        self._fqdn = fqdn
        self._code = self._url = self._keep_uri = None
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) + len(kwargs) == 1:
            self._get()
        else:
            self._post(*args, **kwargs)

    def _get(self):
        """Build an object around an existing DynECT HTTPRedirect Service"""
        self.uri = '/HTTPRedirect/{}/{}/'.format(self._zone, self._fqdn)
        api_args = {'detail': 'Y'}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def _post(self, code, keep_uri, url):
        """Create a new HTTPRedirect Service on the DynECT System"""
        self._code = code
        self._keep_uri = keep_uri
        self._url = url
        self.uri = '/HTTPRedirect/{}/{}/'.format(self._zone, self._fqdn)
        api_args = {'code': self._code, 'keep_uri': self._keep_uri,
                    'url': self._url}
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def _update(self, **kwargs):
        """Update an existing HTTPRedirect Service on the DynECT System"""
        self._code = kwargs.get('code', self._code)
        self._keep_uri = kwargs.get('keep_uri', self.keep_uri)
        self._url = kwargs.get('url', self._url)
        self.uri = '/HTTPRedirect/{}/{}/'.format(self._zone, self._fqdn)
        api_args = {'code': self._code, 'keep_uri': self._keep_uri,
                    'url': self._url}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    @property
    def zone(self):
        """The zone that this HTTPRedirect Service is attached to is a
        read-only attribute
        """
        self._get()
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """The fqdn that this HTTPRedirect Service is attached to is a
        read-only attribute
        """
        self._get()
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def code(self):
        """HTTP response code to return for redirection.
           Valid values:
            301 – Permanent redirect
            302 – Temporary redirect
        """
        self._get()
        return self._code

    @code.setter
    def code(self, value):
        self._update(code=value)

    @property
    def keep_uri(self):
        """A flag indicating whether the redirection should include the
        originally requested URI.
           Valid values: Y, N
        """
        self._get()
        return self._keep_uri

    @keep_uri.setter
    def keep_uri(self, value):
        self._update(keep_uri=value)

    @property
    def url(self):
        """The target URL where the client is sent. Must begin with either
        http:// or https://
        """
        self._get()
        return self._url

    @url.setter
    def url(self, value):
        self._update(url=value)

    def delete(self, publish='Y'):
        """Delete this HTTPRedirect service from the DynECT System
        publish='N' can be passed into this function to do a soft-delete which
        will be acted upon during a zone publish.
        """
        api_args = {'publish': publish}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<HTTPRedirect>: {}').format(self._fqdn)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
