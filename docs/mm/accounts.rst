.. _mm-accounts:

MM Accounts
===========
The :mod:`~dyn.mm.accounts` module contains interfaces for all of the various Account
management features offered by the dyn Message Management REST API

Search/List Functions
---------------------
The following functions return a single ``list`` containing class representations
of their respective types. For instance
:func:`get_all_users` returns a ``list`` of :class:`User` objects.

.. autofunction:: dyn.mm.accounts.get_all_accounts

.. autofunction:: dyn.mm.accounts.get_all_senders

.. autofunction:: dyn.mm.accounts.get_all_suppressions


Account
-------

.. autoclass:: dyn.mm.accounts.Account
    :members:
    :undoc-members:

Create a new Account
^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`~dyn.mm.accounts.Account`
on the Dyn Message Management system::

    >>> from dyn.mm.accounts import Account
    >>> new_account = Account('username', 'password', 'companyname', '1 (603) 867-5309')
    >>> new_account
    <MM Account>: username
    >>> new_account.xheaders
    {}


Using an Existing Account
^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an do some simple manipulation of an existing
dyn Message Management account::

    >>> from dyn.mm.accounts import Account
    >>> new_account = Account('username')
    >>> new_account.apikey
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    >>> new_account.generate_new_apikey()
    >>> new_account.apikey
    'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
    >>> new_account.xheaders
    {'xheader1': '', 'xheader2': '', 'xheader3': '', 'xheader4': ''}
    >>> # The following creates a new xheader for the account
    >>> new_account.xheaders['xheader3'] = 'X-header3_data'


Approved Sender
---------------

.. autoclass:: dyn.mm.accounts.ApprovedSender
    :members:
    :undoc-members:

Create a new Approved Sender
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Approved senders are pretty straightforward as far as functionality goes but here
we'll see how to create a new :class:`~dyn.mm.accounts.ApprovedSender`::

    >>> from dyn.mm.accounts import ApprovedSender
    >>> sender = ApprovedSender('username@email.com', seeding=0)
    >>> sender.status
    1
    >>> sender.seeding
    0
    >>> sender.seeding = 1

Recipient
---------

.. autoclass:: dyn.mm.accounts.Recipient
    :members:
    :undoc-members:

Creating/Using Recipients
^^^^^^^^^^^^^^^^^^^^^^^^^
Recipients are the one model you'll find in this library that don't have an intuitive
way to distinguish what you're trying to accomplish simply from the arguments you provide
at create time. Because of this, you'll need to pass a method type, either GET or POST,
to the Recipient when you create it::

    >>> from dyn.mm.accounts import Recipient
    >>> recipient = Recipient('user@email.com', method='POST')
    >>> recipient.status
    'inactive'
    >>> recipient.activate()
    >>> recipient.status
    'active'

Suppression
-----------

.. autoclass:: dyn.mm.accounts.Suppression
    :members:
    :undoc-members:
