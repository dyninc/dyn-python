.. _dsf-service-index:

DSFRecords
==========

.. autoclass:: dyn.tm.services.dsf.DSFARecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFAAAARecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFCERTRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFCNAMERecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFDHCIDRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFDNAMERecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFDNSKEYRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFDSRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFKEYRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFKXRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFLOCRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFIPSECKEYRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFMXRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFNAPTRRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFPTRRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFPXRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFNSAPRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFRPRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFNSRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFSPFRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFSRVRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFTXTRecord
    :members:
    :undoc-members:

DSFRecordSet
============

.. autoclass:: dyn.tm.services.dsf.DSFRecordSet
    :members:
    :undoc-members:

DSFFailoverChain
================

.. autoclass:: dyn.tm.services.dsf.DSFFailoverChain
    :members:
    :undoc-members:

DSFResponsePool
===============

.. autoclass:: dyn.tm.services.dsf.DSFResponsePool
    :members:
    :undoc-members:

DSFRuleset
==========

.. autoclass:: dyn.tm.services.dsf.DSFRuleset
    :members:
    :undoc-members:

DSFMonitor
==========

.. autoclass:: dyn.tm.services.dsf.DSFMonitor
    :members:
    :undoc-members:
    
Traffic Director
================

.. autoclass:: dyn.tm.services.dsf.TrafficDirector
    :members:
    :undoc-members:

Traffic Director Examples
-------------------------
The following examples highlight how to use the :class:`TrafficDirector` class to
get/create :class:`TrafficDirector`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Creating a new Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`TrafficDirector` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`TrafficDirector` object.
::

    >>> from dyn.tm.records import ARecord
    >>> from dyn.tm.services.dsf import DSFRecord, DSFRecordSet, \
    ...     DSFFailoverChain, DSFResponsePool, DSFRuleset, DSFMonitor, TrafficDirector
    >>> # Create a dyn.tmSession
    >>> # Assuming you own the zone 'example.com'
    >>> zone = 'example.com'
    >>> fqdn = zone + '.'
    >>> a_rec = DSFARecord('1.1.1.1', ttl=60, label='RecordLabel')
    >>> record_set = DSFRecordSet('A', label='RSLabel', records=[record])
    >>> failover_chain = DSFFailoverChain(label='FCLabel', record_sets=[record_set])
    >>> rp = DSFResponsePool(label='RPLabel', rs_chains=[failover_chain])
    >>> criteria = {'geoip': {'country': ['US']}}
    >>> ruleset = DSFRuleset(label='RSLabel', criteria_type='geoip',
    ...                      criteria=criteria, response_pools=[rp])
    >>> monitor = DSFMonitor('MonLabel', 'HTTP', 1, 60, 1, port=8080)
    >>> dsf = TrafficDirector('DSFLabel', rulesets=[ruleset])

Getting an Existing Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`TrafficDirector` from
the dyn.tm System and how to edit some of the same fields mentioned above.
::

    >>> # Continuing from the previous example
    >>> dsf_id = dsf.service_id
    >>> dsf = TrafficDirector(dsf_id)

