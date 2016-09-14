# -*- coding: utf-8 -*-
"""python 2-3 compatability layer. The bulk of this was borrowed from
kennethreitz's requests module
"""
import sys
from datetime import datetime

# -------
# Pythons
# -------

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)

# -----------------
# Version Specifics
# -----------------

if is_py2:
    # If we have no JSON-esque module installed, we can't do anything
    try:
        import json
    except ImportError as ex:
        try:
            import simplejson as json
        except ImportError:
            raise ex
    from httplib import (HTTPConnection, HTTPSConnection,
                         HTTPException)
    from urllib import urlencode, pathname2url

    string_types = (str, unicode)  # NOQA

    def prepare_to_send(args):
        return bytes(args)

    def prepare_for_loads(body, encoding):
        return body

    def force_unicode(s, encoding='UTF-8'):
        try:
            s = unicode(s)  # NOQA
        except UnicodeDecodeError:
            s = str(s).decode(encoding, 'replace')

        return s

    API_FMT = '%Y-%m-%dT%H:%M:%S'

    def str_to_date(date_string):
        """Convert a Message Manamgent API formatted string into a
        standard python ``datetime.datetime`` object.  Note that this
        object's tzinfo will not be set, in other words time zone is
        ignored (this is due to a bug in python 2).
        """
        if date_string[-6:] == '+00:00':
            date_string = date_string[:-6]
        return datetime.strptime(date_string, API_FMT)

    def date_to_str(date_obj):
        """Convert a standard python ``datetime.datetime`` object to a
        Dyn Message Management API formatted string.  Any supplied time
        zone in the input will be ignored (due to a bug in python 2).
        """
        date_string = date_obj.strftime(API_FMT)
        return date_string


elif is_py3:
    from http.client import (HTTPConnection, HTTPSConnection,  # NOQA
                             HTTPException)  # NOQA
    from urllib.parse import urlencode  # NOQA
    from urllib.request import pathname2url  # NOQA
    import json  # NOQA
    string_types = (str,)

    def prepare_to_send(args):
        return bytes(args, 'UTF-8')

    def prepare_for_loads(body, encoding):
        return body.decode(encoding)

    def force_unicode(s, encoding='UTF-8'):
        return str(s)

    API_FMT = '%Y-%m-%dT%H:%M:%S%z'

    def str_to_date(date_string):
        """Convert a Message Manamgent API formatted string into a
        standard python ``datetime.datetime`` object.
        """
        if date_string[-3] == ':':
            date_string = date_string[:-3] + date_string[-2:]
        return datetime.strptime(date_string, API_FMT)

    def date_to_str(date_obj):
        """Convert a standard python ``datetime.datetime`` object to a
        Dyn Message Management API formatted string.
        """
        date_string = date_obj.strftime(API_FMT)
        if date_string[-3] != ':':
            date_string = date_string[:-2] + ':' + date_string[-2:]
        return date_string
