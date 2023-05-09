import sys
from datetime import datetime
from typing import Any, List

from cmd2 import ansi
from cmd2.table_creator import (
    Column,
    SimpleTable,
)

import logging
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

console = Console()
FORMAT = "%(message)s"
log = logging.getLogger(__name__)
log.addHandler(RichHandler())
log.propagate = False

class WMIFunction:
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    def get_class_instances(self, className, properties = None, where = None):
        if properties is None:
            properties = "*"
        else:
            properties = ",".join(properties)

        where = "" if (where is None or where == "") else f"WHERE {where}"

        query = f"SELECT {properties} FROM {className} {where}"

        return self.get_class_instances_raw(query)

    def get_class_instances_raw(self, query):
        log.debug(f"Using following query: {query}")
        iEnumWbemClassObject = self.iWbemServices.ExecQuery(query)

        managementObjects = []
        while True:
            try:
                managementObject = iEnumWbemClassObject.Next(0xffffffff,1)[0]
                managementObjects.append(managementObject)
            except Exception as e:
                break

        return managementObjects

    @staticmethod
    def checkiWbemResponse(banner, resp):
        call_status = resp.GetCallStatus(0) & 0xffffffff
        if call_status != 0:
            from impacket.dcerpc.v5.dcom.wmi import WBEMSTATUS
            try:
                error_name = WBEMSTATUS.enumItems(call_status).name
            except ValueError:
                error_name = 'Unknown'
            log.error('%s - %s (0x%08x)' % (banner, error_name, call_status))
            return resp
        else:
            log.info(f"{banner} - OK")
        return resp

print_conf = {
    "table": True
}

def columnFormatter(prop, obj, customFormatter = None):
    value = prop['value']
    if value is None:
        return str(value)

    if prop['stype'] == 'datetime':
        return str(datetime.strptime(value.split('.')[0], "%Y%m%d%H%M%S"))

    if customFormatter:
        res = customFormatter(prop, obj)
        if isinstance(res, str):
            return res
        else:
            return str(res)

    return str(value)

def print_data(managementObjects, customFormatter = None, columns = None):
    if len(managementObjects):
        if print_conf["table"]:
            title = managementObjects[0].getClassName()
            headers = list(managementObjects[0].getProperties().keys())
            if columns:
                headers = list(filter(lambda x: x in columns, headers))

            table = Table(*headers, title = title)

            for obj in managementObjects:
                if not columns:
                    props = [columnFormatter(prop, obj, customFormatter) for prop in obj.getProperties().values()]
                else:
                    props = [columnFormatter(prop, obj, customFormatter) for k, prop in obj.getProperties().items() if k in columns]
                table.add_row(*props)

            console.print(table)
        else:
            for obj in managementObjects:
                header = f"===== {obj.getClassName()} ====="
                console.print(header)
                for k, v in obj.getProperties().items():
                    console.print("%s - %s" % (k, columnFormatter(v, obj, customFormatter)))
                console.print("=" * len(header))
    else:
        log.info("Empty response")
