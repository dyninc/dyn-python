# -*- coding: utf-8 -*-
"""This module contains Dyn Message Management accounts features. It's important
to note that any/all timestamps are expected as `datetime.datetime` instances
and will be returned as such.
"""
from datetime import datetime

from .utils import str_to_date, date_to_str, APIDict
from .session import MMSession

__author__ = 'jnappi'


def get_all_accounts():
    """Return a list of all :class:`Account`'s accessible to the currently
    authenticated user
    """
    uri = '/accounts'
    response = MMSession.get_session().execute(uri, 'GET')
    accounts = []
    for account in response['accounts']:
        username = account.pop('username')
        cap = response['emailcap']
        accounts.append(Account(username, api=False, emailcap=cap, **account))
    return accounts


def get_all_senders(start_index=0):
    """Return a list of all :class:`ApprovedSenders`'s accessible to the
    currently authenticated user
    """
    uri = '/senders'
    args = {'start_index': start_index}
    response = MMSession.get_session().execute(uri, 'GET', args)
    senders = []
    for sender in response['senders']:
        email = sender.pop('emailaddress')
        senders.append(ApprovedSender(email, api=False, **sender))
    return senders


def get_all_suppressions(startdate=None, enddate=datetime.now(), startindex=0):
    """Return a list of all :class:`Suppression`'s"""
    uri = '/suppressions'
    args = {'start_index': startindex}
    response = MMSession.get_session().execute(uri, 'GET', args)
    suppressions = []
    for sender in response['senders']:
        email = sender.pop('emailaddress')
        suppress_time = sender.pop('suppresstime')
        suppressions.append(Suppression(email, api=False,
                                        suppresstime=suppress_time))
    return suppressions


class Account(object):
    """A Message Management account instance. password, companyname, and phone
    are required for creating a new account. To access an existing Account,
    simply provide the username of the account you wish to access.
    """
    uri = '/accounts'

    def __init__(self, username, *args, **kwargs):
        """Create a new :class:`Account` object

        :param username: The username for this :class:`Account` - must be a
            valid email address, and must be unique among all other
            sub-accounts.
        :param password: :class:`Account` password to be assigned. May be passed
            as clear text or MD5-encrypted with "md5-" as a prefix
        :param companyname: Name of the company assigned to this
            :class:`Account`
        :param phone: Contact Phone number for this :class:`Account`
        :param address: Address
        :param city: City
        :param state: State
        :param zipcode: Zipcode
        :param country: Two-letter English ISO 3166 country code
        :param timezone: The timezone of the account, in [+/-]h.mm format
        :param bounceurl: Bounce postback URL
        :param spamurl: Spam postback URL
        :param unsubscribeurl: Unsubscribe postback URL
        :param trackopens: Toggle open tracking (1 or 0).
        :param tracklinks: Toggle click tracking (1 or 0).
        :param trackunsubscribes: Toggle automatic list-unsubscribe support
            (1 or 0).
        :param generatenewapikey: Used to create a new API key for an existing
            account (1 or 0).
        """
        super(Account, self).__init__()
        self._username = username
        self._accountname = self._address = self._apikey = self._city = None
        self._companyname = self._contactname = self._country = None
        self._created = self._emailsent = self._max_sample_count = None
        self._phone = self._state = self._timezone = self._tracklinks = None
        self._trackopens = self._trackunsubscribes = self._usertype = None
        self._zipcode = self._password = self._emailcap = None
        if 'api' in kwargs:
            del kwargs['api']
            self._update(kwargs)
        elif len(args) + len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)
        self._xheaders = APIDict(session, '/accounts/xheaders')

    def _post(self, password, companyname, phone, address=None, city=None,
              state=None, zipcode=None, country=None, timezone=None,
              bounceurl=None, spamurl=None, unsubscribeurl=None, trackopens=0,
              tracklinks=0, trackunsubscribes=0, generatenewapikey=0):
        """Create a new :class:`Account` on the Dyn Email System"""
        self._password = password
        self._companyname = companyname
        self._phone = phone
        self._address = address
        self._city = city
        self._state = state
        self._zipcode = zipcode
        self._country = country
        self._timezone = timezone
        self._bounceurl = bounceurl
        self._spamurl = spamurl
        self._unsubscribeurl = unsubscribeurl
        self._trackopens = trackopens
        self._tracklinks = tracklinks
        self._trackunsubscribes = trackunsubscribes
        self._generatenewapikey = generatenewapikey
        d = self.__dict__
        api_args = {x: d[x] for x in d if x is not None and
                    not hasattr(d[x], '__call__') and x != 'uri'
                    and x.startswith('_')}
        response = MMSession.get_session().execute(self.uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def _get(self):
        """Retrieve an existing :class:`Account` from the Dyn Email System"""
        accounts = get_all_accounts()
        for account in accounts:
            if account.username == self._username:
                pass

    def _update(self, data):
        """Update the fields in this object with the provided data dict"""
        for key, val in data.items():
            setattr(self, '_' + key, val)

    @property
    def xheaders(self):
        """A list of the configured custom x-header field names associated
        with this :class:`Account`.
        """
        if self._xheaders is None:
            self._get_xheaders()
        return self._xheaders
    @xheaders.setter
    def xheaders(self, value):
        if isinstance(value, dict) and not isinstance(value, APIDict):
            new_xheaders = APIDict(session)
            for key, val in value.items():
                new_xheaders[key] = val
            new_xheaders.uri = '/accounts/xheaders'
            self._xheaders = new_xheaders
        elif isinstance(value, APIDict):
            self._xheaders = value

    @property
    def username(self):
        """A list of the configured custom x-header field names associated
        with this :class:`Account`.
        """
        return self._username
    @username.setter
    def username(self, value):
        pass

    def _get_xheaders(self):
        """Build the list of the configured custom x-header field names
        associated with this :class:`Account`.
        """
        uri = '/accounts/xheaders'
        api_args = {}
        response = MMSession.get_session().execute(uri, 'GET', api_args)
        xheaders = APIDict(session)
        for key, val in response.items():
            xheaders[key] = val
        xheaders.uri = '/accounts/xheaders'
        self._xheaders = xheaders

    def delete(self):
        """Delete this :class:`Account` from the Dyn Email System"""
        uri = '/accounts/delete'
        api_args = {'username': self._username}
        MMSession.get_session().execute(uri, 'POST', api_args)

    def __str__(self):
        """str override"""
        return '<MM Account>: {}'.format(self._username)
    __repr__ = __unicode__ = __str__


class ApprovedSender(object):
    """An email address that is able to be used in the "from" field of messages
    """
    uri = '/senders'

    def __init__(self, emailaddress, *args, **kwargs):
        """Create an :class:`ApprovedSender` object

        :param emailaddress: The email address of this :class:`ApprovedSender`
        :param seeding: 1 to opt this approved sender in for seeding; 0
            (default)to opt them out. Seeding is used to provide insight into
            inbox placement. See the `Approved Senders
            <https://help.dynect.net/email/control-panel/senders/>`_. page for
            more information.
        """
        self._emailaddress = emailaddress
        self._seeding = self._status = self._dkim = self._spf = None
        self._dkimval = None
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
        elif len(args) + len(kwargs) > 0:
            self._post(*args, **kwargs)
        else:
            self._get()

    def _post(self, seeding=0):
        """Create or update a :class:`ApprovedSender` on the Dyn Message
        Management System.

        :param seeding:
        """
        self._seeding = seeding
        api_args = {'emailaddress': self._emailaddress,
                    'seeding': self._seeding}
        response = MMSession.get_session().execute(self.uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def _get(self):
        """Get an existing :class:`ApprovedSender` from the Dyn Message
        Management System.
        """
        uri = '/senders/details'
        api_args = {'emailaddress': self._emailaddress}
        response = MMSession.get_session().execute(uri, 'GET', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def _update(self, api_args):
        """Update this :class:`ApprovedSender` object."""
        response = MMSession.get_session().execute(self.uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    @property
    def seeding(self):
        """1 to opt this approved sender in for seeding; 0 to opt them out
        (default). Seeding is used to provide insight into inbox placement.
        See the `Approved Senders
        <https://help.dynect.net/email/control-panel/senders/>`_. page for more
        information.
        """
        if self._seeding is None:
            self._seeding = self.status
        return self._seeding
    @seeding.setter
    def seeding(self, value):
        if value in range(0, 2):
            self._update({'seeding': value})

    @property
    def status(self):
        """Retrieves the status of an approved sender -- whether or not it is
        ready for use in sending. This is most useful when you create a new
        approved sender and need to know for sure whether it is ready for use.
        """
        uri = '/senders/status'
        args = {'emailaddress': self._emailaddress}
        response = MMSession.get_session().execute(uri, 'GET', args)
        for key in response:
            self._status = response[key]
        return self._status
    @status.setter
    def status(self, value):
        pass

    @property
    def dkim(self):
        """DKIM identifier for this approved sender - identifier may contain
        only aplanumeric characters, dashes, or underscores.
        """
        return self._dkim
    @dkim.setter
    def dkim(self, value):
        uri = '/senders/dkim'
        api_args = {'emailaddress': self._emailaddress, 'dkim': value}
        response = MMSession.get_session().execute(uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    @property
    def spf(self):
        """SPF for this :class:`ApprovedSender`"""
        return self._spf
    @spf.setter
    def spf(self, value):
        pass

    @property
    def dkimval(self):
        """DKIM val for this :class:`ApprovedSender`"""
        return self._dkimval
    @dkimval.setter
    def dkimval(self, value):
        pass

    def delete(self):
        """Delete this :class:`ApprovedSender`"""
        uri = '/senders/delete'
        api_args = {'emailaddress': self._emailaddress}
        MMSession.get_session().execute(uri, 'POST', api_args)

    def __str__(self):
        """str override"""
        return '<MM ApprovedSender>: {}'.format(self._emailaddress)
    __repr__ = __unicode__ = __str__


class Recipient(object):
    """A :class:`Recipient` is an email address that is capable of recieving
    email.
    """
    def __init__(self, emailaddress, method='GET'):
        """Create a :class:`Recipient` object

        :param emailaddress: This :class:`Recipient`'s email adress.
        :param method: A Flag specifying whether you're looking for an existing
            :class:`Recipient` or if you want to create a new one. Because both
            GET and POST calls accept the same requirements there's no way to
            automatically deduce what the user is trying to do so you must
            specify either GET or POST in the constructor
        """
        self.emailaddress = emailaddress
        self.status = self.unsuppressed = self.pending_addition = None
        self.suppressed = self.pending_removal = None
        if method == 'GET':
            self._get()
        else:
            self._post()

    def _get(self):
        """Private getter method"""
        uri = '/recipients/status'
        api_args = {'emailaddress': self.emailaddress}
        response = MMSession.get_session().execute(uri, 'GET', api_args)
        for key, val in response.items():
            setattr(self, key, val)

    def _post(self):
        """Activate a new recipient"""
        uri = '/recipients/activate'
        api_args = {'emailaddress': self.emailaddress}
        # Note: this api call returns nothing, so we won't parse it for data
        MMSession.get_session().execute(uri, 'POST', api_args)

    def activate(self):
        """Updates the status of this recipient to active which allows them to
        receive email.
        """
        uri = '/recipients/activate'
        api_args = {'emailaddress': self.emailaddress}
        MMSession.get_session().execute(uri, 'POST', api_args)


class Suppression(object):
    """A :class:`Supression` representing a suppressed email"""
    uri = '/suppressions'

    def __init__(self, emailaddress, *args, **kwargs):
        """Create a :class:`Suppression` object.

        :param emailaddress: This email address of for the
            :class:`Suppression`'s to apply to.
        """
        self.emailaddress = emailaddress
        self._count = self._suppresstime = None
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                if key == 'suppresstime':
                    self._suppresstime = str_to_date(val)
                else:
                    setattr(self, '_' + key, val)
        elif len(args) + len(kwargs) == 0:
            self._post()

    def _post(self):
        """Activate a new recipient"""
        api_args = {'emailaddress': self.emailaddress}
        # Note: this api call returns nothing, so we won't parse it for data
        MMSession.get_session().execute(self.uri, 'POST', api_args)

    def get_count(self, startdate=None, enddate=None):
        """Get the count attribute of this suppression for the provided range"""
        startdate = date_to_str(startdate)
        enddate = date_to_str(enddate)

        uri = self.uri + '/count'
        api_args = {'startdate': startdate, 'enddate': enddate}
        response = MMSession.get_session().execute(uri, 'GET', api_args)
        self._count = response['count']
        return self._count

    @property
    def count(self):
        """the total number of email addresses in the suppression list for the
        specified account, filtered by date range.
        """
        return self._count
    @count.setter
    def count(self, value):
        pass

    def activate(self):
        """Removes one or more :class:`Recipient`'s from the user's suppression
        list. This will not unbounce/uncomplain the :class:`Recipient`(s), but
        you will be permitted to send to them again.
        """
        uri = self.uri + '/activate'
        api_args = {'emailaddress': self.emailaddress}
        MMSession.get_session().execute(uri, 'POST', api_args)
