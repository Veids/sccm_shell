from lib.Common import WMIFunction

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
        print(f"[?] Request status - {resp.ReturnValue}")
