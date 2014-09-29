.. _dyn-tm:

dyn.tm (Traffic Management) Module
==================================
The dyn.tm (TM) module provides access to all of the Traffic Management
resources provided by
`Dyn's Traffic Management REST API <https://help.dynect.net/rest-resources/>`_.
It's important to note that all code examples assume the existence of a
:class:`~dyn.tm.session.DynectSession` or :class:`~dyn.tm.session.CollectedSession`
instance. This object is used by the modules described below to access the API
and make their associated calls.

.. _tm-api-documentation:

Dyn Traffic Managment Documentation
-----------------------------------

If you are looking for information on a specific function, class or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2
   :numbered:

   tm/zones
   tm/accounts
   tm/records
   tm/services
   tm/reports
   tm/errors

