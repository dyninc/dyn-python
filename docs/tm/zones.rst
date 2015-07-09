.. _zones-index:

Zones
=====
The :mod:`zones` module contains interfaces for all of the various Zone
management features offered by the dyn.tm REST API

List Functions
--------------
The following function is primarily a helper function which performs an API
"Get All" call. This function returns a single ``list`` of :class:`Zone` objects.

.. autofunction:: dyn.tm.zones.get_all_zones
.. autofunction:: dyn.tm.zones.get_all_secondary_zones

Classes
-------
.. toctree::
   :maxdepth: 4

   zones/zone.rst
   zones/secondary.rst
   zones/node.rst
   zones/Tsig.rst

