.. dyn documentation master file, created by
   sphinx-quickstart on Mon Apr 21 21:08:44 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


dyn: The Dyn Python SDK
=======================

Release v\ |version|. (:ref:`Installation <install>`)

With the latest release of this sdk, it's now even easier to manage both your
Dyn Traffic Management and Message Management services.

::

    >>> from dyn.tm.session import DynectSession
    >>> from dyn.tm.zones import Zone
    >>> dynect_session = DynectSession(customer, username, password)
    >>> my_zone = Zone('mysite.com')
    >>> my_zone.status
    'active'
    >>> new_rec = my_zone.add_record('maps', 'A', '127.0.0.1')
    >>> new_rec.fqdn
    'maps.mysite.com.'
    >>> my_zone.get_all_records()
    {u'a_records': [<ARecord>: 127.0.0.1, <ARecord>: 127.0.1.1]}

Contents:

.. toctree::
   :maxdepth: 2
   :numbered:

   intro
   install
   quickstart
   tm
   mm
   advanced


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

