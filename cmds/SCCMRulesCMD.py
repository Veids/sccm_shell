import argparse
import cmd2
from cmd2 import CommandSet, with_default_category, ansi

from lib.SCCMRules import SCCMRules
from lib.Common import print_data

@with_default_category('Rules')
class SCCMRulesCMD(CommandSet):
    def __init__(self, iWbemServices):
        super().__init__()

        self.rules = SCCMRules(iWbemServices)

    get_rule_parser = cmd2.Cmd2ArgumentParser()
    get_rule_parser.add_argument('-i', '--ruleID', action = 'store', type = str, required = True)

    @cmd2.as_subcommand_to('get', 'rule', get_rule_parser)
    def get_rule(self, ns: argparse.Namespace):
        rules = self.rules.get(ns.ruleID)
        print_data(rules)
