from lib.Common import WMIFunction

class SCCMRules(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    def get(self, queryID: str):
        return self.get_class_instances("SMS_Query")
