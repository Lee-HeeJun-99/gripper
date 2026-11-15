#define main original_driver_main
#include "../integrated/Driver.cpp"
#undef main
#include <filesystem>
void memoryBoundary(const char*name){
 std::ifstream in("/proc/self/smaps_rollup");std::string line;long rss=0,pss=0,dirty=0;while(std::getline(in,line)){std::istringstream s(line);std::string k;long v=0;s>>k>>v;if(k=="Rss:")rss=v;if(k=="Pss:")pss=v;if(k=="Private_Dirty:")dirty=v;}size_t fd=0;for(auto&e:std::filesystem::directory_iterator("/proc/self/fd")){(void)e;++fd;}std::cout<<"BOUNDARY {\"name\":\""<<name<<"\",\"rss_kib\":"<<rss<<",\"pss_kib\":"<<pss<<",\"private_dirty_kib\":"<<dirty<<",\"fds\":"<<fd<<"}"<<std::endl;
}
int main(int argc,char**argv){try{
 if(argc!=5)throw std::invalid_argument("SDK SCENE1 SCENE2 MATCHED_PLUGIN");
 sofa::simulation::graph::init();sofa::simpleapi::init();sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");if(!sofa::simpleapi::importPlugin(argv[4]))throw std::runtime_error("matched plugin");
 for(unsigned run=0;run<2;++run){auto root=sofa::simulation::node::load(argv[run+2]);if(!root)throw std::runtime_error("load");sofa::simulation::node::initRoot(root.get());sample(run*120000);memoryBoundary("loaded");for(unsigned step=1;step<=120000;++step){sofa::simulation::node::animate(root.get());if(step%60000==0){sample(run*120000+step);memoryBoundary("animated");}}sofa::simulation::node::unload(root);root.reset();malloc_trim(0);sample(-1-int(run));memoryBoundary("unloaded");}
 sofa::simulation::Simulation::theSimulation.reset();sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
}catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<'\n';return 1;}}
