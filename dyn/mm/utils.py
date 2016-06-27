# -*- coding: utf-8 -*-
"""Utilities for use across the Message Manamgent module"""


class APIDict(dict):
    """Custom API Dict type"""

    def __init__(self, session_func, uri=None, *args, **kwargs):
        super(APIDict, self).__init__(*args, **kwargs)
        self.session_func = session_func
        self.uri = uri

    def __setitem__(self, key, value):
        """Handle adding a new key, value pair in this dict via an appropriate
        API PUT call
        """
        response = super(APIDict, self).__setitem__(key, value)
        api_args = {x: self[x] for x in self if x is not None and
                    not hasattr(self[x], '__call__') and key != 'uri'}
        if self.session_func is not None and self.uri is not None:
            self.session_func().execute(self.uri, 'POST', api_args)
        return response

    def __delitem__(self, key):
        """Handle the removal of an entry in this dict via an appropriate API
        call
        """
        response = super(APIDict, self).__delitem__(key)
        api_args = {x: self[x] for x in self if x is not None and
                    not hasattr(self[x], '__call__') and key != 'uri'}
        if self.session_func is not None and self.uri is not None:
            self.session_func().execute(self.uri, 'POST', api_args)
        return response
