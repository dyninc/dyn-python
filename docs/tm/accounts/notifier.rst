.. _notifier-index:

Notifier
========

.. autoclass:: dyn.tm.accounts.Notifier
    :members:
    :undoc-members:

Notifier Examples
-----------------
The following examples highlight how to use the :class:`Notifier` class to
get/create :class:`Notifier`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new Notifier
^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`Notifier` on the dyn.tm
System and how to edit some of the fields using the returned :class:`Notifier`
object.
::

    >>> from dyn.tm.accounts import Notifier
    >>> # Create a dyn.tmSession
    >>> new_notif = Notifier(label='notifierlabel')
    >>> new_notif.services
    []
    >>> new_notif.recipients
    []
    >>> # Probably want to include more

Getting an Existing Notifier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`Notifier` from the
dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> from dyn.tm.accounts import Notifier
    >>> # Create a dyn.tmSession
    >>> # Note that in order to get a Notifier you will need the ID of that Notifier
    >>> my_notif = Notifier(my_notifier_id)
    >>> my_notif.services
    []
    >>> my_notif.recipients
    []
    >>> # Probably want to include more

