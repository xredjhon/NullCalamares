# NullCalamares

`NullCalamares` is a modular Calamares branding, package selection, and first-boot integration workspace for `NullLinux`.

This workspace includes:

- `project/manifest.json`: project metadata and generated output settings
- `branding/null/`: logo, backgrounds, and QML slideshow assets
- `catalog/packages/repo.json`: official repository package catalog
- `catalog/packages/external.json`: external and first-boot package catalog
- `catalog/profiles/`: Calamares-selectable installation profiles
- `catalog/presets/`: first-boot preset combinations
- `catalog/offline/bundles.json`: offline ISO cache and local repo bundle definitions
- `catalog/services.json`: service, group, and user-service hints
- `modules/`: source Calamares module files
- `scripts/build.py`: generates all output artifacts
- `scripts/verify_repo_packages.py`: validates repo package names with `pacman -Si`
- `scripts/check_ascii.py`: enforces ASCII-only text files
- `dist/rootfs/`: ready-to-copy output tree for the live ISO
- `docs/`: integration and contract notes

This repository is not a full ISO profile by itself. It produces a ready-to-copy output tree for an Arch-based live ISO:

- `/etc/calamares/settings.conf`
- `/etc/calamares/branding/null/`
- `/etc/calamares/modules/netinstall.conf`
- `/etc/calamares/modules/netinstall.yaml`
- `/etc/calamares/modules/packages.conf`
- `/etc/pacman.conf.d/null-offline-repo.conf`
- `/usr/share/nullcalamares/manifests/`
- `/usr/share/nullcalamares/offline/package-list.txt`

## Status

Branding, modular package selection, first-boot handoff, security-focused profiles, and offline bundle manifests are ready.

Deliberately not automated:

- direct Calamares-stage installation of AUR packages
- attack, exploitation, brute-force, wireless attack, or post-exploitation toolchains

Reason:

- Calamares `netinstall` and `pacman` flows are safer and more reliable with official repository packages
- AUR and third-party packages need a separate repo, prebuilt package pool, or explicit post-install opt-in flow

## Build

To build all generated outputs:

```bash
make build
```

To verify official repo package availability:

```bash
make verify-packages
```

To enforce ASCII-only text:

```bash
make ascii-check
```

Generated outputs:

- `modules/netinstall.yaml`
- `dist/rootfs/etc/calamares/`
- `dist/rootfs/usr/share/nullcalamares/manifests/external-apps.json`
- `dist/rootfs/usr/share/nullcalamares/manifests/presets.json`
- `dist/rootfs/usr/share/nullcalamares/manifests/service-hints.json`
- `dist/rootfs/usr/share/nullcalamares/manifests/offline-bundles.json`
- `dist/rootfs/usr/share/nullcalamares/manifests/installer-capabilities.json`
- `dist/rootfs/etc/pacman.conf.d/null-offline-repo.conf`
- `dist/rootfs/usr/share/nullcalamares/offline/package-list.txt`
- `dist/rootfs/etc/skel/.config/autostart/nullwelcome.desktop`
- `dist/rootfs/usr/local/bin/nullwelcome-firstboot`
- `dist/rootfs/usr/local/bin/nullcalamares-netmode`
