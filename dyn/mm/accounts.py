import dyn.mm.session
from dyn.mm import _APIDict

__author__ = 'jnappi'

session = dyn.mm.session.session


def get_all_accounts():
    return [Account(None, None, None, None)]


class Account(object):
    """Create or update an account.
    password, companyname, phone required for POST
    """
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
        self.uri = '/accounts'
        self._password = self._companyname = self._phone = self._address = None
        self._city = self._state = self._zipcode = self._country = None
        self._timezone = self._bounceurl = self._spamurl = None
        self._unsubscribeurl = self._trackopens = self._tracklinks = None
        self._trackunsubscribes = self._generatenewapikey = None
        if len(args) + len(kwargs) == 0:
            self._get()
        else:
            self._post(*args, **kwargs)
        self._xheaders = None

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
        response = session().execute(self.uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def _get(self):
        """Retrieve an existing :class:`Account` from the Dyn Email System"""
        accounts = get_all_accounts()
        for account in accounts:
            if account.username == self._username:
                pass

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
        if isinstance(value, dict) and not isinstance(value, _APIDict):
            new_xheaders = _APIDict(session)
            for key, val in value.items():
                new_xheaders[key] = val
            new_xheaders.uri = '/accounts/xheaders'
            self._xheaders = new_xheaders
        elif isinstance(value, _APIDict):
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
        response = session().execute(uri, 'GET', api_args)
        xheaders = _APIDict(session)
        for key, val in response.items():
            xheaders[key] = val
        xheaders.uri = '/accounts/xheaders'
        self._xheaders = xheaders

    def delete(self):
        """Delete this :class:`Account` from the Dyn Email System"""
        uri = '/accounts/delete'
        api_args = {'username': self._username}
        session().execute(uri, 'POST', api_args)


class ApprovedSender(object):
    """An email address that is able to be used in the "from" field of messages
    """
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
        self._seeding = self._status = self._dkim = None
        if len(args) + len(kwargs) > 0:
            self._post(*args, **kwargs)
        else:
            self._get()

    def _post(self, seeding=0):
        """Create a new :class:`ApprovedSender` on the Dyn Message Management
        System.

        :param seeding:
        """
        self._seeding = seeding
        uri = '/senders'
        api_args = {'emailaddress': self._emailaddress,
                    'seeding': self._seeding}
        response = session().execute(uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def _get(self):
        """Get an existing :class:`ApprovedSender` from the Dyn Message
        Management System.
        """
        uri = '/senders/details'
        api_args = {'emailaddress': self._emailaddress}
        response = session().execute(uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    def delete(self):
        """Delete this :class:`ApprovedSender`"""
        uri = '/senders/delete'
        api_args = {'emailaddress': self._emailaddress}
        session().execute(uri, 'POST', api_args)

    @property
    def seeding(self):
        """1 to opt this approved sender in for seeding; 0 (default)to opt them
        out. Seeding is used to provide insight into inbox placement. See the
        `Approved Senders
        <https://help.dynect.net/email/control-panel/senders/>`_. page for more
        information.
        """
        return self._seeding
    @seeding.setter
    def seeding(self, value):
        self._post(value)

    @property
    def status(self):
        """Retrieves the status of an approved sender -- whether or not it is
        ready for use in sending. This is most useful when you create a new
        approved sender and need to know for sure whether it is ready for use.
        """
        if self._status is None:
            pass
        return self._status
    @status.setter
    def status(self, value):
        pass

    @property
    def dkim(self):
        """DKIM identifier to set for this approved sender - identifier may
        contain only aplanumeric characters, dashes, or underscores.
        """
        return self._dkim
    @dkim.setter
    def dkim(self, value):
        uri = '/senders/dkim'
        api_args = {'emailaddress': self._emailaddress, 'dkim': value}
        response = session().execute(uri, 'POST', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)


class Recipient(object):
    """A :class:`Recipient` is an email address that is capable of recieving
    email.
    """
    def __init__(self, emailaddress):
        """Create a :class:`Recipient` object

        :param emailaddress: This :class:`Recipient`'s email adress.
        """
        self._emailaddress = emailaddress
        self._status = self._unsuppressed = self._pending_addition = None
        self._suppressed = self._pending_removal = None

    def _get(self):
        """Private getter method"""
        uri = '/recipients/status'
        api_args = {'emailaddress': self._emailaddress}
        response = session().execute(uri, 'GET', api_args)
        for key, val in response.items():
            setattr(self, '_' + key, val)

    @property
    def emailaddress(self):
        """This :class:`Recipient`'s email adress; for multiple recipients,
        specify a comma-delimited list of email addresses
        """
        return self._emailaddress
    @emailaddress.setter
    def emailaddress(self, value):
        pass

    def activate(self):
        """Updates the status of this recipient to active which allows them to
        receive email.
        """
        uri = '/recipients/activate'
        api_args = {'emailaddress': self._emailaddress}
        session().execute(uri, 'POST', api_args)


class Suppression(object):
    pass
