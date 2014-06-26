.. _rttm-service-index:

Monitor
=======

.. autoclass:: dyn.tm.services.rttm.Monitor
    :members:
    :undoc-members:

RegionPoolEntry
===============

.. autoclass:: dyn.tm.services.rttm.RegionPoolEntry
    :members:
    :undoc-members:

RTTMRegion
==========

.. autoclass:: dyn.tm.services.rttm.RTTMRegion
    :members:
    :undoc-members:

Real Time Traffic Manager
=========================

.. autoclass:: dyn.tm.services.rttm.RTTM
    :members:
    :undoc-members:

Real Time Traffic Manager Examples
----------------------------------
The following examples highlight how to use the :class:`RTTM` class to
get/create :class:`RTTM`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new Real Time Traffic Manager Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`RTTM` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`RTTM` object.
::

    >>> from dyn.tm.services.rttm import Monitor, RegionPoolEntry, RTTMRegion, \
    ...    RTTM
    >>> # Create a dyn.tmSession
    >>> # Assuming you own the zone 'example.com'
    >>> zone = 'example.com'
    >>> fqdn = zone + '.'
    >>> entry = RegionPoolEntry('1.1.1.1', 'RPE Label', 5, 'always')
    >>> region = RTTMRegion(zone, fqdn, 'global', [self.entry])
    >>> monitor = Monitor('HTTP', 5, expected='Example')
    >>> performance_monitor = Monitor('HTTP', 20)
    >>> rttm = RTTM(zone, fqdn, 'mycontactname', region=[region],
    ...             monitor=monitor, performance_monitor=performance_monitor)

Getting an Existing Real Time Traffic Manager Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`RTTM` from
the dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.services.rttm import RTTM
    >>> # Create a dyn.tmSession
    >>> # Once again, assuming you own 'example.com'
    >>> zone = 'example.com'
    >>> fqdn = zone + '.'
    >>> rttm = RTTM(zone, fqdn)
    >>> rttm.notify_events
    u'ip'
    >>> rttm.notify_events = 'ip, nosrv'
    >>> rttm.notify_events
    u'ip, nosrv'

