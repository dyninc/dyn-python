.. _auth-index:

Authentication
==============
The :mod:`~dyn.tm.session` module is an interface to authentication via the
dyn.tm REST API. As noted in the advanced section, :class:`~dyn.tm.session.DynectSession`'s
are implemented as Singleton types, which means that, in most cases, you don't need to keep track
of your :class:`~dyn.tm.session.DynectSession` instances after you create them. However,
there are several examples of ways in which you can use these session instances which
will be outlined below.

.. autoclass:: dyn.tm.session.DynectSession
    :members:
    :undoc-members:


The Basics
----------
For basic usage, you need not do anything more than simply
::

    >>> from dyn.tm.session import DynectSession
    >>> DynectSession('customer', 'user', 'password')


Permissions
-----------
Using a :class:`~dyn.tm.session.DynectSession` instance, you can also verify
the current permissions associated with your session by simply checking the
permissions property of your :class:`~dyn.tm.session.DynectSession` instance.
::

    >>> from dyn.tm.session import DynectSession
    >>> s = DynectSession('customer', 'user', 'password')
    >>> s.permissions
    [u'ZoneGet', u'ZoneUpdate', u'ZoneCreate', u'ZoneDelete', ...

Additional Features
-------------------
The majority of these features exist mainly to provide a cleaner interface to working
with sessions as Singleton types.

Multiple Sessions
~~~~~~~~~~~~~~~~~
To manage multiple user accounts, call the `new_user_session` method
::

    >>> from dyn.tm.session import DynectSession
    >>> s = DynectSession('customer', 'user', 'password')
    >>> s.new_user_session('customer_two', 'user_two', 'password_two')

This will authenticate a second user. You can then switch between your open user sessions with
`set_active_session` by passing a username. Use the `get_open_sessions` method to get a dictionary of all
open sessions
::

    >>> current_sessions = dynect_session.get_open_sessions()
    >>> # loop through all open sessions and do... something
    >>> for user in current_sessions:
    ...     dynect_session.set_active_session(user)
    ...     print("Zones for {0}".format(dynect_session.username))
    ...     print(get_all_zones())

DynectSession as a Context Manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
As of version 1.2.0 you have the ability to use a DynectSession as a context
manager, like so
::

    >>> from dyn.tm.session import DynectSession
    >>> with DynectSession('customer', 'user', 'password') as s:
    ...     return s.permissions

This feature is particularly useful if you're looking to manage multiple user accounts
programatically.


Overriding Sessions
^^^^^^^^^^^^^^^^^^^
As of version 1.2.0 you have the ability to override an existing DynectSession
with the use of the new_session class method like so
::

    >>> from dyn.tm.session import DynectSession
    >>> s = DynectSession('customer', 'user', 'password')
    >>> s = DynectSession.new_session('customer', 'another_user', 'password')

Getting Sessions
^^^^^^^^^^^^^^^^
If you don't want to track your current DynectSession, but want to be able to
access your current one later, you can make use of the get_session class method
like so
::

    >>> from dyn.tm.session import DynectSession
    >>> DynectSession('customer', 'user', 'password')
    >>> DynectSession.get_session().username
    'user'

Session History
^^^^^^^^^^^^^^^
As of version 1.3.0 users can now optionally allow DynectSessions to store a
history of API calls that are made. This can be particularly useful for
debugging, as well as for use when contacting Support.
::

    >>> >>> from dyn.tm.session import DynectSession
    >>> s = DynectSession('customer', 'user', 'password', history=True)
    >>> s.history
    ... [('2014-10-14T11:15:17.351740',
    ...   '/REST/Session/',
    ...   'POST',
    ...   {'customer_name': 'customer', 'password': '*****', 'user_name': 'user'},
    ...   u'success')]

Please note that if you do not specify `history` as `True` when you log in, that
your history will not be recorded and `s.history` will return `None`

