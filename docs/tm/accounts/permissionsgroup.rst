.. _permissionsgroup-index:

PermissionsGroup
================

.. autoclass:: dyn.tm.accounts.PermissionsGroup
    :members:
    :undoc-members:

PermissionsGroup Examples
-------------------------
The following examples highlight how to use the :class:`PermissionsGroup` class
to get/create :class:`PermissionsGroup`'s on the dyn.tm System and how to edit
these objects from within a Python script.

Creating a new PermissionsGroup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`PermissionsGroup` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`PermissionsGroup` object.
::

    >>> from dyn.tm.accounts import PermissionsGroup
    >>> # Create a dyn.tmSession
    >>> new_group = PermissionsGroup('newgroupname', 'description_of_new_group')
    >>> new_group.type
    u'default'
    >>> new_group.add_permission('ZoneUpdate')
    >>> new_group.permission
    ['ZoneUpdate']
    >>> # Note that assigning new_group.permission will clear all permissions
    >>> new_group.permission = ['ZoneGet']
    >>> new_group.permission
    ['ZoneGet']
    >>> # Also note this is functionally equivalent to calling replace_permission
    >>> new_group.replace_permission(['ZoneCreate'])
    >>> new_group.permission
    ['ZoneCreate']

Getting an Existing PermissionsGroup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`User` from the
dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.accounts import PermissionsGroup
    >>> # Create a dyn.tmSession
    >>> my_group = PermissionsGroup('newgroupname')
    >>> my_group.type
    u'default'
    >>> my_group.type = 'plain'
    >>> my_group.type
    u'plain'
    >>> my_group.description = 'A better group description.'
    >>> my_group.description
    u'A better group description.'

