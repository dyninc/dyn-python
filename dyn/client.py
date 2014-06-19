import sys, time
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        sys.exit("Could not find json or simplejson libraries.")
        
if sys.version_info[0] == 2:
    from httplib import HTTPConnection, HTTPSConnection
    from urllib import pathname2url

class DynTrafficClient(object):
    """
    A class for interacting with the Dynect Managed DNS REST API.

    @ivar host: The host to connect to (defaults to api.dynect.net)
    @type host: C{str}

    @ivar port: The port to connect to (defaults to 443)
    @type port: C{int}

    @ivar ssl: A boolean indicating whether or not to use SSL encryption
    (defaults to True)
    @type ssl: C{bool}

    @ivar poll_incomplete: A boolean indicating whether we should continue to
    poll for a result if a job comes back as incomplete (defaults to True)
    @type poll_incomplete: C{bool}

    @ivar api_version: The version of the API to request (defaults to
    "current")
    @type api_version: C{str}
    """

    def __init__(
        self, host='api.dynect.net', port=443, ssl=True, api_version="current"
    ):
        """
        Basic initializer method

        @param host: The host to connect to
        @type host: C{str}
        @param port: The port to connect to
        @type port: C{int}
        @param ssl: A boolean indicating whether or not to use SSL encryption
        @type ssl: C{bool}
        """
        self.host = host
        self.port = port
        self.ssl = ssl

        # Continue polling for response if a job comes back as incomplete?
        self.poll_incomplete = True

        self.verbose = True
        self.api_version = api_version
        self.content_type = "application/json"

        self._token = None
        self._conn = None
        self._last_response = None

        self._valid_methods = set(('DELETE', 'GET', 'POST', 'PUT'))

    def _debug(self, msg):
        """
        Debug output.
        """
        if self.verbose:
            sys.stderr.write(msg)

    def connect(self):
        """
        Establishes a connection to the REST API server as defined by the host,
        port and ssl instance variables
        """
        if self._token:
            self._debug("Forcing logout from old session.\n")

            orig_value = self.poll_incomplete
            self.poll_incomplete = False
            self.execute('/REST/Session', 'DELETE')
            self.poll_incomplete = orig_value

            self._token = None


        self._conn = None

        if self.ssl:
            msg = "Establishing SSL connection to %s:%s\n" % (
                self.host, self.port
            )
            self._debug(msg)
            self._conn = HTTPSConnection(self.host, self.port)

        else:
            msg = "Establishing unencrypted connection to %s:%s\n" % (
                self.host, self.port
            )
            self._debug(msg)
            self._conn = HTTPConnection(self.host, self.port)

    def execute(self, uri, method, args = None):
        """
        Execute a commands against the rest server

        @param uri: The uri of the resource to access.  /REST/ will be prepended
        if it is not at the beginning of the uri.
        @type uri: C{str}

        @param method: One of 'DELETE', 'GET', 'POST', or 'PUT'
        @type method: C{str}

        @param args: Any arguments to be sent as a part of the request
        @type args: C{dict}
        """
        if self._conn == None:
            self._debug("No established connection\n")
            self.connect()

        # Make sure the command is prefixed by '/REST/'
        if not uri.startswith('/'):
            uri = '/' + uri

        if not uri.startswith('/REST'):
            uri = '/REST' + uri

        # Make sure the method is valid
        if method.upper() not in self._valid_methods:
            msg = "%s is not a valid HTTP method.  Please use one of %s" % (
                method, ", ".join(self._valid_methods)
            )
            raise ValueError(msg)

        # Prepare arguments
        if args is None:
            args = {}

        args = self.format_arguments(args)

        self._debug("uri: %s, method: %s, args: %s\n" % (uri, method, args))

        # Send the command and deal with results
        self.send_command(uri, method, args)

        # Deal with the results
        response = self._conn.getresponse()
        body = response.read()
        try:
            body_json=json.loads(body)
            if body_json['status'] == "success":
                self._debug("Response: Success\n")
            else:
                self._debug("Response: %s, Info: %s\n" % (body_json['status'],body_json['msgs']))
        except Exception, response_err:
            self._debug("Response: %s\n" % (response_err))
        self._last_response = response

        if self.poll_incomplete:
            response, body = self.poll_response(response, body)
            self._last_response = response

        if sys.version_info[0] == 2:
            ret_val = json.loads(body)
        elif sys.version_info[0] == 3:
            ret_val = json.loads(body.decode('UTF-8'))

        self._meta_update(uri, method, ret_val)

        return ret_val

    def _meta_update(self, uri, method, results):
        """
        Private method, not intended for use outside the class
        """
        # If we had a successful log in, update the token
        if uri.startswith('/REST/Session') and method == 'POST':
            if results['status'] == 'success':
                self._token = results['data']['token']

        # Otherwise, if it's a successful logout, blank the token
        if uri.startswith('/REST/Session') and method == 'DELETE':
            if results['status'] == 'success':
                self._token = None

    def poll_response(self, response, body):
        """
        Looks at a response from a REST command, and while indicates that the
        job is incomplete, poll for response
        """

        while response.status == 307:
            time.sleep(1)
            uri = response.getheader('Location')
            self._debug("Polling %s\n" % uri)

            self.send_command(uri, "GET", '')
            response = self._conn.getresponse()
            body = response.read()

        return response, body

    def send_command(self, uri, method, args):
        """
        Responsible for packaging up the API request and sending it to the 
        server over the established connection

        @param uri: The uri of the resource to interact with
        @type uri: C{str}

        @param method: The HTTP method to use
        @type method: C{str}

        @param args: Encoded arguments to send to the server
        @type args: C{str}
        """
        if '%' not in uri:
            uri = pathname2url(uri)

        self._conn.putrequest(method, uri)

        # Build headers
        headers = {
            'Content-Type': self.content_type,
            'API-Version': self.api_version,
            'User-Agent': 'dyn-py v0.0.1',
        }

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

    def format_arguments(self, args):
        """
        Converts the argument dictionary to the format needed to transmit the 
        REST request.

        @param args: Arguments to be passed to the REST call
        @type args: C{dict}

        @return: The encoded string to send in the REST request body
        @rtype: C{str}
        """
        args = json.dumps(args)

        return args

