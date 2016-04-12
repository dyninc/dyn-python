.. _quickstart:

Quickstart
==========

Eager to get started? This guide will help you get started managing your Dyn
services using this module.

If you have not already, :ref:`Install <install>` the Dyn module before proceeding further.

It is also important to understand that this library handles interacting with
both Traffic Management (TM) and Message Management (MM) services. For both
TM and MM, you will need to create Session objects to handle API interactions,
processing API responses, and creating the various objects described
in the :ref:`TM <dyn-tm>` and :ref:`MM <dyn-mm>` API documentation sections.

Here are some simple examples to get you started.

Authentication
--------------
API sessions will need to be created each time you use either of these libraries.
These session objects internally manage interaction with the API.

To create a TM DynectSession, begin by importing the tm.session module::

    >>> from dyn.tm.session import DynectSession

Now create an instance of a DynectSession by using our Dyn
login credentials::

    >>> my_session = DynectSession(customer, username, password)

Now you have a :class:`DynectSession` object called ``my_session``. You will be
able to use this to access your available resources.

For MM, you can import and create an :class:`MMSession` from the mm.session
module::

    >>> from dyn.mm.session import MMSession

Now create an instance of this session by providing it an API Key::

    >>> mm_session = MMSession(my_api_key)

This object will now grant you access to the features provided by the Email API.

Managing Your TM Accounts
-------------------------
The new wrapper allows you easy access to managing all of the elements within
your account, such as new :class:`Users` objects::

    >>> from dyn.tm.accounts import User
    >>> jsmith = User('jsmith')
    >>> jsmith.status
    u'blocked'
    >>> jsmith.unblock()
    >>> jsmith.status
    u'active'
    >>> jsmith.get_permissions_report()
    ['ZoneAdd', 'ZoneDelete', 'Login']
    >>> jsmith.add_permission('ZoneGet')
    >>> jsmith.get_permissions_report()
    ['ZoneAdd', 'ZoneDelete', 'Login', 'ZoneGet']

You can also create new :class:`PermissionGroups` that can later be applied to
:class:`User` objects
::

    >>> from dyn.tm.accounts import PermissionsGroup
    >>> sample = PermissionsGroup('Sample', 'Sample permission Group')
    >>> sample.add_permissions('DSFAdd')
    >>> sample.add_permissions('DSFGet')
    >>> sample.add_permissions('DSFDelete')
    >>> sample.add_zone('mysite.com')

Using your Zones
----------------
Using your current session you can create a new zone::

    >>> from dyn.tm.zones import Zone
    >>> my_zone = Zone('mysite.com', 'myemail@email.com')

You can also access your previously created zones::

    >>> my_old_zone = Zone('example.com')

Using these :class:`Zone` objects you can begin to manipulate your zones,
such as, adding a record::

    >>> a_rec = my_zone.add_record('node', 'A', '127.0.0.1')
    >>> a_rec.ip
    u'127.0.0.1'
    >>> a_rec.fqdn
    u'node.mysite.com.'
    >>> a_rec.get_all_records()
    {'a_records': [127.0.0.1], 'aaaa_records': [], ...}

TM Services
-----------
Try adding a :class:`DynamicDNS` service to your zone::

    >>> ddns = my_zone.add_service(service_type='DDNS', record_type='A',
    ...                            address='127.0.0.1')
    >>> ddns.zone
    u'mysite.com'
    >>> ddns.active
    u'Y'


TM Errors and Exceptions
------------------------
In the event of an authentication problem, dyn.tm will raise a
:class:`~dyn.tm.errors.DynectAuthError` exception.

In the event an error in an API Creation is encountered, dyn.tm will
raise a :class:`~dyn.tm.errors.DynectCreateError` exception with
additional information about why the POST failed.

In the event an error in an API Update is encountered, dyn.tm will
raise a :class:`~dyn.tm.errors.DynectUpdateError` exception with
additional information about why the PUT failed.

In the event an error in an API Get is encountered, dyn.tm will
raise a :class:`~dyn.tm.errors.DynectGetError` exception with
additional information about why the GET failed.

In the event an error in an API Deletion is encountered, dyn.tm will
raise a :class:`~dyn.tm.errors.DynectDeleteError` exception with
additional information about why the DELETE failed.

In the event an error in an API request returns with an incomplete status (i.e.
the requested job has not yet completed) the wrapper will poll until either the
job has completed or the polling times out. In such an event,
dyn.tm will raise a :class:`~dyn.tm.errors.DynectQueryTimeout`
exception

All exceptions that dyn.tm explicitly raises inherit from
:class:`dyn.tm.errors.DynectError`.

MM Errors and Exceptions
------------------------
In the event that an invalid API Key is provided to your :class:`MMSession` an
:class:`~dyn.mm.errors.EmailKeyError` exception will be raised.

If you passed an invalid argument to one of the provided MM objects, a
:class:`~dyn.mm.errors.DynInvalidArgumentError` exception is raised.

The :class:`~dyn.mm.errors.DynInvalidArgumentError` should not be confused with
the :class:`~dyn.mm.errors.EmailInvalidArgumentError`. The latter is raised if a
required field is not provided. This is an unlikely exception to be raised
as the error would likely be raised as
:class:`~dyn.mm.errors.DynInvalidArgumentError`. However, it is still a possible
scenario.

The :class:`~dyn.mm.errors.EmailObjectError` will be raised if you
attempt to create an object that already exists on the Dyn MM system.

All MM exceptions inherit from :class:`~dyn.mm.errors.EmailError`

-----------------------

Ready for more? Check out the :ref:`TM <dyn-tm>` and :ref:`MM <dyn-mm>`
module documentation sections, the full
`TM API Documentation <https://help.dynect.net/rest-resources/>`_ or the
`MM API Documentation <https://help.dynect.net/api/>`_.
