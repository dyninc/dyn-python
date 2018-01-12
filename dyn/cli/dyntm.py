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
    name = "general"
    desc = "An abstract command for dyntm."
    args = []
    def __init__(self):
        return
    def parser(self):
        ap = argparse.ArgumentParser(prog=self.name, description=self.desc)
        for spec in [dict(s) for s in self.args if s]:
            ap.add_argument(spec.pop('arg'), **spec)
        ap.set_defaults(func=self.action, command=self.name)
        return ap
    def action(self, *rest, **args):
        pass

# command classes!

## user commands
class CommandUserPermissions(DyntmCommand):
    name = "perms"
    desc = "List permissions."
    def action(self, *rest, **args):
        session = DynectSession.get_session()
        for perm in sorted(session.permissions):
            print perm


class CommandUserPassword(DyntmCommand):
    name = "passwd"
    desc = "Update password."
    args = [
        {'arg': 'password', 'type':str, 'help':'A new password.'},
    ]
    def action(self, *rest, **args):
        newpass = args['password'] or getpass()
        session = DynectSession.get_session()
        session.update_password(newpass)


class CommandUserList(DyntmCommand):
    name = "users"
    desc = "List users."
    def action(self, *rest, **args):
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
    def action(self, *rest, **args):
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
    def action(self, *rest, **args):
        new = { k : v for k, v in args.iteritems() if v is not None }
        zone = Zone(**new)
        print zone


class CommandZoneDelete(DyntmCommand):
    name = "zone-delete"
    desc = "Make a new zone."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
    ]
    def action(self, *rest, **args):
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
    def action(self, *rest, **args):
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
    def action(self, *rest, **args):
        zone = Zone(args['zone'])
        zone.thaw()


class CommandNodeList(DyntmCommand):
    name = "nodes"
    desc = "List nodes in the given zone."
    args = [
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
    ]
    def action(self, *rest, **args):
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
    def action(self, *rest, **args):
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
    def action(self, *rest, **args):
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
        {'arg':'zone', 'type':str, 'help':'The name of the zone.'},
        {'arg':'node', 'type':str, 'help':'Node on which to create the record.'},
        {'arg':'rtype', 'type':str, 'help':'Record type.', 'metavar': 'rtype', 'choices': rectypes},
        {'arg':'rdata', 'type':str, 'help':'Record data.', 'nargs':'+'},
    ]
    def action(self, *rest, **args):
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        print args['rdata']
        rec = node.add_record(args['rtype'], *args['rdata'])
        print rec
        zone.publish()

        
## redir commands TODO
## gslb commands TODO
## dsf commands TODO

# main
def dyntm(argv=sys.argv):
    # some context
    cpath = os.path.expanduser("~/.dyntm.yml")
    # setup subcommands
    cmds = {c.name : c() for c in DyntmCommand.__subclasses__() }
    # setup argument parser
    ap = argparse.ArgumentParser(description='Interact with Dyn Traffic Management API')
    ap.add_argument('--conf', type=str, dest='conf', help='Alternate configuration file.')
    ap.add_argument('--cust', type=str, dest='cust', help='Customer account name for authentication.')
    ap.add_argument('--user', type=str, dest='user', help='User name for authentication.')
    ap.add_argument('--host', type=str, dest='host', help='Alternate DynECT API host.')
    ap.add_argument('--port', type=int, dest='port', help='Alternate DynECT API port.')
    ap.add_argument('--proxy-host', type=str, dest='proxy_host', help='HTTP proxy host.')
    ap.add_argument('--proxy-port', type=str, dest='proxy_port', help='HTTP proxy port.')
    ap.add_argument('--proxy-user', type=str, dest='proxy_user', help='HTTP proxy user name.')
    ap.add_argument('--proxy-pass', type=str, dest='proxy_pass', help='HTTP proxy password.')
    # setup parsers for commands
    sub = ap.add_subparsers(title="command")
    for cmd in cmds.values():
        sub._name_parser_map[cmd.name] = cmd.parser()
    # parse arguments
    args, rest = ap.parse_known_args(args=argv)
    # read configuration file
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
    try:
        inp = { k : v for k, v in vars(args).iteritems() if k not in ['command', 'func'] }
        args.func(**inp)
    except Exception as err:
        print err.message
        exit(4)
    # done!
    exit(0)

# call it if invoked
dyntm(sys.argv[1:])
