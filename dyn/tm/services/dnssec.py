# -*- coding: utf-8 -*-
from datetime import datetime

from ..utils import APIList, Active, unix_date
from ..session import DynectSession
from ...core import (APIObject, ImmutableAttribute, StringAttribute,
                     ValidatedListAttribute)
from ...compat import force_unicode

__author__ = 'jnappi'
__all__ = ['get_all_dnssec', 'DNSSECKey', 'DNSSEC']


def get_all_dnssec():
    """:return: A ``list`` of :class:`DNSSEC` Services"""
    uri = '/DNSSEC/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    dnssecs = []
    for dnssec in response['data']:
        zone = dnssec['zone']
        del dnssec['zone']
        dnssecs.append(DNSSEC(zone, api=False, **dnssec))
    return dnssecs


class DNSSECKey(object):
    """A Key used by the DNSSEC service"""
    def __init__(self, key_type, algorithm, bits, start_ts=None, lifetime=None,
                 overlap=None, expire_ts=None, **kwargs):
        """Create a :class:`DNSSECKey` object

        :param key_type: The type of this key. (KSK or ZSK)
        :param algorithm: One of (RSA/SHA-1, RSA/SHA-256, RSA/SHA-512, DSA)
        :param bits: length of the key. Valid values: 1024, 2048, or 4096
        :param start_ts: An epoch time when key is to be valid
        :param lifetime: Lifetime of the key expressed in seconds
        :param overlap: Time before key expiration when a replacement key is
            prepared, expressed in seconds. Default = 7 days.
        :param expire_ts: An epoch time when this key is to expire
        """
        super(DNSSECKey, self).__init__()
        self.key_type = key_type
        self.algorithm = algorithm
        if not isinstance(bits, int):
            bits = int(bits)
        self.bits = bits
        self.start_ts = start_ts
        self.lifetime = lifetime
        self.overlap = overlap
        self.expire_ts = expire_ts
        self.dnssec_key_id = self.dnskey = self.ds = None
        for key, val in kwargs.items():
            setattr(self, key, val)

    def to_json(self):
        """The JSON representation of this :class:`DNSSECKey` object"""
        json_blob = {'type': self.key_type,
                     'algorithm': self.algorithm,
                     'bits': self.bits}
        if self.start_ts:
            json_blob['start_ts'] = self.start_ts
        if self.lifetime:
            json_blob['lifetime'] = self.lifetime
        if self.overlap:
            json_blob['overlap'] = self.overlap
        if self.expire_ts:
            json_blob['expire_ts'] = self.expire_ts

        return json_blob

    def _update(self, data):
        """Semi-private _update method"""
        for key, val in data.items():
            if key == 'type':
                setattr(self, 'key_type', val)
            elif key == 'bits':
                setattr(self, key, int(val))
            else:
                setattr(self, key, val)

    def __str__(self):
        return force_unicode('<DNSSECKey>: {0}').format(self.algorithm)


class DNSSEC(APIObject):
    """A DynECT System DNSSEC Service"""
    uri = '/DNSSEC/{zone_name}/'
    session_type = DynectSession
    zone = ImmutableAttribute('zone')
    contact_nickname = StringAttribute('contact_nickname')
    notify_events = ValidatedListAttribute('notify_events',
                                           validator=('create', 'expire',
                                                      'warning'))

    def __init__(self, zone, *args, **kwargs):
        """Create a :class:`DNSSEC` object

        :param zone: the zone this service will be attached to
        :param keys: a list of :class:`DNSSECKey`'s for the service
        :param contact_nickname: Name of contact to receive notifications
        :param notify_events: A ``list`` of events that trigger notifications.
            Valid values are "create" (a new version of a key was created),
            "expire" (a key was automatically expired), or "warning" (early
            warnings (2 weeks, 1 week, 1 day) of events)
        """
        self._active = None
        self.uri = self.uri.format(zone_name=zone)
        super(DNSSEC, self).__init__(*args, **kwargs)
        self._keys.uri = self.uri

    def _post(self, keys, contact_nickname, notify_events=None):
        """Create a new :class:`DNSSEC` Service on the Dynect System"""
        self._keys += keys
        self._contact_nickname = contact_nickname
        self._notify_events = notify_events
        api_args = {'keys': [key.to_json() for key in self._keys],
                    'contact_nickname': self._contact_nickname}
        for key, val in self.__dict__.items():
            if val is not None and not hasattr(val, '__call__') and \
                    key.startswith('_'):
                if key == '_user_name' or key == '_keys':
                    pass
                else:
                    api_args[key[1:]] = val
        # Need to cast to CSV for API
        if self._notify_events is not None:
            api_args['notify_events'] = ', '.join(self._notify_events)
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Iterate over API data responses and update this object according to
        the data returned
        """
        if 'keys' in data:
            keys = data.pop('keys')
            self._keys = APIList(DynectSession.get_session, 'keys')
            for key in keys:
                key['key_type'] = key.pop('type')
                self._keys.append(DNSSECKey(**key))
            self._keys.uri = self.uri
        if 'active' in data:
            self._active = Active(data.pop('active'))
        super(DNSSEC, self)._build(data)

    def _update(self, **api_args):
        if 'notify_events' in api_args:
            api_args['notify_events'] = ', '.join(api_args['notify_events'])
        super(DNSSEC, self)._update(**api_args)

    @property
    def active(self):
        """The current status of this :class:`DNSSEC` service. When setting
        directly, rather than using activate/deactivate valid arguments are 'Y'
        or True to activate, or 'N' or False to deactivate. Note: If your
        service is already active and you try to activate it, nothing will
        happen. And vice versa for deactivation.

        :returns: An :class:`Active` object representing the current state of
            this :class:`DNSSEC` Service
        """
        self._get()  # Do a get to ensure we have the most up-to-date status
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
    def keys(self):
        """A List of :class:`DNSSECKey`'s associated with this :class:`DNSSEC`
        service
        """
        # Need this check for get_all_dnssec calls which do not return key info
        if self._keys is None or self._keys == []:
            self._get()
        return self._keys
    @keys.setter
    def keys(self, value):
        if isinstance(value, list) and not isinstance(value, APIList):
            self._keys = APIList(DynectSession.get_session, 'keys', self.uri,
                                 value)
        elif isinstance(value, APIList):
            self._keys = value

    def activate(self):
        """Activate this :class:`DNSSEC` service"""
        self._update(activate='Y')

    def deactivate(self):
        """Deactivate this :class:`DNSSEC` service"""
        self._update(deactivate='Y')

    def timeline_report(self, start_ts=None, end_ts=None):
        """Generates a report of events this :class:`DNSSEC` service has
        performed and has scheduled to perform

        :param start_ts: datetime.datetime instance identifying point in time
            for the start of the timeline report
        :param end_ts: datetime.datetime instance identifying point in time
            for the end of the timeline report. Defaults to
            datetime.datetime.now()
        """
        api_args = {'zone': self.zone}
        if start_ts is not None:
            api_args['start_ts'] = unix_date(start_ts)
        if end_ts is not None:
            api_args['end_ts'] = unix_date(end_ts)
        elif end_ts is None and start_ts is not None:
            api_args['end_ts'] = unix_date(datetime.now())
        uri = '/DNSSECTimelineReport/'
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        return response['data']

    def __str__(self):
        return force_unicode('<DNSSEC>: {0}').format(self.zone)
