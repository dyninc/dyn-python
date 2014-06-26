.. _afo-service-index:

HealthMonitor
=============

.. autoclass:: dyn.tm.services.active_failover.HealthMonitor
    :members:
    :undoc-members:

Active Failover
===============

.. autoclass:: dyn.tm.services.active_failover.ActiveFailover
    :members:
    :undoc-members:

Active Failover Examples
------------------------
The following examples highlight how to use the :class:`ActiveFailover` class to
get/create :class:`ActiveFailover`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new Active Failover Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`ActiveFailover` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`ActiveFailover` object.
::

    >>> from dyn.tm.services.active_failover import HealthMonitor, ActiveFailover,
    >>> # Create a dyn.tmSession
    >>> mon = HealthMonitor(protocol='HTTP', interval='1', expected='Example')
    >>> # Assuming you own the zone 'example.com'
    >>> afo = ActiveFailover('example.com', 'example.com.', '127.0.0.1', 'ip',
    ...                      '127.0.0.2', mon, 'mycontact')
    >>> afo.notify_events = 'ip, nosrv'
    >>> afo.notify_events
    u'ip, nosrv'

Getting an Existing Active Failover Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`ActiveFailover` from
the dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.services.active_failover import HealthMonitor, ActiveFailover,
    >>> # Create a dyn.tmSession
    >>> # Once again, assuming you own 'example.com'
    >>> afo = ActiveFailover('example.com', 'example.com.')
    >>> afo.active
    u'Y'
    >>> afo.deactivate()
    >>> afo.active
    u'N'

