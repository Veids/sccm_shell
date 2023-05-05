# SCCMShell

A little tool to play with SCCM. A partitial rewrite of [SharpSCCM](https://github.com/Mayyhem/SharpSCCM)

# Usage

```bash
python sccm_shell.py 'domain.local'/'user':'password'@'sccm.domain.local' <SiteCode>
```

# Functionality

```
get
    application - Retrives application object (SMS_Application)
    application-xml - Retrives application XML
    collection - Retrives collection object (SMS_Collection)
    collection-members - Get collection members
    deployment - Get deployment object (SMS_ApplicationAssignment)
    device - Query a device
    primary-device - Query a device matching a user
    site-push-settings - Get various information about SCCM
add
    application - Create an application
    collection - Add SYSTEM or USER collection
    collection-membership-rule - Add a rule for devices to include into collection
    deployment - Create a deployment
del
    application - Set application expired state and remove
    collection - Remove a collection
    collection-membership-rule - Remove a rule from collection
    deployment - Remove a deployment
update
    machine-policy - Force a device to update a machine policy from SCCM
```

# Credits

* [SharpSCCM](https://github.com/Mayyhem/SharpSCCM)
