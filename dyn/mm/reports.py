import dyn.mm.session
import dyn.mm.errors as errors

__author__ = 'jnappi'

session = dyn.mm.session.session


class _Retrieval(object):
    def __init__(self, starttime, endtime, startindex=0, sender=None,
                 xheaders=None):
        """Create a :class:`Sent` object to perform the specified analytics
        searches against the Dyn Message Management API

        :param starttime: Start date/time range in full ISO 8601 format
        :param endtime: End date/time range in full ISO 8601 format
        :param startindex: Starting index value
        :param sender: Email address of sender to filter by
        :param xheaders: Name of custom X-header to search on
        """
        self.uri = ''
        self.starttime = starttime
        self.endtime = endtime
        self.startindex = startindex
        self.sender = sender
        self.xheaders = xheaders
        self._count = None
        self.sent = []
        self._ignore = ('_ignore', '_count', 'startindex', 'uri')
        self._update()

    def _update(self):
        """Private update method"""
        d = self.__dict__
        args = {x: d[x] for x in d if x is not None and not
                hasattr(d[x], '__call__') and x not in self._ignore}
        response = session().execute(self.uri, 'GET', args)
        self.sent = []
        for sent in response['response']['data']['sent']:
            self.sent.append(sent)

    def refresh(self):
        """Refresh the current search results

        :return: A `list` of `dict`'s containing addresses and timestamps of
            emails sent
        """
        self._update()
        return self.sent

    @property
    def count(self):
        """Return the result of a /reports/sent/count API call"""
        if self._count is None:
            uri = ''.join([self.uri, '/count/'])
            d = self.__dict__
            args = {x: d[x] for x in d if x is not None and not
                    hasattr(d[x], '__call__') and x != 'startindex'}
            response = session().execute(uri, 'GET', args)
            self._count = int(response['response']['data']['count'])
        return self._count
    @count.setter
    def count(self, value):
        pass


class _Unique(_Retrieval):
    pass


class Sent(_Retrieval):
    def __init__(self, *args, **kwargs):
        """Create a :class:`Sent` object to perform the specified analytics
        searches against the Dyn Message Management API

        :param starttime: Start date/time range in full ISO 8601 format
        :param endtime: End date/time range in full ISO 8601 format
        :param startindex: Starting index value
        :param sender: Email address of sender to filter by
        :param xheaders: Name of custom X-header to search on
        """
        self.uri = '/reports/sent'
        super(Sent, self).__init__(*args, **kwargs)


class Delivered(_Retrieval):
    def __init__(self, *args, **kwargs):
        """Create a :class:`Sent` object to perform the specified analytics
        searches against the Dyn Message Management API

        :param starttime: Start date/time range in full ISO 8601 format
        :param endtime: End date/time range in full ISO 8601 format
        :param startindex: Starting index value
        :param sender: Email address of sender to filter by
        :param xheaders: Name of custom X-header to search on
        """
        self.uri = '/reports/delivered'
        super(Delivered, self).__init__(*args, **kwargs)


class Bounce(_Retrieval):
    def __init__(self, *args, **kwargs):
        """Create a :class:`Sent` object to perform the specified analytics
        searches against the Dyn Message Management API

        :param starttime: Start date/time range in full ISO 8601 format
        :param endtime: End date/time range in full ISO 8601 format
        :param startindex: Starting index value
        :param sender: Email address of sender to filter by
        :param xheaders: Name of custom X-header to search on
        """
        self.uri = '/reports/bounces'
        super(Bounce, self).__init__(*args, **kwargs)


class Complaint(_Retrieval):
    def __init__(self, *args, **kwargs):
        """Create a :class:`Sent` object to perform the specified analytics
        searches against the Dyn Message Management API

        :param starttime: Start date/time range in full ISO 8601 format
        :param endtime: End date/time range in full ISO 8601 format
        :param startindex: Starting index value
        :param sender: Email address of sender to filter by
        :param xheaders: Name of custom X-header to search on
        """
        self.uri = '/reports/complaints'
        super(Complaint, self).__init__(*args, **kwargs)


class Issue(_Retrieval):
    def __init__(self, *args, **kwargs):
        """Create a :class:`Sent` object to perform the specified analytics
        searches against the Dyn Message Management API

        :param starttime: Start date/time range in full ISO 8601 format
        :param endtime: End date/time range in full ISO 8601 format
        :param startindex: Starting index value
        :param sender: Email address of sender to filter by
        :param xheaders: Name of custom X-header to search on
        """
        self.uri = '/reports/issues'
        super(Issue, self).__init__(*args, **kwargs)


class Interaction(object):
    # TODO: https://help.dynect.net/api/methods/reports/interactions/
    pass
