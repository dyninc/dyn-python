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
                print err.message
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
        session = DynectSession.get_session()
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
        newpass = args['password'] or getpass()
        session = DynectSession.get_session()
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
        {'arg':'name', 'type':str,'help':'The name of the zone.'},
        {'arg':'contact', 'type':str, 'help':'Administrative contact for this zone (RNAME).'},
        {'arg':'--ttl', 'type':int, 'help':'Integer TTL.'},
        {'arg':'--timeout', 'type':int, 'help':'Integer timeout for transfer.'},
        {'arg':'--style', 'type':str, 'dest':'serial_style', 'help':'Serial style.','choices': srstyles},
        {'arg':'--file', 'type':file, 'help':'File from which to import zone data.'},
        {'arg':'--master', 'type':str, 'help':'Master IP from which to transfer zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        new = { k : v for k, v in args.iteritems() if v is not None }
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
        zone = Zone(args['zone'])
        zone.delete()


class CommandZoneFreeze(DyntmCommand):
    name = "freeze"
    desc = "Freeze the given zone."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'--ttl', 'type':int, 'help':'Integer TTL.'},
        {'arg':'--timeout', 'type':int, 'help':'Integer timeout for transfer.'},
        {'arg':'--style', 'dest':'serial_style', 'help':'Serial style.','choices': srstyles},
    ]

    @classmethod
    def action(cls, *rest, **args):
        zone = Zone(args['zone'])
        zone.freeze()


class CommandZoneThaw(DyntmCommand):
    name = "thaw"
    desc = "Thaw the given zone."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'--ttl','type':int, 'help':'Integer TTL.'},
        {'arg':'--timeout', 'type':int, 'help':'Integer timeout for transfer.' },
        {'arg':'--style', 'dest':'serial_style', 'help':'Serial style.','choices': srstyles},
    ]

    @classmethod
    def action(cls, *rest, **args):
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
        zone = Zone(args['name'])
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
        zone = Zone(args['name'])
        node = zone.get_node(args['node'])
        node.delete()


## record commands
class CommandRecordList(DyntmCommand):
    name = "records"
    desc = "List records on the given zone."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'--node', 'type':str, 'help':'Limit list to records appearing on the given node.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        zone = Zone(args['zone'])
        if args.get('node', None) is not None:
            name = None if args['node'] == zone.name else args['node']
            node = zone.get_node(name)
            recs = reduce(lambda r, n: r + n, node.get_all_records().values())
        else:
            recs = reduce(lambda r, n: r + n, zone.get_all_records().values())
            for record in recs:
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
        keys = [ d['arg'] if d.has_key('dest') else d['arg'] for d in cls.args ]
        new = { key : args[key] for key in keys }
        # get zone and node
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        # add a new record on that node
        rec = node.add_record(cls.name, ttl=args['ttl'], **new)
        # publish the zone TODO
        zone.publish()


class CommandRecordCreateA(CommandRecordCreate):
    name = "A"
    desc = "Create an A record."
    args = [
        {'arg':'address', 'type':str, 'help':'An IPv4 address.'},
    ]


class CommandRecordCreateTXT(CommandRecordCreate):
    name = "TXT"
    desc = "Create a TXT record."
    args = [
        {'arg':'txtdata', 'type':str, 'help':'Some text data.'},
    ]




## redir commands TODO
## gslb commands TODO
## dsf commands TODO

# main
def dyntm(argv=sys.argv):
    DyntmCommand.action(argv)

# call it if invoked
dyntm(sys.argv[1:])
