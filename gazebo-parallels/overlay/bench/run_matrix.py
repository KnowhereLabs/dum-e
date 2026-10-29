from pathlib import Path
import os,subprocess,signal,time,json,random,hashlib,shutil
root=Path(__file__).resolve().parent
out=root/'results';out.mkdir(exist_ok=True)
base=os.environ.copy()
for key in ['LD_PRELOAD','LIBGL_ALWAYS_SOFTWARE','GALLIUM_DRIVER','MESA_GL_VERSION_OVERRIDE','MESA_GLSL_VERSION_OVERRIDE','LIBGL_ALWAYS_INDIRECT','GZ_VIRGL_RENDER_ENGINE','GZ_RENDERING_RESOURCE_PATH','GZ_RENDERING_INSTALL_PREFIX','GZ_RENDERING_PLUGIN_PATH']:base.pop(key,None)
if not base.get('DISPLAY'): raise SystemExit('Run in a desktop terminal or set DISPLAY/XAUTHORITY explicitly.')
mesa24=os.environ.get('REVIEW_MESA24',str(root.parent/'mesa24/root/usr/lib/aarch64-linux-gnu'))
gz=os.environ.get('REVIEW_GZ',shutil.which('gz') or '')
if not gz or not Path(mesa24,'dri').is_dir(): raise SystemExit('Missing gz or private Mesa control. Read bench/README.txt.')
base['GZ_VIRGL_DEFAULTS']='0'
plan=[]
for backend in ['mesa24','mesa25']:
 for variant in ['stock','center','uv','center_uv','pad2','pad3','upstream','upstream_uv']:
  plan.append((backend,variant,'single','lidar',1))
for variant in ['stock','center','uv','center_uv','pad3']:
 plan.append(('software25',variant,'single','lidar',1))
for backend in ['mesa24','mesa25']:
 for variant in ['stock','upstream']:
  plan.append((backend,variant,'full360','lidar',1))
 plan.append((backend,'upstream','three_rows','lidar',1))
for backend in ['mesa24','mesa25','software25']:
 for shadows in ['off','on']:
  for rep in [1,2,3]:plan.append((backend,'stock','camera_shadows_'+shadows,'camera',rep))
for backend in ['mesa24','mesa25']:
 for variant in ['stock','center_uv']:
  for rep in [2,3]:plan.append((backend,variant,'single','lidar',rep))
random.Random(20261029).shuffle(plan)
(out/'plan.json').write_text(json.dumps(plan,indent=2))
all_results=[]
for index,(backend,variant,world,mode,rep) in enumerate(plan):
 name=f'{backend}_{variant}_{world}_r{rep}';target=out/name;target.mkdir(exist_ok=True)
 env=base.copy();env['GZ_PARTITION']='review_'+name
 if backend=='mesa24':
  env['LD_LIBRARY_PATH']=mesa24+':'+env.get('LD_LIBRARY_PATH','');env['LIBGL_DRIVERS_PATH']=mesa24+'/dri'
 else:env.pop('LIBGL_DRIVERS_PATH',None)
 if backend=='software25':env['LIBGL_ALWAYS_SOFTWARE']='1'
 driver=subprocess.run(['glxinfo','-B'],env=env,text=True,capture_output=True,timeout=10)
 (target/'renderer.txt').write_text(driver.stdout+driver.stderr)
 engine=root/'variants'/variant/'libgz-rendering-ogre.so';sdf=root/'worlds'/(world+'.sdf')
 command=['ruby',gz,'sim','-r','-s',str(sdf),'--render-engine',str(engine)]
 meta={'backend':backend,'variant':variant,'world':world,'mode':mode,'repeat':rep,'engine_sha256':hashlib.sha256(engine.read_bytes()).hexdigest(),'sdf_sha256':hashlib.sha256(sdf.read_bytes()).hexdigest(),'command':command,'observer_warmup_s':2,'observer_total_s':8}
 logfile=(target/'server.log').open('w');server=subprocess.Popen(command,env=env,stdout=logfile,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  time.sleep(.8)
  observed=subprocess.run([str(root/'build/review_probe'),mode,str(target/'frame')],env=env,text=True,capture_output=True,timeout=14)
  (target/'probe.stderr').write_text(observed.stderr)
  try:meta['observations']=json.loads(observed.stdout)
  except Exception:meta['probe_error']=observed.stdout
  maps=Path(f'/proc/{server.pid}/maps')
  if maps.exists():
   meta['loaded_libraries']=sorted(set(line.split()[-1] for line in maps.read_text().splitlines() if any(x in line for x in ['libgz-rendering8-ogre','libgz-rendering-ogre','virtio_gpu_dri','libgallium','swrast_dri','libGLX_mesa'])))
 finally:
  try:os.killpg(server.pid,signal.SIGINT)
  except ProcessLookupError:pass
  try:server.wait(timeout=5)
  except subprocess.TimeoutExpired:
   os.killpg(server.pid,signal.SIGTERM)
   try:server.wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait()
  logfile.close()
 meta['server_exit']=server.returncode
 (target/'result.json').write_text(json.dumps(meta,indent=2)+'\n');all_results.append(meta)
 (out/'matrix_results.json').write_text(json.dumps(all_results,indent=2)+'\n')
 obs=meta.get('observations',{});summary={k:{a:v for a,v in d.items() if a in ['samples','hz_wall','max_wall_error_m','invalid_wall_returns','nonzero_frames','color_fraction_mean']} for k,d in obs.items()}
 print(f'{index+1}/{len(plan)} {name} '+json.dumps(summary),flush=True)
