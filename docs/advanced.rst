.. _advanced:

Advanced Topics
===============
This section is a collection of advanced topics for users who intend to contribute
and maintain this library.

Sessions
--------

Sessions in this library are designed for ease of use by front-end users.
However, this section is dedicated to a deeper understanding of Sessions for
advanced users and contributors to this library.

Parent Class
^^^^^^^^^^^^
Both :class:`dyn.tm.session.DynectSession` and :class:`dyn.mm.session.MMSession`
are subclasses of :class:`dyn.core.SessionEngine`. The :class:`dyn.core.SessionEngine`
provides a simple internal API for preparing, sending, and processing outbound
API calls. This class was added in v1.0.0 and reduced the amount of logic
and duplicated code that made understanding these Sessions difficult.

Parent Type
^^^^^^^^^^^
Since v0.4.0, Sessions have been implemented as a Singleton type. This made it easier
for end users to use the SDK and to utilize the API. By internally implementing Sessions
as a Singleton, it allows the user discard their Session objects, unless they wish to
keep them. It also doesn’t require users to share their Session information with
other classes in this library to make API calls. (EXAMPLE)::

    >>> from dyn.tm.session import DynectSession
    >>> from dyn.tm.zones import get_all_zones
    >>> DynectSession(**my_credentials)
    >>> zones = get_all_zones()


as opposed to something like this::

    >>> from dyn.tm.session import DynectSession
    >>> from dyn.tm.zones import get_all_zones
    >>> my_session = DynectSession(**my_credentials)
    >>> zones = get_all_zones(my_session)

Or, even worse::

    >>> from dyn.tm.session import DynectSession
    >>> my_session = DynectSession(**my_credentials)
    >>> zones = my_session.get_all_zones(my_session)

In these examples, the changes may not seem significant but gain more relevance when
creating multiple types of records, adding or editing Traffic Director and other complex
services. Not needing to share your Session with other classes, or use it as a point
of entry to other functionality, makes using this SDK much simpler.

What We Used to Do
^^^^^^^^^^^^^^^^^^
From a backend perspective, the following is an example of how Session types were
handled before v0.4.0::

    def session():
        """Accessor for the current Singleton DynectSession"""
        try:
            return globals()['SESSION']
        except KeyError:
            return None


    class DynectSession(object):
        """Base object representing a DynectSession Session"""
        def __init__(self, customer, username, password, host='api.dynect.net',
                     port=443, ssl=True, api_version='current', auto_auth=True):
            # __init__ logic here

        def __new__(cls, *args, **kwargs):
            try:
                if globals()['SESSION'] is None:
                    globals()['SESSION'] = super(DynectSession, cls).__new__(cls,
                                                                             *args,
                                                                             **kwargs)
            except KeyError:
                globals()['SESSION'] = super(DynectSession, cls).__new__(cls, *args)
            return globals()['SESSION']

While this worked for a short while, it had its flaws:
    1. Once Message Management support was added, the code needed to be duplicated to rename the ‘SESSION’ key to ‘MM_SESSION’. This was inefficient.
    2. This allowed you to only have one active Session, even in shared memory space, i.e. threads.
    3. Sessions were only truly “global” in the scope of the dyn.tm module. It could still be accessed externally, but it was less than ideal.

What We Do Now
^^^^^^^^^^^^^^
As of v1.0.0, Session types remain Singletons but are implemented differently.

Sessions are now implemented as :class:`dyn.core.SessionEngine` objects
and :class:`dyn.core.Singleton` *type* objects. EXAMPLE::

    class Singleton(type):
        """A :class:`Singleton` type for implementing a true Singleton design
        pattern, cleanly, using metaclasses
        """
        _instances = {}
        def __call__(cls, *args, **kwargs):
            cur_thread = threading.current_thread()
            key = getattr(cls, '__metakey__')
            if key not in cls._instances:
                cls._instances[key] = {
                    # super(Singleton, cls) evaluates to type; *args/**kwargs get
                    # passed to class __init__ method via type.__call__
                    cur_thread: super(_Singleton, cls).__call__(*args, **kwargs)
                }
            return cls._instances[key][cur_thread]

The Singleton type is applied as a *__metaclass__* in each of the two Session
types. This allows for a much cleaner implementation of Singletons. Every time
one is accessed, it will globally have knowledge of other instances, as those
instances are tied to the classes themselves instead of held in the *globals*
of the session modules. In addition, this allows users to have multiple active
sessions across multiple threads, which was not possible in the prior
implementation.


Password Encryption
-------------------
The Managed DNS REST API only accepts passwords in plain text. The
passwords stored in :class:`~dyn.tm.session.DynectSession` objects only
live in memory, reducing the security risk of plain text passwords in this instance.
However, for users looking to do more advanced things, such as serialize and store
their session objects in something less secure, such as a database, these
plain text passwords are not ideal. In response to this, Dyn added optional AES-256
password encryption for all :class:`~dyn.tm.session.DynectSession` instances in
version 1.1.0. To enable password encryption, install
`PyCrypto <http://www.dlitz.net/software/pycrypto/>`_.

Key Generation
^^^^^^^^^^^^^^
In version 1.1.0, an optional key field parameter was added to the
:class:`~dyn.tm.session.DynectSession` __init__ method. This field will allow
you to specify the key that your encrypted password will be using. You can also
let the Dyn module handle the key generation in addition to using
the :func:`~dyn.encrypt.generate_key` function, which generates a random
50 character key that can be easily consumed by the :class:`~dyn.encrypt.AESCipher`
class (the class responsible for performing the encryption and decryption).

Encrypt Module
^^^^^^^^^^^^^^
::
.. autofunction:: dyn.encrypt.generate_key

.. autoclass:: dyn.encrypt.AESCipher
    :members:
    :undoc-members:
