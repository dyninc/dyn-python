.. _ddns-index:

Dynamic DNS
===========

.. autoclass:: dyn.tm.services.ddns.DynamicDNS
    :members:
    :undoc-members:

Dynamic DNS Examples
--------------------
The following examples highlight how to use the :class:`DynamicDNS` class to
get/create :class:`DynamicDNS`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new Dynamic DNS Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`DynamicDNS` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`DynamicDNS` object.
::

    >>> from dyn.tm.services.ddns import DynamicDNS
    >>> # Create a dyn.tmSession
    >>> # Assuming you own the zone 'example.com'
    >>> dyndns = DynamicDNS('example.com', 'example.com.', 'A', '127.0.0.1')
    >>> dyndns.ttl = 180
    >>> dyndns.ttl
    180
    >>> dyndns.record_type
    u'A'

Getting an Existing Dynamic DNS Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`DynamicDNS` from
the dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.services.ddns import DynamicDNS
    >>> # Create a dyn.tmSession
    >>> # Once again, assuming you own 'example.com'
    >>> dyndns = DynamicDNS('example.com', 'example.com.', record_type='A')
    >>> dyndns.active
    u'Y'
    >>> dyndns.deactivate()
    >>> dyndns.active
    u'N'

