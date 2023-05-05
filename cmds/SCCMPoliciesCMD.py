import argparse
import cmd2
from cmd2 import CommandSet, with_default_category

from lib.SCCMPolicies import SCCMPolicies
from lib.Common import print_data

@with_default_category('Policies')
class SCCMPoliciesCMD(CommandSet):
    def __init__(self, iWbemServices):
        super().__init__()

        self.policies = SCCMPolicies(iWbemServices)

    update_machine_policy_parser = cmd2.Cmd2ArgumentParser()
    update_machine_policy_parser.add_argument('-ci', '--collectionID', action = 'store', type = str, required = True, help = 'ID of the collection')

    @cmd2.as_subcommand_to('update', 'machine-policy', update_machine_policy_parser)
    def update_machine_policy(self, ns: argparse.Namespace):
        self.policies.update_machine(ns.collectionID)
