#include <gz/transport/Node.hh>
#include <gz/msgs/image.pb.h>
#include <gz/msgs/laserscan.pb.h>
#include <chrono>
#include <thread>
#include <mutex>
#include <fstream>
#include <iostream>
#include <cmath>
#include <vector>
#include <iomanip>
#include <algorithm>
using Clock=std::chrono::steady_clock;
struct Stats {
 std::mutex mutex;Clock::time_point start=Clock::now();unsigned n=0;double firstW=0,lastW=0,firstS=0,lastS=0;
 double colorSum=0,colorMin=1;unsigned nonzero=0;double maxError=0;unsigned invalid=0,count=0,finite=0;
 std::vector<double> scan;std::string prefix;
 bool tick(double stamp){double wall=std::chrono::duration<double>(Clock::now()-start).count();if(wall<2)return false;if(!n){firstW=wall;firstS=stamp;}lastW=wall;lastS=stamp;++n;return true;}
 void image(const gz::msgs::Image &m){std::lock_guard<std::mutex> lock(mutex);if(!tick(m.header().stamp().sec()+m.header().stamp().nsec()*1e-9))return;
  const auto &d=m.data();unsigned colored=0,maxv=0,pixels=d.size()/3;for(unsigned i=0;i+2<d.size();i+=3){unsigned a=(unsigned char)d[i],b=(unsigned char)d[i+1],c=(unsigned char)d[i+2];maxv=std::max({maxv,a,b,c});if(std::max({a,b,c})-std::min({a,b,c})>25)++colored;}
  if(maxv)++nonzero;double fraction=pixels?double(colored)/pixels:0;colorSum+=fraction;colorMin=std::min(colorMin,fraction);
  if(n==1 || n==60){std::ofstream f(prefix+"-"+std::to_string(n)+".ppm",std::ios::binary);f<<"P6\n"<<m.width()<<" "<<m.height()<<"\n255\n";f.write(d.data(),d.size());}
 }
 void lidar(const gz::msgs::LaserScan &m){std::lock_guard<std::mutex> lock(mutex);if(!tick(m.header().stamp().sec()+m.header().stamp().nsec()*1e-9))return;
  count=m.ranges_size();finite=0;unsigned horizontal=m.count();unsigned vertical=m.vertical_count();
  for(unsigned row=0;row<vertical;++row){double v=m.vertical_angle_min();if(vertical>1)v+=row*(m.vertical_angle_max()-m.vertical_angle_min())/(vertical-1);
   for(unsigned i=0;i<horizontal;++i){double value=m.ranges(row*horizontal+i);if(std::isfinite(value))++finite;
    double a=m.angle_min()+i*m.angle_step();if(std::abs(a)>1.13)continue;
    double expected=2/(std::cos(a)*std::cos(v));if(!std::isfinite(value)){++invalid;continue;}maxError=std::max(maxError,std::abs(value-expected));
   }}
  if(scan.empty())scan.assign(m.ranges().begin(),m.ranges().end());
 }
 void print(const char *name){std::lock_guard<std::mutex> lock(mutex);std::cout<<"\""<<name<<"\":{\"samples\":"<<n<<",\"hz_wall\":"<<(n>1?(n-1)/(lastW-firstW):0)<<",\"hz_sim\":"<<(n>1?(n-1)/(lastS-firstS):0)<<",\"nonzero_frames\":"<<nonzero<<",\"color_fraction_mean\":"<<(n?colorSum/n:0)<<",\"color_fraction_min\":"<<colorMin<<",\"ray_count\":"<<count<<",\"finite_last\":"<<finite<<",\"invalid_wall_returns\":"<<invalid<<",\"max_wall_error_m\":"<<maxError<<",\"first_scan\":[";
  for(unsigned i=0;i<scan.size();++i){if(i)std::cout<<",";if(std::isfinite(scan[i]))std::cout<<scan[i];else std::cout<<"\"Infinity\"";}std::cout<<"]}";
 }
};
int main(int argc,char**argv){if(argc<3)return 2;std::string mode=argv[1],prefix=argv[2];gz::transport::Node node;Stats a,b;a.prefix=prefix+"-plain";b.prefix=prefix+"-noise";
 if(mode=="camera"){node.Subscribe("/camera_plain",&Stats::image,&a);node.Subscribe("/camera_noise",&Stats::image,&b);}else node.Subscribe("/scan_bench",&Stats::lidar,&a);
 std::this_thread::sleep_for(std::chrono::seconds(8));std::cout<<std::setprecision(12)<<"{";a.print(mode=="camera"?"plain":"lidar");if(mode=="camera"){std::cout<<",";b.print("noise");}std::cout<<"}\n";
}
