# -*- coding: utf-8 -*-
"""This module contains all API classes for DynDNS Service types

These services do not always need to be created via a zone instance but could
for the sake of organization it is recommended to not go creating services
that you do not currently need.

NOTES: LoadBalance and CDNManager are deprecated and not included
"""
from dyn.tm.services.active_failover import *  # NOQA
from dyn.tm.services.ddns import DynamicDNS  # NOQA
from dyn.tm.services.httpredirect import HTTPRedirect  # NOQA
from dyn.tm.services.dnssec import *  # NOQA
from dyn.tm.services.gslb import *  # NOQA
from dyn.tm.services.reversedns import ReverseDNS  # NOQA
from dyn.tm.services.rttm import *  # NOQA
from dyn.tm.services.dsf import *  # NOQA

__author__ = 'jnappi'
