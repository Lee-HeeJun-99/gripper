#define main previous_main
#include "../integrated/Driver.cpp"
#undef main
#include <sofa/core/behavior/Mass.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/linearalgebra/FullMatrix.h>
int main(int argc,char**argv){try{
 if(argc!=4)throw std::invalid_argument("SOFA_ROOT SCENE PLUGIN");
 sofa::simulation::graph::init();sofa::simpleapi::init();sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");
 if(!sofa::simpleapi::importPlugin(argv[3]))throw std::runtime_error("probe plugin load");
 auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("probe scene load");sofa::simulation::node::initRoot(root.get());auto body=root->getChild("Multilayer");if(!body||!body->getMass())throw std::runtime_error("probe missing mass");
 using Types=sofa::defaulttype::Rigid3Types;auto*state=dynamic_cast<sofa::core::behavior::MechanicalState<Types>*>(body->getMechanicalState());if(!state)throw std::runtime_error("probe state");auto*mass=body->getMass();double total=0;for(unsigned i=0;i<state->getSize();++i)total+=mass->getElementMass(i);
 std::cout<<"MASS first="<<mass->getElementMass(0)<<" last="<<mass->getElementMass(state->getSize()-1)<<" total="<<total<<std::endl;sofa::linearalgebra::FullMatrix<double> matrix(6,6);mass->getElementMass(state->getSize()-1,&matrix);std::cout<<"INERTIA ";for(int i=0;i<6;++i)std::cout<<matrix.element(i,i)<<' ';std::cout<<std::endl;
 sofa::core::MechanicalParams params;auto*context=static_cast<sofa::core::objectmodel::BaseContext*>(body);for(auto*ff:context->getObjects<sofa::core::behavior::ForceField<Types>>(sofa::core::objectmodel::BaseContext::Local)){std::cout<<"ENERGY_API "<<ff->getClassName()<<' '<<std::flush;std::cout<<ff->getPotentialEnergy(&params,*state->read(sofa::core::vec_id::read_access::position))<<std::endl;}
 sofa::simulation::node::unload(root);root.reset();sofa::simulation::Simulation::theSimulation.reset();sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
}catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<std::endl;return 1;}}
