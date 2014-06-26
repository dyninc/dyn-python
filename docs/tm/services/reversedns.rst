.. _reversedns-index:

Reverse DNS
===========

.. autoclass:: dyn.tm.services.reversedns.ReverseDNS
    :members:
    :undoc-members:


Reverse DNS Examples
--------------------
The following examples highlight how to use the :class:`ReverseDNS` class to
get/create :class:`ReverseDNS`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new Reverse DNS Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`ReverseDNS` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`ReverseDNS` object.
::

    >>> from dyn.tm.services.reversedns import ReverseDNS
    >>> # Create a dyn.tmSession
    >>> # Assuming you own the zone 'example.com'
    >>> rdns = ReverseDNS('example.com', 'example.com.', ['example.com],
    ...                   '127.0.0.0/8')
    >>> rdns.deactivate()
    >>> rdns.active
    u'N'

Getting an Existing Reverse DNS Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`ReverseDNS` from
the dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.services.reversedns import ReverseDNS
    >>> # Create a dyn.tmSession
    >>> # Once again, assuming you own 'example.com'
    >>> rdns = ReverseDNS('example.com', 'example.com.', my_rdns_id)

