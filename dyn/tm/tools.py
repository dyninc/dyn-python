# -*- coding: utf-8 -*-
"""The tools module is designed to be able to assist users in some of the more
common or complicated tasks one will likely find themselves needing to
accomplish via the DynECT API
"""
from ..compat import string_types

__author__ = 'jnappi'


def change_ip(zone, from_ip, to, v6=False):
    """Change all occurances of an ip address to a new ip address under the
    specified zone

    :param zone: The :class:`~dyn.tm.zones.Zone` you wish to update ips for
    :param from_ip: Either a list of ip addresses or a single ip address that
        you want updated
    :param to: Either a list of ip addresses or a single ip address that will
        overwrite from_ip
    :param v6: Boolean flag to specify if we're replacing ipv4 or ipv6 addresses
        (ie, whether we're updating an ARecord or AAAARecord)
    """
    publish = False
    records = zone.get_all_records_by_type('AAAA') if v6 else \
        zone.get_all_records_by_type('A')

    def update_single_ip(f, t):
        changed = False
        for rrset in records:
            if rrset.address == f:
                rrset.address = t
                changed = True
        return changed

    if isinstance(from_ip, string_types):
        from_ip, to = [from_ip], [to]

    for index, ip in enumerate(from_ip):
        if update_single_ip(ip, to[index]):
            publish = True

    # If we made changes, publish the zone
    if publish:
        zone.publish()


def map_ips(zone, mapping, v6=False):
    """Change all occurances of an ip address to a new ip address under the
    specified zone

    :param zone: The :class:`~dyn.tm.zones.Zone` you wish to update ips for
    :param mapping: A *dict* of the form {'old_ip': 'new_ip'}
    :param v6: Boolean flag to specify if we're replacing ipv4 or ipv6 addresses
        (ie, whether we're updating an ARecord or AAAARecord)
    """
    publish = False
    records = zone.get_all_records_by_type('AAAA') if v6 else \
        zone.get_all_records_by_type('A')

    for old, new in mapping.items():
        for record in records:
            if record.address == old:
                record.address = new
                publish = True

    # If we made changes, publish the zone
    if publish:
        zone.publish()
