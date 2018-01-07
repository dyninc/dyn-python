#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A command line tool for interacting with the Dyn Traffic Management API.

"""

# system libs
import os, sys
import argparse, getpass
import yaml, json

# internal libs
import dyn.tm
from dyn.tm import *
from dyn.tm.zones import *
from dyn.tm.session import *

# globals!
serstyle =  ['increment', 'epoch', 'day', 'minute']

# parent command class
class DyntmCommand(object):
    name = "general"
    desc = "An abstract command for dyntm."
    args = { }
    def __init__(self):
        return
    def parser(self):
        ap = argparse.ArgumentParser(prog=self.name, description=self.desc)
        for key, opt in self.args.iteritems():
            ap.add_argument(key, **opt)
        ap.set_defaults(func=self.action, command=self.name)
        return ap
    def action(self, *rest, **args):
        pass

# command classes!

## user commands
class CommandListPermissions(DyntmCommand):
    name = "perms"
    desc = "List permissions."
    def action(self, *rest, **args):
        session = DynectSession.get_session()
        for perm in sorted(session.permissions):
            print perm


class CommandUpdatePassword(DyntmCommand):
    name = "passwd"
    desc = "Update password."
    args = {
        'password' : {'type':str, 'help':'A new password.'},
    }
    def action(self, *rest, **args):
        newpass = args['password'] or getpass()
        session = DynectSession.get_session()
        session.update_password(newpass)


## zone commands
class CommandListZones(DyntmCommand):
    name = "zones"
    desc = "List all the zones available."
    def action(self, *rest, **args):
        zones = get_all_zones()
        for zone in zones:
            print zone.fqdn


class CommandCreateZone(DyntmCommand):
    name = "zone-create"
    desc = "Make a new zone."
    args = {
        'name'      : {'type':str, 'help':'The name of the zone.', 'metavar':'ZONE-NAME'},
        'contact'   : {'type':str, 'help':'Administrative contact for this zone (RNAME).'},
        '--ttl'     : {'type':int, 'help':'Integer TTL.'},
        '--timeout' : {'type':int, 'help':'Integer timeout for transfer.' },
        '--style'   : {'dest':'serial_style', 'help':'Serial style.','choices': serstyle },
        '--file'    : {'type':file, 'help':'File from which to import zone data.'},
        '--master'  : {'type':str, 'help':'Master IP from which to transfer zone.' },
    }
    def action(self, *rest, **args):
        new = { k : v for k, v in args.iteritems() if v is not None }
        zone = Zone(**new)
        print zone


class CommandDeleteZone(DyntmCommand):
    name = "zone-delete"
    desc = "Make a new zone."
    args = {
        'name'      : {'type':str, 'help':'The name of the zone.', 'metavar':'ZONE-NAME'},
    }
    def action(self, *rest, **args):
        zone = Zone(args['name'])
        zone.delete()


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
