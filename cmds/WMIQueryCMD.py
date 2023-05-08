from datetime import datetime
import argparse
import cmd2
import sys
from cmd2 import CommandSet, with_default_category, ansi, with_argparser

from typing import (
    Any,
    List,
)

from cmd2.table_creator import (
    Column,
    SimpleTable,
)

from lib.WMIQuery import WMIQuery
from lib.Common import print_data

@with_default_category('Query')
class WMIQueryCMD(CommandSet):
    def __init__(self, iWbemServices):
        super().__init__()

        self.WMIQuery = WMIQuery(iWbemServices)

    query_parser = cmd2.Cmd2ArgumentParser()
    query_parser.add_argument('query', action = 'store', type = str)

    @with_argparser(query_parser)
    def do_query(self, ns: argparse.Namespace):
        print_data(self.WMIQuery.get(ns.query))

    @with_argparser(query_parser)
    def do_query_pg(self, ns: argparse.Namespace):
        res = self.WMIQuery.get(ns.query)
        print("[I] Result stores in res value")
        from IPython import embed; embed()  # DEBUG
        print_data(res)
