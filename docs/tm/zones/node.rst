.. _node-index:

Node
====
It is important to note that creation of a Node class will not immediately take
affect on the dyn.tm System unless it is created via a :class:`Zone` instance.
While creating :class:`Node`'s via a  :class:`Zone` you are required to place
either a :class:`DNSRecord` or a service on that :class:`Node` which allows
it to be created. To clerify, because :class:`Node`'s may not exist without
either a record or service ``node = Node('zone.com', 'fqdn.zone.com.')`` will
not actually create anything on the Dyn side until you add a record or service,
whereas ``rec = zone.add_record('fqnd', 'A', '127.0.0.1')`` will create a new
:class:`Node` named 'fqdn' with an :class:`ARecord` attached.

.. autoclass:: dyn.tm.zones.Node
    :members:
    :undoc-members:

Node Examples
-------------
The following examples highlight how to use the :class:`Node` class to
get/create :class:`Zone`'s on the dyn.tm System and how to edit these objects
from within a Python script.

Creating a new Node
^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`Node` on the dyn.tm
System and how to edit some of the fields using the returned :class:`Node`
object. The easiest way to manipulate :class:`Node` objects is via a
:class:`Zone` object. This example will show how to create new :class:`Node`
objects both by using a :class:`Zone` as a proxy, and by creating a
:class:`Node` as a standalone object.
::

    >>> from dyn.tm.zones import Zone
    >>> # Create a dyn.tmSession
    >>> new_zone = Zone('myzone.com', 'me@email.com')
    >>> new_zone.add_record('NewNode', 'A', '127.0.0.1')
    <ARecord>: 127.0.0.1
    >>> node = new_zone.get_node('NewNode')
    >>> node.add_record('A', '127.0.1.1')
    <ARecord>: 127.0.1.1
    >>> node.get_any_records()
    {u'a_records': [<ARecord>: 127.0.0.1, <ARecord>: 127.0.1.1]}

::

    >>> from dyn.tm.zones import Node
    >>> # Create a dyn.tmSession
    >>> # Assuming the :class:`Zone` from the above example still exists
    >>> new_node = Node('myzone.com', 'NewNode.myzone.com')
    >>> new_node.get_any_records()
    {u'a_records': [<ARecord>: 127.0.0.1, <ARecord>: 127.0.1.1]}

Getting an Existing Node
^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`Node` from the
dyn.tm System. Similarly to the above examples the easiest way to manipulate
existing :class:`Node` objects is via a :class:`Zone` object.
::

    >>> from dyn.tm.zones import Zone
    >>> # Create a dyn.tmSession
    >>> new_zone = Zone('myzone.com', 'me@email.com')
    >>> new_zone.add_record('NewNode', 'A', '127.0.0.1')
    >>> node = new_zone.get_node('NewNode')
    >>> node.get_any_records()
    {u'a_records': ['127.0.0.1'], ...}

::

    >>> from dyn.tm.zones import Node
    >>> # Create a dyn.tmSession
    >>> # Assuming the :class:`Zone` from the above example still exists
    >>> new_node = Node('myzone.com', 'NewNode.myzone.com')
    >>> new_node.get_any_records()
    {u'a_records': ['127.0.0.1'], ...}

