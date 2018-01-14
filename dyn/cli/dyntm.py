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
import os, sys
import argparse, getpass
import yaml, json
import itertools

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
    name = "dyntm"
    desc = "Interact with Dyn Traffic Management API"
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
            sub = ap.add_subparsers(title="Commands")
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
                print err
                # print err.message
                exit(4)
        # done!
        exit(0)
    def __init__(self):
        return

# command classes!

## user commands
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


## zone commands
class CommandZoneList(DyntmCommand):
    name = "zones"
    desc = "List all the zones available."

    @classmethod
    def action(cls, *rest, **args):
        zones = get_all_zones()
        for zone in zones:
            print zone.fqdn


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
class CommandRecordList(DyntmCommand):
    name = "records"
    desc = "List records on the given zone."
    args = [
        {'arg':'--node', 'type':str, 'help':'Limit list to records appearing on the given node.'},
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone
        zone = Zone(args['zone'])
        # maybe limit list to a given node
        thing = zone.get_node(args['node']) if args['node'] else zone
        # combine awkward rtype lists
        records = reduce(lambda r, n: r + n, thing.get_all_records().values())
        # print selected records
        for record in records:
            print "{} {} {}".format(record.fqdn, record.rec_name.upper(), record.rdata())


class CommandRecordCreate(DyntmCommand):
    name = "record-new"
    desc = "Create record."
    args = [
        {'arg':'--ttl', 'dest':'ttl', 'type':int, 'help':'TTL for the new record.'},
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'node', 'type':str, 'help':'Node on which to create the record.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # figure out record init arguments specific to this command
        spec = [ d['dest'] if d.has_key('dest') else d['arg'] for d in cls.args ]
        new = { k : args[k] for k in spec if args[k] is not None }
        # get the zone and node
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        # add a new record on that node
        rec = node.add_record(cls.name, ttl=args['ttl'], **new)
        # publish the zone TODO
        zone.publish()

### TODO define these record classes dynamically
class CommandRecordCreateA(CommandRecordCreate):
    name = "A"
    desc = "Create an A record."
    args = [
        {'arg':'address', 'type':str, 'help':'An IPv4 address.'},
    ]


class CommandRecordCreateAAAA(CommandRecordCreate):
    name = "AAAA"
    desc = "Create an AAAA record."
    args = [
        {'arg':'address', 'type':str, 'help':'An IPv6 address.'},
    ]


class CommandRecordCreateTXT(CommandRecordCreate):
    name = "TXT"
    desc = "Create a TXT record."
    args = [
        {'arg':'txtdata', 'type':str, 'help':'Some text data.'},
    ]

    
class CommandRecordCreateCNAME(CommandRecordCreate):
    name = "CNAME"
    desc = "Create a CNAME record."
    args = [
        {'arg':'cname', 'type':str, 'help':'A hostname.'},
    ]

    
class CommandRecordCreateCNAME(CommandRecordCreate):
    name = "ALIAS"
    desc = "Create an ALIAS record."
    args = [
        {'arg':'alias', 'type':str, 'help':'A hostname.'},
    ]

class CommandRecordCreateDNSKEY(CommandRecordCreate):
    name = "DNSKEY"
    desc = "Create a DNSKEY record."
    args = [
        {'arg':'protocol', 'type':int, 'help':'Numeric value for protocol.'},
        {'arg':'public_key', 'type':str, 'help':'The public key for the DNSSEC signed zone.'},
        {'arg':'--algo', 'dest':'algorithm', 'type':int, 'help':'A hostname.'},
        {'arg':'--flags', 'dest':'algorithm', 'type':int, 'help':'A hostname.'},
    ]

    
class CommandRecordCreateCDNSKEY(CommandRecordCreate):
    name = "CDNSKEY"
    desc = "Create a CDNSKEY record."
    args = [
        {'arg':'protocol', 'type':int, 'help':'Numeric value for protocol.'},
        {'arg':'public_key', 'type':str, 'help':'The public key for the DNSSEC signed zone.'},
        {'arg':'--algo', 'dest':'algorithm', 'type':int, 'help':'A hostname.'},
        {'arg':'--flags', 'dest':'algorithm', 'type':int, 'help':'A hostname.'},
    ]




## redir commands TODO
## gslb commands TODO
## dsf commands TODO

# main
def dyntm(argv=sys.argv):
    DyntmCommand.action(argv)

# call it if invoked
dyntm(sys.argv[1:])
