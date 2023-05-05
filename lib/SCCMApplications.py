import uuid
from jinja2 import Environment, FileSystemLoader

from lib.Common import WMIFunction

class SCCMApplications(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices
        self.env = Environment(loader=FileSystemLoader("templates/"))

    def add(self, siteId, name, path, runUser, show = False):
        template = self.env.get_template("basic_application.xml")

        scopeId = f"ScopeId_{siteId}"
        appId = f"Application_{uuid.uuid4()}"
        deploymentId = f"DeploymentType_{uuid.uuid4()}"
        fileId = f"File_{uuid.uuid4()}"

        xml = template.render(
            path = path,
            runUser = runUser,
            name = name,
            siteId = siteId,
            scopeId = scopeId,
            appId = appId,
            deploymentId = deploymentId,
            fileId = fileId
        )

        application, _ = self.iWbemServices.GetObject("SMS_Application")
        application = application.SpawnInstance()
        application.SDMPackageXML = xml
        application.IsDeployable = True

        if show is False:
            application.IsHidden = True
        else:
            application.IsHidden = False

        return self.checkiWbemResponse(
            f"Creating new {name} application",
            self.iWbemServices.PutInstance(application.marshalMe())
        )

    def get(self, name = None, properties = None):
        whereCond = f"LocalizedDisplayName='{name}'" if name else None

        if properties is None:
            properties = ["CI_ID","LocalizedDisplayName", "ExecutionContext", "IsEnabled", "IsDeployed", "IsHidden", "CreatedBy", "LastModifiedBy", "HasContent"]

        return self.get_class_instances("SMS_Application", properties = properties, where = whereCond)

    def get_xml(self, ciID):
        return self.iWbemServices.GetObject(f"SMS_Application.CI_ID={ciID}")[0].SDMPackageXML

    def remove(self, ciID: str):
        whereCond = f"CI_ID={ciID}"
        applications = self.get_class_instances("SMS_Application", properties = None, where = whereCond)

        if len(applications) == 1:
            application = applications[0]
            resp = application.SetIsExpired(True)
            if resp.ReturnValue == 0:
                print(f"[+] Set application {ciID} expired state")
            else:
                print(f"[-] Failed to set application {ciID} expired state. Aborting...")
                return None

            return self.checkiWbemResponse(
                f"Removing application {ciID}",
                self.iWbemServices.DeleteInstance(f"SMS_Application.CI_ID={ciID}")
            )
        else:
            print(f"[-] Found {len(applications)} with CI_ID {ciID}")
