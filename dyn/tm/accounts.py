# -*- coding: utf-8 -*-
"""This module contains interfaces for all Account management features of the
REST API
"""
from .errors import DynectInvalidArgumentError
from .session import DynectSession
from ..core import APIObject, ImmutableAttribute, StringAttribute
from ..compat import force_unicode

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
    :return: a ``list`` of :class:`~dyn.tm.accounts.PermissionGroup` objects"""
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
    :return: a ``list`` of :class:`~dyn.tm.accounts.Contact` objects"""
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
    :return: a ``list`` of :class:`~dyn.tm.accounts.Notifier` objects"""
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


class UpdateUser(APIObject):
    """:class:`~dyn.tm.accounts.UpdateUser` type objects are a special form of
    a :class:`~dyn.tm.accounts.User` which are tied to a specific Dynamic DNS
    services.
    """
    uri = '/UpdateUser/'
    session_type = DynectSession
    user_name = ImmutableAttribute('user_name')
    password = StringAttribute('password')
    nickname = StringAttribute('nickname')
    status = ImmutableAttribute('status')

    def _post(self, nickname, password):
        """Create a new :class:`~dyn.tm.accounts.UpdateUser` on the DynECT
        System
        """
        api_args = {'nickname': nickname, 'password': password}
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
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

    def block(self):
        """Set the status of this :class:`~dyn.tm.accounts.UpdateUser` to
        'blocked'. This will prevent this :class:`~dyn.tm.accounts.UpdateUser`
        from logging in until they are explicitly unblocked.
        """
        self._update(block=True)

    def unblock(self):
        """Set the status of this :class:`~dyn.tm.accounts.UpdateUser` to
        'active'. This will re-enable this :class:`~dyn.tm.accounts.UpdateUser`
        to be able to login if they were previously blocked.
        """
        self._update(unblock=True)

    def sync_password(self):
        """Pull in this :class:`~dyn.tm.accounts.UpdateUser` current password
        from the DynECT System, in the unlikely event that this
        :class:`~dyn.tm.accounts.UpdateUser` object's password may have gotten
        out of sync
        """
        self._update(user_name=self._user_name)

    def delete(self):
        """Delete this :class:`~dyn.tm.accounts.UpdateUser` from the DynECT
        System. It is important to note that this operation can not be undone.
        """
        DynectSession.get_session().execute(self.uri, 'DELETE')

    def __str__(self):
        """Custom str method"""
        return force_unicode('<UpdateUser>: {}').format(self.user_name)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


# noinspection PyAttributeOutsideInit,PyUnresolvedReferences
class User(APIObject):
    """DynECT System User object"""
    uri = '/UpdateUser/{user_name}/'
    session_type = DynectSession
    user_name = ImmutableAttribute('user_name')
    first_name = StringAttribute('first_name')
    last_name = StringAttribute('last_name')
    nickname = StringAttribute('nickname')
    password = StringAttribute('password')
    organization = StringAttribute('organization')
    phone = StringAttribute('phone')
    address = StringAttribute('address')
    address_2 = StringAttribute('address_2')
    city = StringAttribute('city')
    country = StringAttribute('country')
    fax = StringAttribute('fax')
    notify_email = StringAttribute('notify_email')
    pager_email = StringAttribute('pager_email')
    post_code = StringAttribute('post_code')
    group_name = StringAttribute('group_name')
    permision = StringAttribute('permission')
    zone = StringAttribute('zone')
    forbid = StringAttribute('forbid')
    website = StringAttribute('website')
    status = ImmutableAttribute('status')

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
        self.uri = self.uri.format(user_name=user_name)
        self.permissions = []
        self.permission_groups = []
        self.groups = []
        super(User, self).__init__(*args, **kwargs)

    def _post(self, password, email, first_name, last_name, nickname,
              organization, phone, address=None, address_2=None, city=None,
              country=None, fax=None, notify_email=None, pager_email=None,
              post_code=None, group_name=None, permission=None, zone=None,
              forbid=None, status=None, website=None):
        """Create a new :class:`~dyn.tm.accounts.User` object on the DynECT
        System
        """
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
        response = DynectSession.get_session().execute(self.uri, 'POST', self)
        self._build(response['data'])

    def block(self):
        """Blocks this :class:`~dyn.tm.accounts.User` from logging in"""
        self._update(block=True)

    def unblock(self):
        """Restores this :class:`~dyn.tm.accounts.User` to an active status and
        re-enables their log-in
        """
        self._update(unblock=True)

    def add_permission(self, permission):
        """Add individual permissions to this :class:`~dyn.tm.accounts.User`

        :param permission: the permission to add
        """
        self.permissions.append(permission)
        uri = '/UserPermissionEntry/{0}/{1}/'.format(self._user_name,
                                                     permission)
        DynectSession.get_session().execute(uri, 'POST')

    def replace_permissions(self, permissions=None):
        """Replaces the list of permissions for this
        :class:`~dyn.tm.accounts.User`

        :param permissions: A list of permissions. Pass an empty list or omit
            the argument to clear the list of permissions of the
            :class:`~dyn.tm.accounts.User`
        """
        api_args = {}
        if permissions is not None:
            api_args['permissions'] = permissions
            self.permissions = permissions
        else:
            self.permissions = []
        uri = '/UserPermissionEntry/{}/'.format(self._user_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)

    def delete_permission(self, permission):
        """Remove this specific permission from the
        :class:`~dyn.tm.accounts.User`

        :param permission: the permission to remove
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
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
        if group in self.permissions:
            self.permission_groups.remove(group)
        uri = '/UserGroupEntry/{}/{}/'.format(self._user_name, group)
        DynectSession.get_session().execute(uri, 'DELETE')

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

    def __str__(self):
        """Custom str method"""
        return force_unicode('<User>: {}').format(self.user_name)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class PermissionsGroup(APIObject):
    """A DynECT System Permissions Group object"""
    uri = '/PermissionGroup/{group_name}/'
    session_type = DynectSession
    group_name = StringAttribute('group_name')
    description = StringAttribute('description')
    group_type = StringAttribute('group_type')
    all_users = StringAttribute('all_users')
    permission = StringAttribute('permission')
    user_name = StringAttribute('user_name')
    subgroup = StringAttribute('subgroup')
    zone = StringAttribute('zone')

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
        self.uri = self.uri.format(group_name=group_name)
        self._group_name = group_name
        super(PermissionsGroup, self).__init__(*args, **kwargs)

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
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Build the variables in this object by pulling out the data from the
        provided data dict. This overrided method pulls out special keys from
        the dict, prior to passing off the remaining data to super()._build
        """
        setattr(self, '_group_type', data.pop('type'))
        zones = data.pop('zone')
        self._zone = []
        for zone in zones:
            self._zone.append(zone['zone_name'])
        super(PermissionsGroup, self)._build(data)

    def _get(self):
        """Get an existing :class:`~dyn.tm.accounts.PermissionsGroup` from the
        DynECT System
        """
        response = DynectSession.get_session().execute(self.uri, 'GET')
        self._build(response['data'])

    def _update(self, **api_args):
        """Update this object on the DynECT System"""
        if 'group_name' in api_args:
            api_args['new_group_name'] = api_args.pop('group_name')
        super(PermissionsGroup, self)._update(group_name=self.group_name,
                                              **api_args)

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
        uri = '/PermissionGroupPermissionEntry/{0}/'.format(self._group_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        if permission:
            self._permission = permission
        else:
            self._permission = []

    def remove_permission(self, permission):
        """Removes the specific permission from the user

        :param permission: the permission to remove
        """
        uri = '/PermissionGroupPermissionEntry/{0}/{1}/'.format(
            self._group_name, permission)
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
        uri = '/PermissionGroupZoneEntry/{0}/{1}/'.format(self._group_name,
                                                          zone)
        DynectSession.get_session().execute(uri, 'POST', api_args)
        self._zone.append(zone)

    def add_subgroup(self, name):
        """Add a new Sub group to this
        :class:`~dyn.tm.accounts.PermissionsGroup`

        :param name: The name of the :class:`~dyn.tm.accounts.PermissionsGroup`
            to be added to this :class:`~dyn.tm.accounts.PermissionsGroup`'s
            subgroups
        """
        uri = '/PermissionGroupSubgroupEntry/{0}/{1}/'.format(self._group_name,
                                                              name)
        DynectSession.get_session().execute(uri, 'POST')
        self._subgroup.append(name)

    def update_subgroup(self, subgroups):
        """Update the subgroups under this
        :class:`~dyn.tm.accounts.PermissionsGroup`

        :param subgroups: The subgroups with updated information
        """
        api_args = {'subgroup': subgroups}
        uri = '/PermissionGroupSubgroupEntry/{0}/'.format(self._group_name)
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self._subgroup = subgroups

    def delete_subgroup(self, name):
        """Remove a Subgroup from this
        :class:`~dyn.tm.accounts.PermissionsGroup`

        :param name: The name of the :class:`~dyn.tm.accounts.PermissionsGroup`
            to be remoevd from this
            :class:`~dyn.tm.accounts.PermissionsGroup`'s subgroups
        """
        uri = '/PermissionGroupSubgroupEntry/{0}/{1}/'.format(self._group_name,
                                                              name)
        DynectSession.get_session().execute(uri, 'DELETE')
        self._subgroup.remove(name)

    def __str__(self):
        """Custom str method"""
        return force_unicode('<PermissionsGroup>: {0}').format(self.group_name)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


# noinspection PyMissingConstructor
class UserZone(APIObject):
    """A DynECT system UserZoneEntry"""
    user_name = ImmutableAttribute('user_name')
    zone_name = ImmutableAttribute('zone_name')
    recurse = StringAttribute('recurse')

    def __init__(self, user_name, zone_name, recurse='Y'):
        self._user_name = user_name
        self._zone_name = zone_name
        self._recurse = recurse
        api_args = {'recurse': self._recurse}
        self.uri = '/UserZoneEntry/{0}/{1}/'.format(self._user_name,
                                                    self._zone_name)
        respnose = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(respnose['data'])

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
        respnose = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(respnose['data'])

    def delete(self):
        """Delete this :class:`~dyn.tm.accounts.UserZone` object from the
        DynECT System
        """
        api_args = {'recurse': self.recurse}
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """Custom str method"""
        return force_unicode('<UserZone>: {0}').format(self.user_name)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


# noinspection PyUnresolvedReferences,PyMissingConstructor
class Notifier(APIObject):
    """DynECT System Notifier"""
    uri = '/Notifier/'
    session_type = DynectSession
    notifier_id = ImmutableAttribute('notifier_id')
    label = StringAttribute('label')
    recipients = None
    services = None

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
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif len(args) + len(kwargs) > 1:
            self._post(*args, **kwargs)
        elif len(kwargs) > 0 or 'label' in kwargs:
            self._post(**kwargs)
        else:
            self._get(*args, **kwargs)
        self.uri = '/Notifier/{}/'.format(self._notifier_id)

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

    def _get(self, notifier_id):
        """Get an existing :class:`~dyn.tm.accounts.Notifier` object from the
        DynECT System
        """
        self.uri = '/Notifier/{}/'.format(self._notifier_id)
        response = DynectSession.get_session().execute(self.uri, 'GET')
        self._build(response['data'])

    def __str__(self):
        """Custom str method"""
        return force_unicode('<Notifier>: {0}').format(self.label)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class Contact(APIObject):
    """A DynECT System Contact"""
    uri = '/Contact/{nickname}/'
    session_type = DynectSession
    nickname = StringAttribute('nickname')
    email = StringAttribute('email')
    first_name = StringAttribute('first_name')
    last_name = StringAttribute('last_name')
    organization = StringAttribute('organization')
    phone = StringAttribute('phone')
    address = StringAttribute('address')
    address_2 = StringAttribute('address_2')
    city = StringAttribute('city')
    country = StringAttribute('country')
    fax = StringAttribute('fax')
    notify_email = StringAttribute('notify_email')
    pager_email = StringAttribute('pager_email')
    post_code = StringAttribute('post_code')
    state = StringAttribute('state')
    website = StringAttribute('website')

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
        self.uri = self.uri.format(nickname=nickname)
        super(Contact, self).__init__()
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
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

    def _build(self, data):
        if '_nickname' in data:
            setattr(self, 'nickname', data.pop('_nickname'))
        super(Contact, self)._build(data)

    def _update(self, **api_args):
        if 'nickname' in api_args:
            api_args['new_nickname'] = api_args.pop('nickname')
        super(Contact, self)._update(api_args)

    def __str__(self):
        """Custom str method"""
        return force_unicode('<Contact>: {0}').format(self.nickname)
    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())
