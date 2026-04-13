# NullCalamares

NullCalamares is a modular Calamares workspace for NullLinux. It provides branding, curated package catalogs, install profiles, presets, offline bundle manifests, and generated Calamares output for an Arch-based live environment.

This repository is not a full ISO profile on its own. It builds the Calamares tree and related manifests that can be copied into a live ISO root filesystem.

## Scope

- NullLinux branding and slideshow assets
- Modular package catalogs for repository and external handoff items
- Calamares-selectable profiles for kernels, desktops, connectivity, privacy, DFIR, observability, virtualization, and workstation tooling
- Preset manifests for first-boot application setup
- Online and offline installer metadata
- First-boot integration contract for NullWelcome
- Local runtime launcher for isolated NullCalamares testing

## Repository Layout

- `branding/null/` NullLinux branding assets, slideshow, and stylesheet
- `catalog/packages/` repository, external, and user extension catalogs
- `catalog/profiles/` modular install profiles consumed by `netinstall`
- `catalog/presets/` grouped first-boot preset definitions
- `catalog/curated/` generated and hand-maintained category manifests
- `catalog/offline/` offline bundle definitions
- `catalog/services.json` service enablement hints
- `modules/` Calamares module source files
- `project/manifest.json` project metadata and output targets
- `scripts/build.py` build pipeline for generated outputs
- `scripts/verify_repo_packages.py` repository package validation
- `scripts/check_ascii.py` ASCII-only validation for text files
- `scripts/run_nullcalamares.sh` isolated launcher for test and installer modes
- `dist/rootfs/` generated output tree for ISO integration

## Build

```bash
make build
```

## Validation

```bash
make verify-packages
make ascii-check
```

## Generated Output

The build pipeline generates:

- `dist/rootfs/etc/calamares/settings.conf`
- `dist/rootfs/etc/calamares/branding/null/`
- `dist/rootfs/etc/calamares/modules/netinstall.conf`
- `dist/rootfs/etc/calamares/modules/netinstall.yaml`
- `dist/rootfs/etc/calamares/modules/packages.conf`
- `dist/rootfs/etc/pacman.conf.d/null-offline-repo.conf`
- `dist/rootfs/usr/share/nullcalamares/manifests/`
- `dist/rootfs/usr/share/nullcalamares/offline/package-list.txt`
- `dist/rootfs/usr/local/bin/nullwelcome-firstboot`
- `dist/rootfs/usr/local/bin/nullcalamares-netmode`

## Runtime Launcher

The local launcher supports isolated runtime testing without replacing the host Calamares setup:

```bash
./scripts/run_nullcalamares.sh test
./scripts/run_nullcalamares.sh installer
./scripts/run_nullcalamares.sh installer-root
```

- `test` starts a safe UI flow for branding and module checks
- `installer` starts the installer flow in the current user session
- `installer-root` re-launches the installer flow with elevated rights for device detection

## Integration Notes

- `dist/rootfs/` is intended to be copied into an Arch-based live root filesystem
- repository-backed packages are installed through Calamares
- external items are handed off through generated first-boot manifests
- user extension catalogs are kept separate so the base project can stay modular

## Related Files

- `docs/integration.md`
- `docs/nullwelcome-contract.md`
- `docs/visual-map.md`
