from pathlib import Path
import xml.etree.ElementTree as E
root=Path(__file__).resolve().parent
wdir=root/'worlds';wdir.mkdir(exist_ok=True)
for horizontal,vertical,name in [(121,1,'single'),(361,1,'full360'),(121,3,'three_rows')]:
 sdf=E.Element('sdf',version='1.9');world=E.SubElement(sdf,'world',name='wall_bench')
 physics=E.SubElement(world,'physics',name='default',type='ignored');E.SubElement(physics,'max_step_size').text='0.001';E.SubElement(physics,'real_time_factor').text='1'
 for file,plugin in [('physics','Physics'),('sensors','Sensors')]:
  element=E.SubElement(world,'plugin',filename='gz-sim-'+file+'-system',name='gz::sim::systems::'+plugin)
  if file=='sensors':E.SubElement(element,'render_engine').text='ogre'
 wall=E.SubElement(world,'model',name='wall');E.SubElement(wall,'static').text='true';E.SubElement(wall,'pose').text='2.5 0 1 0 0 0';link=E.SubElement(wall,'link',name='link');vis=E.SubElement(link,'visual',name='wall');geometry=E.SubElement(vis,'geometry');box=E.SubElement(geometry,'box');E.SubElement(box,'size').text='1 20 2'
 model=E.SubElement(world,'model',name='sensor');E.SubElement(model,'static').text='true';E.SubElement(model,'pose').text='0 0 0.5 0 0 0';link=E.SubElement(model,'link',name='link');sensor=E.SubElement(link,'sensor',name='laser',type='gpu_lidar');E.SubElement(sensor,'always_on').text='true';E.SubElement(sensor,'update_rate').text='10';E.SubElement(sensor,'topic').text='scan_bench';lidar=E.SubElement(sensor,'lidar');scan=E.SubElement(lidar,'scan');h=E.SubElement(scan,'horizontal')
 for key,val in [('samples',str(horizontal)),('resolution','1'),('min_angle','-3.141592653589793' if name=='full360' else '-0.75'),('max_angle','3.141592653589793' if name=='full360' else '0.75')]:E.SubElement(h,key).text=val
 if vertical>1:
  v=E.SubElement(scan,'vertical')
  for key,val in [('samples','3'),('resolution','1'),('min_angle','-0.1'),('max_angle','0.1')]:E.SubElement(v,key).text=val
 ranges=E.SubElement(lidar,'range')
 for key,val in [('min','0.05'),('max','10'),('resolution','0.001')]:E.SubElement(ranges,key).text=val
 E.ElementTree(sdf).write(wdir/(name+'.sdf'))
for shadows in [False,True]:
 sdf=E.Element('sdf',version='1.9');world=E.SubElement(sdf,'world',name='camera_bench')
 E.SubElement(world,'plugin',filename='gz-sim-physics-system',name='gz::sim::systems::Physics');p=E.SubElement(world,'plugin',filename='gz-sim-sensors-system',name='gz::sim::systems::Sensors');E.SubElement(p,'render_engine').text='ogre'
 scene=E.SubElement(world,'scene');E.SubElement(scene,'ambient').text='.4 .4 .4 1';E.SubElement(scene,'background').text='.3 .3 .3 1'
 light=E.SubElement(world,'light',name='sun',type='directional');E.SubElement(light,'pose').text='0 0 10 0 0 0';E.SubElement(light,'cast_shadows').text=str(shadows).lower();E.SubElement(light,'diffuse').text='.8 .8 .8 1';E.SubElement(light,'direction').text='-.5 -.5 -1'
 for name,pose,size,color in [('ground','0 0 -.05 0 0 0','20 20 .1','.7 .7 .7 1'),('red','2 -.5 .5 0 0 0','1 1 1','1 0 0 1'),('blue','3 1 .5 0 0 0','1 1 1','0 0 1 1')]:
  model=E.SubElement(world,'model',name=name);E.SubElement(model,'static').text='true';E.SubElement(model,'pose').text=pose;link=E.SubElement(model,'link',name='link');vis=E.SubElement(link,'visual',name='visual');g=E.SubElement(vis,'geometry');box=E.SubElement(g,'box');E.SubElement(box,'size').text=size;mat=E.SubElement(vis,'material');E.SubElement(mat,'ambient').text=color;E.SubElement(mat,'diffuse').text=color
 for noise in [False,True]:
  name='noise' if noise else 'plain';model=E.SubElement(world,'model',name=name);E.SubElement(model,'static').text='true';E.SubElement(model,'pose').text='-1 0 .8 0 0 0';link=E.SubElement(model,'link',name='link');sensor=E.SubElement(link,'sensor',name=name,type='camera');E.SubElement(sensor,'always_on').text='true';E.SubElement(sensor,'update_rate').text='30';E.SubElement(sensor,'topic').text='camera_'+name;camera=E.SubElement(sensor,'camera');E.SubElement(camera,'horizontal_fov').text='1.047';image=E.SubElement(camera,'image');E.SubElement(image,'width').text='320';E.SubElement(image,'height').text='240';E.SubElement(image,'format').text='R8G8B8';clip=E.SubElement(camera,'clip');E.SubElement(clip,'near').text='.1';E.SubElement(clip,'far').text='100'
  if noise:
   n=E.SubElement(camera,'noise');E.SubElement(n,'type').text='gaussian';E.SubElement(n,'mean').text='0';E.SubElement(n,'stddev').text='.007'
 E.ElementTree(sdf).write(wdir/('camera_shadows_'+('on' if shadows else 'off')+'.sdf'))
