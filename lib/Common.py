import sys
from typing import Any, List

from cmd2 import ansi
from cmd2.table_creator import (
    Column,
    SimpleTable,
)

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
        print(f"[I] Using following query: {query}")
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
            print('%s - ERROR: %s (0x%08x)' % (banner, error_name, call_status))
            return resp
        else:
            print(f"[+] {banner} - OK")
        return resp

def print_data(managementObjects, columnFormatter = lambda x: x["value"]):
    if len(managementObjects):
        n = len(managementObjects[0].getProperties())
        if n < 10:
            max_width = int(180 / len(managementObjects[0].getProperties()))
        else:
            max_width = 20

        columns = [Column(x, width = max_width) for x in managementObjects[0].getProperties().keys()]
        data_list: List[List[Any]] = [[columnFormatter(prop) for prop in x.getProperties().values()] for x in managementObjects]

        st = SimpleTable(columns)
        table = st.generate_table(data_list)
        ansi_print(table)
    else:
        print("[!] Empty response")

def ansi_print(text):
    """Wraps style_aware_write so style can be stripped if needed"""
    ansi.style_aware_write(sys.stdout, text + '\n\n')
