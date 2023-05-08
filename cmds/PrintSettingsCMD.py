import argparse
import cmd2
from cmd2 import CommandSet, with_default_category

from lib.SCCMDevices import SCCMDevices
import lib.Common as Common

@with_default_category('PrintSettings')
class PrintSettingsCMD(CommandSet):
    def __init__(self):
        super().__init__()

    set_print_parser = cmd2.Cmd2ArgumentParser()
    set_print_parser.add_argument('-t', '--table', action = argparse.BooleanOptionalAction, default = True, help = 'Table output')

    @cmd2.as_subcommand_to('settings', 'print', set_print_parser)
    def settings_print(self, ns: argparse.Namespace):
        Common.print_conf["table"] = ns.table
