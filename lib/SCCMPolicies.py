from lib.Common import WMIFunction

class SCCMPolicies(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    def update_machine(self, collectionID):
        clientOperation, _ = self.iWbemServices.GetObject("SMS_ClientOperation")
        resp = clientOperation.InitiateClientOperation(
            8,
            collectionID,
            None,
            None
        )
        print(f"[?] Requst status - {resp.ReturnValue}")
