.. _secondary-index:

Secondary Zone
==============
.. autoclass:: dyn.tm.zones.SecondaryZone
    :members:
    :undoc-members:

Secondary Zone Examples
-----------------------
The following examples highlight how to use the :class:`SecondaryZone` class to
get/create :class:`SecondaryZone`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new Secondary Zone
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`SecondaryZone` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`SecondaryZone` object.
::

    >>> from dyn.tm.zones import SecondaryZone
    >>> # Create a dyn.tmSession
    >>> new_zone = SecondaryZone('myzone.com', '127.0.0.1', 'mynickame')
    >>> new_zone.active
    'Y'
    >>> new_zone.retransfer()
    >>> new_zone.serial
    1

Getting an Existing Secondary Zone
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`SecondaryZone` from
the dyn.tm System.
::

    >>> from dyn.tm.zones import SecondaryZone
    >>> # Create a dyn.tmSession
    >>> my_zone = SecondaryZone('myzone.com')
    >>> my_zone.serial
    5
    >>> my_zone.contact
    u'mynickname'
    >>> my_zone.deactivate()
    >>> my_zone.active
    'N'

