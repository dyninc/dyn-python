# -*- coding: utf-8 -*-
"""This module implements an interface to a DynECT REST Session. It provides
easy access to all other functionality within the dynect library via
methods that return various types of DynECT objects which will provide their
own respective functionality.
"""
# API Libs
from dyn.compat import force_unicode
from dyn.core import SessionEngine
from dyn.encrypt import AESCipher
from dyn.tm.errors import (DynectAuthError, DynectCreateError,
                           DynectUpdateError, DynectGetError,
                           DynectDeleteError, DynectQueryTimeout)


class DynectSession(SessionEngine):
    """Base object representing a DynectSession Session"""
    __metakey__ = 'bf7886ea-c61d-40df-8c7b-4241ebed0544'
    _valid_methods = ('DELETE', 'GET', 'POST', 'PUT')
    uri_root = '/REST'

    def __init__(self, customer, username, password, host='api.dynect.net',
                 port=443, ssl=True, api_version='current', auto_auth=True,
                 key=None, history=False, proxy_host=None, proxy_port=None,
                 proxy_user=None, proxy_pass=None, timeout=300):
        """Initialize a Dynect Rest Session object and store the provided
        credentials

        :param host: DynECT API server address
        :param port: Port to connect to DynECT API server
        :param ssl: Enable SSL
        :param api_version: version of the api to use
        :param customer: DynECT customer name
        :param username: DynECT Customer's username
        :param password: User's password
        :param auto_auth: declare whether or not to automatically log in
        :param key: A valid AES-256 password encryption key to be used when
            encrypting your password
        :param history: A boolean flag determining whether or not you would
            like to store a record of all API calls made to review later
        :param proxy_host: A proxy host to utilize
        :param proxy_port: The port that the proxy is served on
        :param proxy_user: A username to connect to the proxy with if required
        :param proxy_pass: A password to connect to the proxy with if required
        """
        super(DynectSession, self).__init__(host, port, ssl, history,
                                            proxy_host, proxy_port,
                                            proxy_user, proxy_pass,
                                            timeout=timeout)
        self.__cipher = AESCipher(key)
        self.extra_headers = {'API-Version': api_version}
        self._open_user_sessions = None
        self._active_user_session = {
            "customer_name": customer,
            "user_name": username,
            "password": self.__cipher.encrypt(password)
        }
        self.connect()
        if auto_auth:
            self.authenticate(self._active_user_session['customer_name'],
                              self._active_user_session['user_name'],
                              self._active_user_session['password'])

    def __enter__(self):
        """Yield this instance as a reference for use within the context block
        """
        yield self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """We don't particularly care about any exceptions that occured within
        the context block, so ignore them and force a log out, which handles
        closing the current session.
        """
        self.log_out()

    def _handle_error(self, uri, method, raw_args):
        """Handle the processing of a connection error with the api"""
        # Our token is no longer valid because our session was killed
        self._token = None
        # Need to force a re-connect on next execute
        self._conn.close()
        self._conn.connect()
        self._open_user_sessions = None
        # Need to get a new Session token for the last active session
        self.authenticate(self.__auth_data['customer_name'],
                          self.__auth_data['user_name'],
                          self.__auth_data['password'])

        # Then try the current call again and Specify final as true so
        # if we fail again we can raise the actual error
        return self.execute(uri, method, raw_args, final=True)

    def _process_response(self, response, method, final=False):
        """Process an API response for failure, incomplete, or success and
        throw any appropriate errors

        :param response: the JSON response from the request being processed
        :param method: the HTTP method
        :param final: boolean flag representing whether or not to continue
            polling
        """
        status = response['status']
        self.logger.debug(status)
        if status == 'success':
            return response
        elif status == 'failure':
            msgs = response['msgs']
            if method == 'POST' and 'login' in msgs[0]['INFO']:
                raise DynectAuthError(response['msgs'])
            if method == 'POST':
                raise DynectCreateError(response['msgs'])
            elif method == 'GET':
                raise DynectGetError(response['msgs'])
            elif method == 'PUT':
                raise DynectUpdateError(response['msgs'])
            else:
                raise DynectDeleteError(response['msgs'])
        else:  # Status was incomplete
            job_id = response['job_id']
            if not final:
                response = self.wait_for_job_to_complete(job_id)
                return self._process_response(response, method, True)
            else:
                raise DynectQueryTimeout({})

    def update_password(self, new_password):
        """Update the current users password

        :param new_password: The new password to use
        """
        uri = '/Password/'
        api_args = {'password': new_password}
        self.execute(uri, 'PUT', api_args)
        self._active_user_session['password'] = self.__cipher.encrypt(
            new_password)

    def user_permissions_report(self, user_name=None):
        """Returns information regarding the requested user's permission access

        :param user_name: The user whose permissions will be returned. Defaults
            to the current user
        """
        api_args = dict()
        user_name = user_name or self._active_user_session['user_name']
        api_args['user_name'] = user_name
        uri = '/UserPermissionReport/'
        response = self.execute(uri, 'POST', api_args)
        permissions = []
        for key, val in response['data'].items():
            if key == 'allowed':
                for permission in val:
                    permissions.append(permission['name'])
        return permissions

    @property
    def permissions(self):
        """Permissions of the currently logged in user"""
        if self._permissions is None:
            self._permissions = self.user_permissions_report()
        return self._permissions

    @permissions.setter
    def permissions(self, value):
        pass

    def get_active_session(self):
        """
        :return: dictionary of the currently active user session
        """
        return self._active_user_session

    def get_open_sessions(self):
        """
        :return: dictionary of all active user sessions
        """
        return self._open_user_sessions

    def add_user_session(self, user):
        """Add a new user session to the dict of open user sessions."""
        if self._open_user_sessions is None:
            self._open_user_sessions = {}
        user['token'] = self._token
        self._open_user_sessions[user['user_name']] = user
        self.set_active_user(user['user_name'])

    def set_active_user(self, username):
        """Set the currently active session based on username.
        This will update the token used for API requests
        """
        if username in self._open_user_sessions:
            self._active_user_session = self._open_user_sessions[username]
            self._token = self._active_user_session['token']
        else:
            raise ValueError("No open session for {0}".format(username))

    def log_out_active_user(self):
        """Log the active user session out of the DynECT system. Set active
        user session to next available, None if none available
        """
        # logout of active user session
        self.execute('/Session', 'DELETE', {})
        # remove session from dict of active user sessions
        del self._open_user_sessions[self._active_user_session['user_name']]

        # reset active user session to next open session
        self._active_user_session = None
        for user in self._open_user_sessions:
            self.set_active_user(user)
            break

    def authenticate(self, customer=None, username=None, password=None):
        """Authenticate to the DynectSession service with the provided
        credentials. This can be called to add multiple user sessions.
        User sessions can be managed by calling set_active_user
        """
        if customer is None:
            customer = self._active_user_session['customer_name']
        if username is None:
            username = self._active_user_session['user_name']
        if password is None:
            password = self._active_user_session['password']
        password = self.__cipher.decrypt(password)
        api_args = {'customer_name': customer, 'user_name': username,
                    'password': self.__cipher.decrypt(password)}
        try:
            response = self.execute('/Session/', 'POST', api_args)
        except IOError:
            raise DynectAuthError('Unable to access the API host')
        if response['status'] != 'success':
            self.logger.error('An error was encountered authenticating to Dyn')
            raise DynectAuthError(response['msgs'])
        else:
            self.add_user_session(api_args)
            self.logger.info('DynectSession Authentication Successful')

    def log_out(self):
        """Log the current sessions out from the DynECT API system"""
        for sess in self._open_user_sessions.keys():
            if self._active_user_session['user_name'] != sess:
                self.set_active_user(sess)
            self.log_out_active_user()

        self.close_session()

    @property
    def __auth_data(self):
        """A dict of the authdata required to authenticate as this user"""
        authdata = self._active_user_session
        return authdata

    def __str__(self):
        """str override"""
        header = super(DynectSession, self).__str__()
        return header + force_unicode(': {}, {}').format(
            self.__auth_data['customer_name'],
            self.__auth_data['user_name'])
