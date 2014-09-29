.. _tm-tools:

TM Tools
========
The :mod:`~dyn.tm.tools` module contains utility functions for performing common
and potentially difficult tasks easily.

List Functions
--------------

.. autofunction:: dyn.tm.tools.change_ip
.. autofunction:: dyn.tm.tools.map_ips


Tools Examples
--------------

change_ip
^^^^^^^^^
If you find yourself replacing a server with a new one, or in some other situation
where you might want to replace an ip address with a new one, then :func:`change_ip` makes
it straight forward to apply these changes
::

    >>> from dyn.tm.zones import Zone
    >>> from dyn.tm.tools import change_ip
    >>> my_zone = Zone('example.com')
    >>> old = '1.1.1.1'
    >>> new = '1.1.1.2'
    >>> change_ip(my_zone, old, new, publish=True)

This handles acquiring and ARecords under the provided zone and applying the changes
as you've specified. Need to shift over a handful of ip addresses?
::

    >>> from dyn.tm.zones import Zone
    >>> from dyn.tm.tools import change_ip
    >>> my_zone = Zone('example.com')
    >>> old = ['1.1.1.1', '1.1.1.3', '1.1.1.5']
    >>> new = ['1.1.1.2', '1.1.1.4', '1.1.1.6']
    >>> change_ip(my_zone, old, new, publish=True)

Have IPv6 addresses you need to switch over?
::

    >>> from dyn.tm.zones import Zone
    >>> from dyn.tm.tools import change_ip
    >>> my_zone = Zone('example.com')
    >>> old = '::1'
    >>> new = '2001:db8:85a3::8a2e:370:7334'
    >>> change_ip(my_zone, old, new, v6=True, publish=True)


Don't want to automatically publish, but rather wait and validate the changes
manually?
::

    >>> from dyn.tm.zones import Zone
    >>> from dyn.tm.tools import change_ip
    >>> my_zone = Zone('example.com')
    >>> old = '1.1.1.1'
    >>> new = '1.1.1.2'
    >>> changeset = change_ip(my_zone, old, new)
    >>> changeset
    [(u'example.com.', u'1.1.1.1', u'1.1.1.2')]


map_ips
^^^^^^^
:func:`map_ips` functions in basically the same manner as :func:`change_ip`, the only difference
being that it accepts a *dict* with rules on mapping form one ip to another (as well
as the same v6 flag for specifying that you're working ipv6 addresses.
::

    >>> from dyn.tm.zones import Zone
    >>> from dyn.tm.tools import map_ips
    >>> my_zone = Zone('example.com')
    >>> old = '1.1.1.1'
    >>> new = '1.1.1.2'
    >>> mapping = {old: new}
    >>> map_ips(my_zone, mapping, publish=True)

