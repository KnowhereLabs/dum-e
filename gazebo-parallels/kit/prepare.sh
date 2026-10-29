#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [ "$(dpkg --print-architecture)" != arm64 ]; then
  echo 'STOP: questo kit richiede Ubuntu arm64.' >&2; exit 1
fi
. /etc/os-release
if [ "$ID" != ubuntu ] || [ "$VERSION_ID" != 24.04 ]; then
  echo 'STOP: questo kit richiede Ubuntu 24.04.' >&2; exit 1
fi
set +u
source /opt/ros/jazzy/setup.bash
set -u
sdk_pc=/opt/ros/jazzy/opt/gz_rendering_vendor/lib/pkgconfig/gz-rendering8.pc
if [ ! -f "$sdk_pc" ] || [ "$(awk '/^Version:/ {print $2}' "$sdk_pc")" != 8.2.3 ]; then
  echo 'STOP: SDK gz-rendering diverso da 8.2.3. Non forzare il kit.' >&2; exit 1
fi
if [ "$(pkg-config --modversion OGRE)" != 1.9.0 ]; then
  echo 'STOP: questo kit è stato compilato con OGRE 1.9.0.' >&2; exit 1
fi
phase=${1:-all}
case "$phase" in all|mesa|source|build|assemble) ;; *) echo 'Fasi: mesa, source, build, assemble, all' >&2;exit 1;; esac
mkdir -p build/downloads build/mesa-root build/src
if [ "$phase" = all ] || [ "$phase" = mesa ]; then
(
  cd build/downloads
  apt-get download \
    libegl-mesa0=24.0.5-1ubuntu1 \
    libgbm1=24.0.5-1ubuntu1 \
    libgl1-mesa-dri=24.0.5-1ubuntu1 \
    libglapi-mesa=24.0.5-1ubuntu1 \
    libglx-mesa0=24.0.5-1ubuntu1 \
    libllvm17t64=1:17.0.6-9ubuntu1 \
    libxcb-dri2-0=1.15-1ubuntu2
)
for package in build/downloads/*.deb; do
  dpkg-deb -x "$package" build/mesa-root
done
fi
if [ "$phase" = all ] || [ "$phase" = source ]; then
archive=build/downloads/gz-rendering-8.2.3.tar.gz
if [ ! -f "$archive" ]; then
  curl -fL --retry 3 \
    https://codeload.github.com/gazebosim/gz-rendering/tar.gz/refs/tags/gz-rendering8_8.2.3 \
    -o "$archive"
fi
python3 tools/check_source.py "$archive"
if [ ! -f build/src/.gazebo-virgl-patched ]; then
  if [ -f build/src/CMakeLists.txt ]; then
    echo 'STOP: sorgenti presenti senza marcatore. Usa una nuova copia del kit.' >&2; exit 1
  fi
  tar -xzf "$archive" -C build/src --strip-components=1
  patch -d build/src -p1 --forward < sources/gazebo-virgl.patch
  touch build/src/.gazebo-virgl-patched
fi
fi
if [ "$phase" = all ] || [ "$phase" = build ]; then
cmake -S . -B build/engine -DCMAKE_BUILD_TYPE=Release \
  -DRENDERING_SOURCE_DIR="$PWD/build/src"
cmake --build build/engine --parallel 2
fi
if [ "$phase" = all ] || [ "$phase" = assemble ]; then
python3 tools/assemble_runtime.py
fi
printf '\nPreparazione completata. Nessuna configurazione di sistema modificata.\n'
