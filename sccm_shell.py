#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
import sys
import os
import cmd
import time
import logging
import ntpath
import argparse
from datetime import datetime

import cmd2
from cmd2 import CommandSet, with_argparser, with_category, with_default_category

from impacket.examples import logger
from impacket.examples.utils import parse_target
from impacket import version
from impacket.dcerpc.v5.dcomrt import DCOMConnection, COMVERSION
from impacket.dcerpc.v5.dcom import wmi
from impacket.dcerpc.v5.dtypes import NULL
from impacket.krb5.keytab import Keytab

from cmds.SCCMDevicesCMD import SCCMDevicesCMD
from cmds.SCCMRulesCMD import SCCMRulesCMD
from cmds.SCCMApplicationsCMD import SCCMApplicationsCMD
from cmds.SCCMSettingsCMD import SCCMSettingsCMD
from cmds.SCCMCollectionsCMD import SCCMCollectionsCMD
from cmds.SCCMPoliciesCMD import SCCMPoliciesCMD
from cmds.SCCMDeploymentsCMD import SCCMDeploymentsCMD

class SCCM(cmd2.Cmd):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    get_parser = cmd2.Cmd2ArgumentParser()
    get_subparsers = get_parser.add_subparsers(title='entity', help='information to query')

    @with_argparser(get_parser)
    def do_get(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('get')

    add_parser = cmd2.Cmd2ArgumentParser()
    add_subparsers = add_parser.add_subparsers(title='entity', help='information to add')

    @with_argparser(add_parser)
    def do_add(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('add')

    del_parser = cmd2.Cmd2ArgumentParser()
    del_subparsers = del_parser.add_subparsers(title='entity', help='information to delete')

    @with_argparser(del_parser)
    def do_del(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('del')

    update_parser = cmd2.Cmd2ArgumentParser()
    update_subparsers = update_parser.add_subparsers(title='entity', help='information to update')

    @with_argparser(update_parser)
    def do_update(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('del')

def load_smbclient_auth_file(path):
    '''Load credentials from an smbclient-style authentication file (used by
    smbclient, mount.cifs and others).  returns (domain, username, password)
    or raises AuthFileSyntaxError or any I/O exceptions.'''

    lineno = 0
    domain = None
    username = None
    password = None
    for line in open(path):
        lineno += 1

        line = line.strip()

        if line.startswith('#') or line == '':
            continue

        parts = line.split('=', 1)
        if len(parts) != 2:
            raise AuthFileSyntaxError(path, lineno, 'No "=" present in line')

        (k, v) = (parts[0].strip(), parts[1].strip())

        if k == 'username':
            username = v
        elif k == 'password':
            password = v
        elif k == 'domain':
            domain = v
        else:
            raise AuthFileSyntaxError(path, lineno, 'Unknown option %s' % repr(k))

    return (domain, username, password)

def main(address, username='', password='', domain='', hashes=None, aesKey=None, doKerberos=False, kdcHost=None, code = '', cmds=None):
    lmhash = ''
    nthash = ''
    if hashes is not None:
        lmhash, nthash = hashes.split(':')

    dcom = DCOMConnection(address, username, password, domain, lmhash, nthash,
                          aesKey, oxidResolver=True, doKerberos=doKerberos, kdcHost=kdcHost)
    try:
        iInterface = dcom.CoCreateInstanceEx(wmi.CLSID_WbemLevel1Login, wmi.IID_IWbemLevel1Login)
        iWbemLevel1Login = wmi.IWbemLevel1Login(iInterface)
        iWbemServices = iWbemLevel1Login.NTLMLogin(f'//./root/SMS/site_{code}', NULL, NULL)
        iWbemLevel1Login.RemRelease()

        app = SCCM(command_sets = [
            SCCMCollectionsCMD(iWbemServices),
            SCCMSettingsCMD(iWbemServices),
            SCCMDevicesCMD(iWbemServices),
            SCCMRulesCMD(iWbemServices),
            SCCMApplicationsCMD(iWbemServices),
            SCCMPoliciesCMD(iWbemServices),
            SCCMDeploymentsCMD(iWbemServices)
        ])
        if cmds:
            for x in cmds:
                app.onecmd(x)
        else:
            app.cmdloop()
    except  (Exception, KeyboardInterrupt) as e:
        if logging.getLogger().level == logging.DEBUG:
            import traceback
            traceback.print_exc()
        logging.error(str(e))
        dcom.disconnect()
        sys.stdout.flush()
        sys.exit(1)

    dcom.disconnect()

# Process command-line arguments.
if __name__ == '__main__':
    print(version.BANNER)

    parser = argparse.ArgumentParser(add_help=True, description="Interacts with SCCM")
    parser.add_argument('target', action='store', help='[[domain/]username[:password]@]<targetName or address>')
    parser.add_argument('-ts', action='store_true', help='Adds timestamp to every logging output')
    parser.add_argument('-debug', action='store_true', help='Turn DEBUG output ON')
    parser.add_argument('-com-version', action='store', metavar="MAJOR_VERSION:MINOR_VERSION",
                        help='DCOM version, format is MAJOR_VERSION:MINOR_VERSION e.g. 5.7')
    parser.add_argument('code', action='store', help='Site code (e.g. PO1)')
    parser.add_argument('--cmd', action='append', default=None, help='Executes cmd and exits (can be provided multiple times)')

    group = parser.add_argument_group('authentication')
    group.add_argument('-hashes', action="store", metavar="LMHASH:NTHASH", help='NTLM hashes, format is LMHASH:NTHASH')
    group.add_argument('-no-pass', action="store_true", help='don\'t ask for password (useful for -k)')
    group.add_argument('-k', action="store_true",
                       help='Use Kerberos authentication. Grabs credentials from ccache file '
                       '(KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the '
                       'ones specified in the command line')
    group.add_argument('-aesKey', action="store", metavar="hex key", help='AES key to use for Kerberos Authentication '
                       '(128 or 256 bits)')
    group.add_argument('-dc-ip', action='store', metavar="ip address", help='IP Address of the domain controller. If '
                       'ommited it use the domain part (FQDN) specified in the target parameter')
    group.add_argument('-A', action="store", metavar="authfile", help="smbclient/mount.cifs-style authentication file. "
                       "See smbclient man page's -A option.")
    group.add_argument('-keytab', action="store", help='Read keys for SPN from keytab file')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    options = parser.parse_args()

    # Init the example's logger theme
    logger.init(options.ts)

    if options.debug is True:
        logging.getLogger().setLevel(logging.DEBUG)
        # Print the Library's installation path
        logging.debug(version.getInstallationPath())
    else:
        logging.getLogger().setLevel(logging.INFO)

    if options.com_version is not None:
        try:
            major_version, minor_version = options.com_version.split('.')
            COMVERSION.set_default_version(int(major_version), int(minor_version))
        except Exception:
            logging.error("Wrong COMVERSION format, use dot separated integers e.g. \"5.7\"")
            sys.exit(1)

    domain, username, password, address = parse_target(options.target)

    try:
        if options.A is not None:
            (domain, username, password) = load_smbclient_auth_file(options.A)
            logging.debug('loaded smbclient auth file: domain=%s, username=%s, password=%s' % (
                repr(domain), repr(username), repr(password)))

        if domain is None:
            domain = ''

        if options.keytab is not None:
            Keytab.loadKeysFromKeytab(options.keytab, username, domain, options)
            options.k = True

        if password == '' and username != '' and options.hashes is None and options.no_pass is False and options.aesKey is None:
            from getpass import getpass

            password = getpass("Password:")

        if options.aesKey is not None:
            options.k = True

        main(address, username, password, domain, options.hashes, options.aesKey, options.k, options.dc_ip, options.code, options.cmd)
    except KeyboardInterrupt as e:
        logging.error(str(e))
    except Exception as e:
        if logging.getLogger().level == logging.DEBUG:
            import traceback

            traceback.print_exc()
        logging.error(str(e))
        sys.exit(1)

    sys.exit(0)
