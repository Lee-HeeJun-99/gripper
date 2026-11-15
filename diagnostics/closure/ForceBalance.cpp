#include "BeamProbe.inc"
int main(int argc,char**argv){try{
 if(argc!=4)throw std::invalid_argument("SDK SCENE PLUGIN");
 sofa::simulation::graph::init();sofa::simpleapi::init();sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");if(!sofa::simpleapi::importPlugin(argv[3]))throw std::runtime_error("plugin");auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("scene");sofa::simulation::node::initRoot(root.get());
 for(unsigned i=0;i<27960;++i)sofa::simulation::node::animate(root.get());
 auto*body=root->getChild("Multilayer");auto*state=dynamic_cast<State*>(body->getMechanicalState());if(!state)throw std::runtime_error("state");auto*x=state->read(sofa::core::vec_id::read_access::position);auto*v=state->read(sofa::core::vec_id::read_access::velocity);auto origin=x->getValue().back().getCenter();std::cout<<std::setprecision(17);
 for(auto*field:static_cast<sofa::core::objectmodel::BaseContext*>(body)->getObjects<FF>(sofa::core::objectmodel::BaseContext::Local)){
  FF::DataVecDeriv f;f.setValue(Types::VecDeriv(state->getSize()));sofa::core::MechanicalParams mp;field->addForce(&mp,f,*x,*v);double net[6]{};
  for(unsigned i=0;i<state->getSize();++i){auto r=x->getValue()[i].getCenter()-origin;const auto&a=f.getValue()[i];for(int j=0;j<6;++j)net[j]+=a[j];net[3]+=r[1]*a[2]-r[2]*a[1];net[4]+=r[2]*a[0]-r[0]*a[2];net[5]+=r[0]*a[1]-r[1]*a[0];}
  std::cout<<"FIELD_WRENCH {\"class\":\""<<field->getClassName()<<"\",\"name\":\""<<field->getName()<<"\",\"time\":"<<root->getTime()<<",\"wrench\":[";for(int j=0;j<6;++j)std::cout<<(j?",":"")<<net[j];std::cout<<"]}"<<std::endl;
 }
 sofa::simulation::node::unload(root);root.reset();sofa::simulation::Simulation::theSimulation.reset();sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
}catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<std::endl;return 1;}}
