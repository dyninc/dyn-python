.. _dsf-service-index:

DSFRecords
==========

.. autoclass:: dyn.tm.services.dsf.DSFARecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFAAAARecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFALIASRecord
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

.. autoclass:: dyn.tm.services.dsf.DSFSSHFPRecord
    :members:
    :undoc-members:

.. autoclass:: dyn.tm.services.dsf.DSFTXTRecord
    :members:
    :undoc-members:

DSFRecord Examples
-------------------------
The following examples highlight how to use the :class:`DSFRecord` classes to
get/create/update/delete :class:`DSFRecord`'s on the dyn.tm System and how to edit these
objects from within a Python script. We'll stick to a simple :class:`DSFARecord` in our examples.

Create DSF__Record
^^^^^^^^^^^^^^^^^^
We'll assume you already have a :class:`DSFRecordset` object called `record_set` in existence for this example.

    >>> from dyn.tm.services.dsf import DSFARecord
    >>> record = DSFARecord('10.1.1.1', label='TEST RECORD', weight=1, automation='auto', eligible=True)
    >>> #Now, we create this A record by adding it to an existing record_set
    >>> record.add_to_record_set(record_set) #This is automatically published.

Update DSF__Record
^^^^^^^^^^^^^^^^^^
To change the record IP address of the record we just created, we can use one of our setters.

    >>> record.address = '20.1.1.1' #This gets published implicitly
    >>> #Check to see if it really changed.
    >>> record.address
    >>>'20.1.1.1'

Implicit publishing can be turned off for any object if that is undesirable, check `Modifying Traffic Director
Service Properties` below for an example and explaination

Delete DSF__Record
^^^^^^^^^^^^^^^^^^
To Delete your :class:`DSFRecord`:

    >>> record.delete()

DSFRecordSet
============

.. autoclass:: dyn.tm.services.dsf.DSFRecordSet
    :members:
    :undoc-members:


DSFRecordSet Examples
-------------------------
The following examples highlight how to use the :class:`DSFRecordSet` classes to
get/create/update/delete :class:`DSFRecordSet`'s on the dyn.tm System and how to edit these
objects from within a Python script.


Create DSFRecordSet
^^^^^^^^^^^^^^^^^^
We'll assume you already have a :class:`DSFFailoverChain` object named `failover_chain` in existence for this example.

    >>> from dyn.tm.services.dsf import DSFRecordSet
    >>> #set up recordset for A records,
    >>> record_set = DSFRecordSet('A', label='Record_set_test', ttl=60)
    >>> #Now, we create this record_set by adding it to an existing failvoer_chain
    >>> record_set.add_to_failover_chain(failover_chain) #This is automatically published.

To make the record_set and its child A records in one create action:

    >>> from dyn.tm.services.dsf import DSFRecordSet, DSFARecord
    >>> #Create A Record Prototypes
    >>> record1 = DSFARecord('10.1.1.1', label='TEST RECORD 10', weight=1, automation='auto', eligible=True)
    >>> record2 = DSFARecord('20.1.1.1', label='TEST RECORD 20', weight=1, automation='auto', eligible=True)
    >>> #set up record_set for A records and pass in the two record protypes,
    >>> record_set = DSFRecordSet('A', label='Record_set_test', ttl=60, records=[record1, record2])
    >>> #Now, we create this record_set by adding it to an existing failover_chain
    >>> record_set.add_to_failover_chain(failover_chain) #This is automatically published.

As with all other DSF objects, the prototypes `record1` `record2` can't be used in CRUD operations. You must access these
objects within the record_set.

    >>> record_set.records
    >>>[<ARecord>: 10.1.1.1, <ARecord>: 20.1.1.1]

Update DSFRecordSet
^^^^^^^^^^^^^^^^^^^
To change the label for the above :class:`DSFRecordset`:

    >>> record_set.label = 'New Name'  #This gets published implicitly
    >>> #Check to see if it really changed.
    >>> record_set.label.label
    >>>'New Name'

Implicit publishing can be turned off for any object if that is undesirable, check `Modifying Traffic Director
Service Properties` below for an example and explaination

Adding DSFMonitor to DSFRecordSet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To add a :class:`DSFMonitor` to your :class:`DSFRecordset`:

Existing :class:`DSFRecordset`:

    >>> from dyn.tm.services.dsf import DSFMonitor
    >>> #create your monitor
    >>> monitor = DSFMonitor('testmonitor', 'HTTP', 1, 60, 1, port=80)
    >>> #or get an existing one (example)
    >>> from dyn.tm.services.dsf import get_all_dsf_monitors
    >>> monitor = get_all_dsf_monitors()[0]
    >>> #Now attach monitor to record_set
    >>> record_set.set_monitor(monitor)

New :class:`DSFRecordset`:

    >>> #Create or get your monitor object as above.
    >>> record_set = DSFRecordSet('A', label='Record_set_test', ttl=60, dsf_monitor_id=monitor.dsf_monitor_id)
    >>> record_set.add_to_failover_chain(failover_chain) #create record_set


Delete DSFRecordSet
^^^^^^^^^^^^^^^^^^
To Delete your :class:`DSFRecordset`:

    >>> record_set.delete()

This will delete all child records attached to this object!

DSFFailoverChain
================

.. autoclass:: dyn.tm.services.dsf.DSFFailoverChain
    :members:
    :undoc-members:

DSFFailoverChain Examples
-------------------------
The following examples highlight how to use the :class:`DSFFailoverChain` classes to
get/create/update/delete :class:`DSFFailoverChain`'s on the dyn.tm System and how to edit these
objects from within a Python script.


Create DSFFailoverChain
^^^^^^^^^^^^^^^^^^^^^^^
We'll assume you already have a :class:`DSFResponsePool` object named `response_pool` in existence for this example.

    >>> from dyn.tm.services.dsf import DSFFailoverChain
    >>> #set up failover_chain
    >>> failover_chain = DSFFailoverChain(label='TEST Chain')
    >>> #Now, we create this failover_chain by adding it to an existing response_pool
    >>> failover_chain.add_to_response_pool(response_pool) #This is automatically published.

To make the failover_chain and its child record_set in one create action:

    >>> from dyn.tm.services.dsf import DSFFailoverChain, DSFRecordSet
    >>> #set up record_set prototype
    >>> record_set = DSFRecordSet('A', label='Record_set_test', ttl=60,)
    >>> #set up failover_chain and pass in the record_set prototype
    >>> failover_chain = DSFFailoverChain(label='TEST Chain', record_sets=[record_set])
    >>> #Now, we create this failover_chain by adding it to an existing response_pool
    >>> failover_chain.add_to_response_pool(response_pool) #This is automatically published.

You can continue nesting beyond record_set by adding records = [record1...] to the record_set prototype. See
:class:`TrafficDirector` example for a larger example,

As with all other DSF objects, the prototypes record_set can't be used in CRUD operations. You must access these
objects within the failover_chain.

    >>> failover_chain.record_sets
    >>>[<DSFRecordSet>: RDClass: A, Label: Record_set_test, ID: r6e1_IkchB-Yp93rAEClo8QbZzA]

Update DSFFailoverChain
^^^^^^^^^^^^^^^^^^^^^^^
To change the label for the above :class:`DSFFailoverChain`:

    >>> failover_chain.label = 'New Name'  #This gets published implicitly
    >>> #Check to see if it really changed.
    >>> failover_chain.label
    >>>'New Name'

Implicit publishing can be turned off for any object if that is undesirable, check `Modifying Traffic Director
Service Properties` below for an example and explaination


Delete DSFFailoverChain
^^^^^^^^^^^^^^^^^^^^^^^
To Delete your :class:`DSFFailoverChain`:

    >>> failover_chain.delete()

This will delete all child records attached to this object!



DSFResponsePool
===============

.. autoclass:: dyn.tm.services.dsf.DSFResponsePool
    :members:
    :undoc-members:

DSFResponsePool Examples
-------------------------
The following examples highlight how to use the :class:`DSFResponsePool` classes to
get/create/update/delete :class:`DSFResponsePool`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Create DSFResponsePool
^^^^^^^^^^^^^^^^^^^^^^^
Because the :class:`DSFReponsePool` is at the bottom of the tree, there is nothing to attach to it except for the :class:`TrafficDirector` service.

    >>> from dyn.tm.services.dsf import DSFResponsePool
    >>> #set up Response Pool with label
    >>> response_pool = DSFResponsePool(label='TEST Pool')
    >>> #Now, we create this response_pool by passing in the TrafficDirector object
    >>> response_pool.create(td) #This is automatically published.

To make the response_pool and its child failover_chain in one create action:

    >>> from dyn.tm.services.dsf import DSFFailoverChain, DSFResponsePool
    >>> #set up failover_chain prototype
    >>> failover_chain = DSFFailoverChain(label='TEST Chain')
    >>> #set up response_pool and pass in the failover_chain prototype
    >>> response_pool = DSFResponsePool(label='TEST Pool', rs_chains=[failover_chain])
    >>> #Now, we create this response_pool by adding it to an existing TrafficDirector service
    >>> response_pool.create(td) #This is automatically published.

You can continue nesting beyond failover_chain by adding records_set = [record_set1...] to the failover_chain prototype. See
:class:`TrafficDirector` example for a larger example,

As with all other DSF objects, the prototypes failover_chain can't be used in CRUD operations. You must access these
objects within the response_pool.

    >>> response_pool.failover_chains
    >>>[<DSFFailoverChain>: Label: TEST Chain, ID: AFUQpP2GRADINM1W12j_AVp_AX0]


Update DSFResponsePool
^^^^^^^^^^^^^^^^^^^^^^^
To change the label for the above :class:`DSFResponsePool`:

    >>> response_pool.label = 'New Name'  #This gets published implicitly
    >>> #Check to see if it really changed.
    >>> response_pool.label
    >>>'New Name'

Implicit publishing can be turned off for any object if that is undesirable, check `Modifying Traffic Director
Service Properties` below for an example and explaination


Delete DSFResponsePool
^^^^^^^^^^^^^^^^^^^^^^^
To Delete your :class:`DSFResponsePool`:

    >>> response_pool.delete()

This will delete all child records attached to this object!


DSFRuleset
==========

.. autoclass:: dyn.tm.services.dsf.DSFRuleset
    :members:
    :undoc-members:

DSFRuleset Examples
-------------------
The following examples highlight how to use the :class:`DSFRuleset` classes to
get/create/update/delete :class:`DSFRuleset`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Create DSFRuleset
^^^^^^^^^^^^^^^^^
The :class:`DSFRuleset` contains zero or more Response Pools, and belongs to the :class:`TrafficDirector` service

    >>> from dyn.tm.services.dsf import DSFRuleset
    >>> #Make an empty ruleset:
    >>> ruleset = DSFRuleset('The Rules', criteria_type='always', response_pools=[])

To make the ruleset and its create-link a response_pool in one create action:

    >>> from dyn.tm.services.dsf import DSFRuleset, DSFResponsePool
    >>> response_pool = DSFResponsePool(label='TEST Pool')
    >>> #Make an empty ruleset:
    >>> ruleset = DSFRuleset('The Rules', criteria_type='always', response_pools=[response_pool])

You can continue nesting beyond response_pool by adding rs_chain = [failover_chain1...] to the response_pool prototype. See
:class:`TrafficDirector` example for a larger example,

As with all other DSF objects, the prototypes response_pool can't be used in CRUD operations. You must access these
objects within the ruleset.

    >>> ruleset.response_pools
    >>>[<DSFResponsePool>: Label: TEST Pool, ID: NXAdxSrodSCUO_p9vbbpKuXJIOw]

Adding/Deleting/Modifying DSFResponsePools to DSFRuleset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The order of :class:`DSFResponsePool`s is important in rulesets, so we have a number of functions for handling this.
For this example assume we have 4 response pools pre-existing.

    >>> #Lets add all 4 Response Pools to the ruleset.
    >>> ruleset.add_response_pool(pool1) #First Pool
    >>> ruleset.add_response_pool(pool2) #added to the front of the list
    >>> ruleset.add_response_pool(pool3) #added to the front of the list
    >>> #If we want pool4 to be at the back of the list we can specify the index.
    >>> ruleset.add_response_pool(pool4, index=3)
    >>> ruleset.response_pools
    >>>[<DSFResponsePool>: Label: pool3, ID: 4Vu7lCEb3iDuATWq5Q6-5P-RAfU,
    ...<DSFResponsePool>: Label: pool2, ID: LPDIZfbr0gEVg-AR31CNE_wVDIg,
    ...<DSFResponsePool>: Label: pool1, ID: JybChuDQtCWSyADLFfqp2JKFYoE,
    ...<DSFResponsePool>: Label: pool4, ID: 3a-eVZYaRt3NeNxUXyA87OroswQ]

If you need to re-order your list, there is a helper function

    >>> ruleset.order_response_pools([pool1,pool2,pool3,pool4])
    >>> ruleset.response_pools
    >>> [<DSFResponsePool>: Label: pool1, ID: JybChuDQtCWSyADLFfqp2JKFYoE,
    ...<DSFResponsePool>: Label: pool2, ID: LPDIZfbr0gEVg-AR31CNE_wVDIg,
    ...<DSFResponsePool>: Label: pool3, ID: 4Vu7lCEb3iDuATWq5Q6-5P-RAfU,
    ...<DSFResponsePool>: Label: pool4, ID: 3a-eVZYaRt3NeNxUXyA87OroswQ]

And, if you need to Delete a :class:`DSFResponsePool` from the ruleset
    >>> ruleset.remove_response_pool(pool3)
    >>>[<DSFResponsePool>: Label: pool1, ID: JybChuDQtCWSyADLFfqp2JKFYoE,
    ...<DSFResponsePool>: Label: pool2, ID: LPDIZfbr0gEVg-AR31CNE_wVDIg,
    ...<DSFResponsePool>: Label: pool4, ID: 3a-eVZYaRt3NeNxUXyA87OroswQ]


Adding/manipulating a failover IP to DSFRuleset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:class:`DSFRulesets` have the option to failover to a static IP. Behind the scenes, this is essential a full
 ResponsePool to Record chain with one single host or IP. when manipulating this value, keep that in mind.

Assume we have the same service as the Adding/Deleting/Modifying DSFResponsePools to DSFRuleset example.

    >>> #To Add the failover IP.
    >>> ruleset.add_failover_ip('1.2.3.4')
    >>> # Notice how its essentially a Response_pool -> Record chain -- this is always added to the end of the response pool list.
    >>> ruleset.response_pools
    >>>[<DSFResponsePool>: Label: pool1, ID: JybChuDQtCWSyADLFfqp2JKFYoE,
    ...<DSFResponsePool>: Label: pool2, ID: LPDIZfbr0gEVg-AR31CNE_wVDIg,
    ...<DSFResponsePool>: Label: pool4, ID: 3a-eVZYaRt3NeNxUXyA87OroswQ,
    ...<DSFResponsePool>: Label: 1.2.3.4, ID: wyUslh6c9eTXFvu7OSfW7S6Hj9I]
    >>> # To modify the IP:
    >>> ruleset.response_pools[3].rs_chains[0].record_sets[0].records[0].address = '10.10.10.10'
    >>> #The labels for the chain will still say 1.2.3.4, but the served records will be 10.10.10.10


Update DSFRuleset
^^^^^^^^^^^^^^^^^^^^^^^
To change the label for the above :class:`DSFRuleset`:

    >>> ruleset.label = 'New Name'  #This gets published implicitly
    >>> #Check to see if it really changed.
    >>> ruleset.label
    >>>'New Name'


Delete DSFRuleset
^^^^^^^^^^^^^^^^^^^^^^^
To Delete your :class:`DSFRuleset`:

    >>> ruleset.delete()

This will NOT delete child records, however any child response pools and childre that are not in other :class:`DSFRuleset`s
may not be displayed in the :class:`TrafficDirector` object as it builds its trees from the Rulesets. see `Traffic Director SDK Caveats`


DSFMonitor
==========

.. autoclass:: dyn.tm.services.dsf.DSFMonitor
    :members:
    :undoc-members:

DSFMonitor Examples
-------------------
The following examples highlight how to use the :class:`DSFMonitor` classes to
get/create/update/delete :class:`DSFMonitor`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Create DSFMonitor
^^^^^^^^^^^^^^^^^
Unlike most of the other DSF objects, :class:`DSFMonitor` publishes when the object is created.

    >>> from dyn.tm.services.dsf import DSFMonitor
    >>> monitor = DSFMonitor('MonitorLabel', 'HTTP', 1, 60, 1, port=8080)
    >>> monitor.dsf_monitor_id
    >>> u'SE-6GKx_tEBHyL4G_-i28R2QiNs'

Update DSFMonitor
^^^^^^^^^^^^^^^^^^^^^^^
To change the label for the above :class:`DSFRuleset`:

    >>> monitor.label = 'NewMonitorName'  #Changes are immediate
    >>> #Check to see if it really changed.
    >>> monitor.label
    >>>'NewMonitorName'


Add To DSFMonitor to DSFRecordSet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See :class:`DSFRecordSet` example.


Delete DSFMonitor
^^^^^^^^^^^^^^^^^
To Delete your :class:`DSFMonitor`:

    >>> monitor.delete()


DSFNotifier
==========
.. autoclass:: dyn.tm.services.dsf.DSFNotifier
    :members:
    :undoc-members:

DSFNotifier Examples
-------------------
The following examples highlight how to use the :class:`DSFNotifier` classes to
get/create/update/delete :class:`DSFNotifier`'s on the dyn.tm System and how to edit these
objects from within a Python script.

Create DSFNotifier
^^^^^^^^^^^^^^^^^

Unlike most of the other DSF objects, :class:`DSFNotifier` publishes when the object is created.

    >>> from dyn.tm.services.dsf import DSFNotifier
    >>> #When passing in recipients, pass in a list of strings(s) of your contact(s) nickname(s)
    >>> notifier = DSFNotifier('Notifier', recipients=['youruser'])
    >>> notifier.dsf_notifier_id
    >>> u'BHyL4GxatEBHyR2QiNT28R2QiNs'

You can add the new notifier directly to a :class:`TrafficDirector` as well
    >>> from dyn.tm.services.dsf import DSFNotifier
    >>> #When passing in recipients, pass in a list of strings(s) of your contact(s) nickname(s)
    >>> notifier = DSFNotifier('Notifier', recipients=['youruser'], dsf_services=[td.service_id])
    >>> notifier.dsf_notifier_id
    >>> u'xatEBHyQiNT28R2QiyR2QiNt28R'


Update DSFNotifier
^^^^^^^^^^^^^^^^^^^^^^^
To change the label for the above :class:`DSFRuleset`:

    >>> notifier.label = 'NewNotifierName'  #Changes are immediate
    >>> #Check to see if it really changed.
    >>> notifier.label
    >>>'NewNotifierName'

Delete DSFNotifier
^^^^^^^^^^^^^^^^^
To Delete your :class:`DSFNotifier`:

    >>> notifier.delete()



Traffic Director
================

.. autoclass:: dyn.tm.services.dsf.TrafficDirector
    :members:
    :undoc-members:

Traffic Director Examples
-------------------------
The following examples highlight how to use the :class:`TrafficDirector` class to
get/create/update/delete :class:`TrafficDirector`'s on the dyn.tm System and how to edit these
objects from within a Python script.


Creating an empty Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following shows the creation of the very most basic empty :class:`TrafficDirector`


   >>> from dyn.tm.services.dsf import TrafficDirector
   >>> td = TrafficDirector('TD_test_1', rulesets=[])
   >>> #Now, lets look at the ID to make sure it was actually created.
   >>> td.service_id
   >>>u'w8WWsaqJicADC8OD1k_3GSFru7M'
   >>> #service_id will be a long hash


Adding a Ruleset to your Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The TrafficDirector service has a cascading style of adding sub objects where the child object
is added to the parent by either and `add_to_` function, or a create. This helps enforce
that children objects do not become orphaned.

   >>> #Continuing from the example above.
   >>> from dyn.tm.services.dsf import DSFRuleset
   >>> #Let's make a ruleset called 'The Rules' which always serves, and has no response_pools
   >>> ruleset = DSFRuleset('The Rules', criteria_type='always', response_pools=[])
   >>> #Now, lets add that ruleset to the Traffic Director instance from above.
   >>> ruleset.create(td)
   >>> #Now, Verify it was added. The 'rulesets' getter will return a list of rulesets attached to the td service instance.
   >>> td.rulesets
   >>>[<DSFRuleSet>: Label: The Rules, ID: gthPTkFOYUrJFymEknoHeezBeSQ]

Adding RecordSets, FailoverChains, RecordSets, and Records to your Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please see individual sections for instructions on how to actually do this, as with :class:`DSFRuleset`s, there is a cascading system:

TD <- Ruleset -> ResponsePool <- FailoverChain <- RecordSet <- Record

to 'create' each, the function looks like:
    >>> ruleset.create(td)
    >>> ruleset.add_response_pool(pool)
    >>> pool.create(td)
    >>> failoverchain.add_to_response_pool(pool)
    >>> recordset.add_to_failover_chain(failoverchain)
    >>> record.add_to_record_set(recordset)

Modifying Traffic Director Service Properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can modify such things as labels, ttl, etc for the :class:`TrafficDirector` object.
Note, that modifying these values will immediately publish them. This can be turned off as in the example below.

    >>> #Continuing from the example above.
    >>> #parameter updates will publish implicitly.
    >>> td.label #check what the label is.
    >>>u'TD_test_1'
    >>> td.label='TD_test_2'
    >>> td.label
    >>>u'TD_test_2'

    >>> #Now, say you don't want your update changes to be implicitly published. you can turn off implicit publishing for
    >>> #the service level changes.
    >>> #!!!WARNING!!!! changing the implict publish flag ONLY disables implicit publishing for this Object,
    >>> #not any of its children objects like Rulesets etc.
    >>>
    >>> td.label
    >>>u'TD_test_2'
    >>> td.implicitPublish = False
    >>> td.label = 'TD_test_3'
    >>> td.refresh() #pulls down fresh data from the system, as your td.label is now stale due to it not being published
    >>> td.label
    >>>u'TD_test_2'
    >>> td.ttl = 299
    >>> td.refresh()
    >>> td.ttl
    >>>300
    >>> td.publish()
    >>> td.ttl
    >>>299
    >>> td.label
    >>>u'TD_Test_3'


Getting an Existing Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to get an existing :class:`TrafficDirector` from
the dyn.tm System

    >>> # Continuing from the previous example
    >>> id = td.service_id
    >>> gotTD = TrafficDirector(id)
    >>> gotTD.label
    >>>u'TD_Test_3'

    What if you don't know your service_id? But maybe you know the name...

    >>> from dyn.tm.services.dsf import get_all_dsf_services
    >>> get_all_dsf_services()
    >>>[<TrafficDirector>: notme, ID: qzoiassV-quZ_jGh7jbn_PfYNxY,
    ...<TrafficDirector>: notmeeither, ID: qdE-zi4k7zEVhH6jWugVSbiIxdA,
    ...<TrafficDirector>: imtheone, ID: AwqcnhOZ6r1aCpIZFIj4mTwdd9Y]
    >>> myTD = get_all_dsf_services()[2]
    >>> myTD.label
    >>>u'imtheone'



Adding/Deleting a Notifier to your Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can add notifiers to your Traffic Director service in the following ways:

    Example 1:

    >>> from dyn.tm.services.dsf import DSFNotifier
    >>> notifier = DSFNotifier('deleteme', recipients=['youruser'])
    >>> td.add_notifier(notifier1)
    >>> td.refresh()
    >>> td.notifiers
    >>>[<DSFNotifier>: deleteme, ID: 8lJ9LUcP9sIuB8V58zsGWVu1Hys]
    >>> #To delete:
    >>> td.del_notifier(notifier1)
    >>> td.refresh()
    >>> td.notifiers
    >>>[]

    Example 2:

    >>> #Notifiers can also be added at the creation time of the Notifier by passing in the service_id
    >>> from dyn.tm.services.dsf import DSFNotifier
    >>> notifier = DSFNotifier('deleteme', recipients=['youruser'], dsf_services=[td.service_id])
    >>> td.refresh()
    >>> td.notifiers
    >>>[<DSFNotifier>: deleteme, ID: q-hZOVTn2Q_VCX1LFMSI-4LPTww]



Deleting Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can also delete your service in the following manner:

    >>>td.delete()
    >>>td.refresh()
    >>>DynectGetError: detail: No service found.



Creating a fully populated Traffic Director Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following example shows how to create a new :class:`TrafficDirector` on the
dyn.tm System and how to edit some of the fields using the returned
:class:`TrafficDirector` object.

    >>> #A fully populated service can achieved by creating a full chain and passing child objects into each parent object.
    >>> #These objects are effectively constructor objects. In other words, they will be useless for CRUD operations, except for
    >>> #The TrafficDirector object. There are other means for achieving CRUD operations as you will see.
    >>>
    >>> from dyn.tm.services.dsf import *
    >>> from dyn.tm.zones import Node
    >>>
    >>> #Lets start with our objects that are actually created when the command is executed.
    >>>
    >>> #First, lets make our Monitor. we pass this in to the recordset later. This monitor is created at execution time.
    >>> monitor = DSFMonitor('MonLabel', 'HTTP', 1, 60, 1, port=8080)
    >>>
    >>> #Second, lets make a new Notifier -- this is optional. We'll assume you have a contact named 'contactname'
    >>> notifier = DSFNotifier('Notifier', recipients=['contactname'])
    >>>
    >>>
    >>> #Next lets make our A Record prototype:
    >>> a_rec = DSFARecord('1.1.1.1', ttl=60, label='RecordLabel')
    >>>
    >>> #Next, lets create the record_set. Note how we pass in the a_rec A Record Object, and the monitor_id
    >>> record_set = DSFRecordSet('A', label='RSLabel', dsf_monitor_id = monitor.dsf_monitor_id,records=[a_rec])
    >>>
    >>> #Next, lets create the failover chain Note how we pass in the record_set RecordSet Object
    >>> failover_chain = DSFFailoverChain(label='FCLabel', record_sets=[record_set])
    >>>
    >>> #Next, lets create the response pool Note how we pass in the failover_chain Failover Chain Object
    >>> rp = DSFResponsePool(label='RPLabel', rs_chains=[failover_chain])
    >>> criteria = {'geoip': {'country': ['US']}}
    >>>
    >>> #Next, lets create the ruleset Note how we pass in the rp Response Pool Object
    >>> ruleset = DSFRuleset(label='RSLabel', criteria_type='geoip',
    ...                      criteria=criteria, response_pools=[rp])
    >>>
    >>> #Now, lets create a Node object. This is used for attaching the service to a Node (or zone)
    >>> node = Node('example.com',fqdn = 'example.com.')
    >>>
    >>> Finally, we pass all of this in. upon command execution the service will have been created.
    >>>
    >>> dsf = TrafficDirector('Test_Service', rulesets=[ruleset], nodes=[node], notifiers=[notifier])


Now that you have created your service in one fell swoop, there are a few things you must know:

Prototype objects like your DSFARecord, DSFRecordSet are just that, prototypes. You can't perform CRUD operations on them.
This goes for any child object where you pass in prototypes. See examples below:

    >>> #Trying to access a prototype
    >>> a_rec.address='1.2.3.4'
    >>>DynectUpdateError: record_update: No service found.

    >>> #Instead, do this:
    >>> dsf.records
    >>> [<ARecord>: 1.1.1.1]
    >>> dsf.records[0].address='1.2.3.4'
    >>> dsf.records[0].address
    >>> u'1.2.3.4'


Traffic Director SDK Caveats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*  Creating a fully populated service with prototypes leaves the prototypes unusable.
   CRUD capabilities can only be achieved   by accessing data within the
   :class:`TrafficDirector` object.
   Accessors are `records`, `record_sets`, `failover_chains`, `response_pools`, `rulesets`

*  Accessors like in the previous bullet point only work if the object is fully linked to the service.
   In other words, you can have a full response_pool, but if it does not belong to a ruleset, then it will
   not show up.
   To list all objects under the service, including orphands you must use `all_records`, `all_record_sets`,
   `all_failover_chains`, `all_response_pools`, `all_rulesets`

*  Some `records`, `record_sets`, `failover_chains`, `response_pools`, `rulesets` will appear multiple times.
   This is becasue these record trees are built from the ruleset, and if one response pool belongs to multiple
   Rulesets, then its children will appear as many times as is exists as a ruleset member.

*  :param refresh(): is your friend. When modifying child objects from a parent sometimes the parent doesn't know about
   the changes. If you do a refresh() on the :class:`TrafficDirector` object it will pull down the latest data
   from the Dynect System.

*  :param publish(): is run on the :class:`TrafficDirector` as a whole, even when run from a child object.

*  :param implicitPublish: is non cascading. It is locally bound to the specific object, or child object.




