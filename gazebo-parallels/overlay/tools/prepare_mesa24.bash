#!/usr/bin/env bash
# Download and extract packages into this folder. No dpkg installation, sudo or system writes.
set -euo pipefail
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $(dpkg --print-architecture) == arm64 ]] || { echo 'Requires arm64' >&2;exit 1; }
. /etc/os-release
[[ $ID == ubuntu && $VERSION_ID == 24.04 ]] || { echo 'Requires Ubuntu 24.04' >&2;exit 1; }
mkdir -p "$kit/mesa24/downloads" "$kit/mesa24/root"
cd "$kit/mesa24/downloads"
apt-get download libegl-mesa0=24.0.5-1ubuntu1 libgbm1=24.0.5-1ubuntu1 \
 libgl1-mesa-dri=24.0.5-1ubuntu1 libglapi-mesa=24.0.5-1ubuntu1 \
 libglx-mesa0=24.0.5-1ubuntu1 libllvm17t64=1:17.0.6-9ubuntu1 libxcb-dri2-0=1.15-1ubuntu2
for package in ./*.deb; do dpkg-deb -x "$package" "$kit/mesa24/root"; done
sha256sum ./*.deb > "$kit/mesa24/PACKAGE_SHA256SUMS"
echo 'Extracted private Mesa. The system packages were not changed.'
