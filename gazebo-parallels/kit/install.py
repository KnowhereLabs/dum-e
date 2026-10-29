#!/usr/bin/env python3
"""Fresh-install transaction. --check is read-only; --install needs sudo."""
import argparse,pathlib,os,sys,json,hashlib,shutil,subprocess,datetime
p=argparse.ArgumentParser();p.add_argument('--install',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
kit=pathlib.Path(__file__).resolve().parent;runtime=kit/'build/runtime'
root=pathlib.Path('/usr/local/lib/gazebo-virgl-defaults');manifest_path=pathlib.Path('/usr/local/share/gazebo-virgl-defaults/manifest.json')
entries=[{'path':'/opt/ros/jazzy/opt/gz_tools_vendor/bin/gz','original_sha256':'81c41b1d1b7789efd7dfe623481ddffc684fc9a9b78c387c40e6512cb8842524','source':'gz'},
 {'path':'/opt/ros/jazzy/lib/ros_gz_sim/gzserver','original_sha256':'64d9ae11b7467694cfafca9b81deb37a56808c46bcc512adf6c3123f143074ba','source':'gzserver'}]
if root.exists() or manifest_path.exists():raise SystemExit('STOP: un profilo esiste già. Questa procedura è per una VM standard, non per aggiornare una VM già corretta.')
if not (runtime/'build-manifest.json').is_file():raise SystemExit('Eseguire prima bash prepare.sh')
build=json.loads((runtime/'build-manifest.json').read_text())
for name,digest in build['sha256'].items():
 if hashlib.sha256((runtime/name).read_bytes()).hexdigest()!=digest:raise SystemExit('Hash runtime non valido: '+name)
for e in entries:
 e['diverted_to']=e['path']+'.vendor';target=pathlib.Path(e['path'])
 if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=e['original_sha256']:raise SystemExit('STOP: ingresso diverso dalla versione collaudata: '+e['path'])
 if pathlib.Path(e['diverted_to']).exists():raise SystemExit('STOP: backup .vendor già presente')
 if subprocess.check_output(['dpkg-divert','--list',e['path']],text=True).strip():raise SystemExit('STOP: diversione già presente')
print('Runtime e ingressi verificati. Nessuna modifica eseguita.')
if not a.install:raise SystemExit(0)
if os.geteuid()!=0:raise SystemExit('Usare sudo python3 install.py --install')
backup=pathlib.Path('/var/backups/gazebo-virgl-defaults')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup.mkdir(parents=True)
for e in entries:shutil.copy2(e['path'],backup/e['source'])
completed=[];created_root=False;created_manifest=False
try:
 root.mkdir(parents=True);created_root=True
 shutil.copytree(runtime,root/'runtime-v2',symlinks=True)
 (root/'profile.rb').write_text("require_relative 'runtime-v2/profile'\n")
 for e in entries:
  subprocess.run(['dpkg-divert','--local','--add','--rename','--divert',e['diverted_to'],e['path']],check=True);completed.append(e)
  target=pathlib.Path(e['path']);tmp=target.with_name(target.name+'.new')
  shutil.copy2(kit/'sources'/e['source'],tmp);os.chmod(tmp,0o755);tmp.replace(target)
 manifest_path.parent.mkdir(parents=True,exist_ok=True)
 manifest={'installed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':3,'runtime_directory':str(root/'runtime-v2'),'backup_directory':str(backup),'entries':entries,'build':build}
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');created_manifest=True
 rollback=pathlib.Path('/usr/local/sbin/gazebo-virgl-defaults-rollback')
 shutil.copy2(kit/'rollback.py',rollback);os.chmod(rollback,0o755)
except Exception:
 for e in reversed(completed):
  target=pathlib.Path(e['path'])
  if target.exists():target.unlink()
  subprocess.run(['dpkg-divert','--local','--remove','--rename','--divert',e['diverted_to'],e['path']],check=True)
 if created_manifest and manifest_path.exists():manifest_path.unlink()
 if created_root:shutil.rmtree(root)
 raise
print('Profilo installato. Aprire un nuovo terminale e usare i normali comandi Gazebo/ROS.')
print('Backup:',backup)
