.. _updateuser-index:

UpdateUser
==========
.. autoclass:: dyn.tm.accounts.UpdateUser
    :members:
    :undoc-members:

UpdateUser Examples
-------------------
The following examples highlight how to use the :class:`UpdateUser` class to
get/create :class:`UpdateUser`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new UpdateUser
^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`UpdateUser` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`UpdateUser` object.
::

    >>> from dyn.tm.accounts import UpdateUser
    >>> # Create a dyn.tmSession
    >>> new_user = UpdateUser('ausername', 'anickname', 'passw0rd')
    >>> new_user.user_name
    u'ausername'
    >>> newuser.nickname
    u'anickname'
    >>> new_user.block()
    >>> new_user.status
    u'blocked'
    >>> new_user.unblock()
    >>> new_user.password = 'anewpassword'
    >>> new_user.password
    u'anewpassword'

Getting an Existing UpdateUser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`UpdateUser` from the
dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.accounts import UpdateUser
    >>> # Create a dyn.tmSession
    >>> my_user = UpdateUser('myusername')
    >>> my_user.user_name
    u'myusername'
    >>> my_user.status
    u'blocked'
    >>> my_user.unblock()
    >>> my_user.status
    u'active'

