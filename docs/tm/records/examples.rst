.. _examples-index:

Example Record Usage
====================
Below are a few basic examples of how to use some different record types in a
variety of ways.

Create a new Record
-------------------
::

    >>> from dyn.tm.records import ARecord
    >>> # Create a dyn.tmSession
    >>> # Assuming you own the Zone 'example.com'
    >>> new_a = ARecord('example.com', 'example.com.', address='127.0.0.1')

Getting an Existing Record
--------------------------
Getting records is a slightly more complicated task if you don't have the
record id readily accessible. Below is an example which shows the easiest way
to get a specific record, assuming you don't have the id readily available.
::

    >>> from dyn.tm.zones import Zone
    >>> # Create a dyn.tmSession
    >>> # Once again, assuming you own 'example.com'
    >>> zone = Zone('example.com')
    >>> all_records = zone.get_node().get_any_records()
    >>> for record in all_records:
    ...     # Find your record, more info coming soon...



Delete all Records
------------------
As of v1.4.2 you can also delete all records of a certain type on a specific node

::

    >>> from dyn.tm.records import ARecord
    >>> my_node = ARecord('myzone.com', 'fqdn.myzone.com.', create=False)
    >>> my_node.delete()  # Warning, this will delete ALL ARecords on fqdn.myzone.com.


