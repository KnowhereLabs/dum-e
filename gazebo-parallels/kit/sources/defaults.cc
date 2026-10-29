#include <dlfcn.h>
#include <cstdio>
#include <cstdlib>
#include <string>
// Default ServerConfig values also cover the native ros_gz_sim/gzserver entry.
static void *simSymbol(const char *name){
 auto h=dlopen("/opt/ros/jazzy/opt/gz_sim_vendor/lib/libgz-sim8.so.8", RTLD_LAZY|RTLD_NOLOAD);
 auto f=h?dlsym(h,name):nullptr;
 if(!f){fprintf(stderr,"[gazebo-defaults] Gazebo 8 ABI lookup failed: %s\n",name);std::abort();}
 return f;
}
static void defaultConstruct(void *self){
 using Ctor=void(*)(void*);
 static auto ctor=reinterpret_cast<Ctor>(simSymbol("_ZN2gz3sim2v812ServerConfigC1Ev"));
 ctor(self);
 const char *mode=std::getenv("GZ_VIRGL_DEFAULTS");
 if(mode && std::string(mode)=="0") return;
 using Setter=void(*)(void*,const std::string&);
 static auto server=reinterpret_cast<Setter>(simSymbol("_ZN2gz3sim2v812ServerConfig21SetRenderEngineServerERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE"));
 static auto gui=reinterpret_cast<Setter>(simSymbol("_ZN2gz3sim2v812ServerConfig18SetRenderEngineGuiERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE"));
 static auto serverApi=reinterpret_cast<Setter>(simSymbol("_ZN2gz3sim2v812ServerConfig31SetRenderEngineServerApiBackendERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE"));
 static auto guiApi=reinterpret_cast<Setter>(simSymbol("_ZN2gz3sim2v812ServerConfig28SetRenderEngineGuiApiBackendERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE"));
 const char *engine=std::getenv("GZ_VIRGL_RENDER_ENGINE");
 std::string selected=engine?engine:"ogre";
 server(self,selected);gui(self,selected);serverApi(self,"opengl");guiApi(self,"opengl");
}
extern "C" void configCtor1(void*) asm("_ZN2gz3sim2v812ServerConfigC1Ev");
extern "C" void configCtor1(void *self){defaultConstruct(self);}
extern "C" void configCtor2(void*) asm("_ZN2gz3sim2v812ServerConfigC2Ev");
extern "C" void configCtor2(void *self){defaultConstruct(self);}

// Refresh GUI entity components when a LiDAR topic is selected.
#include <QCoreApplication>
#include <QObject>
#include <QVariant>
#include <QString>
extern "C" void lidarTopic(void*,const QString&) asm("_ZN2gz3sim2v814VisualizeLidar7OnTopicERK7QString");
extern "C" void lidarTopic(void *self,const QString &topic){
 static auto handle=dlopen("/opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins/gui/libVisualizeLidar.so",RTLD_LAZY|RTLD_NOLOAD);
 static auto real=reinterpret_cast<void(*)(void*,const QString&)>(handle?dlsym(handle,"_ZN2gz3sim2v814VisualizeLidar7OnTopicERK7QString"):nullptr);
 if(!real){fprintf(stderr,"[gazebo-defaults] Cannot resolve VisualizeLidar topic handler.\n");std::abort();}
 real(self,topic);
 const char *mode=std::getenv("GZ_VIRGL_DEFAULTS");if(mode && std::string(mode)=="0")return;
 auto app=QCoreApplication::instance();if(!app)return;
 for(auto child:app->children()){
  if(QString::fromLatin1(child->metaObject()->className()).contains("GuiRunner") && child->property("worldName").isValid()){
   if(QMetaObject::invokeMethod(child,"RequestState",Qt::QueuedConnection))
    fprintf(stderr,"[gazebo-defaults] GUI entity state requested after LiDAR topic selection.\n");
  }
 }
}
