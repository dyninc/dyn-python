# -*- coding: utf-8 -*-
"""python 2-3 compatability layer. The bulk of this was borrowed from
kennethreitz's requests module
"""
import sys

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
    from httplib import HTTPConnection, HTTPSConnection, HTTPException
    from urllib import urlencode, pathname2url

    string_types = (str, unicode)

    def prepare_to_send(args):
        return bytes(args)

    def prepare_for_loads(body, encoding):
        return body

    def force_unicode(s, encoding='UTF-8'):
        try:
            s = unicode(s)
        except UnicodeDecodeError:
            s = str(s).decode(encoding, 'replace')

        return s

elif is_py3:
    from http.client import HTTPConnection, HTTPSConnection, HTTPException
    from urllib.parse import urlencode
    from urllib.request import pathname2url
    import json
    string_types = (str,)

    def prepare_to_send(args):
        return bytes(args, 'UTF-8')

    def prepare_for_loads(body, encoding):
        return body.decode(encoding)

    def force_unicode(s, encoding='UTF-8'):
        return str(s)
