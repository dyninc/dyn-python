# -*- coding: utf-8 -*-
"""This module contains all API classes for DynDNS Service types

These services do not always need to be created via a zone instance but could
for the sake of organization it is recommended to not go creating services
that you do not currently need.

NOTES: LoadBalance and CDNManager are deprecated and not included
"""
from .active_failover import *
from .ddns import DynamicDNS
from .httpredirect import HTTPRedirect
from .dnssec import *
from .gslb import *
from .reversedns import ReverseDNS
from .rttm import *
from .dsf import *

__author__ = 'jnappi'
