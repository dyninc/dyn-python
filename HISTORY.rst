Release History
---------------

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