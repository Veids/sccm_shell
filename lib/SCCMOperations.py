from lib.Common import WMIFunction, log

class SCCMOperations(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    def get_status(self, operationID: int = None, properties = None):
        whereCond = None
        if operationID:
            whereCond = f"ID={operationID}"

        if properties is None:
            properties = ["ID", "Type", "TotalClients", "CompletedClients", "FailedClients", "State", "CollectionID"]

        return self.get_class_instances("SMS_ClientOperationStatus", properties = properties, where = whereCond)

    def remove(self, operationID: int):
        clientOperation, _ = self.iWbemServices.GetObject("SMS_ClientOperation")
        resp = clientOperation.DeleteClientOperation(
            operationID
        )

        if resp.ReturnValue == 0:
            log.info(f"ClientOperation {operationID} successfully removed")
        else:
            log.error(f"Failed to remove ClientOperation {operationID}")
        return resp
