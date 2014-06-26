"""This module implements an interface to a DynECT REST Session. It provides
easy access to all other functionality within the dynect library via
methods that return various types of DynECT objects which will provide their
own respective functionality.
"""
import sys
import time
import locale
import logging
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        sys.exit('Could not find json or simplejson libraries.')
if sys.version_info[0] == 2:
    from httplib import HTTPConnection, HTTPSConnection
    from urllib import pathname2url
elif sys.version_info[0] == 3:
    from http.client import HTTPConnection, HTTPSConnection
    from urllib.request import pathname2url
# API Libs
import dyn.mm.errors as errors

__author__ = 'jnappi'


def session():
    """Accessor for the current Singleton MMSession"""
    try:
        return globals()['SESSION']
    except KeyError:
        return None


def new_session(*args, **kwargs):
    """Clear the current session and create a new one"""
    globals()['SESSION'] = None
    globals()['SESSION'] = MMSession(*args, **kwargs)
    return globals()['SESSION']


class MMSession(object):
    """Base object representing a Message Management API Session"""
    def __init__(self, apikey, host='emailapi.dynect.net', port=443, ssl=True):
        """Initialize a Dynect Rest Session object and store the provided
        credentials

        :param host: DynECT API server address
        :param port: Port to connect to DynECT API server
        :param ssl: Enable SSL
        :param apikey: your unique Email API key
        """
        super(MMSession, self).__init__()
        name = str(self.__class__).split('.')[-1][:-2]
        self.logger = logging.getLogger(name)
        self.apikey = apikey
        self.host = host
        self.port = port
        self.ssl = ssl
        self.verbose = True
        self.content_type = 'application/x-www-form-urlencoded'
        self._valid_methods = ('DELETE', 'GET', 'POST', 'PUT')
        self._conn = None
        self._encoding = locale.getdefaultlocale()[-1] or 'UTF-8'
        self.connect()

    def __new__(cls, *args, **kwargs):
        try:
            if globals()['SESSION'] is None:
                globals()['SESSION'] = super(MMSession, cls).__new__(cls)
        except KeyError:
            globals()['SESSION'] = super(MMSession, cls).__new__(cls)
        return globals()['SESSION']

    def connect(self):
        """Establishes a connection to the REST API server as defined by the
        host, port and ssl instance variables
        """
        self._conn = None
        if self.ssl:
            msg = 'Establishing SSL connection to {}:{}'.format(self.host,
                                                                self.port)
            self.logger.info(msg)
            self._conn = HTTPSConnection(self.host, self.port)
        else:
            msg = 'Establishing unencrypted connection to {}:{}'
            msg = msg.format(self.host, self.port)
            self.logger.info(msg)
            self._conn = HTTPConnection(self.host, self.port)

    def execute(self, uri, method, args=None):
        """Execute a commands against the rest server

        :param uri: The uri of the resource to access. /REST/ will be prepended
            if it is not at the beginning of the uri
        :param method: One of 'DELETE', 'GET', 'POST', or 'PUT'
        :param args: Any arguments to be sent as a part of the request
        """
        if self._conn is None:
            self.logger.debug('No established connection')
            self.connect()

        # Make sure the command is prefixed by '/rest/json'
        if not uri.startswith('/'):
            uri = '/' + uri
        if not uri.startswith('/rest/json'):
            uri = '/rest/json' + uri

        # Make sure the method is valid
        if method.upper() not in self._valid_methods:
            msg = '{} is not a valid HTTP method. Please use one of {}'
            msg.format(method, ', '.join(self._valid_methods))
            raise ValueError(msg)

        # Prepare arguments
        if args is None:
            args = {}

        # Make sure we send the apikey along
        if 'apikey' not in args:
            args['apikey'] = self.apikey

        args = json.dumps(args)

        self.logger.debug('uri: {}, method: {}, args: {}'.format(uri, method,
                                                                 args))
        # Send the command and deal with results
        self.send_command(uri, method, args)

        # Deal with the results
        response = self._conn.getresponse()

        body = response.read()
        ret_val = None
        if sys.version_info[0] == 2:
            ret_val = json.loads(body)
        elif sys.version_info[0] == 3:
            ret_val = json.loads(body.decode(self._encoding))

        return self._process_response(ret_val['response'])

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
        headers = {'Content-Type': self.content_type}

        for key, val in headers.items():
            self._conn.putheader(key, val)

        # Now the arguments
        self._conn.putheader('Content-length', '%d' % len(args))
        self._conn.endheaders()
            
        if sys.version_info[0] == 2:
            self._conn.send(args)
        elif sys.version_info[0] == 3:
            self._conn.send(bytes(args, self._encoding))

    def _process_response(self, response):
        """Process an API response for failure, incomplete, or success and
        throw any appropriate errors

        :param response: the JSON response from the request being processed
        """
        status = response['status']
        reason = response['message']
        self.logger.debug(status)
        if status == 200:
            return response
        elif status == 451:
            raise errors.EmailKeyError(reason)
        elif status == 452:
            raise errors.EmailInvalidArgumentError(reason)
        elif status == 453:
            raise errors.EmailObjectError(reason)

if __name__ == '__main__':
    my_session = MMSession('asdfadfsadf')
    my_session.execute('/accounts', 'POST', args=None)
