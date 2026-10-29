#include <gz/transport/Node.hh>
#include <gz/msgs/empty.pb.h>
#include <gz/msgs/stringmsg_v.pb.h>
#include <vector>
#include <gz/msgs/serialized_map.pb.h>
#include <chrono>
#include <thread>
#include <iostream>
int main(int argc,char**argv){
 gz::transport::Node node;std::vector<std::string> worlds;
 if(argc>1)worlds.push_back(argv[1]);
 else {gz::msgs::Empty request;gz::msgs::StringMsg_V list;bool success=false;
 if(!node.Request("/gazebo/worlds",request,5000,list,success)||!success)return 1;
 for(const auto &name:list.data())worlds.push_back(name);}
 for(const auto &world:worlds){
 gz::msgs::Empty req;gz::msgs::SerializedStepMap reply;bool ok=false;
 if(!node.Request("/world/"+world+"/state",req,5000,reply,ok)||!ok){std::cerr<<"State request failed\n";return 1;}
 auto pub=node.Advertise<gz::msgs::SerializedStepMap>("/world/"+world+"/state");
 std::this_thread::sleep_for(std::chrono::milliseconds(500));
 for(int retry=0;retry<30 && !pub.HasConnections();++retry)
  std::this_thread::sleep_for(std::chrono::milliseconds(50));
 std::cout<<"GUI subscribers: "<<pub.HasConnections()<<"\n";
 if(!pub.HasConnections()){std::cerr<<"No GUI subscriber is connected.\n";return 3;}
 if(!pub.Publish(reply))return 2;
 std::this_thread::sleep_for(std::chrono::milliseconds(500));
 std::cout<<"Complete GUI state refreshed for "<<world<<".\n";
 }
}
