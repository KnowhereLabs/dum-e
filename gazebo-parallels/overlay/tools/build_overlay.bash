#!/usr/bin/env bash
set -euo pipefail
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
set +u
source /opt/ros/jazzy/setup.bash
set -u
vendor_prefix=$(ros2 pkg prefix gz_rendering_vendor)
pc="$vendor_prefix/opt/gz_rendering_vendor/lib/pkgconfig/gz-rendering8.pc"
if [[ ! -f "$pc" || $(awk '/^Version:/ {print $2}' "$pc") != 8.2.3 ]]; then
  echo 'This pinned backport requires gz-rendering 8.2.3. See the guide for newer SDKs.' >&2; exit 1
fi
[[ $(pkg-config --modversion OGRE) == 1.9.0 ]] || { echo 'This backport was tested with OGRE 1.9.0.' >&2;exit 1; }
command -v colcon >/dev/null
if [[ ! -f "$kit/overlay/source/gz-rendering/CMakeLists.txt" ]]; then
  python3 "$kit/tools/prepare_sources.py"
fi
cd "$kit/overlay"
export CMAKE_BUILD_PARALLEL_LEVEL=2
export MAKEFLAGS=-j2
colcon build --packages-select gz_rendering_vendor --allow-overriding gz_rendering_vendor \
  --parallel-workers 1 --cmake-args \
  -DFORCE_BUILD_VENDOR_PKG=ON -DBUILD_TESTING=OFF \
  -DREVIEW_RENDERING_SOURCE="$kit/overlay/source/gz-rendering" \
  -DCMAKE_BUILD_TYPE=Release
