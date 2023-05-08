from lib.Common import WMIFunction

class SCCMOperations(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    def get_operation_status(self, operationID: int, properties = None):
        if properties is None:
            properties = ["ID", "Type", "TotalClients", "CompletedClients", "FailedClients", "State"]

        return self.get_class_instances("SMS_ClientOperationStatus", properties = properties, where = f"ID={operationID}")
