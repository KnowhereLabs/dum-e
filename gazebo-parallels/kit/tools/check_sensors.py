import json,math,time,statistics
from pathlib import Path
import rclpy
from sensor_msgs.msg import Image,LaserScan
from rclpy.qos import qos_profile_sensor_data
from PIL import Image as PILImage
out=Path.cwd()
rclpy.init();node=rclpy.create_node('sensor_validation')
start=time.monotonic();samples={'camera':[],'lidar':[]};details={}
def stamp(msg):return msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
def image(msg):
 now=time.monotonic()
 if now-start>3 and (not samples['camera'] or len(samples['camera'])%30==0):
  b=bytes(msg.data);sample=b[::max(1,len(b)//20000)]
  details['camera']={'width':msg.width,'height':msg.height,'encoding':msg.encoding,'bytes':len(b),'sample_min':min(sample),'sample_max':max(sample),'sample_unique_values':len(set(sample))}
  if msg.encoding in ['rgb8','bgr8']:
   PILImage.frombytes('RGB',(msg.width,msg.height),b,'raw','RGB' if msg.encoding=='rgb8' else 'BGR',msg.step,1).save(out/'turtlebot-camera.png')
 if now-start>3:samples['camera'].append((now,stamp(msg)))
def scan(msg):
 now=time.monotonic();valid=[x for x in msg.ranges if math.isfinite(x)]
 details['lidar']={'rays':len(msg.ranges),'finite_returns':len(valid),'range_min':msg.range_min,'range_max':msg.range_max,'minimum_finite_range':min(valid) if valid else None,'maximum_finite_range':max(valid) if valid else None,'angle_min':msg.angle_min,'angle_max':msg.angle_max}
 if now-start>3:samples['lidar'].append((now,stamp(msg)))
node.create_subscription(Image,'/camera/image_raw',image,qos_profile_sensor_data)
node.create_subscription(LaserScan,'/scan',scan,qos_profile_sensor_data)
while time.monotonic()-start<23:rclpy.spin_once(node,timeout_sec=.05)
for key,seq in samples.items():
 details.setdefault(key,{})['messages_after_warmup']=len(seq)
 if len(seq)>1:
  details[key]['received_hz_wall']=(len(seq)-1)/(seq[-1][0]-seq[0][0])
  details[key]['received_hz_sim']=(len(seq)-1)/(seq[-1][1]-seq[0][1])
(out/'sensor-validation.json').write_text(json.dumps(details,indent=2))
print(json.dumps(details,indent=2))
node.destroy_node();rclpy.shutdown()
