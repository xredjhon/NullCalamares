#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="/tmp/nullcalamares-build/calamares"
PREFIX="/tmp/nullcalamares-build/prefix.sh"
SRC_CONFIG="$ROOT/dist/rootfs/etc/calamares"
BUILD_MODULES="/tmp/nullcalamares-build/src/modules"
RUN_ROOT="/tmp/nullcalamares-run"
MODE="${1:-test}"

if [[ "$MODE" != "test" && "$MODE" != "installer" && "$MODE" != "installer-root" ]]; then
    printf 'usage: %s [test|installer|installer-root]\n' "$0" >&2
    exit 1
fi

if [[ "$MODE" == "installer-root" ]]; then
    if [[ "$EUID" -eq 0 ]]; then
        MODE="installer"
    else
        printf -v ROOT_Q '%q' "$ROOT"
        printf -v DISPLAY_Q '%q' "${DISPLAY:-}"
        printf -v XAUTHORITY_Q '%q' "${XAUTHORITY:-}"
        printf -v XDG_RUNTIME_DIR_Q '%q' "${XDG_RUNTIME_DIR:-}"
        printf -v DBUS_Q '%q' "${DBUS_SESSION_BUS_ADDRESS:-}"
        printf -v WAYLAND_Q '%q' "${WAYLAND_DISPLAY:-}"
        printf -v PLATFORM_Q '%q' "${QT_QPA_PLATFORM:-}"
        exec run0 bash -lc "cd $ROOT_Q && DISPLAY=$DISPLAY_Q XAUTHORITY=$XAUTHORITY_Q XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR_Q DBUS_SESSION_BUS_ADDRESS=$DBUS_Q WAYLAND_DISPLAY=$WAYLAND_Q QT_QPA_PLATFORM=$PLATFORM_Q ./scripts/run_nullcalamares.sh installer"
    fi
fi

rm -rf "$RUN_ROOT"
mkdir -p "$RUN_ROOT"
cp -a "$SRC_CONFIG/." "$RUN_ROOT/"
ln -sfn /tmp/nullcalamares-app/share/calamares/qml "$RUN_ROOT/qml"

NULLCALAMARES_MODE="$MODE" python3 - <<'PY'
import os
from pathlib import Path
import shutil

run_root = Path("/tmp/nullcalamares-run")
modules_dir = run_root / "modules"
build_modules = Path("/tmp/nullcalamares-build/src/modules")
mode = os.environ["NULLCALAMARES_MODE"]

for path in build_modules.glob("*/*.conf"):
    target = modules_dir / path.name
    if not target.exists():
        shutil.copy2(path, target)

if mode == "installer":
    settings = """---
modules-search:
  - /tmp/nullcalamares-app/lib/calamares/modules
  - /tmp/nullcalamares-run/modules

branding: "null"
prompt-install: false
dont-chroot: false
oem-setup: false
disable-cancel: false
disable-cancel-during-exec: false
hide-back-and-next-during-exec: false
quit-at-end: false

sequence:
  - show:
      - welcome
      - locale
      - keyboard
      - partition
      - users
      - netinstall
      - summary
  - exec:
      - partition
      - mount
      - unpackfs
      - machineid
      - fstab
      - locale
      - keyboard
      - localecfg
      - users
      - displaymanager
      - networkcfg
      - hwclock
      - packages
      - netinstall
      - services-systemd
      - bootloader
      - umount
  - show:
      - finished
"""
    welcome = """---
showSupportUrl: true
showKnownIssuesUrl: false
showReleaseNotesUrl: false
requirements:
    requiredStorage: 0.1
    requiredRam: 0.1
    internetCheckUrl: http://example.com
    check:
        - ram
        - internet
    required:
        - ram
geoip:
    style: "none"
"""
else:
    settings = """---
modules-search:
  - /tmp/nullcalamares-app/lib/calamares/modules
  - /tmp/nullcalamares-run/modules

branding: "null"
prompt-install: false
dont-chroot: false
oem-setup: false
disable-cancel: false
disable-cancel-during-exec: false
hide-back-and-next-during-exec: false
quit-at-end: false

sequence:
  - show:
      - welcome
      - locale
      - keyboard
      - users
      - netinstall
      - summary
"""
    welcome = """---
showSupportUrl: true
showKnownIssuesUrl: false
showReleaseNotesUrl: false
requirements:
    requiredStorage: 0.1
    requiredRam: 0.1
    internetCheckUrl: http://example.com
    check:
        - ram
        - internet
    required:
        - ram
geoip:
    style: "none"
"""
(run_root / "settings.conf").write_text(settings, encoding="utf-8")
(modules_dir / "welcome.conf").write_text(welcome, encoding="utf-8")
PY

set +u
source "$PREFIX"
set -u
exec "$APP" -d -c "$RUN_ROOT"
