.. _contact-index:

Contact
=======

.. autoclass:: dyn.tm.accounts.Contact
    :members:
    :undoc-members:

Contact Examples
----------------
The following examples highlight how to use the :class:`Contact` class to
get/create :class:`Contact`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new Contact
^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`Contact` on the dyn.tm
System and how to edit some of the fields using the returned :class:`Contact`
object.
::

    >>> from dyn.tm.accounts import Contact
    >>> # Create a dyn.tmSession
    >>> new_contact = Contact('mynickname', 'me@email.com', 'firstname',
    ...                       'lastname', 'MyOrganization')
    >>> new_contact.city
    None
    >>> new_contact.city = 'Manchester'
    >>> new_contact.city
    u'Manchester'

Getting an Existing Contact
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`Contact` from the
dyn.tm System and how to edit some of the same fields mentioned above. It is
also probably worth mentioning that when a :class:`User` is created a
:class:`Contact` is also created and is associated with that :class:`User`.
However, when a :class:`User` is deleted the associated :class:`Contact` is not
deleted along with it, as it may still be associated with active services.
::

    >>> from dyn.tm.accounts import Contact
    >>> # Create a dyn.tmSession
    >>> my_contact = Contact('mynickname')
    >>> my_contact.email
    u'me@email.com'
    >>> my_contact.email = 'mynewemail@email.com'
    >>> my_contact.email
    u'mynewemail@email.com'

