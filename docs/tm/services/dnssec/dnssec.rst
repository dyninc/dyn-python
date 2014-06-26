.. _dnssec-service-index:

DNSSECKey
=========

.. autoclass:: dyn.tm.services.dnssec.DNSSECKey
    :members:
    :undoc-members:

DNSSEC
======

.. autoclass:: dyn.tm.services.dnssec.DNSSEC
    :members:
    :undoc-members:

DNSSEC Examples
---------------
The following examples highlight how to use the :class:`DNSSEC` class to
get/create :class:`DNSSEC`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new DNSSEC Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`DNSSEC` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`DNSSEC` object.
::

    >>> from dyn.tm.services.dnssec import DNSSECKey, DNSSEC
    >>> # Create a dyn.tmSession
    >>> key1 = DNSSECKey('KSK', 'RSA/SHA-1', 1024)
    >>> key2 = DNSSECKey('ZSK', 'RSA/SHA-1', 2048)
    >>> # Assuming you own the zone 'example.com'
    >>> dnssec = DNSSEC('example.com', [key1, key2], 'mycontactnickname')
    >>> dnssec.deactivate()
    >>> dnssec.active
    u'N'

Getting an Existing DNSSEC Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`DNSSEC` from
the dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.services.dnssec import DNSSEC
    >>> # Create a dyn.tmSession
    >>> # Once again, assuming you own 'example.com'
    >>> dnssec = DNSSEC('example.com', [key1, key2], 'mycontactnickname')
    >>> if dnssec.active == 'N':
    ...     dnssec.activate()
    >>> from pprint import pprint
    >>> pprint(dnssec.timeline_report())
    {}

Managing Your DNSSEC Keys
^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to manage an existing :class:`DNSSEC` services
:class:`DNSSECKey`'s.
::

    >>> from dyn.tm.services.dnssec import DNSSEC
    >>> dnssec = DNSSEC('example.com')
    >>> dnssec.keys
    [<__main__.DNSSECKey object at 0x10ca84550>, <__main__.DNSSECKey object at 0x10ca84590>]
    >>> new_key = DNSSECKey('ZSK', 'RSA/SHA-1', 1024)
    >>> # You must always have two keys, so we add a new one first
    >>> dnssec.keys.append(new_key)
    >>> # Now that we have two keys we can delete an onld KSK we don't want
    >>> for index, key in enumerate(dnssec.keys):
    ...     if key.key_type == 'KSK' and key.bits == 1024:
    ...         del dnssec.keys[index]
    ...         break
    >>> dnssec.keys
    [<__main__.DNSSECKey object at 0x10ca84590>, <__main__.DNSSECKey object at 0x10ca78b50>]

