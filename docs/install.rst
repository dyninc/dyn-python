.. _install:

Installation
============

This part of the documentation covers the installation of the dyn module.
The first step to using any software package is getting it properly installed.


Distribute & Pip
----------------

Installing dyn is simple via `pip <http://www.pip-installer.org/>`_. Currently
the dyn module is only available internally within Dyn, because of this it can
only be downloaded while on Dyn's internal VPN::

    $ pip install dyn

Get the Code
------------

dyn is actively developed on GitHub, the code is
`always available <https://github.corp.dyndns.com/jnappi/py-dynect>`_.

You can either clone the public repository::

    git clone https://github.corp.dyndns.com/jnappi/py-dynect.git

Download the `tarball <https://github.corp.dyndns.com/jnappi/py-dynect/tarball/master>`_::

    $ curl -OL https://github.corp.dyndns.com/jnappi/py-dynect/tarball/master

Or, download the `zipball <https://github.corp.dyndns.com/jnappi/py-dynect/zipball/master>`_::

    $ curl -OL https://github.corp.dyndns.com/jnappi/py-dynect/zipball/master

Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages by running::

    $ python setup.py install

