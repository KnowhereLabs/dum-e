#!/usr/bin/env python3
"""Short functional smoke tests, not a stability or GUI-FPS benchmark."""
from pathlib import Path
import argparse,os,subprocess,signal,time,json,hashlib,math,shutil,xml.etree.ElementTree as E
p=argparse.ArgumentParser();p.add_argument('--engine',required=True);p.add_argument('--probe',required=True);p.add_argument('--out',required=True);a=p.parse_args()
kit=Path(__file__).resolve().parents[1];out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
base=os.environ.copy();base.pop('LD_PRELOAD',None);base['GZ_VIRGL_DEFAULTS']='0'
gz=os.environ.get('REVIEW_GZ',shutil.which('gz') or '')
source=kit/'bench/worlds/single.sdf';tree=E.parse(source);world=tree.getroot().find('world');angle=1.2
world.find("model[@name='wall']/pose").text=f'{-2+2.5*math.cos(angle)} {1+2.5*math.sin(angle)} 1 0 0 {angle}'
world.find("model[@name='sensor']/pose").text=f'-2 1 0.5 0 0 {angle}'
transformed=out/'transformed.sdf';tree.write(transformed)
results=[]
for world_name,mode in [('single','lidar'),('full360','lidar'),('three_rows','lidar'),('transformed','lidar'),('camera_shadows_off','camera')]:
 case=out/world_name;case.mkdir(exist_ok=True);env=base.copy();env['GZ_PARTITION']='overlay_review_'+world_name
 sdf=transformed if world_name=='transformed' else kit/'bench/worlds'/(world_name+'.sdf')
 command=['ruby',gz,'sim','-r','-s',str(sdf),'--render-engine',a.engine]
 meta={'world':world_name,'command':command,'engine_sha256':hashlib.sha256(Path(a.engine).read_bytes()).hexdigest(),'sdf_sha256':hashlib.sha256(sdf.read_bytes()).hexdigest()}
 (case/'renderer.txt').write_text(subprocess.run(['glxinfo','-B'],env=env,text=True,capture_output=True,check=True).stdout)
 with (case/'server.log').open('w') as log:
  server=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   time.sleep(.8);probe=subprocess.run([a.probe,mode,str(case/'frame')],env=env,text=True,capture_output=True,timeout=14)
   meta['observations']=json.loads(probe.stdout);(case/'probe.stderr').write_text(probe.stderr)
   maps=Path(f'/proc/{server.pid}/maps')
   meta['loaded_libraries']=sorted(set(line.split()[-1] for line in maps.read_text().splitlines() if any(k in line for k in ['libgz-rendering','libgallium','libGLX_mesa','virtio_gpu_dri'])))
  finally:
   try:os.killpg(server.pid,signal.SIGINT)
   except ProcessLookupError:pass
   try:server.wait(timeout=5)
   except subprocess.TimeoutExpired:
    os.killpg(server.pid,signal.SIGTERM)
    try:server.wait(timeout=3)
    except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait()
 meta['server_exit']=server.returncode;results.append(meta)
 (case/'result.json').write_text(json.dumps(meta,indent=2)+'\n');(out/'overlay_validation.json').write_text(json.dumps(results,indent=2)+'\n')
 print(world_name,{sensor:{k:v for k,v in d.items() if k in ['samples','hz_wall','max_wall_error_m','invalid_wall_returns','nonzero_frames']} for sensor,d in meta['observations'].items()},flush=True)
