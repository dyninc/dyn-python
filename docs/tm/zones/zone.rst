.. _zone-index:

Zone
====
.. autoclass:: dyn.tm.zones.Zone
    :members:
    :undoc-members:

Zone Examples
-------------
The following examples highlight how to use the :class:`Zone` class to
get/create :class:`Zone`'s on the dyn.tm System and how to edit these objects
from within a Python script.

Creating a new Zone
^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`Zone` on the dyn.tm
System and how to edit some of the fields using the returned :class:`Zone`
object.
::

    >>> from dyn.tm.zones import Zone
    >>> # Create a dyn.tmSession
    >>> new_zone = Zone('myzone.com', 'me@email.com')
    >>> new_zone.serial
    0
    >>> new_zone.publish()
    >>> new_zone.serial
    1

Getting an Existing Zone
^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`Zone` from the
dyn.tm System.
::

    >>> from dyn.tm.zones import Zone
    >>> # Create a dyn.tmSession
    >>> my_zone = Zone('myzone.com')
    >>> my_zone.serial
    5
    >>> my_zone.contact
    u'myemail@email.com'

Using lists of Zones
^^^^^^^^^^^^^^^^^^^^
The following example shows how to use the results of a call to the
:func:`get_all_zones` functions
::

    >>> from dyn.tm.zones import get_all_zones
    >>> # Create a dyn.tmSession
    >>> my_zones = get_all_zones()
    >>> for zone in my_zones:
    ...     if zone.serial_style != 'increment':
    ...         zone.serial_style = 'increment'

