# -*- coding: utf-8 -*-
"""This module contains Dyn Message Management accounts features. It's
important to note that any/all timestamps are expected as `datetime.datetime`
instances and will be returned as such.
"""
from datetime import datetime

from ..core import cleared_class_dict
from .utils import str_to_date, date_to_str, APIDict
from .errors import NoSuchAccountError
from .session import MMSession

__author__ = 'jnappi'


def get_all_accounts():
    """Return a list of all :class:`~dyn.mm.accounts.Account`'s accessible to
    the currently authenticated user
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
    """Return a list of all :class:`~dyn.mm.accounts.ApprovedSenders`'s
    accessible to the currently authenticated user
    """
    uri = '/senders'
    args = {'start_index': start_index}
    response = MMSession.get_session().execute(uri, 'GET', args)
    senders = []
    for sender in response['senders']:
        email = sender.pop('emailaddress')
        senders.append(ApprovedSender(email, api=False, **sender))
    return senders


def get_all_suppressions(startdate=None, enddate=None, startindex=0):
    """Return a list of all :class:`~dyn.mm.accounts.Suppression`'s"""
    uri = '/suppressions'
    args = {'start_index': startindex}
    if startdate:
        args['startdate'] = date_to_str(startdate)
        enddate = enddate or datetime.now()
        args['enddate'] = date_to_str(enddate)
    response = MMSession.get_session().execute(uri, 'GET', args)
    suppressions = []
    for suppression in response['suppressions']:
        email = suppression.pop('emailaddress')
        suppress_time = suppression.pop('suppresstime')
        reason_type = suppression.pop('reasontype')
        suppressions.append(Suppression(email, api=False,
                                        reasontype=reason_type,
                                        suppresstime=suppress_time))
    return suppressions


class Account(object):
    """A Message Management account instance. password, companyname, and phone
    are required for creating a new account. To access an existing Account,
    simply provide the username of the account you wish to access.
    """
    uri = '/accounts'

    def __init__(self, username, *args, **kwargs):
        """Create a new :class:`~dyn.mm.accounts.Account` object

        :param username: The username for this
            :class:`~dyn.mm.accounts.Account` - must be a valid email address,
            and must be unique among all other sub-accounts.
        :param password: :class:`~dyn.mm.accounts.Account` password to be
            assigned. May be passed as clear text or MD5-encrypted with "md5-"
            as a prefix
        :param companyname: Name of the company assigned to this
            :class:`~dyn.mm.accounts.Account`
        :param phone: Contact Phone number for this
            :class:`~dyn.mm.accounts.Account`
        :param address: The primary address associated with this
            :class:`~dyn.mm.accounts.Account`
        :param city: The City associated with this
            :class:`~dyn.mm.accounts.Account`
        :param state: The State associated with this
            :class:`~dyn.mm.accounts.Account`
        :param zipcode: The Zipcode associated with this
            :class:`~dyn.mm.accounts.Account`
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
        self._xheaders = None

    def _post(self, password, companyname, phone, address=None, city=None,
              state=None, zipcode=None, country=None, timezone=None,
              bounceurl=None, spamurl=None, unsubscribeurl=None, trackopens=0,
              tracklinks=0, trackunsubscribes=0, generatenewapikey=0):
        """Create a new :class:`~dyn.mm.accounts.Account` on the Dyn Email
        System
        """
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

        valid = ('username', 'password', 'companyname', 'phone', 'address',
                 'city', 'state', 'zipcode', 'country', 'timezone',
                 'bounceurl', 'spamurl', 'unsubscribeurl', 'trackopens',
                 'tracklinks', 'trackunsubscribes', 'generatenewapikey')
        d = cleared_class_dict(self.__dict__)
        api_args = {x[1:]: d[x] for x in d if d[x] is not None and
                    x[1:] in valid}
        response = MMSession.get_session().execute(self.uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def _get(self):
        """Retrieve an existing :class:`~dyn.mm.accounts.Account` from the Dyn
        Email System
        """
        accounts = get_all_accounts()
        found = False
        for account in accounts:
            if account.username == self._username:
                self._update(cleared_class_dict(account.__dict__))
                found = True
        if not found:
            raise NoSuchAccountError('No such Account')

    def _update(self, data):
        """Update the fields in this object with the provided data dict"""
        resp = MMSession.get_session().execute(self.uri, 'POST', data)
        for key, val in resp.items():
            setattr(self, '_' + key, val)

    @property
    def xheaders(self):
        """A list of the configured custom x-header field names associated
        with this :class:`~dyn.mm.accounts.Account`.
        """
        if self._xheaders is None:
            self._get_xheaders()
        return self._xheaders

    @xheaders.setter
    def xheaders(self, value):
        if isinstance(value, dict) and not isinstance(value, APIDict):
            new_xheaders = APIDict(MMSession.get_session)
            for key, val in value.items():
                new_xheaders[key] = val
            new_xheaders.uri = '/accounts/xheaders'
            self._xheaders = new_xheaders
        elif isinstance(value, APIDict):
            self._xheaders = value

    @property
    def username(self):
        """A list of the configured custom x-header field names associated
        with this :class:`~dyn.mm.accounts.Account`.
        """
        return self._username

    @username.setter
    def username(self, value):
        pass

    @property
    def account_name(self):
        return self._accountname

    @account_name.setter
    def account_name(self, value):
        pass

    @property
    def address(self):
        """The primary address associated with this
        :class:`~dyn.mm.accounts.Account`
        """
        return self._address

    @address.setter
    def address(self, value):
        pass

    @property
    def apikey(self):
        """The apikey for this account"""
        return self._apikey

    @apikey.setter
    def apikey(self, value):
        pass

    @property
    def city(self):
        """The City associated with this :class:`~dyn.mm.accounts.Account`"""
        return self._city

    @city.setter
    def city(self, value):
        pass

    @property
    def company_name(self):
        """The name of the company this :class:`~dyn.mm.accounts.Account` is
        registered under
        """
        return self._companyname

    @company_name.setter
    def company_name(self, value):
        pass

    @property
    def contact_name(self):
        """The name of the contact associated with this
        :class:`~dyn.mm.accounts.Account`
        """
        return self._contactname

    @contact_name.setter
    def contact_name(self, value):
        pass

    @property
    def country(self):
        """The Two letter country code associated with this
        :class:`~dyn.mm.accounts.Account`
        """
        return self._country

    @country.setter
    def country(self, value):
        pass

    @property
    def created(self):
        return self._created

    @created.setter
    def created(self, value):
        pass

    @property
    def email_sent(self):
        return self._emailsent

    @email_sent.setter
    def email_sent(self, value):
        pass

    @property
    def max_sample_count(self):
        return self._max_sample_count

    @max_sample_count.setter
    def max_sample_count(self, value):
        pass

    @property
    def phone(self):
        """The primary telephone number of the contact associated with this
        :class:`~dyn.mm.accounts.Account`"""
        return self._phone

    @phone.setter
    def phone(self, value):
        pass

    @property
    def state(self):
        """The state associated with this :class:`~dyn.mm.accounts.Account`"""
        return self._state

    @state.setter
    def state(self, value):
        pass

    @property
    def timezone(self):
        """The current timezone of the primary user of this
        :class:`~dyn.mm.accounts.Account`
        """
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        pass

    @property
    def track_links(self):
        """A settings flag determining whether or not emails sent from this
        :class:`~dyn.mm.accounts.Account` will be monitored for followed links
        """
        return self._tracklinks == 1

    @track_links.setter
    def track_links(self, value):
        pass

    @property
    def track_opens(self):
        """A settings flag determining whether or not emails sent from this
        :class:`~dyn.mm.accounts.Account` will be monitored for opens
        """
        return self._trackopens == 1

    @track_opens.setter
    def track_opens(self, value):
        pass

    @property
    def track_unsubscribes(self):
        """A settings flag determining whether or not emails sent from this
        :class:`~dyn.mm.accounts.Account` will be monitored for unsubscribes
        """
        return self._trackunsubscribes == 1

    @track_unsubscribes.setter
    def track_unsubscribes(self, value):
        pass

    @property
    def user_type(self):
        return self._usertype

    @user_type.setter
    def user_type(self, value):
        pass

    @property
    def zipcode(self):
        """The zipcode of this :class:`~dyn.mm.accounts.Account`
        """
        return self._zipcode

    @zipcode.setter
    def zipcode(self, value):
        pass

    @property
    def password(self):
        """The password for this :class:`~dyn.mm.accounts.Account`. Note:
        Unless you've just created this :class:`~dyn.mm.accounts.Account`,
        this field will be *None*.
        """
        return self._password

    @password.setter
    def password(self, value):
        pass

    @property
    def emailcap(self):
        return self._emailcap

    @emailcap.setter
    def emailcap(self, value):
        pass

    def _get_xheaders(self):
        """Build the list of the configured custom x-header field names
        associated with this :class:`~dyn.mm.accounts.Account`.
        """
        uri = '/accounts/xheaders'
        api_args = {}
        response = MMSession.get_session().execute(uri, 'GET', api_args)
        xheaders = {}
        for key, val in response.items():
            xheaders[key] = val
        self._xheaders = APIDict(MMSession.get_session, '/accounts/xheaders',
                                 xheaders)

    def delete(self):
        """Delete this :class:`~dyn.mm.accounts.Account` from the Dyn Email
        System
        """
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
        """Create an :class:`~dyn.mm.accounts.ApprovedSender` object

        :param emailaddress: The email address of this
            :class:`~dyn.mm.accounts.ApprovedSender`
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
        """Create or update a :class:`~dyn.mm.accounts.ApprovedSender` on the
        Dyn Message Management System.

        :param seeding:
        """
        self._seeding = seeding
        api_args = {'emailaddress': self._emailaddress,
                    'seeding': self._seeding}
        response = MMSession.get_session().execute(self.uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def _get(self):
        """Get an existing :class:`~dyn.mm.accounts.ApprovedSender` from the
        Dyn Message Management System.
        """
        uri = '/senders/details'
        api_args = {'emailaddress': self._emailaddress}
        response = MMSession.get_session().execute(uri, 'GET', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def _update(self, api_args):
        """Update this :class:`~dyn.mm.accounts.ApprovedSender` object."""
        if 'emailaddress' not in api_args:
            api_args['emailaddress'] = self._emailaddress
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
        """SPF for this :class:`~dyn.mm.accounts.ApprovedSender`"""
        return self._spf

    @spf.setter
    def spf(self, value):
        pass

    @property
    def dkimval(self):
        """DKIM val for this :class:`~dyn.mm.accounts.ApprovedSender`"""
        return self._dkimval

    @dkimval.setter
    def dkimval(self, value):
        pass

    def delete(self):
        """Delete this :class:`~dyn.mm.accounts.ApprovedSender`"""
        uri = '/senders/delete'
        api_args = {'emailaddress': self._emailaddress}
        MMSession.get_session().execute(uri, 'POST', api_args)

    def __str__(self):
        """str override"""
        return '<MM ApprovedSender>: {}'.format(self._emailaddress)
    __repr__ = __unicode__ = __str__


class Recipient(object):
    """A :class:`~dyn.mm.accounts.Recipient` is an email address that is
    capable of recieving email.
    """
    def __init__(self, emailaddress, method='GET'):
        """Create a :class:`~dyn.mm.accounts.Recipient` object

        :param emailaddress: This :class:`~dyn.mm.accounts.Recipient`'s email
            address.
        :param method: A Flag specifying whether you're looking for an existing
            :class:`~dyn.mm.accounts.Recipient` or if you want to create a new
            one. Because both GET and POST calls accept the same requirements
            there's no way to automatically deduce what the user is trying to
            do so you must specify either GET or POST in the constructor
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
    """A :class:`~dyn.mm.accounts.Supression` representing a suppressed email
    """
    uri = '/suppressions'

    def __init__(self, emailaddress, *args, **kwargs):
        """Create a :class:`~dyn.mm.accounts.Suppression` object.

        :param emailaddress: This email address of for the
            :class:`~dyn.mm.accounts.Suppression`'s to apply to.
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
        """Get the count attribute of this suppression for the provided range
        """
        if startdate:
            startdate = date_to_str(startdate)
            enddate = enddate or datetime.now()
            enddate = date_to_str(enddate)
            api_args = {'startdate': startdate, 'enddate': enddate}
        else:
            api_args = None

        uri = self.uri + '/count'
        response = MMSession.get_session().execute(uri, 'GET', api_args)
        self._count = int(response['count'])
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
        """Removes a :class:`~dyn.mm.accounts.Recipient` from the user's
        suppression list. This will not unbounce/uncomplain the
        :class:`~dyn.mm.accounts.Recipient`, but you will be permitted to send
        to them again.
        """
        uri = self.uri + '/activate'
        api_args = {'emailaddress': self.emailaddress}
        MMSession.get_session().execute(uri, 'POST', api_args)
