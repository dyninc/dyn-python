.. _sessions:

Advanced Sessions Overview
==========================

The way in which sessions are handled in this library are designed to be super
easy to use for developers who use this library, however, have become relatively
complex internally. Due to their ease of use to the front end user these docs are
mainly for developers who would like to contribute to this code base, or who are
just curious as to what is actually going on under the hood.

Parent Class
------------
Both :class:`dyn.tm.session.DynectSession` and :class:`dyn.mm.session.MMSession`
are subclasses of :class:`dyn.core.SessionEngine`. The :class:`dyn.core.SessionEngine`
provides an easy to use internal API for preparing, sending, and processing outbound
API calls. This class was added in v1.0.0 and greatly reduced the amount of logic
and duplicated code that made looking at these sessions so overly complex.

Parent Type
-----------
Since v0.4.0 sessions had always been implemented as a Singleton type. At this point
you're probably asing "Why?" And that's a bit of a complicated question. One of the main
reasons that these sessions were implemented as a Singleton was to make it easier for
the end user to use this SDK and to make the flow of logic in trying to utilize the
API much smoother. By implementing Sessions as a singleton internally, it allows the
user to not need to hang on to their session objects (unless they want to). It also
means that users don't need to pass their session information around to all of the other
classes in this library in order to make API calls. (ie)::

    >>> from dyn.tm.session import DynectSession
    >>> from dyn.tm.zones import get_all_zones
    >>> DynectSession(**my_credentials)
    >>> zones = get_all_zones()


as opposed to something along these lines::

    >>> from dyn.tm.session import DynectSession
    >>> from dyn.tm.zones import get_all_zones
    >>> my_session = DynectSession(**my_credentials)
    >>> zones = get_all_zones(my_session)

Or, in my opinion, even worse::

    >>> from dyn.tm.session import DynectSession
    >>> my_session = DynectSession(**my_credentials)
    >>> zones = my_session.get_all_zones(my_session)

In these basic examples it may not seem like this is a terribly huge deal, but when
you're dealing with creating multiple types of records, or adding/editing a Traffic
Director service or other complex service, not needing to pass your session around
to the correct places, or use it as a point of entry to other functionality is a huge
relief.

What We Used to Do
^^^^^^^^^^^^^^^^^^
Now that we've gone over the Singleton implementation from a front end POV, let's
talk about it from a backend POV. Effectively what we used to do in each of the Session
types was this::

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

It was a dirty hack that worked for a while, but, it had several fatal flaws.
    1. Once we added Message Management support we needed to duplicate this code to rename the 'SESSION' key to 'MM_SESSION', which is less than ideal due to code duplication
    2. This allowed you to only have one active session, even in shared memory space (ie threads)
    3. Due to the not-so-global scope of globals, this session was really only "global" in the scope of the dyn.tm module. It could still be accessed externally, but it just made me feel dirty knowing that that was what was happening.

What We Do Now
^^^^^^^^^^^^^^
So, as of v1.0.0 this is not how the Session types are implemented anymore. Yes, they
are still Singletons, however, they're implemented completely differently.

Now, on top of these Sessions being implemented as :class:`dyn.core.SessionEngine`
objects, they are also :class:`dyn.core.Singleton` *type* objects. What do these
look like you ask?::

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

So, the Singleton type is applied as a *__metaclass__* in each of the two Session
types. This allows for a much cleaner implementation of Singletons where every time
one is accessed it will globally (actually globally this time) have knowledge of
other instances, since those instances are tied to the classes themselves instead
of held in the *globals* of the session modules. In addition this allows users
to have multiple active sessions across multiple threads, which was previously
impossible in the prior implementation.
