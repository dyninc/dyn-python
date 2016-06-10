# -*- coding: utf-8 -*-
"""This module contains interfaces for all Report generation features of the
REST API
"""
from datetime import datetime, timedelta

from .utils import unix_date, format_csv
from .session import DynectSession

__author__ = 'elarochelle'
__all__ = ['get_check_permission', 'get_dnssec_timeline', 'get_qps',
           'get_rttm_log', 'get_rttm_rrset', 'get_zone_notes']

breakdown_map = {
    "hosts": "Hostname",
    "rrecs": "Record Type",
    "zones": "Zone"
}


def get_check_permission(permission, zone_name=None):
    """Returns a list of allowed and forbidden permissions for the currently
    logged in user based on the provided permissions array.

    :param permission: A list of permissions to check for the current user.
    :param zone_name: The zone to check for specific permissions.
    :return: A *dict* containing permission information.
    """
    api_args = {'permission': permission}
    if zone_name is not None:
        api_args['zone_name'] = zone_name
    response = DynectSession.get_session().execute('/CheckPermissionReport/',
                                                   'POST', api_args)
    return response['data']


def get_dnssec_timeline(zone_name, start_ts=None, end_ts=None):
    """Generates a report of events for the
    :class:`~dyn.tm.services.dnssec.DNSSEC` service attached to the specified
    zone has performed and has scheduled to perform.

    :param zone_name: The name of the zone with DNSSEC service
    :param start_ts: datetime.datetime instance identifying point in time for
        the start of the timeline report
    :param end_ts: datetime.datetime instance identifying point in time
        for the end of the timeline report. Defaults to datetime.datetime.now()
    :return: A *dict* containing log report data
    """
    api_args = {'zone': zone_name}
    if start_ts is not None:
        api_args['start_ts'] = unix_date(start_ts)
    if end_ts is not None:
        api_args['end_ts'] = unix_date(end_ts)
    elif end_ts is None and start_ts is not None:
        api_args['end_ts'] = unix_date(datetime.now())
    response = DynectSession.get_session().execute('/DNSSECTimelineReport/',
                                                   'POST', api_args)
    return response['data']


def get_rttm_log(zone_name, fqdn, start_ts, end_ts=None):
    """Generates a report with information about changes to an existing
    RTTM service.

    :param zone_name: The name of the zone
    :param fqdn: The FQDN where RTTM is attached
    :param start_ts: datetime.datetime instance identifying point in time for
        the log report to start
    :param end_ts: datetime.datetime instance indicating the end of the data
        range for the report. Defaults to datetime.datetime.now()
    :return: A *dict* containing log report data
    """
    end_ts = end_ts or datetime.now()
    api_args = {'zone': zone_name,
                'fqdn': fqdn,
                'start_ts': unix_date(start_ts),
                'end_ts': unix_date(end_ts)}
    response = DynectSession.get_session().execute('/RTTMLogReport/',
                                                   'POST', api_args)
    return response['data']


def get_rttm_rrset(zone_name, fqdn, ts):
    """Generates a report of regional response sets for this RTTM service
    at a given point in time.

    :param zone_name: The name of the zone
    :param fqdn: The FQDN where RTTM is attached
    :param ts: datetime.datetime instance identifying point in time for the
        report
    :return: A *dict* containing rrset report data
    """
    api_args = {'zone': zone_name,
                'fqdn': fqdn,
                'ts': unix_date(ts)}
    response = DynectSession.get_session().execute('/RTTMRRSetReport/',
                                                   'POST', api_args)
    return response['data']


def get_qps(start_ts, end_ts=None, breakdown=None, hosts=None, rrecs=None,
            zones=None):
    """Generates a report with information about Queries Per Second (QPS).

    :param start_ts: datetime.datetime instance identifying point in time for
        the QPS report
    :param end_ts: datetime.datetime instance indicating the end of the data
        range for the report. Defaults to datetime.datetime.now()
    :param breakdown: By default, most data is aggregated together.
        Valid values ('hosts', 'rrecs', 'zones').
    :param hosts: List of hosts to include in the report.
    :param rrecs: List of record types to include in report.
    :param zones: List of zones to include in report.
    :return: A *str* with CSV data
    """
    end_ts = end_ts or datetime.now()
    api_args = {'start_ts': unix_date(start_ts),
                'end_ts': unix_date(end_ts)}
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


def get_qph(start_ts, end_ts=None, breakdown=None, hosts=None, rrecs=None,
                   zones=None):
    """
    A helper method which formats the QPS CSV return data into Queries Per Hour

    :param start_ts: datetime.datetime instance identifying point in time for
        the QPS report
    :param end_ts: datetime.datetime instance indicating the end of the data
        range for the report. Defaults to datetime.datetime.now()
    :param breakdown: By default, most data is aggregated together.
        Valid values ('hosts', 'rrecs', 'zones').
    :param hosts: List of hosts to include in the report.
    :param rrecs: List of record types to include in report.
    :param zones: List of zones to include in report.
    :return: A JSON Object made up of the count of queries by day.

    {
        "data": [
            {
                "hour": "06/08/16 10:00",
                "queries": 16,
                "timestamp": 1465394400
            },
            {
                "hour": "06/08/16 11:00",
                "queries": 13,
                "timestamp": 1465398000
            }
            ...
        ]
    }

    If the 'breakdown' parameter is passed, the data will be formatted by queries per hour per 'breakdown'

    {
        "zone1.com": [
            {
                "hour": "06/08/16 20:00",
                "queries": 106,
                "timestamp": 1465430400
            },
            {
                "hour": "06/09/16 00:00",
                "queries": 1,
                "timestamp": 1465444800
            }
            ...
        ]
        ...
    }

    """

    dates = []

    # break up requests to a maximum of 2 day range
    if end_ts is not None:
        delta = end_ts - start_ts
        max_days = timedelta(days=2)

        if delta.days > 2:
            last_date = start_ts
            temp_date = last_date + max_days
            while temp_date < end_ts:
                dates.append((last_date, temp_date))
                last_date = temp_date
                temp_date = last_date + max_days
            dates.append((last_date, end_ts))

    if len(dates) == 0:
        dates.append((start_ts, end_ts))

    formatted_rows = []

    for start_date, end_date in dates:
        response = get_qps(start_date, end_ts=end_date, breakdown=breakdown, hosts=hosts, rrecs=rrecs, zones=zones)

        rows = response['csv'].encode('utf-8').split('\n')[:-1]

        formatted_rows.extend(format_csv(rows))

    hourly = {}
    hour = None
    current_breakdown_value = None
    hour_query_count = 0

    # if we have a breakdown
    if breakdown is not None:
        # order keys by breakdown (zones, rrecs, or hosts) and timestamp
        rows = sorted(rows, key=lambda k: (k[breakdown_map[breakdown]], k['Timestamp']))

    for row in formatted_rows:
        epoch = int(row['Timestamp'])
        queries = row['Queries']
        bd = row[breakdown_map[breakdown]] if breakdown is not None else None
        dt = datetime.fromtimestamp(epoch)

        # if this is the first time, or a new day, or a new breakdown value
        if (hour is None or hour.hour != dt.hour or (hour.hour == dt.hour and hour.day != dt.day)) or \
                (breakdown is not None and bd != current_breakdown_value):
            if hour is not None:
                # key for data based on if there is a breakdown value or not
                hourly_key = current_breakdown_value if current_breakdown_value is not None else 'data'

                if hourly_key not in hourly:
                    hourly[hourly_key] = []

                # insert data for (breakdown) hour
                hourly[hourly_key].append({'timestamp': int(datetime(hour.year, hour.month, hour.day, hour.hour).strftime("%s")), 'hour': hour.strftime('%x %H:00'), 'queries': hour_query_count})

            # next
            hour = dt
            current_breakdown_value = bd
            hour_query_count = 0

        hour_query_count += int(queries)

    if hour is not None:
        # key for data based on if there is a breakdown value or not
        hourly_key = current_breakdown_value if current_breakdown_value is not None else 'data'

        if hourly_key not in hourly:
            hourly[hourly_key] = []

        # insert data for (breakdown) hour
        hourly[hourly_key].append(
            {'timestamp': int(datetime(hour.year, hour.month, hour.day, hour.hour).strftime("%s")), 'hour': hour.strftime('%x %H:00'), 'queries': hour_query_count})

    return hourly


def get_qpd(start_ts, end_ts=None, breakdown=None, hosts=None, rrecs=None,
                  zones=None):
    """
    A helper method which formats the QPS CSV return data into Queries Per Day

    :param start_ts: datetime.datetime instance identifying point in time for
        the QPS report
    :param end_ts: datetime.datetime instance indicating the end of the data
        range for the report. Defaults to datetime.datetime.now()
    :param breakdown: By default, most data is aggregated together.
        Valid values ('hosts', 'rrecs', 'zones').
    :param hosts: List of hosts to include in the report.
    :param rrecs: List of record types to include in report.
    :param zones: List of zones to include in report.
    :return: A JSON Object made up of the count of queries by day.

    {
        "data": [
            {
                "day": "06/08/16",
                "queries": 296,
                "timestamp": 1465358400
            }
            ...
        ]
    }

    If the 'breakdown' parameter is passed, the data will be formatted by queries per day per 'breakdown'

    {
        "zone1.com": [
            {
                "day": "06/08/16",
                "queries": 106,
                "timestamp": 1465358400
            },
            {
                "day": "06/09/16",
                "queries": 109,
                "timestamp": 1465444800
            }
        ]
        ...
    }

    """
    dates = []

    # break up requests to a maximum of 2 day range
    if end_ts is not None:
        delta = end_ts - start_ts
        max_days = timedelta(days=2)

        if delta.days > 2:
            last_date = start_ts
            temp_date = last_date + max_days
            while temp_date < end_ts:
                dates.append((last_date, temp_date))
                last_date = temp_date
                temp_date = last_date + max_days
            dates.append((last_date, end_ts))
            
    if len(dates) == 0:
        dates.append((start_ts, end_ts))

    formatted_rows = []

    for start_date, end_date in dates:
        response = get_qps(start_date, end_ts=end_date, breakdown=breakdown, hosts=hosts, rrecs=rrecs, zones=zones)

        rows = response['csv'].encode('utf-8').split('\n')[:-1]

        formatted_rows.extend(format_csv(rows))

    daily = {}
    day = None
    current_breakdown_value = None
    day_query_count = 0

    # if we have a breakdown
    if breakdown is not None:
        # order keys by breakdown (zones, rrecs, or hosts) and timestamp
        rows = sorted(rows, key=lambda k: (k[breakdown_map[breakdown]], k['Timestamp']))

    for row in formatted_rows:
        epoch = int(row['Timestamp'])
        queries = row['Queries']
        bd = row[breakdown_map[breakdown]] if breakdown is not None else None
        dt = datetime.fromtimestamp(epoch)

        # if this is the first time, or a new day, or a new breakdown value
        if (day is None or day.day != dt.day) or \
                (breakdown is not None and bd != current_breakdown_value):
            # not the first time
            if day is not None:
                # key for data based on if there is a breakdown value or not
                daily_key = current_breakdown_value if current_breakdown_value is not None else 'data'

                if daily_key not in daily:
                    daily[daily_key] = []

                # insert data for (breakdown) day
                daily[daily_key].append({'timestamp': int(datetime(day.year, day.month, day.day).strftime("%s")), 'day': day.strftime('%x'), 'queries': day_query_count})

            # next
            day = dt
            current_breakdown_value = bd
            day_query_count = 0

        # increment query count for today
        day_query_count += int(queries)

    # repeat for last iteration
    if day is not None:
        daily_key = current_breakdown_value if current_breakdown_value is not None else 'data'

        if daily_key not in daily:
            daily[daily_key] = []

        daily[daily_key].append({'timestamp': int(datetime(day.year, day.month, day.day).strftime("%s")), 'day': day.strftime('%x'), 'queries': day_query_count})

    return daily


def get_zone_notes(zone_name, offset=None, limit=None):
    """Generates a report containing the Zone Notes for given zone.

    :param zone_name: The name of the zone
    :param offset: UNIX timestamp of the starting point at which to
        retrieve the notes
    :param limit: The maximum number of notes to be retrieved
    :return: A *list* of *dict* containing Zone Notes
    """
    api_args = {'zone': zone_name}
    if offset:
        api_args['offset'] = offset
    if limit:
        api_args['limit'] = limit
    response = DynectSession.get_session().execute('/ZoneNoteReport/',
                                                   'POST', api_args)
    return response['data']
