.. _gslb-service-index:

Monitor
=======

.. autoclass:: dyn.tm.services.gslb.Monitor
    :members:
    :undoc-members:
    
GSLBRegionPoolEntry
===================

.. autoclass:: dyn.tm.services.gslb.GSLBRegionPoolEntry
    :members:
    :undoc-members:

GSLBRegion
==========

.. autoclass:: dyn.tm.services.gslb.GSLBRegion
    :members:
    :undoc-members:

GSLB
====

.. autoclass:: dyn.tm.services.gslb.GSLB
    :members:
    :undoc-members:

GSLB Examples
-------------
The following examples highlight how to use the :class:`GSLB` class to
get/create :class:`GSLB`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new GSLB Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`GSLB` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`GSLB` object.
::

    >>> from dyn.tm.services.gslb import Monitor, RegionPoolEntry, GSLBRegion, \
    ...    GSLB
    >>> # Create a dyn.tmSession
    >>> # Assuming you own the zone 'example.com'
    >>> zone = 'example.com'
    >>> fqdn = zone + '.'
    >>> pool = GSLBRegionPoolEntry(zone, fqdn, 'global', '8.8.4.4', None,
    ...                            label='APIv2 GSLB')
    >>> region = GSLBRegion(zone, fqdn, 'mycontactnickname', pool=[pool])
    >>> monitor = Monitor('HTTP', 5, expected='Example')
    >>> gslb = GSLB(zone, fqdn, 'mycontactname', region=[region], monitor=monitor)

Getting an Existing GSLB Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`GSLB` from
the dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.services.gslb import GSLB
    >>> # Create a dyn.tmSession
    >>> # Once again, assuming you own 'example.com'
    >>> zone = 'example.com'
    >>> fqdn = zone + '.'
    >>> gslb = GSLB(zone, fqdn)

