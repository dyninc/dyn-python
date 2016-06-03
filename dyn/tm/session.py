# -*- coding: utf-8 -*-
"""This module implements an interface to a DynECT REST Session. It provides
easy access to all other functionality within the dynect library via
methods that return various types of DynECT objects which will provide their
own respective functionality.
"""
# API Libs
from ..core import SessionEngine
from .errors import *
from ..compat import force_unicode
from ..encrypt import AESCipher


class DynectSession(SessionEngine):
    """Base object representing a DynectSession Session"""
    __metakey__ = 'bf7886ea-c61d-40df-8c7b-4241ebed0544'
    _valid_methods = ('DELETE', 'GET', 'POST', 'PUT')
    uri_root = '/REST'

    def __init__(self, customer, username, password, host='api.dynect.net',
                 port=443, ssl=True, api_version='current', auto_auth=True,
                 key=None, history=False, proxy_host=None, proxy_port=None,
                 proxy_user=None, proxy_pass=None):
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
                                            proxy_user, proxy_pass)
        self.__cipher = AESCipher(key)
        self.extra_headers = {'API-Version': api_version}
        self.customer = customer
        self.username = username
        self.password = self.__cipher.encrypt(password)
        self.connect()
        if auto_auth:
            self.authenticate()

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
        # Need to get a new Session token
        self.execute('/REST/Session/', 'POST', self.__auth_data)
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
        self.password = self.__cipher.encrypt(new_password)

    def user_permissions_report(self, user_name=None):
        """Returns information regarding the requested user's permission access
        :param user_name: The user whose permissions will be returned. Defaults
            to the current user
        """
        api_args = dict()
        api_args['user_name'] = user_name or self.username
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

    def authenticate(self):
        """Authenticate to the DynectSession service with the provided
        credentials
        """
        api_args = {'customer_name': self.customer, 'user_name': self.username,
                    'password': self.__cipher.decrypt(self.password)}
        try:
            response = self.execute('/Session/', 'POST', api_args)
        except IOError:
            raise DynectAuthError('Unable to access the API host')
        if response['status'] != 'success':
            self.logger.error('An error was encountered authenticating to Dyn')
            raise DynectAuthError(response['msgs'])
        else:
            self.logger.info('DynectSession Authentication Successful')

    def log_out(self):
        """Log the current session out from the DynECT API system"""
        self.execute('/Session/', 'DELETE', {})
        self.close_session()

    @property
    def __auth_data(self):
        """A dict of the authdata required to authenticate as this user"""
        return {'customer_name': self.customer, 'user_name': self.username,
                'password': self.__cipher.decrypt(self.password)}

    def __str__(self):
        """str override"""
        header = super(DynectSession, self).__str__()
        return header + force_unicode(': {}, {}').format(self.customer,
                                                         self.username)