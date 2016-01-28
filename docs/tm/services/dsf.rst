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

.. autofunction:: dyn.tm.services.dsf.get_all_notifiers

.. autofunction:: dyn.tm.services.dsf.get_all_records

.. autofunction:: dyn.tm.services.dsf.get_all_record_sets

.. autofunction:: dyn.tm.services.dsf.get_all_failover_chains

.. autofunction:: dyn.tm.services.dsf.get_all_response_pools

.. autofunction:: dyn.tm.services.dsf.get_all_rulesets


Classes
-------
.. toctree::
   :maxdepth: 3

   dsf/dsf.rst