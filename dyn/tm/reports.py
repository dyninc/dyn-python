# -*- coding: utf-8 -*-
"""This module contains interfaces for all Report generation features of the
REST API
"""
from .session import DynectSession

__author__ = 'elarochelle'
__all__ = ['get_check_permission', 'get_dnssec_timeline', 'get_qps',
           'get_rttm_log', 'get_rttm_rrset', 'get_zone_notes']


def get_check_permission(permission, zone_name=None):
    """Returns a list of allowed and forbidden permissions for the currently
    logged in user based on the provided permissions array.

    :param permission: A list of permissions to check for the current user.
    :param zone_name: The zone to check for specific permissions.
    :return: A :class:`dict` containing permission information.
    """
    api_args = {'permission': permission}
    if zone_name is not None:
        api_args['zone_name'] = zone_name
    response = DynectSession.get_session().execute('/CheckPermissionReport/',
                                                   'POST', api_args)
    return response['data']


def get_dnssec_timeline(zone_name, start_ts=None, end_ts=None):
    """Generates a report of events for the :class:`DNSSEC` service
    attached to the specified zone has performed and has scheduled
    to perform.

    :param zone_name: The name of the zone with DNSSEC service
    :param start_ts: UNIX timestamp identifying point in time for the
        report
    :param end_ts: UNIX timestamp indicating the end of the data range for
        the report
    :return: A :class:`dict` containing log report data
    """
    api_args = {'zone': zone_name}
    if start_ts is not None:
        api_args['start_ts'] = start_ts
    if end_ts is not None:
        api_args['end_ts'] = end_ts
    response = DynectSession.get_session().execute('/DNSSECTimelineReport/',
                                                   'POST', api_args)
    return response['data']


def get_rttm_log(zone_name, fqdn, start_ts, end_ts):
    """Generates a report with information about changes to an existing
    RTTM service.

    :param zone_name: The name of the zone
    :param fqdn: The FQDN where RTTM is attached
    :param start_ts: UNIX timestamp identifying point in time for the log
        report
    :param end_ts: UNIX timestamp indicating the end of the data range for
        the report
    :return: A :class:`dict` containing log report data
    """
    api_args = {'zone': zone_name,
                'fqdn': fqdn,
                'start_ts': start_ts,
                'end_ts': end_ts}
    response = DynectSession.get_session().execute('/RTTMLogReport/',
                                                   'POST', api_args)
    return response['data']


def get_rttm_rrset(zone_name, fqdn, ts):
    """Generates a report of regional response sets for this RTTM service
    at a given point in time.

    :param zone_name: The name of the zone
    :param fqdn: The FQDN where RTTM is attached
    :param ts: UNIX timestamp identifying point in time for the report
    :return: A :class:`dict` containing rrset report data
    """
    api_args = {'zone': zone_name,
                'fqdn': fqdn,
                'ts': ts}
    response = DynectSession.get_session().execute('/RTTMRRSetReport/',
                                                   'POST', api_args)
    return response['data']


def get_qps(start_ts, end_ts, breakdown=None, hosts=None, rrecs=None,
            zones = None):
    """Generates a report with information about Queries Per Second (QPS).

    :param start_ts: UNIX timestamp identifying point in time for the QPS
        report
    :param end_ts: UNIX timestamp indicating the end of the data range for
        the report
    :param breakdown: By default, most data is aggregated together.
        Valid values ('hosts', 'rrecs', 'zones').
    :param hosts: List of hosts to include in the report.
    :param rrecs: List of record types to include in report.
    :param zones: List of zones to include in report.
    :return: A :class:`str` with CSV data
    """
    api_args = {'start_ts': start_ts,
                'end_ts': end_ts}
    if breakdown is not None:
        api_args['breakdown'] = breakdown
    if hosts is not None:
        api_args['hosts'] = hosts
    if rrecs is not None:
        api_args['rrecs'] = rrecs
    if zones is not None:
        api_args['zones'] = zones
    response = DynectSession.get_session().execute('/QPSReport/',
                                                   'POST', api_args)
    return response['data']


def get_zone_notes(zone_name, offset=None, limit=None):
    """Generates a report containing the Zone Notes for given zone.

    :param zone_name: The name of the zone
    :param offset: UNIX timestamp of the starting point at which to
        retrieve the notes
    :param limit: The maximum number of notes to be retrieved
    :return: A :class:`list` of :class:`dict` containing Zone Notes
    """
    api_args = {'zone': zone_name}
    if offset:
        api_args['offset'] = offset
    if limit:
        api_args['limit'] = limit
    response = DynectSession.get_session().execute('/ZoneNoteReport/',
                                                   'POST', api_args)
    return response['data']
