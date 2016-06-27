# -*- coding: utf-8 -*-
"""The tools module is designed to be able to assist users in some of the more
common or complicated tasks one will likely find themselves needing to
accomplish via the DynECT API
"""
from dyn.compat import string_types

__author__ = 'jnappi'


def change_ip(zone, from_ip, to, v6=False, publish=False):
    """Change all occurances of an ip address to a new ip address under the
    specified zone

    :param zone: The :class:`~dyn.tm.zones.Zone` you wish to update ips for
    :param from_ip: Either a list of ip addresses or a single ip address that
        you want updated
    :param to: Either a list of ip addresses or a single ip address that will
        overwrite from_ip
    :param v6: Boolean flag to specify if we're replacing ipv4 or ipv6
        addresses (ie, whether we're updating an ARecord or AAAARecord)
    :param publish: A boolean flag denoting whether or not to publish changes
        after making them. You can optionally leave this as *False* and process
        the returned changeset prior to publishing your changes.
    :returns: A list of tuples of the form (fqdn, old, new) where fqdn is
        the fqdn of the record that was updated, old was the old ip address,
        and new is the new ip address.
    """
    records = zone.get_all_records()
    records = records['aaaa_records'] if v6 else records['a_records']
    changset = []
    changed = False

    def update_single_ip(f, t):
        l_changed = False
        for rrset in records:
            if rrset.address == f:
                fqdn, orig = rrset.fqdn, rrset.address
                rrset.address = t
                changset.append((fqdn, orig, t))
                l_changed = True
        return l_changed

    if isinstance(from_ip, string_types):
        from_ip, to = [from_ip], [to]

    for index, ip in enumerate(from_ip):
        if update_single_ip(ip, to[index]):
            publish = True

    # If we made changes, publish the zone
    if publish and changed:
        zone.publish()
    return changset


def map_ips(zone, mapping, v6=False, publish=False):
    """Change all occurances of an ip address to a new ip address under the
    specified zone

    :param zone: The :class:`~dyn.tm.zones.Zone` you wish to update ips for
    :param mapping: A *dict* of the form {'old_ip': 'new_ip'}
    :param v6: Boolean flag to specify if we're replacing ipv4 or ipv6
        addresses (ie, whether we're updating an ARecord or AAAARecord)
    :param publish: A boolean flag denoting whether or not to publish changes
        after making them. You can optionally leave this as *False* and process
        the returned changeset prior to publishing your changes.
    :returns: A list of tuples of the form (fqdn, old, new) where fqdn is
        the fqdn of the record that was updated, old was the old ip address,
        and new is the new ip address.
    """
    records = zone.get_all_records()
    records = records['aaaa_records'] if v6 else records['a_records']
    changeset = []
    changed = False

    for old, new in mapping.items():
        for record in records:
            if record.address == old:
                fqdn, orig = record.fqdn, record.address
                record.address = new
                changeset.append((fqdn, orig, new))
                changed = True

    # If we made changes, publish the zone
    if publish and changed:
        zone.publish()
    return changeset
