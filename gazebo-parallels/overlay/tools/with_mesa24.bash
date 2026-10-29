#!/usr/bin/env bash
# Per-command Mesa selection; arguments are passed unchanged.
set -euo pipefail
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mesa="$kit/mesa24/root/usr/lib/aarch64-linux-gnu"
[[ -f "$mesa/libGLX_mesa.so.0" && -d "$mesa/dri" ]] || { echo 'Run tools/prepare_mesa24.bash first.' >&2;exit 1; }
[[ $# -gt 0 ]] || { echo 'Usage: tools/with_mesa24.bash COMMAND [ARGS...]' >&2;exit 2; }
unset LIBGL_ALWAYS_SOFTWARE GALLIUM_DRIVER MESA_GL_VERSION_OVERRIDE MESA_GLSL_VERSION_OVERRIDE LIBGL_ALWAYS_INDIRECT
export LD_LIBRARY_PATH="$mesa${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LIBGL_DRIVERS_PATH="$mesa/dri"
exec "$@"
