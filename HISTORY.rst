Release History
---------------
1.6.4 (2016-05-20)
*Added Publish Notes to Traffic Director Service. User created Zone Notes can now be generated on a Traffic Director Publish. This includes in line setter publishes, or full Service level publishes.

1.6.3 (2016-3-21)
++++++++++++++++
*Added TrafficDirector:replace_all_rulesets to wholesale replace rulesets on a TrafficDirector
*Added TrafficDirector:replace_one_ruleset to remove and replace a single ruleset entry in place
*Merged Proxy support from PR #73


1.6.2 (2016-3-7)
++++++++++++++++
*Added order_rulesets() to TrafficDirector object, for re-ordering Rulesets
*Added index=n to Ruleset create() so New rulesets can be placed in a certain location in the chain.
*Added getters for single DSF objects get_record(), get_record_set() etc.
*Fixed bug with DSF Monitor options
*Fixed bug where adding criteria to rulesets with 'always' criteria_type changes it to 'geoip' by default.

1.6.1 (2016-2-11)
+++++++++++++++++
*Added UNKNOWN record type
*DSF records status getter added

1.6.0 (2016-1-28)
+++++++++++++++++
*DSF service objects can now be independently Created, Updated, Read, and Deleted.
*Signifigant changes to how DSF service works. There may be some minor breaking changes here.
*Record getters now automatically pull data from system instead of storing them locally.

1.5.2 (2016-1-11)
+++++++++++++++++
*Addition of Delay feature to GSLB Services
*Minor Improvements to GSLB features.
*Addition of Apex Finder

1.5.1 (2015-12-17)
++++++++++++++++++
*Addition of CSYNC records

1.5.0 (2015-12-14)
++++++++++++++++++
*Alias Traffic Director Support, coincides with ALIAS product release.
*Addition of CDS and CDNSKEY records.


1.4.5 (2015-12-9)
+++++++++++++++++

* Added support for new syslog delivery type. `syslog_delivery` where `all` delivers messages no matter what the state and `change` only does so upon a detected change.


1.4.4 (2015-11-25)
++++++++++++++++++

* Added support for ALIAS records.

1.4.3 (2015-08-14)
++++++++++++++++++

*Added support for configurable Syslog Messages


1.4.2 (2015-08-10)
++++++++++++++++++

* Added support for deleting all records of a certain type per #47. Thanks @tarokkk
* Exception classes are now based on `Exception` per #51. Thanks @thedebugger
* Fixed potential circular dependency in `dyn.tm.services`
* Added HTTP response debug logging

1.4.1 (2015-07-23)
++++++++++++++++++

*added zone notes at publish capabilities.
*added TSIG support

1.4.0 (2015-06-26)
++++++++++++++++++

*Added better coverage for passing Node Objects
*New way of handling DSFNodes with new API call

1.3.14 (2015-06-22)
+++++++++++++++++++

* Internal fixes with zone.

1.3.13 (2015-06-15)
+++++++++++++++++++

*DSF Ruleset Feature enhancement

1.3.12 (2015-06-03)
+++++++++++++++++++

*Added active properties for secondary zones.


1.3.4 (2014-11-11)
++++++++++++++++++

* Bugfix for MMSesion JSON Error caused by arg filtering
* Bugfix for DSFRecord Creation on DSF GET calls

1.3.3 (2014-10-26)
++++++++++++++++++

* Fixed the majority of warnings when building docs, per issue #18
* Added `dyn.tm.zones.get_all_secondary_zones` function for retrieving all secondary zones for an account

1.3.2 (2014-10-21)
++++++++++++++++++

* Fixed an issue where attempting to access a Zone's serial resulted in always performing a GET call

1.3.1 (2014-10-16)
++++++++++++++++++

* Adding additional hooks to dyn.tm.errors that return collections of exceptions

1.3.0 (2014-10-14)
++++++++++++++++++

* dyn.tm.session.DynectSession now accepts a `history` flag to enable per-session history recording

1.2.0 (2014-09-29)
++++++++++++++++++

* Addition of dyn.tm.tools module
* Added change_ip and map_ip functions to dyn.tm.tools
* Added __enter__ and __exit__ methods to DynectSession for allow for use as a context manager
* Added dyn.core.SessionEngine.new_session classmethod for forcing new session generation

1.1.0 (2014-09-16)
++++++++++++++++++

* Internally improved Python2/3 compaability with the intoduction of the dyn.compat module
* Timestamps for various report types are accepted as Python datetime.datetime instances
* Added qps report access to Zones
* Added __str__, __repr__, __unicode__, and __bytes__ methods to all API object types
* Added conditional password encryption to allow for better in-app security
* Added the ability for users to specify their own password encryption keys
* Added __getstate__ and __setstate__ methods to SessionEngine, allowing sessions to be serialized
* Misc bug fixes

1.0.3 (2014-09-05)
++++++++++++++++++

* Adding changes provided by @thomasco to allow for GSLB monitor replacements

1.0.2 (2014-08-26)
++++++++++++++++++

* Added reports module
* Updated installation documentation

1.0.1 (2014-08-06)
++++++++++++++++++

* Small bugfix for an issue affecting sending EMails via the HTMLEmail class

1.0.0 (2014-08-05)
++++++++++++++++++

* Revamed how sessions are structured to support the new SessionEngine interface
* Message Management is now out of BETA due to many bug fixes and additional testing
* You can now have one SessionEngine instance (Singleton) per Thread
* Added File Encoding definitions to source code
* Updated dyn.mm docs to actually include code samples
* Adding some general information on sessions, primarily for my own sanity
* Added EMail subclasses for easier formatting/sending of EMail messages
* mm.session.session and tm.session.session functions have been replaced by the SessionEngine get_session class method
* Completed the dyn.mm.reports module
* Misc MM related bug fixes

0.9.11 (2014-07-25)
+++++++++++++++++++

* Fixed a bug with how calls to ``get_all_zones`` created ``Zone`` objects
* Tackled a possible bug also stemming from ``get_all_zones`` calls where a ``Zone``'s ``contact`` and ``ttl`` attributes could always be ``None``

0.9.10 (2014-07-07)
+++++++++++++++++++

* Added fix for potentially improperly formatted search parameters in dyn.tm.accounts.get_users

0.9.9 (2014-06-26)
++++++++++++++++++

* Added SecondaryZone delete method
* Added better User __str__ representations
* Added SOA TTL bug fix

0.9.6 (2014-05-16)
++++++++++++++++++

* Added Zone attribute updating
* Misc Bug fixes for Python 2.x/3.x cross-compatibility
* GSLB _build bug fix

0.9.5 (2014-05-12)
++++++++++++++++++

* Added custom User-Agent to DynectSession
* Added __all__ attributes where appropriate to simplify imports
* Improved dyn.tm.services import structure

0.9.3 (2014-05-08)
++++++++++++++++++

* Added Active class type for all TM services
* Misc DSFMonitor/Record bug fixes
* Added DSFMonitorEndpoint class

0.8.0 (2014-05-08)
++++++++++++++++++

* Integrated _APILists into GSLB and RTTM services
* Added a more intuitive polling solution for Zone XFERs

0.7.0 (2014-05-02)
++++++++++++++++++

* Fixed Notifier URI construction
* Added _APIDict and _APIList implementations to improve seamless updating of services
* Added custom DSF Record Type Objects to greatly improve ease of creation/management of DSF Services

0.6.0 (2014-04-23)
++++++++++++++++++

* Fixed Python 3.x support with singleton DynectSession instance
* Finished implementation of dyn.mm.accounts
* Improved RTTM support
* Added Zone XFER support
* Added code examples to documentation
* Added better Geo TM support including custom Geo Record Type objects

0.5.0 (2014-04-07)
++++++++++++++++++

* Added initial pass at Message Management BETA functionality
* Cleaned up exception raising and general logic involving internal exception handling

0.4.0 (2014-03-25)
++++++++++++++++++

* Initial fork of Cole Tuininga's code base
* Began creation of OO models
* General cleanup of .pyc files

0.3.0 (2012-10-05)
++++++++++++++++++

* Updated by Cole Tuininga <ctuininga@dyn.com>
* Compatibility update to work with Python 3, incorporating patches suggested by Jonathan Kamens <jkamens@quantopian.com>
* Added a newline to debug output when polling for a result

0.2.0 (2012-05-27)
++++++++++++++++++

* Updated by Cole Tuininga <ctuininga@dyn.com>
* Minor reorg to make it easier to add the library to PyPI

0.1.0 (2011-10-08)
++++++++++++++++++

* Updated by Cole Tuininga <ctuininga@dyn.com>
* Initial release
