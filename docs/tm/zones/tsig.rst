.. _tsig-index:

Tsig
====
.. autoclass:: dyn.tm.zones.TSIG
    :members:
    :undoc-members:

Tsig Examples
-------------
The following examples highlight how to use the :class:`TSIG` class to
get/create :class:`TSIG`'s on the dyn.tm System and how to edit these objects
from within a Python script.

Creating a new Tsig
^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`TSIG` on the dyn.tm
System and how to edit some of the fields using the returned :class:`TSIG`
object. The easiest way to manipulate :class:`TSIG` objects is via a
:class:`TSIG` object. This example will show how to create new :class:`TSIG`, view
the secret key and the algorithm. Then, change the secret key, and finally Delete the
:class:`TSIG` from the system.

::

    >>> from dyn.tm.zones import TSIG
    >>> new_Tsig = TSIG('MyKey', secret='C9IzEr7gXLjYRW6EmDCDuA==', algorithm='hmac-md5')
    >>> new_Tsig.secret
    'C9IzEr7gXLjYRW6EmDCDuA=='
    >>> new_Tsig.algorithm
    hmac-md5
    >>> new_Tsig.secret = 'D9IzEr7gXLjYRW6EmDCDuA=='
    >>> new_Tsig.secret
    'D9IzEr7gXLjYRW6EmDCDuA=='
    >>> new_Tsig.delete()


Getting an Existing TSIG object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`TSIG` from the
dyn.tm System. Similarly to the above examples the easiest way to manipulate
existing :class:`TSIG` objects is via a :class:`TSIG` object.
::

    >>> from dyn.tm.zones import TSIG
    >>> old_Tsig = TSIG('oldkey')
    >>> old_Tsig.secret
    'C9IzEr7gXLjYRW6EmDCDuA=='
    >>> old_Tsig.algorithm
    hmac-md5
    >>> old_Tsig.secret = 'D9IzEr7gXLjYRW6EmDCDuA=='
    >>> old_Tsig.secret
    'D9IzEr7gXLjYRW6EmDCDuA=='
    >>> old_Tsig.delete()

