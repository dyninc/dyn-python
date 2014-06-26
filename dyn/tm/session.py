"""This module implements an interface to a DynECT REST Session. It provides
easy access to all other functionality within the dynect library via
methods that return various types of DynECT objects which will provide their
own respective functionality.
"""
import sys
import time
import logging
from datetime import datetime
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        sys.exit('Could not find json or simplejson libraries.')
if sys.version_info[0] == 2:
    from httplib import HTTPConnection, HTTPSConnection, HTTPException
    from urllib import pathname2url
elif sys.version_info[0] == 3:
    from http.client import HTTPConnection, HTTPSConnection, HTTPException
    from urllib.request import pathname2url
# API Libs
import dyn.tm.errors as errors
from dyn import __version__


def session():
    """Accessor for the current Singleton DynectSession"""
    try:
        return globals()['SESSION']
    except KeyError:
        return None


def new_session(*args, **kwargs):
    """Clear the current session and create a new one"""
    globals()['SESSION'] = None
    globals()['SESSION'] = DynectSession(*args, **kwargs)
    return globals()['SESSION']


class DynectSession(object):
    """Base object representing a DynectSession Session"""
    def __init__(self, customer, username, password, host='api.dynect.net', 
                 port=443, ssl=True, api_version='current', auto_auth=True):
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
        :rtype: obj
        :return: DynectSessionBase object
        """
        super(DynectSession, self).__init__()
        name = str(self.__class__).split('.')[-1][:-2]
        self.logger = logging.getLogger(name)
        self.customer = customer
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.ssl = ssl
        self.verbose = True
        self.poll_incomplete = True
        self.content_type = 'application/json'
        self._token = None
        self._conn = None
        self._last_response = None
        self._valid_methods = ('DELETE', 'GET', 'POST', 'PUT')
        self._permissions = None
        self.api_version = api_version
        self.auth_data = {}
        if auto_auth:
            self.authenticate()

    def __new__(cls, *args, **kwargs):
        try:
            if globals()['SESSION'] is None:
                globals()['SESSION'] = super(DynectSession, cls).__new__(cls,
                                                                         *args,
                                                                         **kwargs)
        except KeyError:
            globals()['SESSION'] = super(DynectSession, cls).__new__(cls, *args)
        return globals()['SESSION']

    def connect(self):
        """Establishes a connection to the REST API server as defined by the
        host, port and ssl instance variables
        """
        if self._token:
            self.logger.debug('Forcing logout from old session')
            orig_value = self.poll_incomplete
            self.poll_incomplete = False
            self.execute('/REST/Session', 'DELETE')
            self.poll_incomplete = orig_value
            self._token = None
        self._conn = None
        if self.ssl:
            msg = 'Establishing SSL connection to {}:{}'.format(self.host,
                                                                self.port)
            self.logger.info(msg)
            self._conn = HTTPSConnection(self.host, self.port, timeout=300)
        else:
            msg = 'Establishing unencrypted connection to {}:{}'.format(self.host, self.port)
            self.logger.info(msg)
            self._conn = HTTPConnection(self.host, self.port, timeout=300)

    def execute(self, uri, method, args=None, final=False):
        """Execute a commands against the rest server

        :param uri: The uri of the resource to access. /REST/ will be prepended
            if it is not at the beginning of the uri
        :param method: One of 'DELETE', 'GET', 'POST', or 'PUT'
        :param args: Any arguments to be sent as a part of the request
        :param final: boolean flag representing whether or not we have already 
            failed executing once or not
        """
        if args is None:
            args = {}
        if not isinstance(args, dict):
            # If args is an object type, parse it's dict for valid args
            # If an item in args.__dict__ has a _json attribute, use that in
            # place of the actual object
            d = args.__dict__
            args = {(x if not x.startswith('_') else x[1:]):
                    (d[x] if not hasattr(d[x], '_json') else d[x]._json)
                    for x in d if d[x] is not None and
                    not hasattr(d[x], '__call__') and x.startswith('_')}
        raw_args = args
        if self._conn is None:
            self.logger.debug('No established connection')
            self.connect()

        # Make sure the command is prefixed by '/REST/'
        if not uri.startswith('/'):
            uri = '/' + uri

        if not uri.startswith('/REST'):
            uri = '/REST' + uri

        # Make sure the method is valid
        if method.upper() not in self._valid_methods:
            msg = '{} is not a valid HTTP method. Please use one of {}'
            msg.format(method, ', '.join(self._valid_methods))
            raise ValueError(msg)

        # Prepare arguments
        if args is None:
            args = {}
        args = json.dumps(args)

        self.logger.debug('uri: {}, method: {}, args: {}'.format(uri, method,
                                                                 args))
        # Send the command and deal with results
        self.send_command(uri, method, args)

        # Deal with the results
        try:
            response = self._conn.getresponse()
        except (IOError, HTTPException) as e:
            if final:
                raise e
            else:
                # Our token is no longer valid because our session was killed
                self._token = None
                # Need to force a re-connect on next execute
                self._conn.close()
                self._conn.connect()
                # Need to get a new Session token
                self.execute('/REST/Session/', 'POST', self.auth_data)
                # Then try the current call again and Specify final as true so
                # if we fail again we can raise the actual error
                return self.execute(uri, method, raw_args, final=True)

        body = response.read()
        self._last_response = response

        if self.poll_incomplete:
            response, body = self.poll_response(response, body)
            self._last_response = response
        ret_val = None
        if sys.version_info[0] == 2:
            ret_val = json.loads(body)
        elif sys.version_info[0] == 3:
            ret_val = json.loads(body.decode('UTF-8'))

        if uri.startswith('/REST/Session') and method == 'POST':
            if ret_val['status'] == 'success':
                self.auth_data = raw_args
        self._meta_update(uri, method, ret_val)
        # Handle retrying if ZoneProp is blocking the current task
        error_msg = 'Operation blocked by current task'
        if ret_val['status'] == 'failure' and error_msg in \
                ret_val['msgs'][0]['INFO'] and not final:
            time.sleep(8)
            return self.execute(uri, method, raw_args, final=True)
        else:
            return self._process_response(ret_val, method)

    def _meta_update(self, uri, method, results):
        """Update the HTTP session token if the uri is a login or logout

        :param uri: the uri from the call being updated
        :param method: the api method
        :param results: the JSON results
        """
        # If we had a successful log in, update the token
        if uri.startswith('/REST/Session') and method == 'POST':
            if results['status'] == 'success':
                self._token = results['data']['token']

        # Otherwise, if it's a successful logout, blank the token
        if uri.startswith('/REST/Session') and method == 'DELETE':
            if results['status'] == 'success':
                self._token = None

    @property
    def permissions(self):
        if self._permissions is None:
            self._permissions = self.user_permissions_report()
        return self._permissions
    @permissions.setter
    def permissions(self, value):
        pass

    def poll_response(self, response, body):
        """Looks at a response from a REST command, and while indicates that
        the job is incomplete, poll for response

        :param response: the JSON response containing return codes
        :param body: the body of the HTTP response
        """
        while response.status == 307:
            time.sleep(1)
            uri = response.getheader('Location')
            self.logger.info('Polling {}'.format(uri))

            self.send_command(uri, 'GET', '')
            response = self._conn.getresponse()
            body = response.read()
        return response, body

    def send_command(self, uri, method, args):
        """Responsible for packaging up the API request and sending it to the
        server over the established connection

        :param uri: The uri of the resource to interact with
        :param method: The HTTP method to use
        :param args: Encoded arguments to send to the server
        """
        if '%' not in uri:
            uri = pathname2url(uri)

        self._conn.putrequest(method, uri)

        # Build headers
        user_agent = 'dyn-py v{}'.format(__version__)
        headers = {'Content-Type': self.content_type,
                   'API-Version': self.api_version,
                   'User-Agent': user_agent}

        if self._token is not None:
            headers['Auth-Token'] = self._token

        for key, val in headers.items():
            self._conn.putheader(key, val)

        # Now the arguments
        self._conn.putheader('Content-length', '%d' % len(args))
        self._conn.endheaders()

        if sys.version_info[0] == 2:
            self._conn.send(args)
        elif sys.version_info[0] == 3:
            self._conn.send(bytes(args, 'UTF-8'))

    def authenticate(self):
        """Authenticate to the DynectSession service with the provided
        credentials
        """
        api_args = {'customer_name': self.customer, 'user_name': self.username,
                    'password': self.password}
        try:
            response = self.execute('/Session/', 'POST', api_args)
        except IOError:
            raise errors.DynectAuthError('Unable to access the API host')
        if response['status'] != 'success':
            self.logger.error('An error was encountered authenticating to Dyn')
            raise errors.DynectAuthError(response['msgs'])
        else:
            self.logger.info('DynectSession Authentication Successful')

    def log_out(self):
        """Log the current session out from the DynECT API system"""
        self.execute('/Session/', 'DELETE', {})

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
                raise errors.DynectAuthError(response['msgs'])
            if method == 'POST':
                raise errors.DynectCreateError(response['msgs'])
            elif method == 'GET':
                raise errors.DynectGetError(response['msgs'])
            elif method == 'PUT':
                raise errors.DynectUpdateError(response['msgs'])
            else:
                raise errors.DynectDeleteError(response['msgs'])
        else:
            # Status was incomplete
            job_id = response['job_id']
            if not final:
                response = self.wait_for_job_to_complete(job_id)
                return self._process_response(response, method, True)
            else:
                raise errors.DynectQueryTimeout({})

    def wait_for_job_to_complete(self, job_id, timeout=120):
        """When a response comes back with a status of "incomplete" we need to
        wait and poll for the status of that job until it comes back with
        success or failure

        :param job_id: the id of the job to poll for a response from
        :param timeout: how long (in seconds) we should wait for a valid 
            response before giving up on this request
        """
        self.logger.debug('Polling for job_id: {}'.format(job_id))
        start = datetime.now()
        uri = '/Job/{}/'.format(job_id)
        api_args = {}
        # response = self.execute(uri, 'GET', api_args)
        response = {'status': 'incomplete'}
        now = datetime.now()
        self.logger.warn('Waiting for job {}'.format(job_id))
        while response['status'] is 'incomplete' and (now - start).seconds < timeout:
            time.sleep(10)
            response = self.execute(uri, 'GET', api_args)
        return response

    def update_password(self, new_password):
        """Update the current users password

        :param new_password: The new password to use
        """
        self.password = new_password
        uri = '/PASSWORD/'
        api_args = {'password': self.password}
        self.execute(uri, 'PUT', api_args)
        self.password = new_password

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

    def __str__(self):
        """str override"""
        return '<Session>: {}, {}'.format(self.customer, self.username)

    def __repr__(self):
        """print override"""
        return '<Session>: {}, {}'.format(self.customer, self.username)
