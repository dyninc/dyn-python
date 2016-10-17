# -*- coding: utf-8 -*-
from datetime import datetime

from dyn.compat import force_unicode
from dyn.tm.errors import DynectInvalidArgumentError
from dyn.tm.session import DynectSession
from dyn.tm.utils import APIList, Active, unix_date

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
        :param dnskey: The KSK or ZSK record data
        :param ds: One of the DS records for the KSK. ZSKs will have this
            value intialized, but with null values.
        :param all_ds: All the DS records associated with this KSK. Applies
            only to KSK, ZSK will have a zero-length list.
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
        self.dnssec_key_id = self.dnskey = self.ds = self.all_ds = None
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def _json(self):
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
        """str override"""
        return force_unicode('<DNSSECKey>: {}').format(self.algorithm)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class DNSSEC(object):
    """A DynECT System DNSSEC Service"""

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
        super(DNSSEC, self).__init__()
        self.valid_notify_events = ('create', 'expire', 'warning')
        self._zone = zone
        self._contact_nickname = self._notify_events = None
        self._keys = APIList(DynectSession.get_session, 'keys')
        self._active = None
        self.uri = '/DNSSEC/{}/'.format(self._zone)
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)
        self._keys.uri = self.uri

    def _post(self, keys, contact_nickname, notify_events=None):
        """Create a new :class:`DNSSEC` Service on the Dynect System"""
        self._keys += keys
        self._contact_nickname = contact_nickname
        self._notify_events = notify_events
        api_args = {'keys': [key._json for key in self._keys],
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
            api_args['notify_events'] = ','.join(self._notify_events)
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _get(self):
        """Update this object from an existing :class:`DNSSEC` service from the
        Dynect System.
        """
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Iterate over API data responses and update this object according to
        the data returned
        """
        for key, val in data.items():
            if key == 'keys':
                self._keys = APIList(DynectSession.get_session, 'keys')
                for key_data in val:
                    key_data['key_type'] = key_data['type']
                    del key_data['type']
                    self._keys.append(DNSSECKey(**key_data))
            elif key == 'active':
                self._active = Active(val)
            else:
                setattr(self, '_' + key, val)
        self.uri = '/DNSSEC/{}/'.format(self._zone)
        self._keys.uri = self.uri

    @property
    def zone(self):
        """The name of the zone where this service exists. This is a read-only
        property
        """
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

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
        self._get()  # Do a get to ensure an up-to-date status is returned
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
    def contact_nickname(self):
        """Name of contact to receive notifications"""
        return self._contact_nickname

    @contact_nickname.setter
    def contact_nickname(self, value):
        self._contact_nickname = value
        api_args = {'contact_nickname': self._contact_nickname}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def notify_events(self):
        """A list of events that trigger notifications. Valid values are:
        create (a new version of a key was created), expire (a key was
        automatically expired), warning (early warnings (2 weeks, 1 week, 1
        day) of events)
        """
        return self._notify_events

    @notify_events.setter
    def notify_events(self, value):
        for val in value:
            if val not in self.valid_notify_events:
                raise DynectInvalidArgumentError('notify_events', val,
                                                 self.valid_notify_events)
        value = ','.join(value)
        api_args = {'notify_events': value}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

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
            self._keys = APIList(DynectSession.get_session, 'keys', None,
                                 value)
        elif isinstance(value, APIList):
            self._keys = value
        self._keys.uri = self.uri

    def activate(self):
        """Activate this :class:`DNSSEC` service"""
        api_args = {'activate': 'Y'}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def deactivate(self):
        """Deactivate this :class:`DNSSEC` service"""
        api_args = {'deactivate': 'Y'}
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def timeline_report(self, start_ts=None, end_ts=None):
        """Generates a report of events this :class:`DNSSEC` service has
        performed and has scheduled to perform

        :param start_ts: datetime.datetime instance identifying point in time
            for the start of the timeline report
        :param end_ts: datetime.datetime instance identifying point in time
            for the end of the timeline report. Defaults to
            datetime.datetime.now()
        """
        api_args = {'zone': self._zone}
        if start_ts is not None:
            api_args['start_ts'] = unix_date(start_ts)
        if end_ts is not None:
            api_args['end_ts'] = unix_date(end_ts)
        elif end_ts is None and start_ts is not None:
            api_args['end_ts'] = unix_date(datetime.now())
        uri = '/DNSSECTimelineReport/'
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        return response['data']

    def delete(self):
        """Delete this :class:`DNSSEC` Service from the DynECT System"""
        api_args = {}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<DNSSEC>: {}').format(self._zone)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
