.. _user-index:

User
====
.. autoclass:: dyn.tm.accounts.User
    :members:
    :undoc-members:

User Examples
-------------
The following examples highlight how to use the :class:`User` class to
get/create :class:`User`'s on the dyn.tm System and how to edit these objects
from within a Python script.


Creating a new User
^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`User` on the dyn.tm
System and how to edit some of the fields using the returned :class:`User`
object.
::

    >>> from dyn.tm.accounts import User
    >>> # Create a dyn.tmSession
    >>> new_user = User('newuser', 'passw0rd', 'contact@email.com', 'first',
    ...                 'last', 'nickname', 'MyOrganization', '(123)456-7890')
    >>> new_user.status
    u'active'
    >>> new_user.city
    None
    >>> new_user.city = 'Manchester'
    >>> new_user.permission
    ['ZoneGet', 'ZoneUpdate']
    >>> new_user.add_permission('ZoneCreate')
    >>> new_user.permission
    ['ZoneGet', 'ZoneUpdate', 'ZoneCreate']

Getting an Existing User
^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`User` from the
dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.accounts import User
    >>> # Create a dyn.tmSession
    >>> my_user = User('myusername')
    >>> my_user.status
    u'blocked'
    >>> my_user.unblock()
    >>> my_user.status
    u'active'

