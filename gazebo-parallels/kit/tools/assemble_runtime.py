from pathlib import Path
import shutil,os,json,hashlib,subprocess
kit=Path(__file__).resolve().parents[1]
build=kit/'build';runtime=build/'runtime';mesa_src=build/'mesa-root/usr/lib/aarch64-linux-gnu'
if runtime.exists():raise SystemExit('STOP: build/runtime esiste già. Non sovrascrivo un runtime precedente.')
(runtime/'mesa/dri').mkdir(parents=True);(runtime/'engine').mkdir()
for p in mesa_src.iterdir():
 if p.name.startswith('lib') and (p.is_file() or p.is_symlink()):
  if p.is_symlink():(runtime/'mesa'/p.name).symlink_to(os.readlink(p))
  else:shutil.copy2(p,runtime/'mesa'/p.name)
shutil.copy2(mesa_src/'dri/virtio_gpu_dri.so',runtime/'mesa/dri/virtio_gpu_dri.so')
(runtime/'mesa/dri/swrast_dri.so').symlink_to('virtio_gpu_dri.so')
for source,target in [('libgz-rendering8-ogre.so','engine/libgz-rendering8-ogre.so'),('libgazebo_virgl_defaults.so','libgazebo_virgl_defaults.so'),('refresh_gui_state','refresh_gui_state')]:
 shutil.copy2(build/'engine'/source,runtime/target)
(runtime/'engine/libgz-rendering-ogre.so').symlink_to('libgz-rendering8-ogre.so')
shutil.copy2(kit/'sources/profile.rb',runtime/'profile.rb')
shutil.copytree(kit/'sources',runtime/'source')
shutil.copy2(kit/'CMakeLists.txt',runtime/'source/CMakeLists.txt')
shutil.copytree(build/'mesa-root/usr/share/doc',runtime/'licenses',symlinks=True)
for p in runtime.rglob('*'):
 if p.is_symlink():continue
 os.chmod(p,0o755 if p.is_dir() or p.name=='refresh_gui_state' else 0o644)
package_info=[]
for p in sorted((build/'downloads').glob('*.deb')):
 info=subprocess.check_output(['dpkg-deb','-f',str(p),'Package','Version'],text=True)
 package_info.append({'file':p.name,'metadata':info,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
manifest={'revision':3,'gz_rendering':'8.2.3','platform':'Ubuntu 24.04 arm64','packages':package_info,
 'sha256':{str(p.relative_to(runtime)):hashlib.sha256(p.read_bytes()).hexdigest() for p in runtime.rglob('*') if p.is_file() and not p.is_symlink()}}
(runtime/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Runtime privato preparato in',runtime)
