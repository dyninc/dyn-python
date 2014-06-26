.. _dsf-index:

Traffic Director
================
The :mod:`services` module contains interfaces to all of the various service
management features offered by the dyn.tm REST API

List Functions
--------------
The following function is primarily a helper function which performs an API
"Get All" call. This function returns a single ``list`` of
:class:`TrafficDirector` service objects.

.. autofunction:: dyn.tm.services.dsf.get_all_dsf_services

.. autofunction:: dyn.tm.services.dsf.get_all_dsf_monitors

Classes
-------
.. toctree::
   :maxdepth: 3

   dsf/dsf.rst