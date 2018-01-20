#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A command line tool for interacting with the Dyn Traffic Management API.

"""

# TODO
## Persistent session tokens via file cache. Requires changes to dyn.tm.session?
### Publishing changes after multiple invocations of the script.
## A file cache of zones, nodes, services etc. Any of the 'get_all_X'.
### DTRT with one argument specifying a zone and node.
## Cleaned up error messages.

# system libs
import os
import sys
import re
import copy
import itertools
import argparse
import getpass
import yaml
import json

# internal libs
import dyn.tm
from dyn.tm import *
from dyn.tm.accounts import *
from dyn.tm.zones import *
from dyn.tm.session import *

# globals!
srstyles = ['increment', 'epoch', 'day', 'minute']
rectypes = sorted(dyn.tm.zones.RECS.keys())

# parent command class
class DyntmCommand(object):
    '''
    This is a help string right?
    '''

    name = "dyntm"
    desc = "Interact with Dyn Traffic Management API"
    subtitle = "Commands"
    args = [
        {'arg':'--conf', 'type':str, 'dest':'conf', 'help':'Alternate configuration file.'},
        {'arg':'--cust', 'type':str, 'dest':'cust', 'help':'Customer account name for authentication.'},
        {'arg':'--user', 'type':str, 'dest':'user', 'help':'User name for authentication.'},
        {'arg':'--host', 'type':str, 'dest':'host', 'help':'Alternate DynECT API host.'},
        {'arg':'--port', 'type':int, 'dest':'port', 'help':'Alternate DynECT API port.'},
        {'arg':'--proxy-host', 'type':str, 'dest':'proxy_host', 'help':'HTTP proxy host.'},
        {'arg':'--proxy-port', 'type':str, 'dest':'proxy_port', 'help':'HTTP proxy port.'},
        {'arg':'--proxy-user', 'type':str, 'dest':'proxy_user', 'help':'HTTP proxy user name.'},
        {'arg':'--proxy-pass', 'type':str, 'dest':'proxy_pass', 'help':'HTTP proxy password.'},
    ]

    @classmethod
    def parser(cls):
        # setup parser
        ap = argparse.ArgumentParser(prog=cls.name, description=cls.desc)
        for spec in [dict(s) for s in cls.args if s]:
            ap.add_argument(spec.pop('arg'), **spec)
        ap.set_defaults(func=cls.action, command=cls.name)
        # setup subcommand parsers
        if len(cls.__subclasses__()) != 0:
            sub = ap.add_subparsers(title=cls.subtitle)
            for cmd in cls.__subclasses__():
                sub._name_parser_map[cmd.name] = cmd.parser()
        return ap

    @classmethod
    def action(cls, *argv, **opts):
        # parse arguments
        args = cls.parser().parse_args() # (args=argv) TODO list unhashable?
        # read configuration file
        cpath = os.path.expanduser("~/.dyntm.yml")
        conf = {}
        try:
            with open(args.conf or cpath, 'r') as cf:
                conf = yaml.load(cf)
        except IOError as e:
            sys.stderr.write(str(e))
            exit(1)
        # require credentials
        cust = args.cust or conf.get('cust')
        user = args.user or conf.get('user')
        if not user or not cust:
            sys.stderr.write("A customer name and user name must be provided!")
            exit(2)
        # require password
        pswd = conf.get('pass') or getpass("Password for {}/{}".format(cust, user))
        if not pswd:
            sys.stderr.write("A password must be provided!")
            exit(2)
        # maybe more session options
        keys = ['host', 'port', 'proxy_host', 'proxy_port', 'proxy_user', 'proxy_pass', 'proxy_pass']
        opts = { k : v for d in [conf, vars(args)] for k, v in d.iteritems() if k in keys and v is not None }
        # setup session
        try:
            # TODO cache session token! update SessionEngine.connect maybe?
            session = DynectSession(cust, user, pswd, **opts)
        except DynectAuthError as auth:
            print auth.message
            exit(3)
        # dispatch to command
        if args.command != cls.name:
            try:
                inp = { k : v for k, v in vars(args).iteritems() if k not in ['command', 'func'] }
                args.func(**inp)
            except Exception as err:
                # TODO catch specific errors for meaningful exit codes
                print err.message
                exit(4)
        # done!
        exit(0)
    def __init__(self):
        return

# command classes!

### user permissions
class CommandUserPermissions(DyntmCommand):
    name = "perms"
    desc = "List permissions."

    @classmethod
    def action(cls, *rest, **args):
        # get active session
        session = DynectSession.get_session()
        # print each permission available to current session
        for perm in sorted(session.permissions):
            print perm


### update password
class CommandUserPassword(DyntmCommand):
    name = "passwd"
    desc = "Update password."
    args = [
        {'arg': 'password', 'type':str, 'help':'A new password.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get active session
        session = DynectSession.get_session()
        # get password or prompt for it
        newpass = args['password'] or getpass()
        # update password
        session.update_password(newpass)


### list users
class CommandUserList(DyntmCommand):
    name = "users"
    desc = "List users."

    @classmethod
    def action(cls, *rest, **args):
        # TODO verbose output
        # attrs = ['user_name', 'first_name', 'last_name', 'organization',
        #         'email', 'phone', 'address', 'city', 'country', 'fax', 'status']
        # for user in get_users():
        #     print ",".join([getattr(user, attr, "") for attr in attrs])
        for user in get_users():
            print user.user_name


### list zones
class CommandZoneList(DyntmCommand):
    name = "zones"
    desc = "List all the zones available."

    @classmethod
    def action(cls, *rest, **args):
        zones = get_all_zones()
        for zone in zones:
            print zone.fqdn

### create zone
class CommandZoneCreate(DyntmCommand):
    name = "zone-new"
    desc = "Make a new zone."
    args = [
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'Integer TTL.'},
        {'arg':'--timeout', 'dest':'timeout', 'type':int, 'help':'Integer timeout for transfer.'},
        {'arg':'--style', 'dest':'style', 'type':str, 'dest':'serial_style', 'help':'Serial style.','choices': srstyles},
        {'arg':'--file', 'dest':'file', 'type':file, 'help':'File from which to import zone data.'},
        {'arg':'--master', 'dest':'master', 'type':str, 'help':'Master IP from which to transfer zone.'},
        {'arg':'name', 'type':str,'help':'The name of the zone.'},
        {'arg':'contact', 'type':str, 'help':'Administrative contact for this zone (RNAME).'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # figure out zone init arguments
        spec = [ d['dest'] if d.has_key('dest') else d['arg'] for d in cls.args ]
        new = { k : args[k] for k in spec if args[k] is not None }
        # make a new zone
        zone = Zone(**new)
        print zone


### delete zone
class CommandZoneDelete(DyntmCommand):
    name = "zone-delete"
    desc = "Make a new zone."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and delete it!
        zone = Zone(args['zone'])
        zone.delete()


### freeze zone
class CommandZoneFreeze(DyntmCommand):
    name = "freeze"
    desc = "Freeze the given zone."
    args = [
        {'arg':'--ttl', 'type':int, 'help':'Integer TTL.'},
        {'arg':'--timeout', 'type':int, 'help':'Integer timeout for transfer.'},
        {'arg':'--style', 'dest':'serial_style', 'help':'Serial style.','choices': srstyles},
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and freeze it solid
        zone = Zone(args['zone'])
        zone.freeze()

### thaw zone
class CommandZoneThaw(DyntmCommand):
    name = "thaw"
    desc = "Thaw the given zone."
    args = [
        {'arg':'--ttl','type':int, 'help':'Integer TTL.'},
        {'arg':'--timeout', 'type':int, 'help':'Integer timeout for transfer.' },
        {'arg':'--style', 'dest':'serial_style', 'help':'Serial style.','choices': srstyles},
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and thaw it out
        zone = Zone(args['zone'])
        zone.thaw()


### list nodes
class CommandNodeList(DyntmCommand):
    name = "nodes"
    desc = "List nodes in the given zone."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone
        zone = Zone(args['zone'])
        # print all of the zone's nodes
        for node in zone.get_all_nodes():
            print node.fqdn


### delete nodes
class CommandNodeDelete(DyntmCommand):
    name = "node-delete"
    desc = "Delete the given node."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'node', 'type':str, 'help':'The name of the node.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and node
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        # delete the node
        node.delete()


## record commands

# record type specifications for child class generation
# TODO write sensible help strings
rtypes = {
    # 'RTYPE' : [ {'arg':'', 'dest':'','type':str, 'help':''}, ]
    'A' : [
        {'arg':'address', 'type':str, 'help':'An IPv4 address.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'AAAA' : [
        {'arg':'address', 'type':str, 'help':'An IPv6 address.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'ALIAS' : [
        {'arg':'alias', 'type':str, 'help':'A hostname.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'CAA' : [
        {'arg':'flags', 'type':str, 'help':'A byte?.'},
        {'arg':'tag', 'type':str, 'help':'A string representing the name of the property.'},
        {'arg':'value', 'type':str, 'help':'A string representing the value of the property.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'CDNSKEY' : [
        {'arg':'protocol', 'type':int, 'help':'Numeric value for protocol.'},
        {'arg':'public_key', 'type':str, 'help':'The public key for the DNSSEC signed zone.'},
        {'arg':'--algo', 'dest':'algorithm', 'type':int, 'help':'Numeric code of encryption algorithm.'},
        {'arg':'--flags', 'dest':'flags', 'type':int, 'help':'A hostname.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'CDS' : [
        {'arg':'digest', 'type':str, 'help':'Hexadecimal digest string of a DNSKEY.'},
        {'arg':'--keytag', 'dest':'keytag', 'type':int, 'help':'Numeric code of digest mechanism for verification.'},
        {'arg':'--algo', 'dest':'algorithm', 'type':int, 'help':'Numeric code of encryption algorithm.'},
        {'arg':'--digtype', 'dest':'digtype', 'type':int, 'help':'Numeric code of digest mechanism for verification.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'CERT' : [
        {'arg':'format', 'type':int, 'help':'Numeric value of certificate type.'},
        {'arg':'tag', 'type':int, 'help':'Numeric value of public key certificate.'},
        {'arg':'--algo', 'dest':'algorithm', 'type':int, 'help':'Numeric code of encryption algorithm.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'CNAME' : [
        {'arg':'cname', 'type':str, 'help':'A hostname.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'CSYNC' : [
        {'arg':'soa_serial', 'type':int, 'help':'SOA serial to bind to this record.'},
        {'arg':'flags', 'type':str, 'help':'SOA serial to bind to this record.'},
        {'arg':'rectypes', 'type':str, 'help':'SOA serial to bind to this record.', 'nargs':'+'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'DHCID' : [
        {'arg':'digest', 'type':str, 'help':'Base-64 encoded digest of DHCP data.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'DNAME' : [
        {'arg':'cname', 'type':str, 'help':'A hostname.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'DNSKEY' : [
        {'arg':'protocol', 'type':int, 'help':'Numeric value for protocol.'},
        {'arg':'public_key', 'type':str, 'help':'The public key for the DNSSEC signed zone.'},
        {'arg':'--algo', 'dest':'algorithm', 'type':int, 'help':'Numeric code of encryption algorithm.'},
        {'arg':'--flags', 'dest':'flags', 'type':int, 'help':'A hostname.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'DS' : [
        {'arg':'digest', 'type':str, 'help':'Hexadecimal digest string of a DNSKEY.'},
        {'arg':'--keytag', 'dest':'keytag', 'type':int, 'help':'Numeric code of digest mechanism for verification.'},
        {'arg':'--algo', 'dest':'algorithm', 'type':int, 'help':'Numeric code of encryption algorithm.'},
        {'arg':'--digtype', 'dest':'digtype', 'type':int, 'help':'Numeric code of digest mechanism for verification.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'KEY' : [
        {'arg':'algorithm', 'type':int, 'help':'Numeric code of encryption algorithm.'},
        {'arg':'flags', 'type':int, 'help':'Flags!? RTFRFC!'},
        {'arg':'protocol', 'type':int, 'help':'Numeric code of protocol.'},
        {'arg':'public_key', 'type':str, 'help':'The public key..'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'KX' : [
        {'arg':'exchange', 'type':str, 'help':'Hostname of key exchange.'},
        {'arg':'preference', 'type':int, 'help':'Numeric priority of this exchange.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'LOC' : [
        {'arg':'altitude', 'type':str, 'help':''},
        {'arg':'latitude', 'type':str, 'help':''},
        {'arg':'longitude', 'type':str, 'help':''},
        {'arg':'--horiz_pre', 'dest':'horiz_pre','type':str, 'help':''},
        {'arg':'--vert_pre', 'dest':'vert_pre','type':str, 'help':''},
        {'arg':'--size', 'dest':'size','type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'IPSECKEY' : [
        {'arg':'precedence', 'type':str, 'help':''},
        {'arg':'gatetype', 'type':str, 'help':''},
        {'arg':'algorithm', 'type':str, 'help':''},
        {'arg':'gateway', 'type':str, 'help':''},
        {'arg':'public_key', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'MX' : [
        {'arg':'exchange', 'type':str, 'help':''},
        {'arg':'prefernce', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'NAPTR' : [
        {'arg':'order', 'type':str, 'help':''},
        {'arg':'preference', 'type':str, 'help':''},
        {'arg':'services', 'type':str, 'help':''},
        {'arg':'regexp', 'type':str, 'help':''},
        {'arg':'replacement', 'type':str, 'help':''},
        {'arg':'flags', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'PTR' : [
        {'arg':'ptrdname', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'PX' : [
        {'arg':'prefernce', 'type':str, 'help':''},
        {'arg':'map822', 'type':str, 'help':''},
        {'arg':'map400', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'NSAP' : [
        {'arg':'nsap', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'RP' : [
        {'arg':'mbox', 'type':str, 'help':''},
        {'arg':'txtdname', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'NS' : [
        {'arg':'nsdname', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'SOA' : [
        # TODO
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'SPF' : [
        {'arg':'txtdata', 'type':str, 'help':'Some text data.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'SRV' : [
        {'arg':'port', 'type':str, 'help':''},
        {'arg':'priority', 'type':str, 'help':''},
        {'arg':'target', 'type':str, 'help':''},
        {'arg':'weight', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'SSHFP' : [
        {'arg':'algorithm', 'type':str, 'help':''},
        {'arg':'fptype', 'type':str, 'help':''},
        {'arg':'fingerprint', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'TLSA' : [
        {'arg':'cert_usage', 'type':str, 'help':''},
        {'arg':'selector', 'type':str, 'help':''},
        {'arg':'match_type', 'type':str, 'help':''},
        {'arg':'certificate', 'type':str, 'help':''},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
    'TXT' : [
        {'arg':'txtdata', 'type':str, 'help':'Some text data.'},
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL of the record.'},
    ],
}


### create record
class CommandRecordCreate(DyntmCommand):
    name = "record-new"
    desc = "Create record."
    subtitle = "Record Types"
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'node', 'type':str, 'help':'Node on which to create the record.'},
        # could have TTL here but that requires the option to appear before the record type
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and node
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        # figure out record init arguments specific to this command
        spec = [ d['dest'] if d.has_key('dest') else d['arg'] for d in cls.args ]
        new = { k : args[k] for k in spec if args[k] is not None }
        # add a new record on that node
        rec = node.add_record(cls.name, **new)
        # publish the zone
        zone.publish()


# setup record creation command subclass for each record type
rcreate = {}
for rtype in [k for k in sorted(rtypes.keys()) if k not in ['SOA']] :
    opts = copy.deepcopy(rtypes[rtype])
    attr = {
        'name':rtype,
        'args':opts,
        'desc':"Create one {} record.".format(rtype),
    }
    rcreate[rtype] = type("CommandRecordCreate" + rtype, (CommandRecordCreate,), attr)


### list records
class CommandRecordList(DyntmCommand):
    name = "records"
    desc = "Get an existing record."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # context
        zone = Zone(args['zone'])
        # get records
        recs = reduce(lambda x, y: x + y, zone.get_all_records().values())
        # print all records
        for r in sorted(recs, cmp=lambda x, y: cmp(y.fqdn, x.fqdn)) :
            print "{} {} {} {}".format(r._record_id, r.fqdn, r.rec_name.upper(), r.rdata())


### get records
class CommandRecordGet(DyntmCommand):
    name = "record"
    desc = "List records."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'node', 'type':str, 'help':'Node on which the the record appears.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # context
        rtype = cls.name
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        # get set of records
        recs = node.get_all_records_by_type(rtype)
        fields =  ['_record_id'] + [a['dest'] if a.has_key('dest') else a['arg'].strip("-") for a in cls.args]
        found = [r for r in recs if any([re.search(str(args[f]), str(getattr(r, f, ""))) for f in fields if args[f]])]
        # print selected records
        for r in sorted(found, cmp=lambda x, y: cmp(y.fqdn, x.fqdn)) :
            print "{} {} {} {}".format(r._record_id, r.fqdn, r.rec_name.upper(), r.rdata())


rget = {}
for rtype in sorted(rtypes.keys()):
    # tweak args to make them all optional
    opts = copy.deepcopy(rtypes[rtype]) # list(rtypes[rtype])
    opts += [ {'arg':'--id', 'type':int, 'dest':'_record_id', 'help':'Awkward internal record ID'} ]
    for opt in opts:
        if not opt['arg'].startswith('--'):
            opt['arg'] = "--" + opt['arg']
    attr = {
        'name':rtype,
        'args':opts,
        'desc':"List some {} records.".format(rtype),
    }
    rget[rtype] = type("CommandRecordGet" + rtype, (CommandRecordGet,), attr)


### update record
class CommandRecordUpdate(DyntmCommand):
    name = "record-update"
    desc = "Update a record."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'node', 'type':str, 'help':'Node on which the the record appears.'},
    ]
    subtitle = "Record Types"

    @classmethod
    def action(cls, *rest, **args):
        # context
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        rid = args['id']
        # identify target record
        recs = node.get_all_records_by_type(cls.name)
        them = [r for r in recs if str(r._record_id) == str(rid)]
        if len(them) == 0:
            raise Exception("Record {} not found.".format(rid))
        that = them.pop()
        # build update arguments
        fields = [a['dest'] if a.has_key('dest') else a['arg'].strip("-") for a in cls.args]
        # update the record
        for field in fields:
            if args[field]:
                setattr(that, field, args[field])
        # publish the zone
        zone.publish()
        # success
        print that


# setup record update command subclass for each record type
rupdate = {}
for rtype in [k for k in sorted(rtypes.keys())] :
    # tweak args to make them all optional
    opts = copy.deepcopy(rtypes[rtype]) # list(rtypes[rtype])
    for opt in opts:
        if not opt['arg'].startswith('--'):
            opt['arg'] = "--" + opt['arg']
    # require record ID argument
    opts += {'arg':'id', 'type':str, 'help':'The unique numeric ID of the record.'},
    # setup the class attributes
    attr = {
        'name':rtype,
        'args':opts,
        'desc':"Update one {} record.".format(rtype),
    }
    # make the record update subclass
    rupdate[rtype] = type("CommandRecordUpdate" + rtype, (CommandRecordUpdate,), attr)


### delete record
class CommandRecordDelete(DyntmCommand):
    name = "record-delete"
    desc = "Delete a record."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'node', 'type':str, 'help':'Node on which the the record appears.'},
    ]
    subtitle = "Record Types"

    @classmethod
    def action(cls, *rest, **args):
        # context
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        rid = args['id']
        # identify target record
        recs = node.get_all_records_by_type(cls.name)
        them = [r for r in recs if str(r._record_id) == str(rid)]
        if len(them) == 0:
            raise Exception("Record {} not found.".format(rid))
        that = them.pop()
        # delete the record
        that.delete()
        # publish the zone
        zone.publish()
        # success
        print that


# setup record delete command subclass for each record type
rdelete = {}
for rtype in [k for k in sorted(rtypes.keys())] :
    # require record ID argument
    opts = {'arg':'id', 'type':str, 'help':'The unique numeric ID of the record.'},
    # setup the class attributes
    attr = {
        'name':rtype,
        'args':opts,
        'desc':"Update one {} record.".format(rtype),
    }
    # make the record delete subclass
    rdelete[rtype] = type("CommandRecordDelete" + rtype, (CommandRecordDelete,), attr)



## redir commands TODO
## gslb commands TODO
## dsf commands TODO

# main
def dyntm(argv=sys.argv):
    DyntmCommand.action(argv)

# call it if invoked
dyntm(sys.argv[1:])
