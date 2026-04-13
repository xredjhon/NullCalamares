# Integration

Source files stay in the repository for development.

The ready-to-copy distribution tree is generated under `dist/rootfs/`.

## Build

```bash
make build
```

## Verify

```bash
python3 scripts/verify_repo_packages.py
python3 scripts/check_ascii.py
```

## ISO Layout

`dist/rootfs/etc/calamares/settings.conf`

`dist/rootfs/etc/calamares/modules/`

`dist/rootfs/etc/calamares/branding/null/`

`dist/rootfs/usr/share/nullcalamares/manifests/`

`dist/rootfs/etc/pacman.conf.d/null-offline-repo.conf`

`dist/rootfs/usr/share/nullcalamares/offline/package-list.txt`

`dist/rootfs/etc/skel/.config/autostart/nullwelcome.desktop`

`dist/rootfs/usr/local/bin/nullwelcome-firstboot`

`dist/rootfs/usr/local/bin/nullcalamares-netmode`

## Flow

The Calamares stage installs only official-repository profiles.

At first login, `nullwelcome-firstboot` passes external package and preset manifests to `NullWelcome`.

For offline installation, the ISO builder must pre-populate a local pacman repository at `/opt/nullcalamares/offline/repo` using the generated offline package list.
