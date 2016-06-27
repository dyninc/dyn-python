# -*- coding: utf-8 -*-
"""This module contains all DynectDNS Errors. Each Error subclass inherits from
the base DynectError class which is only ever directly raised if something
completely unexpected happens
TODO: add a DynectInvalidPermissionsError
"""
__all__ = ['DynectAuthError', 'DynectInvalidArgumentError',
           'DynectCreateError', 'DynectUpdateError', 'DynectGetError',
           'DynectDeleteError', 'DynectQueryTimeout']
__author__ = 'jnappi'


class DynectError(Exception):
    """Base Dynect Error class"""
    def __init__(self, json_response_messages, api_type=None):
        """Create the error message based on the response in the raw JSON

        :param json_response_messages: list of messages or a single message
        :param api_type: the type of api POST that caused the failure
        """
        super(DynectError, self).__init__()
        self.message = ''
        if isinstance(json_response_messages, list):
            for message in json_response_messages:
                self.message += '{}. '.format(message['INFO'])
            if self.message == '':
                self.message = 'An unknown error occured.'
            else:
                self.message = self.message.strip()
        else:
            self.message = json_response_messages
        if api_type is not None:
            self.message = '{}: {}'.format(api_type, self.message)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class DynectAuthError(DynectError):
    """Error raised if Authentication to Dynect failed"""
    def __init__(self, *args, **kwargs):
        """Format this errors message to report back the JSON messages returned
        from a faulty Session POST
        """
        super(DynectAuthError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class DynectInvalidArgumentError(DynectError):
    """Error raised if a given argument is determined to be invalid"""
    def __init__(self, arg, value, valid_args=None):
        """Format this error's message to report back the invalid argument and
        a list of valid arguments, if such a list exists
        """
        super(DynectInvalidArgumentError, self).__init__({})
        self.message = 'Invalid argument ({}, {})'.format(arg, value)
        if valid_args is not None:
            self.message += ' :: valid values are: {}'.format(valid_args)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class DynectCreateError(DynectError):
    """Error raised if an API POST method returns with a failure"""
    def __init__(self, *args, **kwargs):
        """Format this error's message to report back the JSON error message(s)
        """
        super(DynectCreateError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class DynectUpdateError(DynectError):
    """Error raised if an API PUT method returns with a failure"""
    def __init__(self, *args, **kwargs):
        """Format this error's message to report back the JSON error message(s)
        """
        super(DynectUpdateError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class DynectGetError(DynectError):
    """Error raised if an API PUT method returns with a failure"""
    def __init__(self, *args, **kwargs):
        """Format this error's message to report back the JSON error message(s)
        """
        super(DynectGetError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class DynectDeleteError(DynectError):
    """Error raised if an API DELETE method returns with a failure"""
    def __init__(self, *args, **kwargs):
        """Format this error's message to report back the JSON error message(s)
        """
        super(DynectDeleteError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class DynectQueryTimeout(DynectError):
    """Error raised if an API call times out even after waiting for a response
    """
    def __init__(self, *args, **kwargs):
        """Format this error's message to report back the JSON error message(s)
        """
        super(DynectQueryTimeout, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message

ACTION_ERRORS = (DynectAuthError, DynectCreateError, DynectUpdateError,
                 DynectGetError, DynectDeleteError)

ALL = ACTION_ERRORS + (DynectQueryTimeout, DynectInvalidArgumentError)
