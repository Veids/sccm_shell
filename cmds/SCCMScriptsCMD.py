from base64 import b64decode
import argparse
import cmd2
from cmd2 import CommandSet, with_default_category, ansi, with_argparser

from lib.SCCMScripts import SCCMScripts
from lib.Common import print_data, log

@with_default_category('Scripts')
class SCCMScriptsCMD(CommandSet):
    def __init__(self, iWbemServices):
        super().__init__()

        self.scripts = SCCMScripts(iWbemServices)

    @staticmethod
    def columnFormatter(property, obj):
        value = property['value']
        if value is None:
            return value

        if property['name'] == "Script":
            try:
                return b64decode(value).decode("UTF-16")
            except Exception:
                log.error('Script decode failure')
                return value

        if property['name'] == "ApprovalState":
            if value == 0:
                return f"{value} (Waiting)"
            if value == 1:
                return f"{value} (Declined)"
            if value == 3:
                return f"{value} (Approved)"

        if property['name'] == "ScriptType":
            if value == 0:
                return f"{value} (PSH)"

        return value

    get_script_parser = cmd2.Cmd2ArgumentParser()
    get_script_parser.add_argument('-sg', '--scriptGuid', action = 'store', type = str, required = True)
    get_script_parser.add_argument('-p', '--property', action = 'append', type = str, default = None, help = 'Property to output')

    @cmd2.as_subcommand_to('get', 'script', get_script_parser)
    def get_script(self, ns: argparse.Namespace):
        columns = ns.property
        if columns is None:
            columns = ["ScriptGuid", "Author", "Script", "MemberCount", "Parameterlist"]

        print_data([self.scripts.get(ns.scriptGuid)], self.columnFormatter, columns)

    get_scripts_parser = cmd2.Cmd2ArgumentParser()
    get_scripts_parser.add_argument('-p', '--property', action = 'append', type = str, default = None, help = 'Property to output')

    @cmd2.as_subcommand_to('get', 'scripts', get_scripts_parser)
    def get_scripts(self, ns: argparse.Namespace):
        print_data(self.scripts.gets(ns.property), self.columnFormatter)

    get_scripts_execution_summary = cmd2.Cmd2ArgumentParser()
    get_scripts_execution_summary.add_argument('-sg', '--scriptGuid', action = 'store', type = str, default = None, help = 'Script Guid (Optional)')

    @cmd2.as_subcommand_to('get', 'scripts-execution-summary', get_scripts_execution_summary)
    def get_scripts_execution_summary(self, ns: argparse.Namespace):
        print_data(self.scripts.get_execution_summary_lazy(ns.scriptGuid))

    add_script_parser = cmd2.Cmd2ArgumentParser()
    add_script_parser.add_argument('-sn', '--scriptName', action = 'store', type = str, default = None, required = True, help = 'Name of the script')
    add_script_parser.add_argument('-sc', '--scriptContent', action = 'store', type = str, default = None, required = True, help = 'Script payload (e.g. "whoami")')
    add_script_parser.add_argument('-st', '--scriptTimeout', action = 'store', type = int, default = 60, help = 'Script timeout')

    @cmd2.as_subcommand_to('add', 'script', add_script_parser)
    def add_script(self, ns: argparse.Namespace):
        self.scripts.add(ns.scriptName, ns.scriptContent, ns.scriptTimeout)

    del_script_parser = cmd2.Cmd2ArgumentParser()
    del_script_parser.add_argument('-sg', '--scriptGuid', action = 'store', type = str, required = True, help = 'ScriptGuid')

    @cmd2.as_subcommand_to('del', 'script', del_script_parser)
    def del_script(self, ns: argparse.Namespace):
        self.scripts.remove(ns.scriptGuid)

    update_script_approval_parser = cmd2.Cmd2ArgumentParser()
    update_script_approval_parser.add_argument('-sg', '--scriptGuid', action = 'store', type = str, required = True, help = 'ScriptGuid')

    @cmd2.as_subcommand_to('update', 'script-approval', update_script_approval_parser)
    def update_script_approval(self, ns: argparse.Namespace):
        self.scripts.approve(ns.scriptGuid)

    run_script_parser = cmd2.Cmd2ArgumentParser()
    run_script_parser.add_argument('-sg', '--scriptGuid', action = 'store', type = str, required = True, help = 'ScriptGuid')
    run_script_parser.add_argument('-ci', '--collectionID', action = 'store', type = str, default = '', help = 'ScriptGuid')
    run_script_parser.add_argument('-ri', '--resourceID', action = 'append', type = int, default = [], help = 'Target resource (May be specified multiple times)')

    @with_argparser(run_script_parser)
    def do_run(self, ns: argparse.Namespace):
        self.scripts.run(ns.scriptGuid, ns.collectionID, ns.resourceID)
