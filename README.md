# HomeAssistant-iDRAC

A custom component for DELL iDRAC in HomeAssistant

Uses the redFish API

**Available integration:**

- System On/Off Switch
- System Power Status

**Inside Configuration.yaml:**
```
idrac:
  - host: SERVER
    username: USERNAME
    password: PASSWORD


```

The component has a class that uses the redfish API, it was tested on iDRAC 8

Currently not available on HomeAssistant, so could be added as a custom component
**Folder structure:**
```
/config
|--custom_components
   |--idrac

```
