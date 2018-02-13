#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A command line tool for interacting with the Dyn Traffic Management API.

"""

# TODO
# A file cache of zones, nodes, services etc. Any of the 'get_all_X'.
# DTRT with one argument specifying a zone and node.
# Better documentation, help messages, and error messages.

# system libs
import os
import sys
import re
import copy
import argparse
import shlex
import subprocess
import functools
import getpass
import yaml
import json

# internal libs
import dyn.tm
from dyn.tm.accounts import get_users
from dyn.tm.zones import Zone, get_all_zones
from dyn.tm.zones import SecondaryZone, get_all_secondary_zones
from dyn.tm.session import DynectSession
from dyn.tm.errors import DynectError, DynectAuthError

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
        {'arg': '--conf', 'type': str, 'dest': 'conf',
            'help': 'Alternate configuration file.'},
        {'arg': '--cust', 'type': str, 'dest': 'cust',
            'help': 'Customer account name for authentication.'},
        {'arg': '--user', 'type': str, 'dest': 'user',
            'help': 'User name for authentication.'},
        {'arg': '--host', 'type': str, 'dest': 'host',
            'help': 'Alternate DynECT API host.'},
        {'arg': '--port', 'type': int, 'dest': 'port',
            'help': 'Alternate DynECT API port.'},
        {'arg': '--proxy-host', 'type': str,
            'dest': 'proxy_host', 'help': 'HTTP proxy host.'},
        {'arg': '--proxy-port', 'type': str,
            'dest': 'proxy_port', 'help': 'HTTP proxy port.'},
        {'arg': '--proxy-user', 'type': str, 'dest': 'proxy_user',
            'help': 'HTTP proxy user name.'},
        {'arg': '--proxy-pass', 'type': str,
            'dest': 'proxy_pass', 'help': 'HTTP proxy password.'},
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
    def config(cls, conf):
        # maybe generate an empty configuration file
        cpath = os.path.expanduser(conf)
        if not os.path.exists(cpath):
            creds = {"customer": "", "user": "", "password": ""}
            with open(cpath, 'w') as cf:
                yaml.dump(creds, cf, default_flow_style=False)
        # read configuration file and return config dict
        with open(cpath, 'r') as cf:
            return yaml.load(cf)

    @classmethod
    def session(cls, auth=False, **kwargs):
        # return session singleton if it exists already
        session = DynectSession.get_session()
        if session and not auth:
            return session
        # require credentials
        cust = kwargs.get('customer')
        user = kwargs.get('user')
        if not user or not cust:
            msg = "A customer name and user name must be provided!\n"
            raise ValueError(msg)
        # run system command to fetch password if possible
        password = None
        passcmd = kwargs.get('passcmd')
        if passcmd:
            toks = shlex.split(passcmd)
            proc = subprocess.Popen(toks, stdout=subprocess.PIPE)
            if proc.wait() == 0:
                output = proc.stdout.readline().decode('UTF-8')
                password = output.strip()
        else:
            password = kwargs.get('password')
        # or get password interactively if practical
        if not password and sys.stdout.isatty():
            prompt = "Password for {}/{} > ".format(cust, user)
            password = getpass.getpass(prompt)
        # require a password
        if not password:
            raise ValueError("A password must be provided!")
        # setup session
        token = None
        tpath = os.path.expanduser("~/.dyntm_{}_{}".format(cust, user))
        # maybe load cached session token
        if os.path.isfile(tpath):
            with open(tpath, 'r') as tf:
                token = tf.readline()
        # figure session fields
        keys = ['host', 'port', 'proxy_host', 'proxy_port',
                'proxy_user', 'proxy_pass']
        opts = {k: v for k, v in kwargs.items()
                if k in keys and v is not None}
        # create session
        if not token or auth:
            # authenticate
            session = DynectSession(cust, user, password, **opts)
            session.authenticate()
        else:
            # maybe use cached session token
            session = DynectSession(cust, user, password,
                                    auto_auth=False, **opts)
            session._token = token
        # record session token for later use
        if session._token and session._token != token:
            with open(tpath, 'w') as tf:
                tf.write(session._token)
        # return the session handle
        return session

    @classmethod
    def action(cls, *argv, **opts):
        # parse arguments
        args = vars(cls.parser().parse_args())
        # get configuration
        try:
            conf = cls.config(args.get('conf') or "~/.dyntm.yml")
        except Exception as e:
            msg = "Configuration problem!\n{}\n".format(e.message or str(e))
            sys.stderr.write(msg)
            sys.exit(1)
        # command line arguments take precedence over config
        auth = ['customer', 'user', 'password', 'passcmd', 'host', 'port',
                'proxy_host', 'proxy_port', 'proxy_user', 'proxy_pass']
        plan = {k: args.get(k) or conf.get(k) for k in auth}
        # get session
        try:
            cls.session(auth=False, **plan)
        except Exception as e:
            msg = "Authentication problem!\n{}\n".format(str(e))
            sys.stderr.write(msg)
            sys.exit(2)
        # figure out arguments for subcommand
        mine = auth + ['command', 'func']
        inp = {k: v for k, v in args.items() if k not in mine}
        # run the command, reauthenticate if needed
        func = args.get('func')
        command = args.get('command')
        context = "{} {}".format(command, str(inp))
        try:
            try:
                func(**inp)
            except DynectAuthError as err:
                cls.session(auth=True, **plan)
                func(**inp)
        except DynectError as err:
            msg = "{}\n{}\n".format(context, str(err))
            sys.stderr.write(msg)
            exit(3)
        except Exception as err:
            msg = "{}\n{}\n".format(context, str(err))
            sys.stderr.write(msg)
            exit(4)
        # done!
        exit(0)

    def __init__(self):
        return

# command classes!

# user permissions


class CommandUserPermissions(DyntmCommand):
    name = "perms"
    desc = "List permissions."

    @classmethod
    def action(cls, *rest, **args):
        # get active session
        session = cls.session()
        # print each permission available to current session
        for perm in sorted(session.permissions):
            sys.stdout.write("{}\n".format(str(perm)))

# log out


class CommandUserLogOut(DyntmCommand):
    name = "logout"
    desc = "Log out of the current session."

    @classmethod
    def action(cls, *rest, **args):
        # get active session and log out
        session = cls.session()
        session.log_out()


# update password
class CommandUserPassword(DyntmCommand):
    name = "passwd"
    desc = "Update password."
    args = [
        {'arg': 'password', 'type': str,
         'help': 'A new password.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get active session
        session = cls.session()
        # get password or prompt for it
        newpass = args['password'] or getpass()
        # update password
        session.update_password(newpass)


# list users
class CommandUserList(DyntmCommand):
    name = "users"
    desc = "List users."

    @classmethod
    def action(cls, *rest, **args):
        # TODO verbose output
        # attrs = ['user_name', 'email', 'phone', 'organization',
        #         'first_name', 'last_name',
        #         'address', 'city', 'country', 'fax', 'status']
        # for user in get_users():
        #     print ",".join([getattr(user, attr, "") for attr in attrs])
        for user in get_users():
            sys.stdout.write("{}\n".format(user.user_name))


# list zones
class CommandZoneList(DyntmCommand):
    name = "zones"
    desc = "List all the zones available."

    @classmethod
    def action(cls, *rest, **args):
        zones = get_all_zones()
        for zone in zones:
            sys.stdout.write("{}\n".format(zone.name))


# list primary zones
class CommandZonePrimaryList(DyntmCommand):
    name = "primary"
    desc = "List all the primary zones available."

    @classmethod
    def action(cls, *rest, **args):
        zones = get_all_zones()
        secondary = get_all_secondary_zones()
        primary = [z for z in zones
                   if z.name not in [s.zone for s in secondary]]
        for zone in primary:
            sys.stdout.write("{}\n".format(zone.name))


# list secondary zones
class CommandZoneSecondaryList(DyntmCommand):
    name = "secondary"
    desc = "List all the secondary zones available."

    @classmethod
    def action(cls, *rest, **args):
        secondary = get_all_secondary_zones()
        for zone in secondary:
            sys.stdout.write("{}\n".format(zone.zone))


# create zone
class CommandZoneCreate(DyntmCommand):
    name = "zone-new"
    desc = "Make a new zone."
    args = [
        {'arg': '--ttl', 'dest': 'ttl', 'type': int,
         'help': 'Integer TTL.'},
        {'arg': '--timeout', 'dest': 'timeout', 'type': int,
         'help': 'Integer timeout for transfer.'},
        {'arg': '--style', 'type': str, 'dest': 'serial_style',
         'help': 'Serial style.', 'choices': srstyles},
        {'arg': '--file', 'dest': 'file', 'type': str,
         'help': 'File from which to import zone data.'},
        {'arg': '--master', 'dest': 'master', 'type': str,
         'help': 'Master IP from which to transfer zone.'},
        {'arg': 'name', 'type': str,
         'help': 'The name of the zone.'},
        {'arg': 'contact', 'type': str,
         'help': 'Administrative contact for this zone (RNAME).'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # figure out zone init arguments
        spec = [d['dest'] if 'dest' in d else d['arg'] for d in cls.args]
        new = {k: args[k] for k in spec if args[k] is not None}
        # make a new zone
        zone = Zone(**new)
        sys.stdout.write("{}".format(str(zone)))


# create secondary zone
class CommandSecondaryZoneCreate(DyntmCommand):
    name = "secondary-new"
    desc = "Make a new secondary zone."
    args = [
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
        {'arg': 'masters', 'type': str, 'nargs': '+',
         'help': 'IPs of master nameservers of the zone.'},
        {'arg': '--contact', 'type': str, 'dest': 'contact_nickname',
         'help': 'Administrative contact for this zone (RNAME).'},
        {'arg': '--tsig-key', 'type': str, 'dest': 'tsig_key_name',
         'help': 'Name of TSIG key to use when communicating with masters.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # figure out zone init arguments
        spec = [d['dest'] if 'dest' in d else d['arg'] for d in cls.args]
        new = {k: args[k] for k in spec if args[k] is not None}
        # make a new secondary zone
        zone = SecondaryZone(**new)
        sys.stdout.write("{}".format(str(zone)))


# delete zone
class CommandZoneDelete(DyntmCommand):
    name = "zone-delete"
    desc = "Make a new zone."
    args = [
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and delete it!
        zone = Zone(args['zone'])
        zone.delete()


# freeze zone
class CommandZoneFreeze(DyntmCommand):
    name = "freeze"
    desc = "Freeze the given zone."
    args = [
        {'arg': '--ttl', 'type': int,
         'help': 'Integer TTL.'},
        {'arg': '--timeout', 'type': int,
         'help': 'Integer timeout for transfer.'},
        {'arg': '--style', 'dest': 'serial_style',
         'help': 'Serial style.', 'choices': srstyles},
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and freeze it solid
        zone = Zone(args['zone'])
        zone.freeze()


# thaw zone
class CommandZoneThaw(DyntmCommand):
    name = "thaw"
    desc = "Thaw the given zone."
    args = [
        {'arg': '--ttl', 'type': int,
         'help': 'Integer TTL.'},
        {'arg': '--timeout', 'type': int,
         'help': 'Integer timeout for transfer.'},
        {'arg': '--style', 'dest': 'serial_style',
         'help': 'Serial style.', 'choices': srstyles},
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and thaw it out
        zone = Zone(args['zone'])
        zone.thaw()


# list nodes
class CommandNodeList(DyntmCommand):
    name = "nodes"
    desc = "List nodes in the given zone."
    args = [
        {'arg': 'zone', 'type': str, 'help': 'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone
        zone = Zone(args['zone'])
        # output all of the zone's nodes
        for node in zone.get_all_nodes():
            sys.stdout.write("{}\n".format(node.fqdn))


# delete nodes
class CommandNodeDelete(DyntmCommand):
    name = "node-delete"
    desc = "Delete the given node."
    args = [
        {'arg': 'zone', 'type': str, 'help': 'The name of the zone.'},
        {'arg': 'node', 'type': str, 'help': 'The name of the node.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and node
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        # delete the node
        node.delete()


# zone changes
class CommandZoneChanges(DyntmCommand):
    name = "changes"
    desc = "List pending changes to a zone."
    args = [
        {'arg': 'zone', 'type': str, 'help': 'The name of the zone.'},
        {'arg': 'note', 'type': str, 'nargs': '?',
            'help': 'A note associated with this change.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone
        zone = Zone(args['zone'])
        for change in zone.get_changes():
            fqdn = change["fqdn"]
            ttl = change["ttl"]
            rtype = change["rdata_type"]
            rdata = change["rdata"].get("rdata_{}".format(rtype.lower()), {})
            msg = "{} {} {} {}\n".format(fqdn, rtype, ttl, json.dumps(rdata))
            sys.stdout.write(msg)


# zone publish
class CommandZonePublish(DyntmCommand):
    name = "publish"
    desc = "Publish pending changes to a zone."
    args = [
        {'arg': 'zone', 'type': str, 'help': 'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone
        zone = Zone(args['zone'])
        zone.publish(notes=args.get('note', None))


# zone change reset
class CommandZoneChangeDiscard(DyntmCommand):
    name = "discard"
    desc = "Discard pending changes to a zone."
    args = [
        {'arg': 'zone', 'type': str, 'help': 'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone
        zone = Zone(args['zone'])
        zone.discard_changes()

# record commands

# record type specifications for child class generation


# TODO write sensible help strings
rtypes = {
    # 'RTYPE' : [ {'arg':'', 'dest':'','type':str, 'help':''}, ]
    'A': [
        {'arg': 'address', 'type': str,
         'help': 'An IPv4 address.'},
    ],
    'AAAA': [
        {'arg': 'address', 'type': str,
         'help': 'An IPv6 address.'},
    ],
    'ALIAS': [
        {'arg': 'alias', 'type': str,
         'help': 'A hostname.'},
    ],
    'CAA': [
        {'arg': 'flags', 'type': str,
         'help': 'A byte?.'},
        {'arg': 'tag', 'type': str,
         'help': 'A string representing the name of the property.'},
        {'arg': 'value', 'type': str,
         'help': 'A string representing the value of the property.'},
    ],
    'CDNSKEY': [
        {'arg': 'protocol', 'type': int,
         'help': 'Numeric value for protocol.'},
        {'arg': 'public_key', 'type': str,
            'help': 'The public key for the DNSSEC signed zone.'},
        {'arg': '--algo', 'dest': 'algorithm', 'type': int,
            'help': 'Numeric code of encryption algorithm.'},
        {'arg': '--flags', 'dest': 'flags', 'type': int,
         'help': 'A hostname.'},
    ],
    'CDS': [
        {'arg': 'digest', 'type': str,
         'help': 'Hexadecimal digest string of a DNSKEY.'},
        {'arg': '--keytag', 'dest': 'keytag', 'type': int,
         'help': 'Numeric code of digest mechanism for verification.'},
        {'arg': '--algo', 'dest': 'algorithm', 'type': int,
         'help': 'Numeric code of encryption algorithm.'},
        {'arg': '--digtype', 'dest': 'digtype', 'type': int,
         'help': 'Numeric code of digest mechanism for verification.'},
    ],
    'CERT': [
        {'arg': 'format', 'type': int,
         'help': 'Numeric value of certificate type.'},
        {'arg': 'tag', 'type': int,
         'help': 'Numeric value of public key certificate.'},
        {'arg': '--algo', 'dest': 'algorithm', 'type': int,
            'help': 'Numeric code of encryption algorithm.'},
    ],
    'CNAME': [
        {'arg': 'cname', 'type': str, 'help': 'A hostname.'},
    ],
    'CSYNC': [
        {'arg': 'soa_serial', 'type': int,
         'help': 'SOA serial to bind to this record.'},
        {'arg': 'flags', 'type': str,
         'help': 'SOA serial to bind to this record.'},
        {'arg': 'rectypes', 'type': str,
         'help': 'SOA serial to bind to this record.', 'nargs': '+'},
    ],
    'DHCID': [
        {'arg': 'digest', 'type': str,
         'help': 'Base-64 encoded digest of DHCP data.'},
    ],
    'DNAME': [
        {'arg': 'cname', 'type': str,
         'help': 'A hostname.'},
    ],
    'DNSKEY': [
        {'arg': 'protocol', 'type': int,
         'help': 'Numeric value for protocol.'},
        {'arg': 'public_key', 'type': str,
         'help': 'The public key for the DNSSEC signed zone.'},
        {'arg': '--algo', 'dest': 'algorithm', 'type': int,
         'help': 'Numeric code of encryption algorithm.'},
        {'arg': '--flags', 'dest': 'flags', 'type': int,
         'help': 'A hostname.'},
    ],
    'DS': [
        {'arg': 'digest', 'type': str,
         'help': 'Hexadecimal digest string of a DNSKEY.'},
        {'arg': '--keytag', 'dest': 'keytag', 'type': int,
         'help': 'Numeric code of digest mechanism for verification.'},
        {'arg': '--algo', 'dest': 'algorithm', 'type': int,
         'help': 'Numeric code of encryption algorithm.'},
        {'arg': '--digtype', 'dest': 'digtype', 'type': int,
         'help': 'Numeric code of digest mechanism for verification.'},
    ],
    'KEY': [
        {'arg': 'algorithm', 'type': int,
         'help': 'Numeric code of encryption algorithm.'},
        {'arg': 'flags', 'type': int,
         'help': 'Flags!? RTFRFC!'},
        {'arg': 'protocol', 'type': int,
         'help': 'Numeric code of protocol.'},
        {'arg': 'public_key', 'type': str,
         'help': 'The public key..'},
    ],
    'KX': [
        {'arg': 'exchange', 'type': str,
         'help': 'Hostname of key exchange.'},
        {'arg': 'preference', 'type': int,
         'help': 'Numeric priority of this exchange.'},
    ],
    'LOC': [
        {'arg': 'altitude', 'type': str,
         'help': ''},
        {'arg': 'latitude', 'type': str,
         'help': ''},
        {'arg': 'longitude', 'type': str,
         'help': ''},
        {'arg': '--horiz_pre', 'dest': 'horiz_pre', 'type': str,
         'help': ''},
        {'arg': '--vert_pre', 'dest': 'vert_pre', 'type': str,
         'help': ''},
        {'arg': '--size', 'dest': 'size', 'type': str,
         'help': ''},
    ],
    'IPSECKEY': [
        {'arg': 'precedence', 'type': str,
         'help': ''},
        {'arg': 'gatetype', 'type': str,
         'help': ''},
        {'arg': 'algorithm', 'type': str,
         'help': ''},
        {'arg': 'gateway', 'type': str,
         'help': ''},
        {'arg': 'public_key', 'type': str,
         'help': ''},
    ],
    'MX': [
        {'arg': 'exchange', 'type': str,
         'help': ''},
        {'arg': 'prefernce', 'type': str,
         'help': ''},
    ],
    'NAPTR': [
        {'arg': 'order', 'type': str,
         'help': ''},
        {'arg': 'preference', 'type': str,
         'help': ''},
        {'arg': 'services', 'type': str,
         'help': ''},
        {'arg': 'regexp', 'type': str,
         'help': ''},
        {'arg': 'replacement', 'type': str,
         'help': ''},
        {'arg': 'flags', 'type': str,
         'help': ''},
    ],
    'PTR': [
        {'arg': 'ptrdname', 'type': str,
         'help': ''},
    ],
    'PX': [
        {'arg': 'prefernce', 'type': str,
         'help': ''},
        {'arg': 'map822', 'type': str,
         'help': ''},
        {'arg': 'map400', 'type': str,
         'help': ''},
    ],
    'NSAP': [
        {'arg': 'nsap', 'type': str,
         'help': ''},
    ],
    'RP': [
        {'arg': 'mbox', 'type': str,
         'help': ''},
        {'arg': 'txtdname', 'type': str,
         'help': ''},
    ],
    'NS': [
        {'arg': 'nsdname', 'type': str,
         'help': ''},
    ],
    'SOA': [
        # TODO
    ],
    'SPF': [
        {'arg': 'txtdata', 'type': str,
         'help': 'Some text data.'},
    ],
    'SRV': [
        {'arg': 'port', 'type': str,
         'help': ''},
        {'arg': 'priority', 'type': str,
         'help': ''},
        {'arg': 'target', 'type': str,
         'help': ''},
        {'arg': 'weight', 'type': str,
         'help': ''},
    ],
    'SSHFP': [
        {'arg': 'algorithm', 'type': str,
         'help': ''},
        {'arg': 'fptype', 'type': str,
         'help': ''},
        {'arg': 'fingerprint', 'type': str,
         'help': ''},
    ],
    'TLSA': [
        {'arg': 'cert_usage', 'type': str,
         'help': ''},
        {'arg': 'selector', 'type': str,
         'help': ''},
        {'arg': 'match_type', 'type': str,
         'help': ''},
        {'arg': 'certificate', 'type': str,
         'help': ''},
    ],
    'TXT': [
        {'arg': 'txtdata', 'type': str, 'help':
         'Some text data.'},
    ],
}


# create record
class CommandRecordCreate(DyntmCommand):
    name = "record-new"
    desc = "Create record."
    subtitle = "Record Types"
    args = [
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
        {'arg': 'node', 'type': str,
         'help': 'Node on which to create the record.'},
        {'arg': '--publish', 'type': bool,
         'help': 'Zone should be published immediately.'},
        # MAYBE have TTL here instead
    ]

    @classmethod
    def action(cls, *rest, **args):
        # get the zone and node
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        # figure out record init arguments specific to this command
        spec = [d['dest'] if 'dest' in d else d['arg'].strip('-')
                for d in cls.args]
        new = {k: args[k] for k in spec if args[k] is not None}
        # add a new record on that node
        rec = node.add_record(cls.name, **new)
        # publish the zone
        if args['publish']:
            zone.publish()
        # output the new record
        sys.stdout.write("{}\n".format(rec))


# setup record creation command subclass for each record type
rcreate = {}
for rtype in [k for k in sorted(rtypes.keys()) if k not in ['SOA']]:
    opts = copy.deepcopy(rtypes[rtype])
    opts += [{'arg': '--ttl', 'dest': 'ttl', 'type': int,
              'help': 'TTL of the record.'}]
    attr = {
        'name': rtype,
        'args': opts,
        'desc': "Create one {} record.".format(rtype),
    }
    rcreate[rtype] = type("CommandRecordCreate" + rtype,
                          (CommandRecordCreate,), attr)


# list records
class CommandRecordList(DyntmCommand):
    name = "records"
    desc = "Get an existing record."
    args = [
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # context
        zone = Zone(args['zone'])
        # get records
        recs = functools.reduce(
            lambda x, y: x + y, zone.get_all_records().values())
        # output all records
        for r in sorted(recs, key=lambda x: x.fqdn):
            rtype = r.rec_name.upper()
            rdata = json.dumps(dyn.tm.records.DNSRecord.rdata(r))
            sys.stdout.write("{} {} {} {} {}\n".format(
                r.fqdn, rtype, r._record_id, r.ttl, rdata))


# get records
class CommandRecordGet(DyntmCommand):
    name = "record"
    desc = "List records."
    args = [
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
        {'arg': 'node', 'type': str,
         'help': 'Node on which the the record appears.'},
    ]

    @classmethod
    def action(cls, *rest, **args):
        # context
        rtype = cls.name
        zone = Zone(args['zone'])
        node = zone.get_node(args['node'])
        # get set of records
        recs = node.get_all_records_by_type(rtype)
        fields = ['_record_id']
        fields.extend([a['dest']
                       if 'dest' in a else a['arg'].strip('-')
                       for a in cls.args])
        found = [r for r in recs
                 if any([re.search(str(args[f]), str(getattr(r, f, "")))
                         for f in fields if args[f]])]
        # output selected records
        for r in sorted(found, key=lambda x: x.fqdn):
            rtype = r.rec_name.upper()
            rdata = json.dumps(dyn.tm.records.DNSRecord.rdata(r))
            sys.stdout.write("{} {} {} {} {}\n".format(
                r.fqdn, rtype, r._record_id, r.ttl, rdata))


# setup record selection command subclass for each record type
rget = {}
for rtype in sorted(rtypes.keys()):
    # setup argument spec
    opts = copy.deepcopy(rtypes[rtype])  # list(rtypes[rtype])
    opts += [
        {'arg': '--ttl', 'dest': 'ttl', 'type': int,
         'help': 'TTL of the record.'},
        {'arg': '--id', 'type': int, 'dest': '_record_id',
         'help': 'Awkward internal record ID'},
    ]
    # tweak args to make them all optional
    for opt in opts:
        if not opt['arg'].startswith('--'):
            opt['arg'] = "--" + opt['arg']
    attr = {
        'name': rtype,
        'args': opts,
        'desc': "List some {} records.".format(rtype),
    }
    rget[rtype] = type("CommandRecordGet" + rtype, (CommandRecordGet,), attr)


# update record
class CommandRecordUpdate(DyntmCommand):
    name = "record-update"
    desc = "Update a record."
    args = [
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
        {'arg': 'node', 'type': str,
         'help': 'Node on which the the record appears.'},
        {'arg': '--publish', 'type': bool,
         'help': 'Zone should be published immediately.'},
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
        fields = [a['dest'] if 'dest' in a else a['arg'].strip("-")
                  for a in cls.args]
        # update the record
        for field in fields:
            if args[field]:
                setattr(that, field, args[field])
        # maybe publish the zone
        if args['publish']:
            zone.publish()
        # success
        sys.stdout.write("{}\n".format(str(that)))


# setup record update command subclass for each record type
rupdate = {}
for rtype in [k for k in sorted(rtypes.keys())]:
    # tweak args to make them all optional
    opts = copy.deepcopy(rtypes[rtype])  # list(rtypes[rtype])
    for opt in opts:
        if not opt['arg'].startswith('--'):
            opt['arg'] = "--" + opt['arg']
    # require record ID argument
    opts += [{'arg': 'id', 'type': str,
              'help': 'The unique numeric ID of the record.'}]
    opts += [{'arg': '--ttl', 'dest': 'ttl', 'type': int,
              'help': 'TTL of the record.'}]
    # setup the class attributes
    attr = {
        'name': rtype,
        'args': opts,
        'desc': "Update one {} record.".format(rtype),
    }
    # make the record update subclass
    rupdate[rtype] = type("CommandRecordUpdate" + rtype,
                          (CommandRecordUpdate,), attr)


# delete record
class CommandRecordDelete(DyntmCommand):
    name = "record-delete"
    desc = "Delete a record."
    args = [
        {'arg': 'zone', 'type': str,
         'help': 'The name of the zone.'},
        {'arg': 'node', 'type': str,
         'help': 'Node on which the the record appears.'},
        {'arg': '--publish', 'type': bool,
         'help': 'Zone should be published immediately.'},
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
        # maybe publish the zone
        if args['publish']:
            zone.publish()
        # success
        sys.stdout.write("{}\n".format(str(that)))


# setup record delete command subclass for each record type
rdelete = {}
for rtype in [k for k in sorted(rtypes.keys())]:
    # require record ID argument
    opts = {'arg': 'id', 'type': str,
            'help': 'The unique numeric ID of the record.'},
    # setup the class attributes
    attr = {
        'name': rtype,
        'args': opts,
        'desc': "Update one {} record.".format(rtype),
    }
    # make the record delete subclass
    rdelete[rtype] = type("CommandRecordDelete{}".format(rtype),
                          (CommandRecordDelete,), attr)


# redir commands TODO
# gslb commands TODO
# dsf commands TODO


# main
def main():
    DyntmCommand.action(sys.argv[1:])


if __name__ == "__main__":
    main()
