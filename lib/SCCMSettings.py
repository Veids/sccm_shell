from lib.Common import WMIFunction, log

class SCCMSettings(WMIFunction):
    SCCMFILTERS = {
        0: "Workstations and Servers (including domain controllers)",
        1: "Servers only (including domain controllers)",
        2: "Workstations and Servers (excluding domain controllers)",
        3: "Servers only (excluding domain controllers)",
        4: "Workstations and domain controllers only (excluding other servers)",
        5: "Domain controllers only",
        6: "Workstations only",
        7: "No computers"
    }

    def __init__(self, iWbemServices):
        super(SCCMSettings, self).__init__(iWbemServices)
        self.iWbemServices = iWbemServices

    def show_site_push_settings(self):
        query = "SELECT PropertyName, Value, Value1 FROM SMS_SCI_SCProperty WHERE ItemType='SMS_DISCOVERY_DATA_MANAGER' AND (PropertyName='ENABLEKERBEROSCHECK' OR PropertyName='FILTERS' OR PropertyName='SETTINGS')"
        objects = self.get_class_instances_raw(query)

        for x in objects:
            if x.PropertyName == "SETTINGS":
                if x.Value1 == "Active":
                    log.info("Automatic site-wide client push installation is enabled")
                else:
                    log.info("Automatic site-wide client push installation is not enabled")
            elif x.PropertyName == "ENABLEKERBEROSCHECK":
                if x.Value == 3:
                    log.info("Fallback to NTLM is enabled")
            elif x.PropertyName == "FILTERS":
                log.info("Install client software on the following computers:")
                if x.Value in self.SCCMFILTERS:
                    log.info(f"\t{self.SCCMFILTERS[x.Value]}")

        query = "SELECT Values FROM SMS_SCI_SCPropertyList WHERE PropertyListName='Reserved2'"
        objects = self.get_class_instances_raw(query)
        if len(objects):
            for x in objects:
                if x.Values is not None and len(x.Values) != 0:
                    for value in x.Values:
                        log.info(f"Discovered client push installation account: {value}")
                else:
                    log.info("No client push installation accounts were configured, but the server may still use its machine account")
        else:
            log.info("No client push installation accounts were configured, but the server may still use its machine account")

        query = "SELECT * FROM SMS_SCI_SQLTask WHERE ItemName='Clear Undiscovered Clients'"
        objects = self.get_class_instances_raw(query)

        for x in objects:
            if x.Enabled == "True":
                log.info(f"[{x.SiteCode}] The client installed flag is automatically cleared on inactive clients after {x['DeleteOlderThan']} days, resulting in reinstallation if automatic site-wide client push installation is enabled")
            else:
                log.info(f"[{x.SiteCode}] The client installed flag is not automatically cleared on inactive clients, preventing automatic reinstallation")
