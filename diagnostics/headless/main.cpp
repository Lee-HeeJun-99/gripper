// Diagnostic engine control, separate from the certified runSofa execution path.
#include <sofa/simpleapi/SimpleApi.h>
#include <sofa/simpleapi/init.h>
#include <sofa/simulation/graph/init.h>
#include <sofa/simulation/Node.h>
#include <sofa/helper/system/FileRepository.h>
#include <sofa/helper/AdvancedTimer.h>
#include <iostream>
#include <stdexcept>
int main(int argc,char**argv){
 try{
  if(argc<5)throw std::invalid_argument("usage: regrip_headless SOFA_ROOT SCENE STEPS CLEAR_TIMER_INTERVAL [PLUGIN...]");
  int steps=std::stoi(argv[3]),clear=std::stoi(argv[4]);if(steps<1||steps>120000||clear<0)throw std::invalid_argument("bounded steps/interval required");
  sofa::simulation::graph::init();sofa::simpleapi::init();
  sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");
  sofa::helper::system::DataRepository.addFirstPath(std::string(argv[1])+"/share/sofa");
  sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");
  for(int i=5;i<argc;++i)if(!sofa::simpleapi::importPlugin(argv[i]))throw std::runtime_error("plugin load failed");
  auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("scene load failed");
  sofa::simulation::node::initRoot(root.get());
  for(int i=0;i<steps;++i){sofa::simulation::node::animate(root.get());if(clear && (i+1)%clear==0)sofa::helper::AdvancedTimer::clear();}
  std::cout<<steps<<" iterations done; t="<<root->getTime()<<"\n";
  sofa::simulation::node::unload(root);root.reset();sofa::simulation::Simulation::theSimulation.reset();
  sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
 }catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<"\n";return 1;}
}
