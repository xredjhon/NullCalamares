# NullWelcome Contract

This repository generates the following `NullWelcome` invocation contract:

```bash
nullwelcome --manifest /usr/share/nullcalamares/manifests/external-apps.json --presets /usr/share/nullcalamares/manifests/presets.json --services /usr/share/nullcalamares/manifests/service-hints.json
```

Expected behavior:

- list AUR or external package candidates from `external-apps.json`
- show ready-made combinations from `presets.json`
- show service, group, and user service hints from `service-hints.json`
- manage the extra install flow according to user selections

This keeps the Calamares and first-boot layers separate.
