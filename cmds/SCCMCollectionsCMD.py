import argparse
from datetime import datetime
import cmd2
from cmd2 import CommandSet, with_default_category

from typing import (
    Any,
    List,
)

from cmd2.table_creator import (
    Column,
    SimpleTable,
)

from lib.Common import print_data, ansi_print
from lib.SCCMCollections import SCCMCollections

@with_default_category('Collections')
class SCCMCollectionsCMD(CommandSet):
    def __init__(self, iWbemServices):
        super().__init__()

        self.proxy = SCCMCollections(iWbemServices)

    @staticmethod
    def format_column(property):
        value = property['value']
        if value is None:
            return value

        if property['stype'] == 'datetime':
            return datetime.strptime(value.split('.')[0], "%Y%m%d%H%M%S")
        if property['name'] == "CollectionType":
            return f"{value} ({SCCMCollections.collectionTypeToStr(value)})"
        return value


    get_collections_parser = cmd2.Cmd2ArgumentParser()
    get_collections_parser.add_argument('-n', '--collectionName', action = 'store', type = str, default = None, help = 'Name of the collection')
    get_collections_parser.add_argument('-i', '--collectionID', action = 'store', type = str, default = None, help = 'ID of the collection')
    get_collections_parser.add_argument('-p', '--property', action = 'append', type = str, default = None, help = 'Property to output')

    @cmd2.as_subcommand_to('get', 'collection', get_collections_parser)
    def get_collection(self, ns: argparse.Namespace):
        collections = self.proxy.get(ns.collectionName, ns.collectionID, ns.property)
        print_data(collections, self.format_column)


    add_collection_parser = cmd2.Cmd2ArgumentParser()
    add_collection_parser.add_argument('-n', '--collectionName', action = 'store', type = str, required = True, help = 'Name of the collection')
    add_collection_parser.add_argument('-t', '--collectionType', action = 'store', type = str, choices = ["user", "device"], required = True, help = 'Type of the collection')

    @cmd2.as_subcommand_to('add', 'collection', add_collection_parser)
    def add_collection(self, ns: argparse.Namespace):
        self.proxy.create(ns.collectionName, ns.collectionType)


    add_collection_membership_rule_parser = cmd2.Cmd2ArgumentParser()
    add_collection_membership_rule_parser.add_argument('-i', '--collectionID', action = 'store', type = str, required = True, help = 'ID of the collection')
    add_collection_membership_rule_parser.add_argument('-ri', '--resourceID', action = 'store', type = str, required = True, help = 'ID of the resource')
    add_collection_membership_rule_parser.add_argument('-n', '--ruleName', action = 'store', type = str, required = True, help = 'Name of the rule')

    @cmd2.as_subcommand_to('add', 'collection-membership-rule', add_collection_membership_rule_parser)
    def add_collection_membership_rule(self, ns: argparse.Namespace):
        self.proxy.add_membership_rule(ns.collectionID, ns.resourceID, ns.ruleName)


    del_collection_membership_rule_parser = cmd2.Cmd2ArgumentParser()
    del_collection_membership_rule_parser.add_argument('-i', '--collectionID', action = 'store', type = str, required = True, help = 'ID of the collection')
    del_collection_membership_rule_parser.add_argument('-qi', '--queryID', action = 'store', type = int, required = True, help = 'ID of the query')

    @cmd2.as_subcommand_to('del', 'collection-membership-rule', del_collection_membership_rule_parser)
    def del_collection_membership_rule(self, ns: argparse.Namespace):
        self.proxy.del_membership_rule(ns.collectionID, ns.queryID)


    del_collections_parser = cmd2.Cmd2ArgumentParser()
    del_collections_parser.add_argument('-i', '--collectionID', action = 'store', type = str, required = True, help = 'ID of the collection')

    @cmd2.as_subcommand_to('del', 'collection', del_collections_parser)
    def del_collections(self, ns: argparse.Namespace):
        self.proxy.remove(ns.collectionID)


    get_collection_rules_parser = cmd2.Cmd2ArgumentParser()
    get_collection_rules_group = get_collection_rules_parser.add_mutually_exclusive_group(required=True)
    get_collection_rules_group.add_argument('-n', '--collectionName', action = 'store', type = str, default = None, help = 'Name of the collection')
    get_collection_rules_group.add_argument('-i', '--collectionID', action = 'store', type = str, default = None, help = 'ID of the collection')

    @cmd2.as_subcommand_to('get', 'collection-rules', get_collection_rules_parser)
    def get_collection_rules(self, ns: argparse.Namespace):
        collection = self.proxy.get_non_lazy(ns.collectionID)

        columns = [
            Column("CollectionID"),
            Column("Name", width = 20),
            Column("CollectionRules", width = 90),
            Column("MemberCount")
        ]

        if collection.CollectionRules:
            rules = [", ".join(["%s: %s" % (ruleProp['name'], ruleProp['value']) for ruleProp in ruleObj.getProperties().values()]) for ruleObj in collection.CollectionRules]
        else:
            rules = None

        data_list: List[List[Any]] = list()
        data_list.append(
            [collection.CollectionID, collection.Name, rules, collection.MemberCount]
        )

        st = SimpleTable(columns)
        table = st.generate_table(data_list)
        ansi_print(table)


    get_collection_members_parser = cmd2.Cmd2ArgumentParser()
    get_collection_members_parser.add_argument('-i', '--collectionID', action = 'store', type = str, required = True, help = 'ID of the collection')

    @cmd2.as_subcommand_to('get', 'collection-members', get_collection_members_parser)
    def get_collection_members(self, ns: argparse.Namespace):
        members = self.proxy.get_members(ns.collectionID)
        print_data(members, self.format_column)
