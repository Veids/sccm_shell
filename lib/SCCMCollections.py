import random

from lib.Common import WMIFunction, log

class SCCMCollections(WMIFunction):
    def __init__(self, iWbemServices):
        self.iWbemServices = iWbemServices

    @staticmethod
    def collectionTypeToStr(collectionType: int):
        if collectionType == 0:
            return "Other"
        elif collectionType == 1:
            return "User"
        elif collectionType == 2:
            return "Device"
        else:
            return ""

    def get(self, collectionName: str = None, collectionID: str = None, properties = None):
        whereCond = []
        if collectionName:
            whereCond.append(f"Name='{collectionName}'")

        if collectionID:
            whereCond.append(f"CollectionID='{collectionID}'")

        if len(whereCond):
            whereCond = " and ".join(whereCond)
        else:
            whereCond = None

        if properties is None:
            properties = ["CollectionID", "CollectionType", "IsBuiltIn", "LastMemberChangeTime", "LastRefreshTime", "LimitToCollectionName", "MemberClassName", "MemberCount", "Name"]

        return self.get_class_instances("SMS_Collection", properties=properties, where = whereCond)

    def get_non_lazy(self, collectionID: str = None):
        if collectionID == "":
            raise Exception("Provided collectionID is empty")
        return self.iWbemServices.GetObject(f"SMS_Collection.CollectionID='{collectionID}'")[0]

    def create(self, collectionName: str, collectionType: str):
        collection, _ = self.iWbemServices.GetObject('SMS_Collection')
        collection = collection.SpawnInstance()
        collection.Name = collectionName
        collection.OwnedByThisSite = "True"
        if collectionType == "device":
            collection.CollectionType = 2
            collection.LimitToCollectionID = "SMS00001"
        elif collectionType == "user":
            collection.CollectionType = 1
            collection.LimitToCollectionID = "SMS00002"
        else:
            raise Exception(f"Unsupported collection type {collectionType}")

        return self.checkiWbemResponse(
            f"Creating new {collectionType} collection {collectionName}",
            self.iWbemServices.PutInstance(collection.marshalMe())
        )

    def remove(self, collectionID: str):
        if collectionID == "":
            raise Exception("CollectionID is empty")

        return self.checkiWbemResponse(
            f"Removing collection {collectionID}",
            self.iWbemServices.DeleteInstance('SMS_Collection.CollectionID="%s"' % collectionID)
        )

    def get_rules(self, collectionName: str = None, collectionID: str = None):
        objs = self.get(collectionName = collectionName, collectionID = collectionID, properties = ["*"])
        return objs

    def get_members(self, collectionID: str = None):
        return self.get_class_instances("SMS_FullCollectionMembership", ["CollectionID", "ResourceID", "ResourceType", "Domain", "Name", "IsActive", "IsApproved", "IsAssigned", "SiteCode"], f"CollectionID='{collectionID}'")

    def add_membership_rule(self, collectionID: str, resourceID: str, ruleName: str):
        if collectionID == "":
            raise Exception("CollectionID is empty")

        if resourceID == "":
            raise Exception("ResourceID is empty")

        collection = self.get_non_lazy(collectionID)
        if collection:
            collectionTypeStr = self.collectionTypeToStr(collection.CollectionType)
            targetClass = None
            if collectionTypeStr == "User":
                targetClass = "SMS_R_User"
            elif collectionTypeStr == "Device":
                targetClass = "SMS_R_System"
            else:
                log.error(f"Unsupported collection type {collection.CollectionType}")
                return None

            query = f"SELECT * FROM {targetClass} WHERE ResourceID='{resourceID}'"

            collectionRule, _ = self.iWbemServices.GetObject('SMS_CollectionRuleQuery')
            collectionRule = collectionRule.SpawnInstance()
            collectionRule.QueryExpression = query
            collectionRule.RuleName = ruleName
            collectionRule.QueryID = random.randint(0, 0xFFFFFFFF)

            resp = collectionRule.ValidateQuery(query)
            if resp.ReturnValue == "False":
                log.error(f"Specified query is not valid: {query}")
                return

            resp = collection.AddMembershipRule(collectionRule)
            if resp.ReturnValue == 0:
                log.info(f"Membership rule successfully added to collection {collectionID}")
            else:
                log.error(f"Failed to add membership rule to collection {collectionID}")
            return resp
        else:
            log.error("Specified collection is not found")
            return None

    def del_membership_rule(self, collectionID: str, queryID: int):
        if collectionID == "":
            raise Exception("CollectionID is empty")

        if queryID == "":
            raise Exception("QueryID is empty")

        collection = self.get_non_lazy(collectionID)
        if collection:
            for rule in collection.CollectionRules:
                if rule.QueryID == queryID:
                    resp = collection.DeleteMembershipRule(rule)
                    if resp.ReturnValue == 0:
                        log.info(f"Query {queryID} from collection {collectionID} has been removed")
                    else:
                        log.error(f"Failed to remove query {queryID} from collection {collectionID}")
                    return resp
        else:
            log.error("Specified collection is not found")
            return None
