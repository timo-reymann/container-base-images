#!/usr/bin/env bash
# Regenerate images/ubuntu-runtime/slices/busybox.yaml. See the file header
# for the design. Needs docker.
#
# Usage: tools/enumerate-applets.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SLICES_DIR="$REPO/images/ubuntu-runtime/slices"
CHISEL_IMAGE=ghcr.io/containerhive/helper-images/chisel:1.5
PYTHON_IMAGE=python:3-slim
RELEASES=(ubuntu-24.04 ubuntu-26.04)

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK" 2>/dev/null || true' EXIT

# Clone the release branches and cut a plain rootfs to list the applets.
docker run --rm --entrypoint sh \
  --user "$(id -u):$(id -g)" \
  -e RELEASES="${RELEASES[*]}" \
  -e XDG_CACHE_HOME=/work/cache \
  -v "$WORK:/work" \
  "$CHISEL_IMAGE" -c '
    set -eu
    git clone --depth 1 -b "ubuntu-24.04" https://github.com/canonical/chisel-releases /work/ubuntu-24.04
    git clone --depth 1 -b "ubuntu-26.04" https://github.com/canonical/chisel-releases /work/ubuntu-26.04
    rm -rf /work/plain-rootfs
    mkdir -p /work/plain-rootfs
    chisel cut --release /work/ubuntu-24.04 --root /work/plain-rootfs --arch amd64 \
      base-files_base base-files_copyright base-passwd_data base-files_release-info \
      busybox_bins busybox_copyright ca-certificates_copyright ca-certificates_data-with-certs \
      libc6_copyright libc6_libs tzdata_zoneinfo tzdata_copyright >/dev/null 2>&1
    /work/plain-rootfs/usr/bin/busybox --list-full > /work/applets.txt
'

# Generate the slice file against the releases of every supported tag.
docker run --rm --entrypoint sh \
  --user "$(id -u):$(id -g)" \
  -e RELEASES="${RELEASES[*]}" \
  -v "$WORK:/work" -v "$REPO/tools:/tools" \
  "$PYTHON_IMAGE" -c '
    set -eu
    rel_dirs=""
    for release in $RELEASES; do
        rel_dirs="$rel_dirs /work/$release"
    done
    # shellcheck disable=SC2086
    python3 /tools/gen-busybox-slices.py /work /work/applets.txt /work/busybox.yaml $rel_dirs
'

mv "$WORK/busybox.yaml" "$SLICES_DIR/busybox.yaml"
echo "Regenerated $SLICES_DIR/busybox.yaml"
