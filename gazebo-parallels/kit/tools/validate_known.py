#!/usr/bin/env python3
"""Validate analytic wall distances; run in the same GZ_PARTITION as the test."""
import argparse,subprocess,json,math,pathlib
p=argparse.ArgumentParser();p.add_argument('--3d',dest='three_d',action='store_true');a=p.parse_args()
topic='/known_3d_scan' if a.three_d else '/known_scan'
r=subprocess.run(['timeout','10','gz','topic','-e','--json-output','-n','1','-t',topic],text=True,capture_output=True)
lines=[line for line in r.stdout.splitlines() if line.strip().startswith('{')]
if not lines:raise SystemExit('STOP: nessun messaggio. Verificare simulazione avviata e GZ_PARTITION identico.')
m=json.loads(lines[0]);ranges=m['ranges'];expected_count=1083 if a.three_d else 361
if len(ranges)!=expected_count:raise SystemExit('Numero raggi inatteso: '+str(len(ranges)))
errors=[]
for row,v in enumerate([-.1,0,.1] if a.three_d else [0]):
 for i in (range(150,211) if a.three_d else range(115,246)):
  theta=-math.pi+i*math.pi/180;expected=2/(math.cos(theta)*math.cos(v));actual=ranges[row*361+i]
  if not isinstance(actual,(float,int)) or not math.isfinite(actual):raise SystemExit('STOP: ritorno non finito verso la parete')
  errors.append(abs(actual-expected))
result={'rays':len(ranges),'tested_rays':len(errors),'front_distance_m':ranges[(361 if a.three_d else 0)+180],'max_absolute_error_m':max(errors),'tolerance_m':.02,'passed':max(errors)<.02}
print(json.dumps(result,indent=2));pathlib.Path('known-distance-result.json').write_text(json.dumps(result,indent=2)+'\n')
if not result['passed']:raise SystemExit(1)
