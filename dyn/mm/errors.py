"""This module contains all Dyn Email Errors. Each Error subclass inherits from
the base EmailError class which is only ever directly raised if something
completely unexpected happens
"""
__author__ = 'jnappi'


class EmailError(BaseException):
    """Base Dynect Error class"""
    def __init__(self, reason):
        """Create the error message based on the response in the raw JSON

        :param reason: single message describing the reason behind this error
            being raised
        """
        super(EmailError, self).__init__()
        self.message = reason

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class EmailKeyError(EmailError):
    """Error raised if the associated API Key is missing or invalid"""
    def __init__(self, *args, **kwargs):
        super(EmailKeyError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class DynInvalidArgumentError(EmailError):
    """Error raised if a given argument is determined to be invalid"""
    def __init__(self, arg, value, valid_args=None):
        """Format this error's message to report back the invalid argument and
        a list of valid arguments, if such a list exists
        """
        super(DynInvalidArgumentError, self).__init__({})
        self.message = 'Invalid argument ({}, {})'.format(arg, value)
        if valid_args is not None:
            self.message += ' :: valid values are: {}'.format(valid_args)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class EmailInvalidArgumentError(EmailError):
    """Error raised if a required field is not provided. However, due to the
    nature or the wrapper being used this error is most likely caused but
    uncaught invalid input (i.e., letters instead of numbers, etc.).
    """
    def __init__(self, *args, **kwargs):
        super(EmailInvalidArgumentError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class EmailObjectError(EmailError):
    """This error can come up if you try to create an object that already
    exists on the Dyn Email system.
    """
    def __init__(self, *args, **kwargs):
        super(EmailObjectError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message
