.. _quickstart:

Quickstart
==========

Eager to get started? This page gives a good introduction on how to get started
with managing your dyn services with this module. This assumes you already have
the dyn module installed. If  you do not, head over to the 
:ref:`Installation <install>` section for information on installing the package.

First, make sure that dyn is :ref:`installed <install>`

Second, it's important to understand that this library handles interacting with
both your Traffic Management (TM) and Message Management (MM) services. For both
TM and MM you will need to create Session objects which handle interacting with
the API, processing API responses, and creating the various objects described
in the :ref:`TM <dyn-tm>` and :ref:`MM <dyn-mm>` API documentation sections.

So, with that in mind, let's get started with some simple examples.

Authentication
--------------
The first step you'll need to take every time you use either of these libraries,
is creating an API Session. These session objects are what, internally, manage
interacting with the API.

So, to create a TM DynectSession, we begin by importing the tm.session module::

    >>> from dyn.tm.session import DynectSession

Now we simply create an instance of a DynectSession by using our Dynect
login credentials::
    
    >>> my_session = DynectSession(customer, username, password)

Now we have a :class:`DynectSession` object called ``my_session``. We will be
able to use this to access all of the resources that you have access to.

Similarly for MM, we import and create an :class:`MMSession` from the mm.session
module::

    >>> from dyn.mm.session import MMSession

Now we create an instance of that this session by providing it an API Key::

    >>> mm_session = MMSession(my_api_key)
    
This object will now grant us access to the features provided by the Email API.

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

We can also create new :class:`PermissionGroups` that can later be applied to
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
Using our current session we can create a new zone::

    >>> from dyn.tm.zones import Zone
    >>> my_zone = Zone('mysite.com', 'myemail@email.com')

We can also access our previously created zones::

    >>> my_old_zone = Zone('example.com')

Using these :class:`Zone` objects we can then perform any manipulations one
might normally perform on a zone. Such as, adding a record::

    >>> a_rec = my_zone.add_record('node', 'A', '127.0.0.1')
    >>> a_rec.ip
    u'127.0.0.1'
    >>> a_rec.fqdn
    u'node.mysite.com.'
    >>> a_rec.get_all_records()
    {'a_records': [127.0.0.1], 'aaaa_records': [], ...}

TM Services
-----------
Now let's try adding a :class:`DynamicDNS` service to our zone::

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

In the event an error in an API request returns with a status of incomplete (ie
the requested job has not yet completed) the wrapper will poll until either the
job has copmleted or the polling times out. In such an unlikely event, 
dyn.tm will raise a :class:`~dyn.tm.errors.DynectQueryTimeout` 
exception

All exceptions that dyn.tm explicitly raises inherit from
:class:`dyn.tm.errors.DynectError`.

MM Errors and Exceptions
------------------------
In the event that an invalid API Key is provided to your :class:`MMSession` an
:class:`~dyn.mm.errors.EmailKeyError` exception will be raised.

If you were to pass an invalid argument to one of the provided MM objects, a
:class:`~dyn.mm.errors.DynInvalidArgumentError` exception is raised.

The :class:`~dyn.mm.errors.DynInvalidArgumentError` should not be confused with
the :class:`~dyn.mm.errors.EmailInvalidArgumentError` that is raised if a
required field is not provided. This is an unlikely exception to get raised
because the error would likely first be raised as a
:class:`~dyn.mm.errors.DynInvalidArgumentError`. However, it is still a possible
situation.

Finally, the :class:`~dyn.mm.errors.EmailObjectError` will be raised if you
attempt to create an object that already exists on the Dyn Email System.

All MM exceptions inherit from :class:`~dyn.mm.errors.EmailError`

-----------------------

Ready for more? Check out the :ref:`TM <dyn-tm>` and :ref:`MM <dyn-mm>`
module documentation sections, the full
`TM API Documentation <https://help.dynect.net/rest-resources/>`_ or the
`MM API Documentation <https://help.dynect.net/api/>`_.
