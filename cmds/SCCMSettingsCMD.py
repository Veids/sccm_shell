import argparse
import cmd2
from cmd2 import CommandSet, with_default_category

from lib.SCCMSettings import SCCMSettings

@with_default_category('Settings')
class SCCMSettingsCMD(CommandSet):
    def __init__(self, iWbemServices):
        super().__init__()

        self.settings = SCCMSettings(iWbemServices)

    get_site_push_settings_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.as_subcommand_to('get', 'site-push-settings', get_site_push_settings_parser)
    def get_site_push_settings(self, ns: argparse.Namespace):
        self.settings.show_site_push_settings()
