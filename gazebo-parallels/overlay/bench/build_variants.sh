#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
set +u
source /opt/ros/jazzy/setup.bash
set -u
echo '5bfe18d164414e098b2ba6ef81bf9391f7ff8f2c39b8a4fa9f8543f778e921c8  gz-rendering-8.2.3.tar.gz' | sha256sum -c -
mkdir -p source
if [ ! -f source/CMakeLists.txt ]; then tar -xf gz-rendering-8.2.3.tar.gz -C source --strip-components=1; fi
cp OgreLight.original.cc source/ogre/src/OgreLight.cc
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release > configure.log 2>&1
for variant in stock center uv center_uv pad2 pad3 upstream upstream_uv; do
 cp "variants/$variant/OgreGpuRays.cc" source/ogre/src/OgreGpuRays.cc
 cmake --build build --parallel 3 > "variants/$variant/build.log" 2>&1
 cp build/libgz-rendering8-ogre.so "variants/$variant/libgz-rendering-ogre.so"
 echo "Built $variant"
done
