#include <sofa/simpleapi/SimpleApi.h>
#include <sofa/simpleapi/init.h>
#include <sofa/simulation/graph/init.h>
#include <sofa/simulation/Node.h>
#include <sofa/helper/system/FileRepository.h>
#include <malloc.h>
#include <dlfcn.h>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <unistd.h>
#include <sys/resource.h>
void sample(int step){
 auto m=mallinfo2();std::ifstream f("/proc/self/statm");long v=0,r=0;f>>v>>r;
 std::cout<<"MEM {\"step\":"<<step<<",\"rss\":"<<r*sysconf(_SC_PAGESIZE)<<",\"live_heap\":"<<m.uordblks<<",\"free_heap\":"<<m.fordblks<<",\"mmap\":"<<m.hblkhd<<"}"<<std::endl;
}
int main(int argc,char**argv){try{
 if(argc<5)throw std::invalid_argument("SOFA_ROOT SCENE STEPS TRIM [PLUGIN ...]");
 int steps=std::stoi(argv[3]),trim=std::stoi(argv[4]);if(steps<1||steps>240000||trim<0)throw std::invalid_argument("bounded steps/trim required");
 setrlimit(RLIMIT_CORE,&(const rlimit&)(rlimit{0,0}));
 sofa::simulation::graph::init();sofa::simpleapi::init();
 sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");
 sofa::helper::system::DataRepository.addFirstPath(std::string(argv[1])+"/share/sofa");
 sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");
 for(int i=5;i<argc;++i)if(!sofa::simpleapi::importPlugin(argv[i]))throw std::runtime_error("plugin load failed");
 auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("scene loading failed");
 sofa::simulation::node::initRoot(root.get());sample(0);
 for(int i=1;i<=steps;++i){sofa::simulation::node::animate(root.get());if(i%1000==0){if(trim)malloc_trim(0);sample(i);}}
 auto dump=reinterpret_cast<void(*)()>(dlsym(RTLD_DEFAULT,"regrip_allocation_dump"));if(dump)dump();
 std::cout<<steps<<" iterations done; time="<<root->getTime()<<std::endl;
 sofa::simulation::node::unload(root);root.reset();sofa::simulation::Simulation::theSimulation.reset();sample(-1);
 if(trim)malloc_trim(0);sample(-2);
 sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
}catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<std::endl;return 1;}}
