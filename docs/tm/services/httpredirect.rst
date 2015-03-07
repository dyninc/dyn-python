.. _reversedns-index:

HTTP Redirect
=============

.. autoclass:: dyn.tm.services.httpredirect.HTTPRedirect
    :members:
    :undoc-members:


HTTP Redirect Examples
----------------------
The following examples highlight how to use the :class:`HTTPRedirect` class to
get/create :class:`HTTPRedirect`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new HTTP Redirect Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`HTTPRedirect` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`HTTPRedirect` object.
::

    >>> from dyn.tm.services.httpredirect import HTTPRedirect
    >>> # Create a dyn.tmSession
    >>> # Assuming you own the zone 'example.com'
    >>> redir = HTTPRedirect('example.com', 'example.com', 302, keep_uri='Y',
    ...                      url='http://dyn.com')
    >>> redir.zone
    'example.com'
    >>> redir.code
    302

Getting an Existing HTTP Redirect DNS Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`HTTPRedirect` from
the dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.services.httpredirect import HTTPRedirect
    >>> # Create a dyn.tmSession
    >>> # Once again, assuming you own 'example.com'
    >>> rdns = HTTPRedirect('example.com', 'example.com', my_rdns_id)

