from lib.Common import WMIFunction

class WMIQuery(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    def get(self, query: str):
        return self.get_class_instances_raw(query)
