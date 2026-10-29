REPRODUCING THE NUMERICAL ABLATION

Requires the pinned 8.2.3 SDK, OGRE 1.9.0 and the build dependencies in the guide.
Run in Ubuntu. Start from a terminal without a previous private driver preload.
No other simulation or compilation should run during the timing matrix.

From the archive root:
  python3 tools/prepare_sources.py
  bash tools/prepare_mesa24.bash
  cp overlay/downloads/gz-rendering-8.2.3.tar.gz bench/
  cd bench
  python3 make_worlds.py
  python3 make_variants.py
  bash build_variants.sh
  source /opt/ros/jazzy/setup.bash
  export DISPLAY=<your Ubuntu desktop display>
  export XAUTHORITY=<your Ubuntu desktop authority file>
  python3 run_matrix.py | tee matrix-progress.log

The original runner used :0 and /run/user/1000/gdm/Xauthority on the measured
VM. The portable runner uses the DISPLAY/XAUTHORITY values from your terminal.
The original VM used its read-only installed Mesa 24 control; in this archive
the default is ../mesa24/root/usr/lib/aarch64-linux-gnu. REVIEW_MESA24 can name
another fully extracted matching control. REVIEW_GZ can select an unmodified
Ruby gz entry point; on the old VM this was the preserved gz.vendor file.
The runner's default is the gz resolved by PATH. GZ_VIRGL_DEFAULTS=0 is set to
bypass the old machine-wide profile if present. No defaults.so is loaded.

Output: results/<case>/{result.json,renderer.txt,server.log,probe.stderr,*.ppm}
and results/matrix_results.json, results/plan.json. Existing case names are
reused; use a fresh archive copy for another run, or move previous results.
Failures must be retained, not replaced by a successful retry without notice.
The probe uses two seconds of warmup, then approximately six seconds of data.
Frequencies measure received messages. Error and invalid counts are separate.
Raw PPM frames may be viewed with an ordinary image viewer; the all-black
noise frames are intentionally retained as evidence.

The original run is preserved in ../evidence/results. The portable copy only
changes paths/environment selection, not numerical variants or fixture logic.
It has not been certified on a freshly installed VM. build_variants.sh rebuilds
the full OGRE plugin against the installed rendering SDK; the public colcon
overlay additionally rebuilds the rendering core. These are distinct builds.

All ordinary SDF light shadow flags are respected by the benchmark plugins.
No shader/flicker correction is hidden in the variants. pad2 and pad3 are
experimental controls and are not part of the recommended overlay.
