from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "project" / "manifest.json"
REPO_CATALOG = ROOT / "catalog" / "packages" / "repo.json"
EXTERNAL_CATALOG = ROOT / "catalog" / "packages" / "external.json"
USER_REPO_CATALOG = ROOT / "catalog" / "packages" / "user-repo.json"
USER_EXTERNAL_CATALOG = ROOT / "catalog" / "packages" / "user-external.json"
AUR_HELPERS_CATALOG = ROOT / "catalog" / "managers" / "aur-helpers.json"
CURATED_DIR = ROOT / "catalog" / "curated"
SERVICE_CATALOG = ROOT / "catalog" / "services.json"
PROFILE_DIR = ROOT / "catalog" / "profiles"
PRESET_DIR = ROOT / "catalog" / "presets"
OFFLINE_BUNDLE_CATALOG = ROOT / "catalog" / "offline" / "bundles.json"
MODULE_DIR = ROOT / "modules"
BRANDING_DIR = ROOT / "branding"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def load_package_catalog(path: Path, allowed_sources: set[str]) -> dict[str, dict]:
    items = read_json(path)
    if not isinstance(items, list):
        raise SystemExit(f"{path.name}: liste bekleniyor")
    catalog = {}
    package_owners = {}
    for item in items:
        required = {"id", "label", "source", "packages", "summary"}
        missing = required.difference(item)
        if missing:
            raise SystemExit(f"{path.name}: eksik alanlar: {', '.join(sorted(missing))}")
        if item["source"] not in allowed_sources:
            allowed = ", ".join(sorted(allowed_sources))
            raise SystemExit(f"{path.name}: beklenen kaynaklar {allowed}, gelen {item['source']}")
        item_id = item["id"]
        if item_id in catalog:
            raise SystemExit(f"{path.name}: tekrar eden katalog kimligi: {item_id}")
        packages = item["packages"]
        if not isinstance(packages, list) or not packages:
            raise SystemExit(f"{path.name}: {item_id} icin packages dolu liste olmali")
        normalized = []
        seen = set()
        for package in packages:
            if not isinstance(package, str) or not package.strip():
                raise SystemExit(f"{path.name}: {item_id} icin gecersiz paket")
            package = package.strip()
            if package in seen:
                continue
            if package in package_owners:
                raise SystemExit(f"{path.name}: paket birden fazla kayitta kullaniliyor: {package}")
            package_owners[package] = item_id
            seen.add(package)
            normalized.append(package)
        item["packages"] = normalized
        catalog[item_id] = item
    return catalog


def merge_catalogs(*catalogs: dict[str, dict]) -> dict[str, dict]:
    merged = {}
    package_owners = {}
    for catalog in catalogs:
        for item_id, item in catalog.items():
            if item_id in merged:
                raise SystemExit(f"duplicate catalog id across package catalogs: {item_id}")
            for package in item["packages"]:
                if package in package_owners:
                    raise SystemExit(f"duplicate package across package catalogs: {package}")
                package_owners[package] = item_id
            merged[item_id] = item
    return merged


def load_profiles(repo_catalog: dict[str, dict]) -> list[dict]:
    profiles = []
    names = set()
    for path in sorted(PROFILE_DIR.glob("*.json")):
        profile = read_json(path)
        required = {"name", "description", "selected", "critical", "items"}
        missing = required.difference(profile)
        if missing:
            raise SystemExit(f"{path.name}: eksik alanlar: {', '.join(sorted(missing))}")
        if profile["name"] in names:
            raise SystemExit(f"{path.name}: tekrar eden profil adi: {profile['name']}")
        if not isinstance(profile["items"], list):
            raise SystemExit(f"{path.name}: items liste olmali")
        names.add(profile["name"])
        packages = []
        package_set = set()
        expanded = []
        for item_id in profile["items"]:
            if item_id not in repo_catalog:
                raise SystemExit(f"{path.name}: bilinmeyen repo kimligi: {item_id}")
            item = repo_catalog[item_id]
            expanded.append(item)
            for package in item["packages"]:
                if package in package_set:
                    continue
                package_set.add(package)
                packages.append(package)
        profile["packages"] = packages
        profile["resolvedItems"] = expanded
        profiles.append(profile)
    return profiles


def load_presets(profiles: list[dict], external_catalog: dict[str, dict]) -> list[dict]:
    presets = []
    profile_names = {profile["name"]: profile for profile in profiles}
    seen = set()
    for path in sorted(PRESET_DIR.glob("*.json")):
        preset = read_json(path)
        required = {"id", "label", "description", "profiles", "externalItems"}
        missing = required.difference(preset)
        if missing:
            raise SystemExit(f"{path.name}: eksik alanlar: {', '.join(sorted(missing))}")
        if preset["id"] in seen:
            raise SystemExit(f"{path.name}: tekrar eden preset kimligi: {preset['id']}")
        seen.add(preset["id"])
        repo_packages = []
        repo_seen = set()
        for profile_name in preset["profiles"]:
            if profile_name not in profile_names:
                raise SystemExit(f"{path.name}: bilinmeyen profil: {profile_name}")
            for package in profile_names[profile_name]["packages"]:
                if package in repo_seen:
                    continue
                repo_seen.add(package)
                repo_packages.append(package)
        external_items = []
        for item_id in preset["externalItems"]:
            if item_id not in external_catalog:
                raise SystemExit(f"{path.name}: bilinmeyen external kimligi: {item_id}")
            external_items.append(external_catalog[item_id])
        preset["repoPackages"] = repo_packages
        preset["resolvedExternalItems"] = external_items
        presets.append(preset)
    return presets


def load_service_hints(repo_catalog: dict[str, dict]) -> list[dict]:
    items = read_json(SERVICE_CATALOG)
    if not isinstance(items, list):
        raise SystemExit("services.json: liste bekleniyor")
    hints = []
    for item in items:
        item_id = item.get("itemId")
        if item_id not in repo_catalog:
            raise SystemExit(f"services.json: bilinmeyen itemId: {item_id}")
        hints.append(
            {
                "itemId": item_id,
                "label": repo_catalog[item_id]["label"],
                "packages": repo_catalog[item_id]["packages"],
                "systemServices": item.get("systemServices", []),
                "userServices": item.get("userServices", []),
                "groups": item.get("groups", []),
            }
        )
    return hints


def load_offline_bundles(profiles: list[dict], external_catalog: dict[str, dict]) -> list[dict]:
    items = read_json(OFFLINE_BUNDLE_CATALOG)
    if not isinstance(items, list):
        raise SystemExit("bundles.json: liste bekleniyor")
    profile_names = {profile["name"]: profile for profile in profiles}
    bundles = []
    seen = set()
    for item in items:
        required = {"id", "label", "description", "profiles", "externalItems"}
        missing = required.difference(item)
        if missing:
            raise SystemExit(f"bundles.json: eksik alanlar: {', '.join(sorted(missing))}")
        if item["id"] in seen:
            raise SystemExit(f"bundles.json: tekrar eden bundle kimligi: {item['id']}")
        seen.add(item["id"])
        packages = []
        package_set = set()
        for profile_name in item["profiles"]:
            if profile_name not in profile_names:
                raise SystemExit(f"bundles.json: bilinmeyen profil: {profile_name}")
            for package in profile_names[profile_name]["packages"]:
                if package in package_set:
                    continue
                package_set.add(package)
                packages.append(package)
        external_items = []
        for item_id in item["externalItems"]:
            if item_id not in external_catalog:
                raise SystemExit(f"bundles.json: bilinmeyen external kimligi: {item_id}")
            external_items.append(external_catalog[item_id])
        item["repoPackages"] = packages
        item["resolvedExternalItems"] = external_items
        bundles.append(item)
    return bundles


def render_netinstall(profiles: list[dict]) -> str:
    blocks = []
    for profile in profiles:
        lines = [
            f'- name: {yaml_quote(profile["name"])}',
            f'  description: {yaml_quote(profile["description"])}',
            f'  selected: {"true" if profile["selected"] else "false"}',
            f'  critical: {"true" if profile["critical"] else "false"}',
            "  packages:",
        ]
        if profile["packages"]:
            lines.extend(f"    - {yaml_quote(package)}" for package in profile["packages"])
        else:
            lines.append("    []")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def build_dist(project: dict, profiles: list[dict], external_catalog: dict[str, dict], presets: list[dict], service_hints: list[dict], offline_bundles: list[dict], netinstall_text: str) -> None:
    dist_root = ROOT / project["distRoot"]
    if dist_root.exists():
        shutil.rmtree(dist_root)
    etc_calamares = dist_root / "etc" / "calamares"
    etc_pacman = dist_root / "etc" / "pacman.conf.d"
    modules_dir = etc_calamares / "modules"
    branding_dst = etc_calamares / "branding" / project["branding"]
    manifests_dir = dist_root / "usr" / "share" / "nullcalamares" / "manifests"
    offline_dir = dist_root / "usr" / "share" / "nullcalamares" / "offline"
    autostart_dir = dist_root / "etc" / "skel" / ".config" / "autostart"
    bin_dir = dist_root / "usr" / "local" / "bin"
    modules_dir.mkdir(parents=True, exist_ok=True)
    etc_pacman.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    offline_dir.mkdir(parents=True, exist_ok=True)
    autostart_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    copy_tree(BRANDING_DIR / project["branding"], branding_dst)
    shutil.copy2(ROOT / "settings.conf", etc_calamares / "settings.conf")
    shutil.copy2(MODULE_DIR / "netinstall.conf", modules_dir / "netinstall.conf")
    shutil.copy2(MODULE_DIR / "packages.conf", modules_dir / "packages.conf")
    (modules_dir / "netinstall.yaml").write_text(netinstall_text, encoding="utf-8")
    external_payload = {
        "generatedBy": project["id"],
        "productName": project["productName"],
        "items": list(external_catalog.values())
    }
    preset_payload = {
        "generatedBy": project["id"],
        "productName": project["productName"],
        "presets": [
            {
                "id": preset["id"],
                "label": preset["label"],
                "description": preset["description"],
                "profiles": preset["profiles"],
                "repoPackages": preset["repoPackages"],
                "externalItems": [item["id"] for item in preset["resolvedExternalItems"]]
            }
            for preset in presets
        ]
    }
    service_payload = {
        "generatedBy": project["id"],
        "productName": project["productName"],
        "items": service_hints
    }
    offline_payload = {
        "generatedBy": project["id"],
        "productName": project["productName"],
        "bundles": [
            {
                "id": bundle["id"],
                "label": bundle["label"],
                "description": bundle["description"],
                "profiles": bundle["profiles"],
                "repoPackages": bundle["repoPackages"],
                "externalItems": [item["id"] for item in bundle["resolvedExternalItems"]]
            }
            for bundle in offline_bundles
        ]
    }
    capabilities_payload = {
        "generatedBy": project["id"],
        "productName": project["productName"],
        "installerModes": project["installerModes"],
        "netinstall": {
            "groupsSource": "file:///etc/calamares/modules/netinstall.yaml",
            "supportsOfflineUi": True,
            "supportsOfflinePackages": True
        }
    }
    aur_helpers_payload = {
        "generatedBy": project["id"],
        "productName": project["productName"],
        "items": read_json(AUR_HELPERS_CATALOG)
    }
    offline_package_list = []
    offline_package_set = set()
    for bundle in offline_bundles:
        for package in bundle["repoPackages"]:
            if package in offline_package_set:
                continue
            offline_package_set.add(package)
            offline_package_list.append(package)
    summary_payload = {
        "project": project["id"],
        "branding": project["branding"],
        "profiles": [
            {
                "name": profile["name"],
                "items": [item["id"] for item in profile["resolvedItems"]],
                "packages": profile["packages"]
            }
            for profile in profiles
        ],
        "repoPackageCount": len({package for profile in profiles for package in profile["packages"]}),
        "externalPackageCount": len(external_catalog),
        "presetCount": len(presets),
        "serviceHintCount": len(service_hints),
        "offlineBundleCount": len(offline_bundles),
        "offlineRepoPackageCount": len(offline_package_list)
    }
    offline_repo_conf = "\n".join([
        "[null-offline]",
        f"Server = file://{project['installerModes']['offlineRepoPath']}"
    ]) + "\n"
    offline_package_text = "\n".join(offline_package_list) + "\n"
    mode_script = "\n".join([
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "if ping -c 1 -W 1 archlinux.org >/dev/null 2>&1; then",
        '  printf "online\\n"',
        "else",
        '  printf "offline\\n"',
        "fi"
    ]) + "\n"
    launcher = "\n".join([
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"manifest={json.dumps(project['nullWelcome']['manifestPath'])}",
        f"presets={json.dumps(project['nullWelcome']['presetPath'])}",
        f"services={json.dumps(project['nullWelcome']['servicePath'])}",
        f"command={json.dumps(project['nullWelcome']['command'])}",
        'if ! command -v "$command" >/dev/null 2>&1; then',
        "  exit 0",
        "fi",
        'exec "$command" --manifest "$manifest" --presets "$presets" --services "$services"'
    ]) + "\n"
    desktop = "\n".join([
        "[Desktop Entry]",
        "Type=Application",
        "Version=1.0",
        "Name=NullWelcome First Boot",
        "Exec=/usr/local/bin/nullwelcome-firstboot",
        "Terminal=false",
        "X-GNOME-Autostart-enabled=true",
        "NoDisplay=true"
    ]) + "\n"
    launcher_path = bin_dir / "nullwelcome-firstboot"
    launcher_path.write_text(launcher, encoding="utf-8")
    launcher_path.chmod(0o755)
    mode_path = bin_dir / "nullcalamares-netmode"
    mode_path.write_text(mode_script, encoding="utf-8")
    mode_path.chmod(0o755)
    (autostart_dir / "nullwelcome.desktop").write_text(desktop, encoding="utf-8")
    write_json(manifests_dir / "external-apps.json", external_payload)
    write_json(manifests_dir / "presets.json", preset_payload)
    write_json(manifests_dir / "service-hints.json", service_payload)
    write_json(manifests_dir / "offline-bundles.json", offline_payload)
    write_json(manifests_dir / "installer-capabilities.json", capabilities_payload)
    write_json(manifests_dir / "aur-helpers.json", aur_helpers_payload)
    for path in sorted(CURATED_DIR.glob("*.json")):
        write_json(manifests_dir / path.name, read_json(path))
    (etc_pacman / "null-offline-repo.conf").write_text(offline_repo_conf, encoding="utf-8")
    (offline_dir / "package-list.txt").write_text(offline_package_text, encoding="utf-8")
    write_json(ROOT / "dist" / "build-summary.json", summary_payload)


def main() -> None:
    project = read_json(PROJECT)
    repo_catalog = merge_catalogs(
        load_package_catalog(REPO_CATALOG, {"repo"}),
        load_package_catalog(USER_REPO_CATALOG, {"repo"})
    )
    external_catalog = merge_catalogs(
        load_package_catalog(EXTERNAL_CATALOG, {"aur", "manual"}),
        load_package_catalog(USER_EXTERNAL_CATALOG, {"aur", "manual"})
    )
    profiles = load_profiles(repo_catalog)
    presets = load_presets(profiles, external_catalog)
    service_hints = load_service_hints(repo_catalog)
    offline_bundles = load_offline_bundles(profiles, external_catalog)
    netinstall_text = render_netinstall(profiles)
    (MODULE_DIR / "netinstall.yaml").write_text(netinstall_text, encoding="utf-8")
    build_dist(project, profiles, external_catalog, presets, service_hints, offline_bundles, netinstall_text)


if __name__ == "__main__":
    main()
