from lib.Common import WMIFunction, log

class SCCMPolicies(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    def update_machine(self, collectionID: str, resourceIDs: int):
        clientOperation, _ = self.iWbemServices.GetObject("SMS_ClientOperation")
        resp = clientOperation.InitiateClientOperation(
            8,
            collectionID,
            0,
            resourceIDs
        )

        if resp.ReturnValue == 0:
            log.info(f"Operation successfully initiated {resp.OperationID}")
        else:
            log.error(f"Failed to initiate an operation")
        return resp
