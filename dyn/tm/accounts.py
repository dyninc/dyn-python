# -*- coding: utf-8 -*-
"""This module contains interfaces for all Account management features of the
REST API
"""
from dyn.tm.errors import DynectInvalidArgumentError
from dyn.tm.session import DynectSession
from dyn.compat import force_unicode
import re

__author__ = 'jnappi'
__all__ = ['get_updateusers', 'get_users', 'get_permissions_groups',
           'get_contacts', 'get_notifiers', 'UpdateUser', 'User',
           'PermissionsGroup', 'UserZone', 'Notifier', 'Contact']


def get_updateusers(search=None):
    """Return a ``list`` of :class:`~dyn.tm.accounts.UpdateUser` objects. If
    *search* is specified, then only :class:`~dyn.tm.accounts.UpdateUsers` who
    match those search criteria will be returned in the list. Otherwise, all
    :class:`~dyn.tm.accounts.UpdateUsers`'s will be returned.

    :param search: A ``dict`` of search criteria. Key's in this ``dict`` much
        map to an attribute a :class:`~dyn.tm.accounts.UpdateUsers` instance
        and the value mapped to by that key will be used as the search criteria
        for that key when searching.
    :return: a ``list`` of :class:`~dyn.tm.accounts.UpdateUser` objects
    """
    uri = '/UpdateUser/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    update_users = []
    for user in response['data']:
        update_users.append(UpdateUser(api=False, **user))
    if search is not None:
        original = update_users
        update_users = []
        for uu in original:
            for key, val in search.items():
                if hasattr(uu, key) and getattr(uu, key) == val:
                    update_users.append(uu)
    return update_users


def get_users(search=None):
    """Return a ``list`` of :class:`~dyn.tm.accounts.User` objects. If *search*
    is specified, then only users who match those search parameters will be
    returned in the list. Otherwise, all :class:`~dyn.tm.accounts.User`'s will
    be returned.

    :param search: A ``dict`` of search criteria. Key's in this ``dict`` much
        map to an attribute a :class:`~dyn.tm.accounts.User` instance and the
        value mapped to by that key will be used as the search criteria for
        that key when searching.
    :return: a ``list`` of :class:`~dyn.tm.accounts.User` objects
    """
    uri = '/User/'
    api_args = {'detail': 'Y'}
    if search is not None:
        search_string = ''
        for key, val in search.items():
            if search_string != '':
                ' AND '.join([search_string, '{}:"{}"'.format(key, val)])
            else:
                search_string = '{}:"{}"'.format(key, val)
        api_args['search'] = search_string
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    users = []
    for user in response['data']:
        user_name = None
        if 'user_name' in user:
            user_name = user['user_name']
            del user['user_name']
        users.append(User(user_name, api=False, **user))
    return users


def get_permissions_groups(search=None):
    """Return a ``list`` of :class:`~dyn.tm.accounts.PermissionGroup` objects.
    If *search* is specified, then only
    :class:`~dyn.tm.accounts.PermissionGroup`'s that match those search
    criteria will be returned in the list. Otherwise, all
    :class:`~dyn.tm.accounts.PermissionGroup`'s will be returned.

    :param search: A ``dict`` of search criteria. Key's in this ``dict`` much
        map to an attribute a :class:`~dyn.tm.accounts.PermissionGroup`
        instance and the value mapped to by that key will be used as the search
        criteria for that key when searching.
    :return: a ``list`` of :class:`~dyn.tm.accounts.PermissionGroup` objects
    """
    uri = '/PermissionGroup/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    groups = []
    for group in response['data']:
        groups.append(PermissionsGroup(None, api=False, **group))
    if search is not None:
        original = groups
        groups = []
        for group in original:
            for key, val in search.items():
                if hasattr(group, key) and getattr(group, key) == val:
                    groups.append(group)
    return groups


def get_contacts(search=None):
    """Return a ``list`` of :class:`~dyn.tm.accounts.Contact` objects. If
    *search* is specified, then only :class:`~dyn.tm.accounts.Contact`'s who
    match those search criteria will be returned in the list. Otherwise, all
    :class:`~dyn.tm.accounts.Contact`'s will be returned.

    :param search: A ``dict`` of search criteria. Key's in this ``dict`` much
        map to an attribute a :class:`~dyn.tm.accounts.Contact` instance and
        the value mapped to by that key will be used as the search criteria
        for that key when searching.
    :return: a ``list`` of :class:`~dyn.tm.accounts.Contact` objects
    """
    uri = '/Contact/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    contacts = []
    for contact in response['data']:
        if 'nickname' in contact:
            contact['_nickname'] = contact['nickname']
            del contact['nickname']
        contacts.append(Contact(None, api=False, **contact))
    if search is not None:
        original = contacts
        contacts = []
        for contact in original:
            for key, val in search.items():
                if hasattr(contact, key) and getattr(contact, key) == val:
                    contacts.append(contact)
    return contacts


def get_notifiers(search=None):
    """Return a ``list`` of :class:`~dyn.tm.accounts.Notifier` objects. If
    *search* is specified, then only :class:`~dyn.tm.accounts.Notifier`'s who
    match those search criteria will be returned in the list. Otherwise, all
    :class:`~dyn.tm.accounts.Notifier`'s will be returned.

    :param search: A ``dict`` of search criteria. Key's in this ``dict`` much
        map to an attribute a :class:`~dyn.tm.accounts.Notifier` instance and
        the value mapped to by that key will be used as the search criteria for
        that key when searching.
    :return: a ``list`` of :class:`~dyn.tm.accounts.Notifier` objects
    """
    uri = '/Notifier/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    notifiers = []
    for notifier in response['data']:
        notifiers.append(Notifier(None, api=False, **notifier))
    if search is not None:
        original = notifiers
        notifiers = []
        for notifier in original:
            for key, val in search.items():
                if hasattr(notifier, key) and getattr(notifier, key) == val:
                    notifiers.append(notifier)
    return notifiers


class UpdateUser(object):
    """:class:`~dyn.tm.accounts.UpdateUser` type objects are a special form of
    a :class:`~dyn.tm.accounts.User` which are tied to a specific Dynamic DNS
    services.
    """

    def __init__(self, *args, **kwargs):
        """Create an :class:`~dyn.tm.accounts.UpdateUser` object

        :param user_name: the Username this
            :class:`~dyn.tm.accounts.UpdateUser` uses or will use to log in to
            the DynECT System. A :class:`~dyn.tm.accounts.UpdateUser`'s
            `user_name` is required for both creating and getting
            :class:`~dyn.tm.accounts.UpdateUser`'s.
        :param nickname: When creating a new
            :class:`~dyn.tm.accounts.UpdateUser` on the DynECT System, this
            `nickname` will be the System nickname for this
            :class:`~dyn.tm.accounts.UpdateUser`
        :param password: When creating a new
            :class:`~dyn.tm.accounts.UpdateUser` on the DynECT System, this
            `password` will be the password this
            :class:`~dyn.tm.accounts.UpdateUser` uses to log into the System
        """
        super(UpdateUser, self).__init__()
        self.uri = '/UpdateUser/'
        self._password = self._status = self._user_name = self._nickname = None
        if 'api' in kwargs:
            good_args = ('user_name', 'status', 'password')
            for key, val in kwargs.items():
                if key in good_args:
                    setattr(self, '_' + key, val)
            self.uri = '/UpdateUser/{}/'.format(self._user_name)
        elif len(args) + len(kwargs) == 1:
            self._get(*args, **kwargs)
        else:
            self._post(*args, **kwargs)

    def _post(self, nickname, password):
        """Create a new :class:`~dyn.tm.accounts.UpdateUser` on the DynECT
        System
        """
        self._nickname = nickname
        self._password = password
        uri = '/UpdateUser/'
        api_args = {'nickname': self._nickname,
                    'password': self._password}
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])
        self.uri = '/UpdateUser/{}/'.format(self._user_name)

    def _get(self, user_name):
        """Get an existing :class:`~dyn.tm.accounts.UpdateUser` from the
        DynECT System
        """
        self._user_name = user_name
        self.uri = '/UpdateUser/{}/'.format(self._user_name)
        response = DynectSession.get_session().execute(self.uri, 'GET')
        self._build(response['data'])

    def _build(self, data):
        for key, val in data.items():
            setattr(self, '_' + key, val)

    def _update(self, api_args=None):
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def user_name(self):
        """This :class:`~dyn.tm.accounts.UpdateUser`'s `user_name`. An
        :class:`~dyn.tm.accounts.UpdateUser`'s user_name is a read-only
        property which can not be updated after the :class:`UpdateUser` has
        been created.
        """
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        pass

    @property
    def nickname(self):
        """This :class:`~dyn.tm.accounts.UpdateUser`s `nickname`. An
        :class:`~dyn.tm.accounts.UpdateUser`'s `nickname` is a read-only
        property which can not be updated after the
        :class:`~dyn.tm.accounts.UpdateUser` has been created.
        """
        return self._nickname

    @nickname.setter
    def nickname(self, value):
        pass

    @property
    def status(self):
        """The current `status` of an :class:`~dyn.tm.accounts.UpdateUser` will
        be one of either 'active' or 'blocked'. Blocked
        :class:`~dyn.tm.accounts.UpdateUser`'s are unable to log into the
        DynECT System, where active :class:`~dyn.tm.accounts.UpdateUser`'s are.
        """
        return self._status

    @status.setter
    def status(self, value):
        pass

    @property
    def password(self):
        """The current `password` for this
        :class:`~dyn.tm.accounts.UpdateUser`. An
        :class:`~dyn.tm.accounts.UpdateUser`'s `password` may be reassigned.
        """
        if self._password is None or self._password == u'':
            self._get(self._user_name)
        return self._password

    @password.setter
    def password(self, new_password):
        """Update this :class:`~dyn.tm.accounts.UpdateUser`'s password to be
        the provided password

        :param new_password: The new password to use
        """
        api_args = {'password': new_password}
        self._update(api_args)

    def block(self):
        """Set the status of this :class:`~dyn.tm.accounts.UpdateUser` to
        'blocked'. This will prevent this :class:`~dyn.tm.accounts.UpdateUser`
        from logging in until they are explicitly unblocked.
        """
        api_args = {'block': True}
        self._update(api_args)

    def unblock(self):
        """Set the status of this :class:`~dyn.tm.accounts.UpdateUser` to
        'active'. This will re-enable this :class:`~dyn.tm.accounts.UpdateUser`
        to be able to login if they were previously blocked.
        """
        api_args = {'unblock': True}
        self._update(api_args)

    def sync_password(self):
        """Pull in this :class:`~dyn.tm.accounts.UpdateUser` current password
        from the DynECT System, in the unlikely event that this
        :class:`~dyn.tm.accounts.UpdateUser` object's password may have gotten
        out of sync
        """
        api_args = {'user_name': self._user_name}
        self._update(api_args)

    def delete(self):
        """Delete this :class:`~dyn.tm.accounts.UpdateUser` from the DynECT
        System. It is important to note that this operation may not be undone.
        """
        DynectSession.get_session().execute(self.uri, 'DELETE')

    def __str__(self):
        """Custom str method"""
        return force_unicode('<UpdateUser>: {}').format(self.user_name)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class User(object):
    """DynECT System User object"""

    def __init__(self, user_name, *args, **kwargs):
        """Create a new :class:`~dyn.tm.accounts.User` object

        :param user_name: This :class:`~dyn.tm.accounts.User`'s system
            username; used for logging into the system
        :param password: Password for this :class:`~dyn.tm.accounts.User`
            account
        :param email: This :class:`~dyn.tm.accounts.User`'s Email address
        :param first_name: This :class:`~dyn.tm.accounts.User`'s first name
        :param last_name: This :class:`~dyn.tm.accounts.User`'s last name
        :param nickname: The nickname for the `Contact` associated with this
            :class:`~dyn.tm.accounts.User`
        :param organization: This :class:`~dyn.tm.accounts.User`'s organization
        :param phone: This :class:`~dyn.tm.accounts.User`'s phone number. Can
            be of the form: (0) ( country-code ) ( local number ) ( extension )
            Only the country-code (1-3 digits) and local number (at least 7
            digits) are required. The extension can be up to 4 digits. Any
            non-digits are ignored.
        :param address: This :class:`~dyn.tm.accounts.User`'s street address
        :param address2: This :class:`~dyn.tm.accounts.User`'s street address,
            line 2
        :param city: This :class:`~dyn.tm.accounts.User`'s city, part of the
            user's address
        :param country: This :class:`~dyn.tm.accounts.User`'s country, part of
            the user's address
        :param fax: This :class:`~dyn.tm.accounts.User`'s fax number
        :param notify_email: Email address where this
            :class:`~dyn.tm.accounts.User` should receive notifications
        :param pager_email: Email address where this
            :class:`~dyn.tm.accounts.User` should receive messages destined
            for a pager
        :param post_code: Zip code or Postal code
        :param group_name: A list of permission groups this
            :class:`~dyn.tm.accounts.User` belongs to
        :param permission: A list of permissions assigned to this
            :class:`~dyn.tm.accounts.User`
        :param zone: A list of zones where this
            :class:`~dyn.tm.accounts.User`'s permissions apply
        :param forbid: A list of forbidden permissions for this
            :class:`~dyn.tm.accounts.User`
        :param status: Current status of this :class:`~dyn.tm.accounts.User`
        :param website: This :class:`~dyn.tm.accounts.User`'s website
        """
        super(User, self).__init__()
        self._user_name = user_name
        self.uri = '/User/{}/'.format(self._user_name)
        self._permission_report_uri = '/UserPermissionReport/'
        self._password = self._email = self._first_name = None
        self._last_name = self._nickname = self._organization = None
        self._phone = self._address = self._address_2 = self._city = None
        self._country = self._fax = self._notify_email = None
        self._pager_email = self._post_code = self._group_name = None
        self._zone = self._forbid = self._status = None
        self._website = None
        self._permission = []
        self.permission_groups = []
        self.groups = []
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                if key != '_user_name':
                    setattr(self, '_' + key, val)
                else:
                    setattr(self, key, val)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)

    def _post(self, password, email, first_name, last_name, nickname,
              organization, phone, address=None, address_2=None, city=None,
              country=None, fax=None, notify_email=None, pager_email=None,
              post_code=None, group_name=None, permission=None, zone=None,
              forbid=None, status=None, website=None):
        """Create a new :class:`~dyn.tm.accounts.User` object on the DynECT
        System
        """

        api_args = {'password': password, 'email': email,
                    'first_name': first_name, 'last_name': last_name,
                    'nickname': nickname, 'organization': organization,
                    'phone': phone, 'address': address,
                    'address_2': address_2, 'city': city, 'country': country,
                    'fax': fax, 'notify_email': notify_email,
                    'pager_email': pager_email, 'post_code': post_code,
                    'group_name': group_name, 'permission': permission,
                    'zone': zone, 'forbid': forbid,
                    'website': website}

        self._password = password
        self._email = email
        self._first_name = first_name
        self._last_name = last_name
        self._nickname = nickname
        self._organization = organization
        self._phone = phone
        self._address = address
        self._address_2 = address_2
        self._city = city
        self._country = country
        self._fax = fax
        self._notify_email = notify_email
        self._pager_email = pager_email
        self._post_code = post_code
        self._group_name = group_name
        self._permission = permission
        self._zone = zone
        self._forbid = forbid
        self._status = status
        self._website = website

        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _get(self):
        """Get an existing :class:`~dyn.tm.accounts.User` object from the
        DynECT System
        """
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])
        self._get_permission()

    def _update_permission(self):
        api_args = {'user_name': self._user_name}
        response = DynectSession.get_session().execute(
            self._permission_report_uri, 'POST', api_args)
        self._build_permission(response)

    def _update(self, api_args=None):
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Private build method"""
        for key, val in data.items():
            setattr(self, '_' + key, val)

    def _get_permission(self):
        api_args = {'user_name': self._user_name}
        response = DynectSession.get_session().execute(
            self._permission_report_uri, 'POST', api_args)
        self._build_permission(response)

    def _build_permission(self, response):
        self._zone = list()
        for val in response['data']['allowed']:
            self._permission.append(val['name'])
            for zone in val['zone']:
                if zone['zone_name'] not in self._zone:
                    self._zone.append(zone['zone_name'])

    @property
    def user_name(self):
        """A :class:`~dyn.tm.accounts.User`'s user_name is a read-only property
        """
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        pass

    @property
    def status(self):
        """A :class:`~dyn.tm.accounts.User`'s status is a read-only property.
        To change you must use the :meth:`block`/:meth:`unblock` methods
        """
        return self._status

    @status.setter
    def status(self, value):
        pass

    @property
    def email(self):
        """This :class:`~dyn.tm.accounts.User`'s Email address"""
        return self._email

    @email.setter
    def email(self, value):
        api_args = {'email': value}
        self._update(api_args)

    @property
    def first_name(self):
        """This :class:`~dyn.tm.accounts.User`'s first name"""
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        api_args = {'first_name': value}
        self._update(api_args)

    @property
    def last_name(self):
        """This :class:`~dyn.tm.accounts.User`'s last name"""
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        api_args = {'last_name': value}
        self._update(api_args)

    @property
    def nickname(self):
        """The nickname for the `Contact` associated with this
        :class:`~dyn.tm.accounts.User`"""
        return self._nickname

    @nickname.setter
    def nickname(self, value):
        api_args = {'nickname': value}
        self._update(api_args)

    @property
    def organization(self):
        """This :class:`~dyn.tm.accounts.User`'s organization"""
        return self._organization

    @organization.setter
    def organization(self, value):
        api_args = {'organization': value}
        self._update(api_args)

    @property
    def phone(self):
        """This :class:`~dyn.tm.accounts.User`'s phone number. Can be of the
        form: (0) ( country-code ) ( local number ) ( extension ) Only the
        country-code (1-3 digits) and local number (at least 7 digits) are
        required. The extension can be up to 4 digits. Any non-digits are
        ignored.
        """
        return self._phone

    @phone.setter
    def phone(self, value):
        api_args = {'phone': value}
        self._update(api_args)

    @property
    def address(self):
        """This :class:`~dyn.tm.accounts.User`'s street address"""
        return self._address

    @address.setter
    def address(self, value):
        api_args = {'address': value}
        self._update(api_args)

    @property
    def address_2(self):
        """This :class:`~dyn.tm.accounts.User`'s street address, line 2"""
        return self._address_2

    @address_2.setter
    def address_2(self, value):
        api_args = {'address_2': value}
        self._update(api_args)

    @property
    def city(self):
        """This :class:`~dyn.tm.accounts.User`'s city, part of the user's
        address
        """
        return self._city

    @city.setter
    def city(self, value):
        api_args = {'city': value}
        self._update(api_args)

    @property
    def country(self):
        """This :class:`~dyn.tm.accounts.User`'s country, part of the user's
        address
        """
        return self._country

    @country.setter
    def country(self, value):
        api_args = {'country': value}
        self._update(api_args)

    @property
    def fax(self):
        """This :class:`~dyn.tm.accounts.User`'s fax number"""
        return self._fax

    @fax.setter
    def fax(self, value):
        api_args = {'fax': value}
        self._update(api_args)

    @property
    def notify_email(self):
        """Email address where this :class:`~dyn.tm.accounts.User` should
        receive notifications
        """
        return self._notify_email

    @notify_email.setter
    def notify_email(self, value):
        api_args = {'notify_email': value}
        self._update(api_args)

    @property
    def pager_email(self):
        """Email address where this :class:`~dyn.tm.accounts.User` should
        receive messages destined for a pager
        """
        return self._pager_email

    @pager_email.setter
    def pager_email(self, value):
        api_args = {'pager_email': value}
        self._update(api_args)

    @property
    def post_code(self):
        """This :class:`~dyn.tm.accounts.User`'s postal code, part of the
        user's address
        """
        return self._post_code

    @post_code.setter
    def post_code(self, value):
        api_args = {'post_code': value}
        self._update(api_args)

    @property
    def group_name(self):
        """A list of permission groups this :class:`~dyn.tm.accounts.User`
        belongs to
        """
        return self._group_name

    @group_name.setter
    def group_name(self, value):
        api_args = {'group_name': value}
        self._update(api_args)

    @property
    def permission(self):
        """A list of permissions assigned to this
        :class:`~dyn.tm.accounts.User`
        """
        return self._permission

    @permission.setter
    def permission(self, value):
        api_args = {'permission': value}
        self._update(api_args)

    @property
    def zone(self):
        """A list of zones where this :class:`~dyn.tm.accounts.User`'s
        permissions apply
        """
        return self._zone

    @zone.setter
    def zone(self, value):
        api_args = {'zone': value}
        self._update(api_args)

    @property
    def forbid(self):
        """A list of forbidden permissions for this
        :class:`~dyn.tm.accounts.User`
        """
        return self._forbid

    @forbid.setter
    def forbid(self, value):
        """Apply a new list of forbidden permissions for the
        :class:`~dyn.tm.accounts.User`
        """
        api_args = {'forbid': value}
        self._update(api_args)

    @property
    def website(self):
        """This :class:`~dyn.tm.accounts.User`'s website"""
        return self._website

    @website.setter
    def website(self, value):
        api_args = {'website': value}
        self._update(api_args)

    def block(self):
        """Blocks this :class:`~dyn.tm.accounts.User` from logging in"""
        api_args = {'block': 'True'}
        uri = '/User/{}/'.format(self._user_name)
        response = DynectSession.get_session().execute(uri, 'PUT', api_args)
        self._status = response['data']['status']

    def unblock(self):
        """Restores this :class:`~dyn.tm.accounts.User` to an active status and
        re-enables their log-in
        """
        api_args = {'unblock': 'True'}
        uri = '/User/{}/'.format(self._user_name)
        response = DynectSession.get_session().execute(uri, 'PUT', api_args)
        self._status = response['data']['status']

    def add_permission(self, permission):
        """Add individual permissions to this :class:`~dyn.tm.accounts.User`

        :param permission: the permission to add
        """
        if permission not in self._permission:
            self._permission.append(permission)
            uri = '/UserPermissionEntry/{}/{}/'.format(self._user_name,
                                                       permission)
            DynectSession.get_session().execute(uri, 'POST')

    def replace_permission(self, permission=None):
        """Replaces the list of permissions for this
        :class:`~dyn.tm.accounts.User`

        :param permissions: A list of permissions. Pass an empty list or omit
            the argument to clear the list of permissions of the
            :class:`~dyn.tm.accounts.User`
        """
        api_args = {}
        if permission is not None:
            api_args['permission'] = permission
            self._permission = permission
        else:
            self._permission = []
        uri = '/UserPermissionEntry/{}/'.format(self._user_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    def delete_permission(self, permission):
        """Remove this specific permission from the
        :class:`~dyn.tm.accounts.User`

        :param permission: the permission to remove
        """
        if permission in self._permission:
            self._permission.remove(permission)
        uri = '/UserPermissionEntry/{}/{}/'.format(self._user_name, permission)
        DynectSession.get_session().execute(uri, 'DELETE')

    def add_permissions_group(self, group):
        """Assigns the permissions group to this :class:`~dyn.tm.accounts.User`

        :param group: the permissions group to add to this
            :class:`~dyn.tm.accounts.User`
        """
        self.permission_groups.append(group)
        uri = '/UserGroupEntry/{}/{}/'.format(self._user_name, group)
        DynectSession.get_session().execute(uri, 'POST')

    def replace_permissions_group(self, groups=None):
        """Replaces the list of permissions for this
        :class:`~dyn.tm.accounts.User`

        :param groups: A list of permissions groups. Pass an empty list or omit
            the argument to clear the list of permissions groups of the
            :class:`~dyn.tm.accounts.User`
        """
        api_args = {}
        if groups is not None:
            api_args['groups'] = groups
            self.groups = groups
        else:
            self.groups = []
        uri = '/UserGroupEntry/{}/'.format(self._user_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    def delete_permissions_group(self, group):
        """Removes the permissions group from the
        :class:`~dyn.tm.accounts.User`

        :param group: the permissions group to remove from this
            :class:`~dyn.tm.accounts.User`
        """
        if group in self.permission:
            self.permission_groups.remove(group)
        uri = '/UserGroupEntry/{}/{}/'.format(self._user_name, group)
        DynectSession.get_session().execute(uri, 'DELETE')

    def add_zone(self, zone, recurse='Y'):
        """Add individual zones to this :class:`~dyn.tm.accounts.User`
        :param zone: the zone to add
        :param recurse: determine if permissions should be extended to
         subzones.
        """
        if self._zone is not None:
            if zone not in self._zone:
                uri = '/UserZoneEntry/{}/{}/'.format(self._user_name, zone)
                DynectSession.get_session().execute(uri, 'POST')
        else:
            uri = '/UserZoneEntry/{}/{}/'.format(self._user_name, zone)
            DynectSession.get_session().execute(uri, 'POST')
        self._get_permission()

    def replace_zones(self, zones):
        """Remove this specific zones from the
        :class:`~dyn.tm.accounts.User`
        :param zones: array of the zones to be updated
        format must be [{'zone_name':[yourzone], recurse: 'Y'},{ ...}]
        recurse is optional.
        """
        api_args = {}
        if zones is not None:
            api_args['zone'] = zones
        uri = '/UserZoneEntry/{}/'.format(self._user_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self._get_permission()

    def delete_zone(self, zone):
        """Remove this specific zones from the
        :class:`~dyn.tm.accounts.User`

        :param zone: the zone to remove
        """
        uri = '/UserZoneEntry/{}/{}/'.format(self._user_name, zone)
        DynectSession.get_session().execute(uri, 'DELETE')
        self._get_permission()

    def add_forbid_rule(self, permission, zone=None):
        """Adds the forbid rule to the :class:`~dyn.tm.accounts.User`'s
        permission group

        :param permission: the permission to forbid from this
            :class:`~dyn.tm.accounts.User`
        :param zone: A list of zones where the forbid rule applies
        """
        api_args = {}
        if zone is not None:
            api_args['zone'] = zone
        uri = '/UserForbidEntry/{}/{}/'.format(self._user_name, permission)
        DynectSession.get_session().execute(uri, 'POST', api_args)

    def replace_forbid_rules(self, forbid=None):
        """Replaces the list of forbidden permissions in the
        :class:`~dyn.tm.accounts.User`'s permissions group with a new list.

        :param forbid: A list of rules to replace the forbidden rules on the
            :class:`~dyn.tm.accounts.User`'s permission group. If empty or not
            passed in, the :class:`~dyn.tm.accounts.User`'s forbid list will be
            cleared
        """
        api_args = {}
        if forbid is not None:
            api_args['forbid'] = forbid
        uri = '/UserForbidEntry/{}/'.format(self._user_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    def delete_forbid_rule(self, permission, zone=None):
        """Removes a forbid permissions rule from the
        :class:`~dyn.tm.accounts.User`'s permission group

        :param permission: permission
        :param zone: A list of zones where the forbid rule applies
        """
        api_args = {}
        if zone is not None:
            api_args['zone'] = zone
        uri = '/UserForbidEntry/{}/{}/'.format(self._user_name, permission)
        DynectSession.get_session().execute(uri, 'DELETE', api_args)

    def delete(self):
        """Delete this :class:`~dyn.tm.accounts.User` from the system"""
        uri = '/User/{}/'.format(self._user_name)
        DynectSession.get_session().execute(uri, 'DELETE')

    def __str__(self):
        """Custom str method"""
        return force_unicode('<User>: {}').format(self.user_name)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class PermissionsGroup(object):
    """A DynECT System Permissions Group object"""

    def __init__(self, group_name, *args, **kwargs):
        """Create a new permissions Group

        :param group_name: The name of the permission group to update
        :param description: A description of the permission group
        :param group_type: The type of the permission group. Valid values:
            plain or default
        :param all_users: If 'Y', all current users will be added to the group.
            Cannot be used if user_name is passed in
        :param permission: A list of permissions that the group contains
        :param user_name: A list of users that belong to the permission group
        :param subgroup: A list of groups that belong to the permission group
        :param zone: A list of zones where the group's permissions apply
        """
        super(PermissionsGroup, self).__init__()
        self._group_name = group_name
        self._description = self._group_type = self._all_users = None
        self._permission = self._user_name = self._subgroup = self._zone = None
        self.uri = '/PermissionGroup/{}/'.format(self._group_name)
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)

    def _post(self, description, group_type=None, all_users=None,
              permission=None, user_name=None, subgroup=None, zone=None):
        """Create a new :class:`~dyn.tm.accounts.PermissionsGroup` on the
        DynECT System
        """
        self._description = description
        self._group_type = group_type
        self._all_users = all_users
        self._permission = permission
        self._user_name = user_name
        self._subgroup = subgroup
        self._zone = zone
        api_args = {}
        # Any fields that were not explicitly set should not be passed through
        for key, val in self.__dict__.items():
            if val is not None and not hasattr(val, '__call__') and \
                    key.startswith('_'):
                if key is '_group_type':
                    api_args['type'] = val
                else:
                    api_args[key[1:]] = val
        uri = '/PermissionGroup/{}/'.format(self._group_name)
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        for key, val in response['data'].items():
            if key == 'type':
                setattr(self, '_group_type', val)
            elif key == 'zone':
                self._zone = []
                for zone in val:
                    self._zone.append(zone['zone_name'])
            else:
                setattr(self, '_' + key, val)

    def _get(self):
        """Get an existing :class:`~dyn.tm.accounts.PermissionsGroup` from the
        DynECT System
        """
        response = DynectSession.get_session().execute(self.uri, 'GET')
        for key, val in response['data'].items():
            if key == 'type':
                setattr(self, '_group_type', val)
            elif key == 'zone':
                self._zone = []
                for zone in val:
                    self._zone.append(zone['zone_name'])
            else:
                setattr(self, '_' + key, val)

    def _update(self, api_args=None):
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        for key, val in response['data'].items():
            if key == 'type':
                setattr(self, '_group_type', val)
            elif key == 'zone':
                self._zone = []
                for zone in val:
                    self._zone.append(zone['zone_name'])
            else:
                setattr(self, '_' + key, val)

    @property
    def group_name(self):
        """The name of this permission group"""
        return self._group_name

    @group_name.setter
    def group_name(self, value):
        new_group_name = value
        api_args = {'new_group_name': new_group_name,
                    'group_name': self._group_name}
        self._update(api_args)
        self._group_name = new_group_name
        self.uri = '/PermissionGroup/{}/'.format(self._group_name)

    @property
    def description(self):
        """A description of this permission group"""
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        api_args = {'group_name': self._group_name,
                    'description': self._description}
        self._update(api_args)

    @property
    def group_type(self):
        """The type of this permission group"""
        return self._group_type

    @group_type.setter
    def group_type(self, value):
        self._group_type = value
        api_args = {'type': self._group_type,
                    'group_name': self._group_name}
        self._update(api_args)

    @property
    def all_users(self):
        """If 'Y', all current users will be added to the group. Cannot be
        used if user_name is passed in
        """
        return self._all_users

    @all_users.setter
    def all_users(self, value):
        self._all_users = value
        api_args = {'all_users': self._all_users,
                    'group_name': self._group_name}
        self._update(api_args)

    @property
    def permission(self):
        """A list of permissions that this group contains"""
        return self._permission

    @permission.setter
    def permission(self, value):
        self._permission = value
        api_args = {'permission': self._permission,
                    'group_name': self._group_name}
        self._update(api_args)

    @property
    def user_name(self):
        """A list of users that belong to the permission group"""
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        self._user_name = value
        api_args = {'user_name': self._user_name,
                    'group_name': self._group_name}
        self._update(api_args)

    @property
    def subgroup(self):
        """A list of groups that belong to the permission group"""
        return self._subgroup

    @subgroup.setter
    def subgroup(self, value):
        self._subgroup = value
        api_args = {'subgroup': self._subgroup,
                    'group_name': self._group_name}
        self._update(api_args)

    @property
    def zone(self):
        """A list of users that belong to the permission group"""
        return self._zone

    @zone.setter
    def zone(self, value):
        self._zone = value
        api_args = {'zone': self._zone,
                    'group_name': self._group_name}
        self._update(api_args)

    def delete(self):
        """Delete this permission group"""
        uri = '/PermissionGroup/{}/'.format(self._group_name)
        DynectSession.get_session().execute(uri, 'DELETE')

    def add_permission(self, permission):
        """Adds individual permissions to the user

        :param permission: the permission to add to this user
        """
        uri = '/PermissionGroupPermissionEntry/{}/{}/'.format(self._group_name,
                                                              permission)
        DynectSession.get_session().execute(uri, 'POST')
        self._permission.append(permission)

    def replace_permissions(self, permission=None):
        """Replaces a list of individual user permissions for the user

        :param permission: A list of permissions. Pass an empty list or omit
            the argument to clear the list of permissions of the user
        """
        api_args = {}
        if permission is not None:
            api_args['permission'] = permission
        uri = '/PermissionGroupPermissionEntry/{}/'.format(self._group_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        if permission:
            self._permission = permission
        else:
            self._permission = []

    def remove_permission(self, permission):
        """Removes the specific permission from the user

        :param permission: the permission to remove
        """
        uri = '/PermissionGroupPermissionEntry/{}/{}/'.format(self._group_name,
                                                              permission)
        DynectSession.get_session().execute(uri, 'DELETE')
        self._permission.remove(permission)

    def add_zone(self, zone, recurse='Y'):
        """Add a new Zone to this :class:`~dyn.tm.accounts.PermissionsGroup`

        :param zone: The name of the Zone to be added to this
            :class:`~dyn.tm.accounts.PermissionsGroup`
        :param recurse: A flag determining whether or not to add all sub-nodes
            of a Zone to this :class:`~dyn.tm.accounts.PermissionsGroup`
        """
        api_args = {'recurse': recurse}
        uri = '/PermissionGroupZoneEntry/{}/{}/'.format(self._group_name, zone)
        DynectSession.get_session().execute(uri, 'POST', api_args)
        self._zone.append(zone)

    def add_subgroup(self, name):
        """Add a new Sub group to this
        :class:`~dyn.tm.accounts.PermissionsGroup`

        :param name: The name of the :class:`~dyn.tm.accounts.PermissionsGroup`
            to be added to this :class:`~dyn.tm.accounts.PermissionsGroup`'s
            subgroups
        """
        uri = '/PermissionGroupSubgroupEntry/{}/{}/'.format(self._group_name,
                                                            name)
        DynectSession.get_session().execute(uri, 'POST')
        self._subgroup.append(name)

    def update_subgroup(self, subgroups):
        """Update the subgroups under this
        :class:`~dyn.tm.accounts.PermissionsGroup`

        :param subgroups: The subgroups with updated information
        """
        api_args = {'subgroup': subgroups}
        uri = '/PermissionGroupSubgroupEntry/{}/'.format(self._group_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self._subgroup = subgroups

    def delete_subgroup(self, name):
        """Remove a Subgroup from this
        :class:`~dyn.tm.accounts.PermissionsGroup`

        :param name: The name of the :class:`~dyn.tm.accounts.PermissionsGroup`
            to be remoevd from this
            :class:`~dyn.tm.accounts.PermissionsGroup`'s subgroups
        """
        uri = '/PermissionGroupSubgroupEntry/{}/{}/'.format(self._group_name,
                                                            name)
        DynectSession.get_session().execute(uri, 'DELETE')
        self._subgroup.remove(name)

    def __str__(self):
        """Custom str method"""
        return force_unicode('<PermissionsGroup>: {}').format(self.group_name)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class UserZone(object):
    """A DynECT system UserZoneEntry"""

    def __init__(self, user_name, zone_name, recurse='Y'):
        super(UserZone, self).__init__()
        self._user_name = user_name
        self._zone_name = zone_name
        self._recurse = recurse
        api_args = {'recurse': self._recurse}
        uri = '/UserZoneEntry/{}/{}/'.format(self._user_name, self._zone_name)
        respnose = DynectSession.get_session().execute(uri, 'POST', api_args)
        for key, val in respnose['data'].items():
            setattr(self, '_' + key, val)

    @property
    def user_name(self):
        """User_name property of :class:`~dyn.tm.accounts.UserZone` object is
        read only
        """
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        pass

    @property
    def recurse(self):
        """Indicates whether or not permissions should apply to subnodes of
        the `zone_name` as well
        """
        return self._recurse

    @recurse.setter
    def recurse(self, value):
        self._recurse = value
        api_args = {'recurse': self._recurse, 'zone_name': self._zone_name}
        uri = '/UserZoneEntry/{}/'.format(self._user_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    def update_zones(self, zone=None):
        """Replacement list zones where the user will now have permissions.
        Pass an empty list or omit the argument to clear the user's zone
        permissions

        :param zone: a list of zone names where the user will now have
            permissions
        """
        if zone is None:
            zone = []
        api_args = {'zone': []}
        for zone_data in zone:
            api_args['zone'].append({'zone_name': zone_data})
        uri = '/UserZoneEntry/{}/'.format(self._user_name)
        respnose = DynectSession.get_session().execute(uri, 'PUT', api_args)
        for key, val in respnose['data'].items():
            setattr(self, '_' + key, val)

    def delete(self):
        """Delete this :class:`~dyn.tm.accounts.UserZone` object from the
        DynECT System
        """
        api_args = {'recurse': self.recurse}
        uri = '/UserZoneEntry/{}/{}/'.format(self._user_name, self._zone_name)
        DynectSession.get_session().execute(uri, 'DELETE', api_args)

    def __str__(self):
        """Custom str method"""
        return force_unicode('<UserZone>: {}').format(self.user_name)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class Notifier(object):
    """DynECT System Notifier"""

    def __init__(self, *args, **kwargs):
        """Create a new :class:`~dyn.tm.accounts.Notifier` object

        :param label: The label used to identify this
            :class:`~dyn.tm.accounts.Notifier`
        :param recipients: List of Recipients attached to this
            :class:`~dyn.tm.accounts.Notifier`
        :param services: List of services attached to this
            :class:`~dyn.tm.accounts.Notifier`
        :param notifier_id: The system id of this
            :class:`~dyn.tm.accounts.Notifier`
        """
        super(Notifier, self).__init__()
        self._label = self._recipients = self._services = None
        self._notifier_id = self.uri = None
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
            self.uri = '/Notifier/{}/'.format(self._notifier_id)
        elif len(args) + len(kwargs) > 1:
            self._post(*args, **kwargs)
        elif len(kwargs) > 0 or 'label' in kwargs:
            self._post(**kwargs)
        else:
            self._get(*args, **kwargs)

    def _post(self, label=None, recipients=None, services=None):
        """Create a new :class:`~dyn.tm.accounts.Notifier` object on the
        DynECT System
        """
        if label is None:
            raise DynectInvalidArgumentError
        uri = '/Notifier/'
        self._label = label
        self._recipients = recipients
        self._services = services
        response = DynectSession.get_session().execute(uri, 'POST', self)
        self._build(response['data'])
        self.uri = '/Notifier/{}/'.format(self._notifier_id)

    def _get(self, notifier_id):
        """Get an existing :class:`~dyn.tm.accounts.Notifier` object from the
        DynECT System
        """
        self._notifier_id = notifier_id
        self.uri = '/Notifier/{}/'.format(self._notifier_id)
        response = DynectSession.get_session().execute(self.uri, 'GET')
        self._build(response['data'])

    def _build(self, data):
        for key, val in data.items():
            setattr(self, '_' + key, val)

    def _update(self, api_args=None):
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def notifier_id(self):
        """The unique System id for this Notifier"""
        return self._notifier_id

    @notifier_id.setter
    def notifier_id(self, value):
        pass

    @property
    def label(self):
        """The label used to identify this :class:`~dyn.tm.accounts.Notifier`
        """
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        self._update(api_args)

    @property
    def recipients(self):
        """List of Recipients attached to this
        :class:`~dyn.tm.accounts.Notifier`
        """
        return self._recipients

    @recipients.setter
    def recipients(self, value):
        self._recipients = value
        api_args = {'recipients': self._recipients}
        self._update(api_args)

    @property
    def services(self):
        """List of services attached to this
        :class:`~dyn.tm.accounts.Notifier`
        """
        return self._services

    @services.setter
    def services(self, value):
        self._services = value
        api_args = {'services': self._services}
        self._update(api_args)

    def delete(self):
        """Delete this :class:`~dyn.tm.accounts.Notifier` from the Dynect
        System
        """
        DynectSession.get_session().execute(self.uri, 'DELETE')

    def __str__(self):
        """Custom str method"""
        return force_unicode('<Notifier>: {}').format(self.label)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class Contact(object):
    """A DynECT System Contact"""

    def __init__(self, nickname, *args, **kwargs):
        """Create a :class:`~dyn.tm.accounts.Contact` object

        :param nickname: The nickname for this
            :class:`~dyn.tm.accounts.Contact`
        :param email: The :class:`~dyn.tm.accounts.Contact`'s email address
        :param first_name: The :class:`~dyn.tm.accounts.Contact`'s first name
        :param last_name: The :class:`~dyn.tm.accounts.Contact`'s last name
        :param organization: The :class:`~dyn.tm.accounts.Contact`'s
            organization
        :param phone: The :class:`~dyn.tm.accounts.Contact`'s phone number. Can
            be of the form: ( 0 ) ( country-code ) ( local number )
            ( extension ) Only the country-code (1-3 digits) and local number
            (at least 7 digits) are required. The extension can be up to 4
            digits. Any non-digits are ignored.
        :param address: The :class:`~dyn.tm.accounts.Contact`'s street address
        :param address2: The :class:`~dyn.tm.accounts.Contact`'s street
            address, line 2
        :param city: The :class:`~dyn.tm.accounts.Contact`'s city, part of the
            user's address
        :param country: The :class:`~dyn.tm.accounts.Contact`'s country, part
            of the :class:`~dyn.tm.accounts.Contact`'s address
        :param fax: The :class:`~dyn.tm.accounts.Contact`'s fax number
        :param notify_email: Email address where the
            :class:`~dyn.tm.accounts.Contact` should receive notifications
        :param pager_email: Email address where the
            :class:`~dyn.tm.accounts.Contact` should receive messages destined
            for a pager
        :param post_code: Zip code or Postal code
        :param state: The :class:`~dyn.tm.accounts.Contact`'s state, part of
            the :class:`~dyn.tm.accounts.Contact`'s address
        :param website: The :class:`~dyn.tm.accounts.Contact`'s website
        """
        super(Contact, self).__init__()
        self._nickname = nickname
        self._email = self._first_name = self._last_name = None
        self._organization = self._address = self._address_2 = None
        self._city = self._country = self._fax = self._notify_email = None
        self._pager_email = self._phone = self._post_code = self._state = None
        self._website = None
        self.uri = '/Contact/{}/'.format(self._nickname)
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                if key != '_nickname':
                    setattr(self, '_' + key, val)
                else:
                    setattr(self, key, val)
            self.uri = '/Contact/{}/'.format(self._nickname)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)

    def _post(self, email, first_name, last_name, organization, address=None,
              address_2=None, city=None, country=None, fax=None,
              notify_email=None, pager_email=None, phone=None, post_code=None,
              state=None, website=None):
        """Create a new :class:`~dyn.tm.accounts.Contact` on the DynECT System
        """
        self._email = email
        self._first_name = first_name
        self._last_name = last_name
        self._organization = organization
        self._address = address
        self._address_2 = address_2
        self._city = city
        self._country = country
        self._fax = fax
        self._notify_email = notify_email
        self._pager_email = pager_email
        self._phone = phone
        self._post_code = post_code
        self._state = state
        self._website = website
        response = DynectSession.get_session().execute(self.uri, 'POST', self)
        self._build(response['data'])

    def _get(self):
        """Get an existing :class:`~dyn.tm.accounts.Contact` from the DynECT
        System
        """
        response = DynectSession.get_session().execute(self.uri, 'GET')
        for key, val in response['data'].items():
            setattr(self, '_' + key, val)

    def _build(self, data):
        for key, val in data.items():
            setattr(self, '_' + key, val)

    def _update(self, api_args=None):
        """Private update method which handles building this
        :class:`~dyn.tm.accounts.Contact` object from the API JSON respnose
        """
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    @property
    def nickname(self):
        """This :class:`~dyn.tm.accounts.Contact`'s DynECT System Nickname"""
        return self._nickname

    @nickname.setter
    def nickname(self, value):
        self._nickname = value
        api_args = {'new_nickname': self._nickname}
        self._update(api_args)

    @property
    def email(self):
        """This :class:`~dyn.tm.accounts.Contact`'s DynECT System Email address
        """
        return self._email

    @email.setter
    def email(self, value):
        self._email = value
        api_args = {'email': self._email}
        self._update(api_args)

    @property
    def first_name(self):
        """The first name of this :class:`~dyn.tm.accounts.Contact`"""
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = value
        api_args = {'first_name': self._first_name}
        self._update(api_args)

    @property
    def last_name(self):
        """The last name of this :class:`~dyn.tm.accounts.Contact`"""
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = value
        api_args = {'last_name': self._last_name}
        self._update(api_args)

    @property
    def organization(self):
        """The organization this :class:`~dyn.tm.accounts.Contact` belongs to
        within the DynECT System
        """
        return self._organization

    @organization.setter
    def organization(self, value):
        self._organization = value
        api_args = {'organization': self._organization}
        self._update(api_args)

    @property
    def phone(self):
        """The phone number associated with this
        :class:`~dyn.tm.accounts.Contact`
        """
        return self._phone

    @phone.setter
    def phone(self, value):
        self._phone = value
        api_args = {'phone': self._phone}
        self._update(api_args)

    @property
    def address(self):
        """This :class:`~dyn.tm.accounts.Contact`'s street address"""
        return self._address

    @address.setter
    def address(self, value):
        self._address = value
        api_args = {'address': self._address}
        self._update(api_args)

    @property
    def address_2(self):
        """This :class:`~dyn.tm.accounts.Contact`'s street address, line 2"""
        return self._address_2

    @address_2.setter
    def address_2(self, value):
        self._address_2 = value
        api_args = {'address_2': self._address_2}
        self._update(api_args)

    @property
    def city(self):
        """This :class:`~dyn.tm.accounts.Contact`'s city"""
        return self._city

    @city.setter
    def city(self, value):
        self._city = value
        api_args = {'city': self._city}
        self._update(api_args)

    @property
    def country(self):
        """This :class:`~dyn.tm.accounts.Contact`'s Country"""
        return self._country

    @country.setter
    def country(self, value):
        self._country = value
        api_args = {'country': self._country}
        self._update(api_args)

    @property
    def fax(self):
        """The fax number associated with this
        :class:`~dyn.tm.accounts.Contact`
        """
        return self._fax

    @fax.setter
    def fax(self, value):
        self._fax = value
        api_args = {'fax': self._fax}
        self._update(api_args)

    @property
    def notify_email(self):
        """Email address where this :class:`~dyn.tm.accounts.Contact` should
        receive notifications
        """
        return self._notify_email

    @notify_email.setter
    def notify_email(self, value):
        self._notify_email = value
        api_args = {'notify_email': self._notify_email}
        self._update(api_args)

    @property
    def pager_email(self):
        """Email address where this :class:`~dyn.tm.accounts.Contact` should
        receive messages destined for a pager
        """
        return self._pager_email

    @pager_email.setter
    def pager_email(self, value):
        self._pager_email = value
        api_args = {'pager_email': self._pager_email}
        self._update(api_args)

    @property
    def post_code(self):
        """This :class:`~dyn.tm.accounts.Contacts`'s postal code, part of the
        contacts's address
        """
        return self._post_code

    @post_code.setter
    def post_code(self, value):
        self._post_code = value
        api_args = {'post_code': self._post_code}
        self._update(api_args)

    @property
    def state(self):
        """This :class:`~dyn.tm.accounts.Contact`'s state"""
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        api_args = {'state': self._state}
        self._update(api_args)

    @property
    def website(self):
        """This :class:`~dyn.tm.accounts.Contact`'s website"""
        return self._website

    @website.setter
    def website(self, value):
        self._website = value
        api_args = {'website': self._website}
        self._update(api_args)

    def delete(self):
        """Delete this :class:`~dyn.tm.accounts.Contact` from the Dynect System
        """
        DynectSession.get_session().execute(self.uri, 'DELETE')

    def __str__(self):
        """Custom str method"""
        return force_unicode('<Contact>: {}').format(self.nickname)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class IPACL(object):
    """A scoped IP ACL for logins on a customer"""

    def __init__(self, *args, **kwargs):
        """Create a :class:`~dyn.tm.accounts.IPACL` object
        :param netmasks: a list of netmasks, in CIDR
            form; no '/' assumes exact address
        :param active: Whether or not this ACL is active: 'Y' (default) or 'N'
        :param scope: The scope this :class:`~dyn.tm.accounts.IPACL` covers:
            'web' (default) or 'api'
        """
        super(IPACL, self).__init__()
        valid_scope = ['api', 'web']
        self._scope = kwargs.get('scope', 'web').lower()
        if self._scope not in valid_scope:
            raise Exception('scope can only be: {}'.format(" ".join(
                                                           valid_scope)))
        if not isinstance(kwargs.get('netmasks', []), list):
            raise Exception('Must be list of netmasks.')
        self._netmasks = " ".join(kwargs.get('netmasks', []))
        self._active = kwargs.get('active', 'Y')
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) == 0 and len(kwargs) == 0:
            self._get()
        elif len(args) == 0 and len(kwargs) == 1 and kwargs['scope']:
            self._get(scope=self._scope)
        else:
            kwargs['netmasks'] = self._netmasks
            self._post(*args, **kwargs)

    def _post(self, netmasks=None, active=None, scope=None):
        """Create a new :class:`~dyn.tm.accounts.IPACL` on the DynECT System
        """
        self.uri = '/CustomerIPACL/{}/'.format(self.scope)
        api_args = {'netmasks': self._netmasks, 'active': self._active}
        response = DynectSession.get_session().execute(
                            self.uri, 'PUT', api_args)
        self._build(response['data'])

    def _get(self, scope='web'):
        """Get an existing :class:`~dyn.tm.accounts.IPACL` from the DynECT
        System
        """
        self._scope = scope
        self.uri = '/CustomerIPACL/{}/'.format(self._scope)
        response = DynectSession.get_session().execute(self.uri, 'GET')
        self._build(response['data'])

    def _build(self, data):
        for scope in data:
            if scope['scope'] == self._scope:
                for key, val in scope.items():
                    setattr(self, '_' + key, val)

    def _update(self, api_args=None):
        """Private update method which handles building this
        :class:`~dyn.tm.accounts.IPACL` object from the API JSON response
        """
        self.uri = '/CustomerIPACL/{}/'.format(self._scope)
        response = DynectSession.get_session().execute(
                                self.uri, 'PUT', api_args)
        self._build(response['data'])

    @property
    def netmasks(self):
        """The netmask list of this :class:`~dyn.tm.accounts.IPACL`"""
        #
        return [x for x in (re.split('\r\n| |,', self._netmasks)) if x]

    @netmasks.setter
    def netmasks(self, values):
        if not isinstance(values, list):
            raise Exception('Must be list of netmasks.')

        self._netmasks = " ".join(values)
        api_args = {'netmasks': self._netmasks}
        self._update(api_args)

    @property
    def active(self):
        """The active status of this :class:`~dyn.tm.accounts.IPACL`"""
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        api_args = {'active': self._active}
        self._update(api_args)

    @property
    def scope(self):
        """The scope of this :class:`~dyn.tm.accounts.IPACL`"""
        return self._scope

    @scope.setter
    def scope(self, value):
        self._scope = value.lower()
        api_args = {'scope': self._scope}
        self._update(api_args)

    def delete(self):
        """Delete this :class:`~dyn.tm.accounts.IPACL` from the Dynect System
        """
        api_args = {'netmasks': '', 'scope': self._scope}
        DynectSession.get_session().execute(self.uri, 'PUT', api_args)
        self._netmasks = ''

    def __str__(self):
        """Custom str method"""
        return force_unicode(
            '<IPACL>: Scope: {}, Active: {}, Netmasks: {}').format(
            self._scope, self._active, " ".join(self.netmasks))

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
