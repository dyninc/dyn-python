# -*- coding: utf-8 -*-
"""The reports module provides users with an interface to the entire /reporting
functionality of the Dyn Message Management API. While date ranges are not
explicitly required for some calls, it is strongly recommended that you include
a date range in any call that can accepts one. Without a starting and ending
date, the call will retrieve data for all time, which can take a very long
time. If you are specifically looking for data over your entire time, it is
much more efficient to retrieve the data one piece (i.e. month) at a time
rather than to retrieve it all at once.

Also worth noting is Dyn's delivery data retention policy: "DynECT Email
Delivery data retention policy states that detail data is kept for 30 days, and
aggregate (count) data is kept for 18 months. So please be aware as you search
history, that it is likely no results will appear beyond 30 days."
"""
from datetime import datetime

from ..core import cleared_class_dict
from .utils import str_to_date, date_to_str
from .session import MMSession

__author__ = 'jnappi'


class _Retrieval(object):
    """The base Report type. Because all reports have basically the same exact
    structure this class will handle all the heavy lifting. Really the only
    thing that will change between classes is the URI.
    """
    uri = ''

    def __init__(self, starttime, endtime=None, startindex=0, sender=None,
                 xheaders=None):
        """Create a :class:`~dyn.mm.reports.Sent` object to perform the
        specified analytics searches against the Dyn Message Management API

        :param starttime: Start as a datetime.datetime object
        :param endtime: End as a datetime.datetime object. Defaults to
            the value of datetime.datetime.now()
        :param startindex: Starting index value
        :param sender: Email address of sender to filter by
        :param xheaders: Name of custom X-header to search on
        """
        self.starttime = starttime
        self.endtime = endtime or datetime.now()
        self.startindex = startindex
        self.sender = sender
        self.xheaders = xheaders
        self._count = None
        self.report = []
        self._ignore = ('_ignore', '_count', 'startindex', 'uri')
        self._update()

    def _update(self):
        """Private update method"""
        d = cleared_class_dict(self.__dict__)
        args = {x: d[x] for x in d if x not in self._ignore}
        args['starttime'] = date_to_str(args['starttime'])
        args['endtime'] = date_to_str(args['endtime'])
        response = MMSession.get_session().execute(self.uri, 'GET', args)

        self.report = []
        for key in response:
            for data in response[key]:
                if 'date' in data:
                    data['date'] = str_to_date(data['date'])
                self.report.append(data)

    def refresh(self):
        """Refresh the current search results

        :return: A `list` of `dict`'s containing addresses and timestamps of
            emails sent
        """
        self._update()
        return self.report

    @property
    def count(self):
        """Return the result of a /reports/sent/count API call"""
        if self._count is None:
            uri = ''.join([self.uri, '/count/'])
            d = cleared_class_dict(self.__dict__)
            args = {x: d[x] for x in d if x != 'startindex'}
            response = MMSession.get_session().execute(uri, 'GET', args)
            self._count = response['count']
        return self._count

    @count.setter
    def count(self, value):
        pass


class _Unique(_Retrieval):
    """A subclass of _Retrieval which accepts some additional arguments and
    provides access to the "unique" query
    """
    def __init__(self, starttime, endtime=None, startindex=0, sender=None,
                 xheaders=None, domain=None, recipient=None):
        super(_Unique, self).__init__(starttime, endtime, startindex, sender,
                                      xheaders)
        self.domain = domain
        self.recipient = recipient
        self._unique = self._unique_count = None

    @property
    def unique(self):
        """A listing of all the unique interactions that occured in the provided
        time frame
        """
        if self._unique is None:
            uri = '/'.join([self.uri, 'unique'])
            d = cleared_class_dict(self.__dict__)
            args = {x: d[x] for x in d if x != 'startindex'}
            response = MMSession.get_session().execute(uri, 'GET', args)
            self._count = response['unique']
        return self._unique

    @unique.setter
    def unique(self, value):
        pass

    @property
    def unique_count(self):
        """A Count of all the unique interactions that occured in the provided
        time frame
        """
        if self._unique_count is None:
            uri = '/'.join([self.uri, 'count', 'unique'])
            d = cleared_class_dict(self.__dict__)
            args = {x: d[x] for x in d if x != 'startindex'}
            response = MMSession.get_session().execute(uri, 'GET', args)
            self._count = response['unique']
        return self._unique_count

    @unique_count.setter
    def unique_count(self, value):
        pass


class Sent(_Retrieval):
    """Returns all emails sent through the specified account for the specified
    date range, optionally filtered by sender.
    """
    uri = '/reports/sent'


class Delivered(_Retrieval):
    """Returns all emails sent through the specified account that were
    successfully delivered for the specified date range, optionally filtered by
    sender. Including a date range is highly recommended.
    """
    uri = '/reports/delivered'


class Bounce(_Retrieval):
    """Returns all email bounces for the specified account for the specified
    date range, optionally filtered by sender.
    """
    uri = '/reports/bounces'


class Complaint(_Retrieval):
    """Returns all spam complaints that the specified account received for the
    specified date range, optionally filtered by sender. Including a date range
    is highly recommended.
    """
    uri = '/reports/complaints'


class Issue(_Retrieval):
    """Returns all issues concerning the specified account for the specified
    date range. Including a date range is highly recommended.
    """
    uri = '/reports/issues'


class Opens(_Unique):
    """Returns total number of opens (or unique opens) for the specified account
    for the specified date range. Including a date range is highly recommended.
    """
    uri = '/reports/opens'


class Clicks(_Unique):
    """Returns total number of clicks (or unique clicks) for the specified
    account for the specified date range. Including a date range is highly
    recommended.
    """
    uri = '/reports/clicks'
