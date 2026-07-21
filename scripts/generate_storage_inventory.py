#!/usr/bin/env python3
"""Generate Atlas storage inventory files for the internal ecosystem portal."""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTAL = ROOT / "internal-portal"
INVENTORY_PATH = PORTAL / "storage-inventory.json"
HTML_PATH = PORTAL / "storage.html"
REGISTRY_PATH = ROOT / "ecosystem.json"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def human_size(value) -> str:
    try:
        n = float(value)
    except Exception:
        return str(value)
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(n) < 1024.0:
            return f"{n:.1f}{unit}" if unit != "B" else f"{int(n)}B"
        n /= 1024.0
    return f"{n:.1f}EB"


def symlink_map() -> dict[str, list[str]]:
    links: dict[str, list[str]] = {}
    for base in ["/dev/disk/by-id", "/dev/disk/by-path", "/dev/disk/by-label", "/dev/disk/by-uuid"]:
        root = Path(base)
        if not root.exists():
            continue
        for item in root.iterdir():
            try:
                target = str(item.resolve())
            except Exception:
                continue
            links.setdefault(target, []).append(str(item))
    return links


def df_usage() -> dict[str, dict]:
    usage: dict[str, dict] = {}
    lines = run(["df", "-B1", "-T", "-x", "tmpfs", "-x", "devtmpfs", "-x", "squashfs", "-x", "overlay"]).splitlines()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 7:
            continue
        fs, typ, size, used, avail, pct, mount = parts[:7]
        usage[mount] = {
            "filesystem": fs,
            "type": typ,
            "sizeBytes": int(size),
            "usedBytes": int(used),
            "availableBytes": int(avail),
            "usePercent": pct,
        }
    return usage


def top_contents(mount: str) -> list[dict]:
    path = Path(mount)
    if not path.exists():
        return []
    contents: list[dict] = []
    try:
        proc = subprocess.run(
            ["du", "-B1", "-x", "--max-depth=1", mount],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=120,
            check=False,
        )
        sizes: dict[str, int] = {}
        if proc.returncode == 0:
            for line in proc.stdout.splitlines():
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    sizes[parts[1]] = int(parts[0])
        with os.scandir(mount) as entries:
            for entry in entries:
                if entry.name in {".Trash-1000", "lost+found"}:
                    continue
                entry_path = str(Path(mount) / entry.name)
                try:
                    stat = entry.stat(follow_symlinks=False)
                    kind = "directory" if entry.is_dir(follow_symlinks=False) else "file"
                except Exception:
                    stat = None
                    kind = "unknown"
                contents.append({
                    "name": entry.name,
                    "path": entry_path,
                    "kind": kind,
                    "sizeBytes": sizes.get(entry_path, stat.st_size if stat else None),
                })
    except Exception as exc:
        contents.append({"error": f"{type(exc).__name__}: {exc}"})
    contents.sort(key=lambda item: item.get("sizeBytes") or 0, reverse=True)
    return contents[:40]


def flatten_devices(dev: dict, links: dict[str, list[str]], usage: dict[str, dict], parent: str | None = None, disk: str | None = None):
    current_disk = dev.get("path") if dev.get("type") == "disk" else disk
    mounts = [m for m in (dev.get("mountpoints") or []) if m]
    rec = {key: dev.get(key) for key in [
        "name", "kname", "path", "type", "size", "rota", "tran", "hotplug", "fstype", "fsver",
        "label", "uuid", "partlabel", "partuuid", "model", "vendor", "serial", "wwn", "state",
    ]}
    rec["sizeHuman"] = human_size(dev.get("size")) if isinstance(dev.get("size"), int) else str(dev.get("size"))
    rec["parent"] = parent
    rec["disk"] = current_disk
    rec["mountpoints"] = mounts
    device_path = str(dev.get("path") or "")
    rec["links"] = sorted(links.get(device_path, []))
    if mounts:
        rec["usage"] = {mount: usage.get(mount) for mount in mounts if usage.get(mount)}
        rec["topContents"] = {
            mount: top_contents(mount)
            for mount in mounts
            if mount == "/" or mount.startswith("/mnt/")
        }
    yield rec
    for child in dev.get("children") or []:
        yield from flatten_devices(child, links, usage, dev.get("path"), current_disk)


def proposed_names() -> dict[str, dict]:
    return {
        "/dev/mapper/ubuntu--vg-ubuntu--lv": {"filesystemLabel": "atlas-root", "why": "Root filesystem; optional ext4 label."},
        "/dev/sdb1": {"filesystemLabel": "ATLAS-EFI", "why": "EFI system partition; vfat label max 11 chars."},
        "/dev/sdb2": {"filesystemLabel": "atlas-boot", "why": "Boot partition."},
        "/dev/sde1": {"filesystemLabel": "atlas-data0", "why": "Mounted at /mnt/data; contains Documents plus Atlas data directories."},
        "/dev/sdf1": {"filesystemLabel": "atlas-data1", "why": "Mounted at /mnt/data1; mostly empty except atlas-vault-backups stub."},
        "/dev/sdc1": {"filesystemLabel": "atlas-data2", "why": "Mounted at /mnt/data2; current label data4 is misleading."},
        "/dev/sdd1": {"filesystemLabel": "atlas-data3", "why": "Mounted at /mnt/data3; mostly empty."},
        "/dev/sdg1": {"partitionLabel": "atlas-sabrent-a", "why": "Sabrent bridge slot 0:0; no filesystem detected, so use GPT partition label unless a filesystem is later found."},
        "/dev/sdh1": {"filesystemLabel": "atlas-sabrent-b", "partitionLabel": "atlas-sabrent-b", "why": "Sabrent bridge slot 0:1; ext4 filesystem currently labeled wd6tb-b."},
        "/dev/sda": {"logicalName": "atlas-perc-vd-spare-0", "why": "PERC virtual disk visible with no partitions/filesystem; requires sudo/PERC probe before use."},
    }


def missing_fstab_uuids(devices: list[dict]) -> list[dict]:
    known = {item.get("uuid") for item in devices if item.get("uuid")}
    missing: list[dict] = []
    for line in Path("/etc/fstab").read_text(errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "/dev/disk/by-uuid/" not in stripped:
            continue
        uuid = stripped.split()[0].split("/dev/disk/by-uuid/")[-1]
        if uuid not in known:
            missing.append({"uuid": uuid, "line": stripped})
    return missing


def build_inventory() -> dict:
    lsblk = json.loads(run([
        "lsblk", "-J", "-b", "-o",
        "NAME,KNAME,PATH,TYPE,SIZE,ROTA,TRAN,HOTPLUG,FSTYPE,FSVER,LABEL,UUID,PARTLABEL,PARTUUID,MOUNTPOINTS,MODEL,VENDOR,SERIAL,WWN,STATE",
    ]))
    links = symlink_map()
    usage = df_usage()
    devices: list[dict] = []
    for dev in lsblk["blockdevices"]:
        if dev.get("type") in {"loop", "rom"}:
            continue
        devices.extend(flatten_devices(dev, links, usage))
    proposed = proposed_names()
    for item in devices:
        if item["path"] in proposed:
            item["proposedName"] = proposed[item["path"]]
    logical = [
        item for item in devices
        if item["type"] in {"disk", "part", "lvm"}
        and (item.get("mountpoints") or item.get("fstype") or item.get("proposedName") or item["path"] in {"/dev/sdg", "/dev/sdh"})
    ]
    return {
        "schema": "drewbefree.atlas.storage.v1",
        "host": "atlas",
        "generatedAt": dt.datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "linuxVisibleDisks": len([item for item in devices if item["type"] == "disk"]),
            "percVirtualDisksVisible": len([item for item in devices if item["type"] == "disk" and "PERC" in (item.get("model") or "")]),
            "sabrentDisksVisible": len([item for item in devices if item["type"] == "disk" and (item.get("vendor") or "").strip() == "Sabrent"]),
            "mountedDataVolumes": [item["path"] for item in devices if item.get("mountpoints") and any(str(m).startswith("/mnt/data") for m in item.get("mountpoints", []))],
            "note": "Linux currently sees PERC virtual disks, not the physical internal bay members. Drew expects 8 internal physical drives; that requires sudo + PERC/SMART probing.",
        },
        "limitations": [
            "No sudo available in this Hermes session, so raw block probing, read-only mounting of unmounted externals, and PERC physical bay enumeration were not performed.",
            "The Sabrent bridge reports duplicate serial/WWN values for both slots; use USB path slot 0:0 vs 0:1 and filesystem/partition labels instead of by-id WWN for identity.",
            "/dev/sdg1 has a partition but no filesystem was detected by lsblk/blkid without sudo; contents are unknown until sudo wipefs/blkid/read-only mount confirms it.",
        ],
        "devices": devices,
        "logicalDevices": logical,
        "fstabMissingUuidEntries": missing_fstab_uuids(devices),
        "recommendedCommands": {
            "readOnlyProbeBeforeNaming": [
                "sudo wipefs -n /dev/sdg",
                "sudo wipefs -n /dev/sdg1",
                "sudo blkid -p /dev/sdg1 || true",
                "sudo parted -s /dev/sdg print",
                "sudo smartctl -i /dev/sdg",
                "sudo smartctl -i /dev/sdh",
            ],
            "setFilesystemAndPartitionNames": [
                "sudo e2label /dev/mapper/ubuntu--vg-ubuntu--lv atlas-root",
                "sudo fatlabel /dev/sdb1 ATLAS-EFI",
                "sudo e2label /dev/sdb2 atlas-boot",
                "sudo e2label /dev/sde1 atlas-data0",
                "sudo e2label /dev/sdf1 atlas-data1",
                "sudo e2label /dev/sdc1 atlas-data2",
                "sudo e2label /dev/sdd1 atlas-data3",
                "sudo parted /dev/sdg name 1 atlas-sabrent-a",
                "sudo e2label /dev/sdh1 atlas-sabrent-b",
                "sudo parted /dev/sdh name 1 atlas-sabrent-b",
                "sudo udevadm trigger",
                "lsblk -o NAME,PATH,SIZE,FSTYPE,LABEL,PARTLABEL,UUID,MOUNTPOINTS,MODEL,SERIAL,WWN",
            ],
            "percPhysicalDriveDiscovery": [
                "sudo smartctl --scan-open",
                "for n in $(seq 0 15); do echo \"=== megaraid,$n ===\"; sudo smartctl -i -d megaraid,$n /dev/sda 2>/dev/null | sed -n \"1,35p\"; done",
                "sudo apt-get update && sudo apt-get install -y storcli || true",
                "sudo storcli /c0 /eall /sall show all",
            ],
            "readOnlyExternalMountExample": [
                "sudo mkdir -p /mnt/probe-sabrent-b",
                "sudo mount -o ro,noload /dev/sdh1 /mnt/probe-sabrent-b",
                "find /mnt/probe-sabrent-b -maxdepth 2 -mindepth 1 -printf \"%y %s %p\\n\" | sort | sed -n \"1,120p\"",
                "sudo umount /mnt/probe-sabrent-b",
            ],
        },
    }


def render_html(inventory: dict) -> str:
    rows: list[str] = []
    for item in inventory["logicalDevices"]:
        mounts = []
        for mount in item.get("mountpoints") or []:
            usage = (item.get("usage") or {}).get(mount)
            if usage:
                mounts.append(
                    f'<div><code>{html.escape(mount)}</code> <span class="pill ok">{usage["usePercent"]} used</span>'
                    f'<br><span class="muted">{human_size(usage["usedBytes"])} used / {human_size(usage["availableBytes"])} free</span></div>'
                )
            else:
                mounts.append(f'<div><code>{html.escape(mount)}</code></div>')
        mount_html = "".join(mounts) if mounts else '<span class="muted">not mounted</span>'
        current_bits = [
            f'<code>{html.escape(item["path"])}</code>',
            f'<span class="muted">{html.escape(item.get("type") or "")} · {html.escape(item.get("sizeHuman") or "")}</span>',
        ]
        for label in [item.get("fstype"), item.get("label") and f'label {item.get("label")}', item.get("partlabel") and f'part {item.get("partlabel")}', item.get("uuid") and "uuid present"]:
            if label:
                current_bits.append(f'<span class="pill">{html.escape(label)}</span>')
        proposed = item.get("proposedName") or {}
        proposed_bits = []
        for key in ["logicalName", "filesystemLabel", "partitionLabel"]:
            if proposed.get(key):
                proposed_bits.append(f'<span class="pill ok">{html.escape(key)}: {html.escape(proposed[key])}</span>')
        proposed_html = "".join(proposed_bits) + (f'<div class="muted">{html.escape(proposed.get("why", ""))}</div>' if proposed else '<span class="muted">no change proposed</span>')
        content_bits = []
        for mount, entries in (item.get("topContents") or {}).items():
            for entry in entries[:8]:
                if "error" in entry:
                    content_bits.append(f'<span>{html.escape(entry["error"])}</span>')
                else:
                    content_bits.append(f'<span>{html.escape(entry["name"])} · {human_size(entry.get("sizeBytes"))}</span>')
        contents_html = f'<div class="contents">{"".join(content_bits)}</div>' if content_bits else '<span class="muted">not verified from current mount</span>'
        hardware = "<br>".join(html.escape(x) for x in [
            item.get("vendor") and f'vendor {str(item.get("vendor")).strip()}',
            item.get("model") and f'model {str(item.get("model")).strip()}',
            item.get("serial") and f'serial {str(item.get("serial")).strip()}',
            item.get("wwn") and f'wwn {str(item.get("wwn")).strip()}',
        ] if x)
        slot_links = [link for link in item.get("links", []) if "by-path" in link or "Sabrent" in link or "by-label" in link]
        if slot_links:
            hardware += '<br><span class="muted">' + '<br>'.join(html.escape(link) for link in slot_links[:4]) + '</span>'
        rows.append(
            f'<tr><td>{"<br>".join(current_bits)}</td><td>{html.escape(item.get("label") or item.get("partlabel") or item.get("uuid") or "unlabeled")}</td><td>{proposed_html}</td><td>{mount_html}</td><td>{contents_html}</td><td>{hardware}</td></tr>'
        )

    limitations = "".join(f'<tr><td><span class="pill warn">needs verification</span></td><td>{html.escape(item)}</td></tr>' for item in inventory["limitations"])
    stale = "".join(f'<tr><td><span class="pill warn">stale fstab</span></td><td><code>{html.escape(item["uuid"])}</code><br>{html.escape(item["line"])}</td></tr>' for item in inventory["fstabMissingUuidEntries"])
    label_commands = html.escape("\n".join(inventory["recommendedCommands"]["setFilesystemAndPartitionNames"]))
    probe_commands = html.escape("\n".join(inventory["recommendedCommands"]["readOnlyProbeBeforeNaming"]))
    perc_commands = html.escape("\n".join(inventory["recommendedCommands"]["percPhysicalDriveDiscovery"]))
    mount_commands = html.escape("\n".join(inventory["recommendedCommands"]["readOnlyExternalMountExample"]))

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Atlas Drive Map</title>
  <style>
    :root {{ --bg:#f4f7fb; --panel:#fff; --ink:#172033; --muted:#64748b; --line:#dbe4f0; --blue:#2563eb; --green:#059669; --amber:#d97706; --rose:#e11d48; --shadow:0 18px 48px rgba(15,23,42,.10); }}
    * {{ box-sizing:border-box; }} body {{ margin:0; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:linear-gradient(135deg,#eef4ff,#fbfdff 45%,#eef7f1); }}
    header {{ position:sticky; top:0; z-index:5; padding:18px 22px; display:flex; gap:16px; align-items:center; justify-content:space-between; background:rgba(255,255,255,.82); border-bottom:1px solid var(--line); backdrop-filter:blur(18px); }}
    h1 {{ margin:0; font-size:clamp(1.35rem,3vw,2.2rem); letter-spacing:-.05em; }} .sub {{ margin:4px 0 0; color:var(--muted); }} main {{ padding:22px; max-width:1500px; margin:0 auto; }}
    .nav {{ display:flex; gap:10px; flex-wrap:wrap; }} a.btn {{ display:inline-flex; align-items:center; min-height:38px; padding:0 14px; border:1px solid var(--line); border-radius:999px; background:#fff; color:var(--ink); text-decoration:none; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:18px 0; }} .card {{ background:rgba(255,255,255,.88); border:1px solid var(--line); border-radius:22px; padding:16px; box-shadow:var(--shadow); }} .card strong {{ display:block; font-size:1.55rem; }} .card span {{ color:var(--muted); font-size:.88rem; }}
    .section {{ margin:22px 0; }} .section h2 {{ margin:0 0 10px; letter-spacing:-.03em; }} .table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:22px; background:#fff; box-shadow:var(--shadow); }} table {{ width:100%; border-collapse:collapse; min-width:980px; }} th,td {{ padding:11px 12px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; font-size:.92rem; }} th {{ position:sticky; top:76px; z-index:2; background:#f8fafc; color:#334155; }} tr:hover td {{ background:#f8fbff; }} code {{ padding:2px 5px; border-radius:7px; background:#eef2ff; color:#1e3a8a; }}
    .pill {{ display:inline-flex; padding:3px 8px; border-radius:999px; font-weight:750; font-size:.75rem; background:#eef2ff; color:#1e40af; margin:2px 3px 2px 0; }} .ok {{ background:#dcfce7; color:#166534; }} .warn {{ background:#fef3c7; color:#92400e; }} .muted {{ color:var(--muted); }} .contents {{ display:flex; flex-wrap:wrap; gap:6px; }} .contents span {{ background:#f1f5f9; border:1px solid #e2e8f0; border-radius:999px; padding:4px 8px; font-size:.8rem; }} pre {{ margin:0; padding:16px; overflow:auto; background:#0f172a; color:#e2e8f0; border-radius:18px; }} details {{ background:#fff; border:1px solid var(--line); border-radius:18px; padding:12px 14px; box-shadow:var(--shadow); }} summary {{ cursor:pointer; font-weight:850; }}
    @media (max-width:900px) {{ header {{ align-items:flex-start; flex-direction:column; }} .grid {{ grid-template-columns:1fr 1fr; }} main {{ padding:14px; }} th {{ top:0; }} }} @media (max-width:560px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<header>
  <div><h1>Atlas Drive Map</h1><p class="sub">Live inventory snapshot from Atlas · generated {html.escape(inventory['generatedAt'])}</p></div>
  <nav class="nav"><a class="btn" href="launcher.html">Launcher</a><a class="btn" href="world.html">World</a><a class="btn" href="ecosystem.json">Registry</a><a class="btn" href="storage-inventory.json">Raw JSON</a></nav>
</header>
<main>
  <section class="grid">
    <div class="card"><strong>{inventory['summary']['linuxVisibleDisks']}</strong><span>Linux-visible disks</span></div>
    <div class="card"><strong>{inventory['summary']['percVirtualDisksVisible']}</strong><span>Dell PERC virtual disks</span></div>
    <div class="card"><strong>{inventory['summary']['sabrentDisksVisible']}</strong><span>Sabrent USB disks currently attached</span></div>
    <div class="card"><strong>{len(inventory['summary']['mountedDataVolumes'])}</strong><span>Mounted /mnt/data* volumes</span></div>
  </section>
  <section class="section"><h2>Known gaps / risk</h2><div class="table-wrap"><table><thead><tr><th>Status</th><th>Detail</th></tr></thead><tbody>{limitations}{stale}</tbody></table></div></section>
  <section class="section"><h2>Drive / volume map</h2><div class="table-wrap"><table><thead><tr><th>Device</th><th>Current identity</th><th>Proposed name</th><th>Mount / usage</th><th>Contents verified</th><th>Hardware identity</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
  <section class="section"><h2>Commands to apply names</h2><details open><summary>Safe label commands after read-only probe</summary><pre>{label_commands}</pre></details></section>
  <section class="section"><h2>Commands to finish unknowns</h2><div style="display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(280px,1fr));"><details open><summary>Read-only probe Sabrent A before naming</summary><pre>{probe_commands}</pre></details><details><summary>Enumerate physical PERC bays</summary><pre>{perc_commands}</pre></details><details><summary>Read-only inspect unmounted Sabrent B contents</summary><pre>{mount_commands}</pre></details></div></section>
</main>
</body>
</html>
'''


def update_registry() -> None:
    registry = json.loads(REGISTRY_PATH.read_text())
    registry["updatedAt"] = dt.date.today().isoformat()
    if "live Atlas storage inventory scan" not in registry.get("generatedFrom", []):
        registry.setdefault("generatedFrom", []).append("live Atlas storage inventory scan")
    service = {
        "id": "atlas-storage-map",
        "name": "Atlas Storage Map",
        "type": "storage-inventory",
        "host": "atlas",
        "visibility": "private",
        "summary": "Live drive and mount map for Atlas: PERC virtual disks, mounted /mnt/data volumes, Sabrent external bays, proposed labels, known contents, and sudo commands needed for physical bay discovery.",
        "liveUrls": ["http://atlas/ecosystem/storage.html"],
        "docs": [{"label": "Raw storage inventory JSON", "url": "http://atlas/ecosystem/storage-inventory.json"}],
        "deployTargets": [{"type": "nginx-static", "host": "atlas", "path": "/opt/homelab-status-dashboard/ecosystem/storage.html", "url": "http://atlas/ecosystem/storage.html"}],
        "statusControl": {"state": "generated", "actions": ["open", "review", "update"]},
    }
    services = registry.setdefault("services", [])
    for idx, item in enumerate(services):
        if item.get("id") == "atlas-storage-map":
            services[idx] = service
            break
    else:
        services.append(service)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n")


def main() -> None:
    PORTAL.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory()
    INVENTORY_PATH.write_text(json.dumps(inventory, indent=2) + "\n")
    HTML_PATH.write_text(render_html(inventory))
    update_registry()
    print(json.dumps({
        "inventory": str(INVENTORY_PATH),
        "html": str(HTML_PATH),
        "registry": str(REGISTRY_PATH),
        "summary": inventory["summary"],
        "fstabMissingUuidEntries": inventory["fstabMissingUuidEntries"],
    }, indent=2))


if __name__ == "__main__":
    main()
