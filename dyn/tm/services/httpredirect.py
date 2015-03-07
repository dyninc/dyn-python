# -*- coding: utf-8 -*-
"""This module contains API Wrapper implementations of the HTTP Redirect
service
"""
from ...core import (ImmutableAttribute, ValidatedAttribute, StringAttribute,
                     BooleanAttribute)
from ..session import DynectSession, DNSAPIObject
from ...compat import force_unicode

__author__ = 'xorg'
__all__ = ['HTTPRedirect']


class HTTPRedirect(DNSAPIObject):
    """HTTPRedirect is a service which sets up a redirect to the specified URL.//
    """
    uri = '/HTTPRedirect/{zone}/{fqdn}/'

    #: The zone that this HTTPRedirect Service is attached to
    zone = ImmutableAttribute('zone')

    #: The FQDN of the node where this service is attached
    fqdn = ImmutableAttribute('fqdn')

    #: HTTP response code to return for redirection
    code = ValidatedAttribute('code', default=302, validator=(301, 302))

    #: The target URL where the client is sent. Must begin with either http://
    #: or https://
    url = StringAttribute('url')

    #: A flag indicating whether the redirection should include the originally
    #: requested URI.
    keep_uri = BooleanAttribute('keep_uri', default=True)

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a new :class:`HTTPRedirect` service object

        :param zone: The zone to attach this HTTPRedirect Service to
        :param fqdn: The FQDN of the node where this service will be attached
        :param code:  HTTP response code to return for redirection.
        :param url: The target URL where the client is sent. Must begin with
            either http:// or https://
        :param keep_uri: A flag indicating whether the redirection should
            include the originally requested URI
        """
        self._zone, self._fqdn = zone, fqdn
        self.uri = self.uri.format(zone=zone, fqdn=fqdn)
        super(HTTPRedirect, self).__init__(*args, **kwargs)

    def _get(self):
        """Build an object around an existing DynECT HTTPRedirect Service"""
        api_args = {'detail': 'Y'}
        response = DynectSession.get(self.uri, api_args)
        self._build(response['data'])

    def _post(self, url, code=302, keep_uri=True):
        """Create a new HTTPRedirect Service on the DynECT System"""
        self._url, self._code, self._keep_uri = url, code, keep_uri
        api_args = {'code': self._code,
                    'keep_uri': self._keep_uri,
                    'url': self._url}
        response = DynectSession.post(self.uri, api_args)
        self._build(response['data'])

    def __str__(self):
        """str override"""
        return force_unicode('<HTTPRedirect>: {0}').format(self._fqdn)
