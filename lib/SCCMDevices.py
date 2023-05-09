from lib.Common import WMIFunction

class SCCMDevices(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    def get(self, userName = None, netbiosName = None, properties = None):
        whereCond = []
        if userName:
            whereCond.append(f"LastLogonUserName='{userName}'")

        if netbiosName:
            whereCond.append(f"NetbiosName='{netbiosName}'")

        if len(whereCond):
            whereCond = " and ".join(whereCond)
        else:
            whereCond = None

        if properties is None:
            properties = ["Active", "Client", "ClientType", "ResourceID", "NetbiosName", "LastLogonUserName", "LastLogonTimestamp", "ResourceNames"]

        return self.get_class_instances("SMS_R_System", properties = properties, where = whereCond)

    def get_primary(self, userName = None, resourceID = None, resourceName = None):
        whereCond = None
        if userName:
            whereCond = f"UniqueUserName='{userName}'"
        elif resourceID:
            whereCond = f"ResourceID='{resouceID}'"
        elif resourceName:
            whereCond = f"ResourceName='{resourceName}'"

        return self.get_class_instances("SMS_UserMachineRelationship", properties = None, where = whereCond)
