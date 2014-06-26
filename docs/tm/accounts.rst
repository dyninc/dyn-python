.. _accounts-index:

Accounts
========
The :mod:`accounts` module contains interfaces for all of the various Account
management features offered by the dyn.tm REST API

Search/List Functions
---------------------
The following functions are primarily helper functions which will perform API
"Get All" calls. These functions all return a single ``list`` containing
class representations of their respective types. For instance
:func:`get_all_users` returns a ``list`` of :class:`User` objects.

.. autofunction:: dyn.tm.accounts.get_updateusers

.. autofunction:: dyn.tm.accounts.get_users

.. autofunction:: dyn.tm.accounts.get_permissions_groups

.. autofunction:: dyn.tm.accounts.get_contacts

.. autofunction:: dyn.tm.accounts.get_notifiers

Search/List Function Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Using these search functions is a fairly straightforward endeavour, you can
either leave your search criteria as None and get a list of ALL objects of that
type, or you can specify a search dict like so
::

    >>> from dyn.tm.accounts import get_users
    >>> all_users = get_users()
    >>> all_users
    [User: <jnappi>, User: <rshort>, User: <tmpuser35932>,...]
    >>> search_criteria = {'first_name': 'Jon'}
    >>> jons = get_users(search_criteria)
    >>> jons
    [User: <jnappi>, User: <jsmith>]


Classes
-------
.. toctree::
   :maxdepth: 3

   accounts/updateuser.rst
   accounts/user.rst
   accounts/permissionsgroup.rst
   accounts/notifier.rst
   accounts/contact.rst
