# -*- coding: utf-8 -*-
"""This module contains API Wrapper implementations of the Advanced Redirect
service
"""
from dyn.compat import force_unicode
from dyn.tm.session import DynectSession

__author__ = 'mhowes'
__all__ = ['AdvancedRedirect',
           'AdvancedRedirectRule',
           'get_all_advanced_redirect_rules']


def get_all_advanced_redirect_rules(zone, fqdn):
    """
    Gets all rules for service attached to zone/fqdn.
    :param zone: zone for query
    :param fqdn: fqdn for query
    """
    uri = '/AdvRedirectRule/{}/{}/'.format(zone, fqdn)
    response = DynectSession.get_session().execute(uri, 'GET',
                                                   {})
    return [AdvancedRedirectRule(zone, fqdn, api=True, **rule) for rule in
            response['data']]


class AdvancedRedirect(object):
    """:class:`AdvancedRedirect` is a service which sets up a
     redirect which utilizes an ordered list of rules to match.
     requests to and then forward them.
    """
    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a new :class:`AdvancedRedirect` service object

        :param zone: The zone to attach this :class:`AdvancedRedirect`
         Service to
        :param fqdn: The FQDN of the node where this service will be attached
        :param rules: list of :class:`AdvancedRedirectRule` In the order which
         they are to be implemented.
        :param active:  Y/N Whether this service is active or not.

        """
        self._zone = zone
        self._fqdn = fqdn
        self._active = kwargs.get("active", None)
        self._rules = kwargs.get("rules", None)
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) + len(kwargs) == 0:
            self._get()
        else:
            self._post()

    def _get(self):
        """Build an object around an existing DynECT :class:`AdvancedRedirect`
         Service"""
        self.uri = '/AdvRedirect/{}/{}/'.format(self._zone, self._fqdn)
        api_args = {'detail': 'Y'}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def _post(self):
        """Create a new :class:`AdvancedRedirect` Service on
         the DynECT System"""
        self.uri = '/AdvRedirect/{}/{}/'.format(self._zone, self._fqdn)

        api_args = {'active': self._active}
        if self._rules:
            api_args['rules'] = list()
            for rule in self._rules:
                if isinstance(rule, AdvancedRedirectRule):
                    api_args['rules'].append(rule._json)
                else:
                    api_args['rules'].append(rule)
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args=None):
        """Update an existing :class:`AdvancedRedirect` Service
         on the DynECT System"""
        self.uri = '/AdvRedirect/{}/{}/'.format(self._zone, self._fqdn)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        self._rules = []
        for key, val in data.items():
            if key == 'rules':
                for rule in val:
                    rule['api'] = 'Y'
                    self._rules.append(AdvancedRedirectRule(self._zone,
                                                            self._fqdn,
                                                            **rule))
                continue
            setattr(self, '_' + key, val)

    @property
    def zone(self):
        """The zone that this :class:`AdvancedRedirect` Service is
         attached to is a read-only attribute
        """
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """The fqdn that this :class:`AdvancedRedirect` Service is
         attached to is a read-only attribute
        """
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def active(self):
        """
        :class:`AdvancedRedirect` active Y/N
        """
        self._get()
        return self._active

    @active.setter
    def active(self, value):
        api_args = {'active': value}
        self._update(api_args)

    @property
    def rules(self):
        """
        :class:`AdvancedRedirect` rules. An ordered list of
         :class:`AdvancedRedirectRules`
        """
        self._get()
        return [AdvancedRedirectRule(self.zone, self.fqdn, api=True, **rule)
                for rule in self._rules]

    @rules.setter
    def rules(self, value):
        api_args = dict()
        api_args['rules'] = list()
        for rule in value:
            if isinstance(rule, AdvancedRedirectRule):
                api_args['rules'].append(rule._json)
            else:
                api_args['rules'].append(rule)
        self._update(api_args)

    def delete(self):
        """Delete this :class:`AdvancedRedirect` service from the DynECT
        System """
        self.uri = '/AdvRedirect/{}/{}'.format(self._zone, self._fqdn)
        DynectSession.get_session().execute(self.uri, 'DELETE', {})

    def __str__(self):
        """str override"""
        return force_unicode('<AdvRedirect>: {}').format(self._fqdn)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class AdvancedRedirectRule(object):
    """:class:`AdvancedRedirectRule` handles Rules for the
     :class:`AdvancedRedirect` service """
    def __init__(self, *args, **kwargs):
        """Create a new :class:`AdvancedRedirectRule` service object
        AdvancedRedirectRule(zone, fqdn, option1=..., option2=...)

        :param zone: The zone to attach this :class:`AdvancedRedirectRule`
         Service to
        :param fqdn: The FQDN of the node where this service will be attached.
        :param code: HTTP response code to return for redirection.
        :param url_pattern: The target URL pattern for matching this rule.
        :param active: Y/N whether this Rule should be active or not.
        :param host_prefix: host prefix for rule to match.
        :param path: path for rule to match.
        :param next_public_id: public_id of the next rule to match in the
         chain.
        :param public_id: public_id of this rule.
        """
        self._zone = None
        self._fqdn = None
        if len(args) >= 1:
            self._zone = args[0]
        if len(args) >= 2:
            self._fqdn = args[1]
        self._code = kwargs.get("code", None)
        self._host_prefix = kwargs.get("host_prefix", None)
        self._path = kwargs.get("path", None)
        # self._query = kwargs.get("query",None)
        self._url_pattern = kwargs.get("url_pattern", None)
        self._active = kwargs.get("active", None)
        self._next_public_id = kwargs.get("next_public_id", None)
        self._public_id = kwargs.get("public_id", None)
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) == 0 and len(kwargs) > 0:
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) == 2 and self._public_id:
            self._get()
        else:
            self._post()

    def _get(self):
        """Build an object around an existing DynECT
        :class:`AdvancedRedirectRule` Service"""
        self.uri = '/AdvRedirectRule/{}/{}/{}'.format(self._zone,
                                                      self._fqdn,
                                                      self._public_id)
        api_args = {'detail': 'Y'}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def _post(self):
        """Create a new :class:`AdvancedRedirectRule` Service
         on the DynECT System"""
        api_args = dict()
        self.uri = '/AdvRedirectRule/{}/{}/'.format(self._zone,
                                                    self._fqdn)
        if self._code:
            api_args['code'] = self._code
        if self._host_prefix:
            api_args['host_prefix'] = self._host_prefix
        if self._path:
            api_args['path'] = self._path
        # if self._query:
        #     api_args['query'] = self._query
        if self._url_pattern:
            api_args['url_pattern'] = self._url_pattern
        if self._active:
            api_args['active'] = self._active
        if self._next_public_id:
            api_args['next_public_id'] = self._next_public_id
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args=None):
        """Update an existing :class:`AdvancedRedirectRule` Service
        on the DynECT System"""
        self.uri = '/AdvRedirectRule/{}/{}/{}'.format(self._zone,
                                                      self._fqdn,
                                                      self._public_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        for key, val in data.items():
            setattr(self, '_' + key, val)

    @property
    def _json(self):
        """Get the JSON representation of this :class:`AdvancedRedirectRule`
        object
        """
        json_blob = {'code': self._code,
                     'host_prefix': self._host_prefix,
                     'active': self._active,
                     'path': self._path,
                     # 'query': self._query,
                     'next_public_id': self._next_public_id,
                     'url_pattern': self._url_pattern,
                     }
        return {x: json_blob[x] for x in json_blob if json_blob[x] is not None}

    @property
    def zone(self):
        """The zone that this :class:`AdvancedRedirectRule` Service is
        attached to is a read-only attribute
        """
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """The fqdn that this :class:`AdvancedRedirectRule` Service is
        attached to is a read-only attribute
        """
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def active(self):
        """
        :class:`AdvancedRedirectRule` active Y/N
        """
        self._get()
        return self._active

    @active.setter
    def active(self, value):
        api_args = {'active': value}
        self._update(api_args)

    @property
    def code(self):
        """
        :class:`AdvancedRedirectRule` Code: 301, 302, 404
        """
        self._get()
        return self._code

    @code.setter
    def code(self, value):
        api_args = {'code': value}
        self._update(api_args)

    @property
    def public_id(self):
        """
        :class:`AdvancedRedirectRule` public_id
        """
        self._get()
        return self._public_id

    @public_id.setter
    def public_id(self, value):
        api_args = {'public_id': value}
        self._update(api_args)

    @property
    def next_public_id(self):
        """
        :class:`AdvancedRedirectRule` next_public_id. That is, public_id of
         the next :class:`AdvancedRedirectRule` to be acted upon
        """
        self._get()
        return self._next_public_id

    @next_public_id.setter
    def next_public_id(self, value):
        api_args = {'next_public_id': value}
        self._update(api_args)

    @property
    def host_prefix(self):
        """
        :class:`AdvancedRedirectRule` host_prefix. the `help`
         in `http://help.dyn.com`
        """
        self._get()
        return self._host_prefix

    @host_prefix.setter
    def host_prefix(self, value):
        api_args = {'host_prefix': value}
        self._update(api_args)

    # @property
    # def query(self):
    #     """
    #     query of Rule
    #     """
    #     self._get()
    #     return self._query
    #
    # @query.setter
    # def query(self, value):
    #     api_args = {'query': value}
    #     self._update(api_args)

    @property
    def path(self):
        """
        :class:`AdvancedRedirectRule` path. the `help` in
         `http://www.dyn.com/help`
        """
        self._get()
        return self._path

    @path.setter
    def path(self, value):
        api_args = {'path': value}
        self._update(api_args)

    @property
    def url_pattern(self):
        """
        :class:`AdvancedRedirectRule` url pattern.
         used to implement how the redirect is written.
        """
        self._get()
        return self._url_pattern

    @url_pattern.setter
    def url_pattern(self, value):
        api_args = {'url_pattern': value}
        self._update(api_args)

    def delete(self):
        """Delete this :class:`AdvancedRedirectRule` service
         from the DynECT System
        """
        self.uri = '/AdvRedirectRule/{}/{}/{}'.format(self._zone,
                                                      self._fqdn,
                                                      self._public_id)
        DynectSession.get_session().execute(self.uri, 'DELETE', {})

    def __str__(self):
        """str override"""
        return force_unicode(
            '<AdvRedirectRule>: {}, {}, Active: {}, Public_Id: {}').format(
            self._fqdn,
            self._url_pattern,
            self._active,
            self._public_id)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
