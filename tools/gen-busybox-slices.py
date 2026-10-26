#!/usr/bin/env python3
# Generate images/ubuntu-runtime/slices/busybox.yaml: one symlink per busybox
# applet. Applet paths that another release package declares keep their
# alternate /bin or /sbin spelling, which resolves to the same physical file
# through the usrmerge symlinks. Paths colliding under all spellings are
# dropped and reported.
#
# The essential blocks stay out of the file: the cut spec lists the needed
# slices, and the block form differs between release formats (v1 list, v3
# map).
#
# Usage: gen-busybox-slices.py <workdir> <applet-list-file> <output>
#        <release-dir>...
import re
import sys
from pathlib import Path

APPLET_PATH = "/usr/bin/busybox"


def checked(base: Path, value: str, *, exists: bool) -> Path:
    """Resolve value and confine it to the work directory."""
    raw = Path(value)
    target = base / raw
    if raw.is_absolute():
        target = raw
    try:
        resolved = target.resolve(strict=exists)
    except FileNotFoundError as err:
        raise SystemExit(f"path {value} does not exist: {err}") from err
    if resolved != base and not resolved.is_relative_to(base):
        raise SystemExit(f"path {value} escapes the work directory {base}")
    return resolved


def entries(source: Path):
    """Path declarations of one chisel-releases slice file."""
    text = source.read_text(encoding="utf-8-sig")
    match = re.search(r"^package:\s*(\S+)", text, re.MULTILINE)
    if not match:
        return
    pkg = match.group(1)
    for line in text.splitlines():
        entry = re.match(r"^(\s+)(/[^:\s]+):\s*(\{[^}]*\})?\s*(#.*)?$", line)
        if not entry:
            if re.search(r"^\s*/", line):
                print(f"WARN unparsed in {source}: {line.strip()}")
            continue
        yield pkg, entry.group(2), entry.group(3) or ""


def alternate(path):
    """Alternate textual spelling with a different physical location."""
    for src, dst in (
        ("/usr/bin/", "/sbin/"),
        ("/sbin/", "/usr/bin/"),
        ("/usr/sbin/", "/bin/"),
        ("/bin/", "/usr/sbin/"),
    ):
        if path.startswith(src):
            return dst + path[len(src):]
    return None


def main():
    workdir, applet_list, output, releases = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
    if not workdir or not applet_list or not output or not releases:
        raise SystemExit(
            "usage: gen-busybox-slices.py <workdir> <applet-list-file> "
            "<output> <release-dir>..."
        )
    base = Path(workdir).resolve()
    applets_file = checked(base, applet_list, exists=True)
    with applets_file.open(encoding="utf-8") as f:
        applets = ["/" + line.strip() for line in f if line.strip()]
    declarers = {}
    for release_value in releases:
        release = checked(base, release_value, exists=True)
        for source in sorted(release.glob("slices/*.yaml")):
            for pkg, path_entry, opts in entries(source):
                if pkg == "busybox":
                    continue
                declarers.setdefault(path_entry, set()).add(pkg)
    used = set()
    lines = [f"      {APPLET_PATH}:\n"]
    dropped = []
    for path_entry in applets:
        if path_entry == APPLET_PATH:
            continue
        chosen = None
        if path_entry not in declarers:
            chosen = path_entry
        else:
            alt = alternate(path_entry)
            if alt and alt not in declarers:
                chosen = alt
        if chosen is None or chosen in used:
            dropped.append((path_entry, sorted(declarers.get(path_entry, []))))
            continue
        used.add(chosen)
        lines.append(f"      {chosen}: {{symlink: /usr/bin/busybox}}\n")
    header = (
        "# Busybox slice for the ContainerHive chisel build backend.\n"
        "# Upstream base: canonical/chisel-releases (slices/busybox.yaml).\n"
        "# One symlink per busybox applet, so the cut installs the applets\n"
        "# like the old post-cut `busybox --install` instruction. Applet\n"
        "# paths that another release package declares keep their alternate\n"
        "# /bin or /sbin spelling, which resolves to the same physical file\n"
        "# through the usrmerge symlinks. The essential blocks are omitted:\n"
        "# the cut spec lists the needed slices, and the block form differs\n"
        "# between release formats.\n"
        "# Regenerate with tools/enumerate-applets.sh.\n\n"
        "package: busybox\n\n"
        "slices:\n"
        "  bins:\n"
        "    contents:\n"
    )
    footer = (
        "\n"
        "  copyright:\n"
        "    contents:\n"
        "      /usr/share/doc/busybox/copyright:\n"
    )
    target = checked(base, output, exists=False)
    with target.open("w", encoding="utf-8") as out:
        out.write(header)
        out.writelines(lines)
        out.write(footer)
    print(f"applets={len(applets)} written={len(lines)} dropped={len(dropped)}")
    for path_entry, others in dropped:
        print(f"  dropped {path_entry} (declared by: {', '.join(others)})")


if __name__ == "__main__":
    main()
