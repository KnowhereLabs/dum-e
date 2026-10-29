#!/usr/bin/env python3
import json,os,pathlib,subprocess
if os.geteuid()!=0:raise SystemExit('Usare sudo')
p=pathlib.Path('/usr/local/share/gazebo-virgl-defaults/manifest.json');m=json.loads(p.read_text())
for e in m['entries']:
 target=pathlib.Path(e['path'])
 if 'GAZEBO_VIRGL_DEFAULTS_ENTRY_V1' not in target.read_text():raise SystemExit('STOP: ingresso modificato da altri, richiede revisione: '+str(target))
 if not pathlib.Path(e['diverted_to']).is_file():raise SystemExit('Originale .vendor mancante')
for e in reversed(m['entries']):
 pathlib.Path(e['path']).unlink()
 subprocess.run(['dpkg-divert','--local','--remove','--rename','--divert',e['diverted_to'],e['path']],check=True)
p.rename(p.with_name('manifest.rolled-back.json'))
print('Ingressi originali ripristinati. Chiudere e riavviare Gazebo.')
print('Il runtime privato rimane su disco, ma non viene più caricato dagli ingressi ripristinati.')
