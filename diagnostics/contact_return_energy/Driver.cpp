#include "Audit.h"
#include <sofa/simpleapi/SimpleApi.h>
#include <sofa/simpleapi/init.h>
#include <sofa/simulation/graph/init.h>
#include <sofa/simulation/Node.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/helper/system/FileRepository.h>
#include <fstream>
#include <iomanip>
#include <iostream>
class Journal:public sofa::core::objectmodel::BaseObject{
public:
 SOFA_CLASS(Journal,sofa::core::objectmodel::BaseObject);
 sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*contact=nullptr;
 std::ofstream out;unsigned ends=0;double maxResidual=0,plastic=0,projection=0,detachment=0;unsigned born=0,dead=0;
 Journal(){f_listening.setValue(true);}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;
  auto b=auditCurveReturn(contact);++ends;maxResidual=std::max(maxResidual,std::abs(b.residual));plastic+=b.plastic;projection+=b.projection;detachment+=b.detachment;born+=b.born;dead+=b.dead;
  out<<getContext()->getTime()<<','<<ends<<','<<b.oldEnergy<<','<<b.newEnergy<<','<<b.endpointWork<<','<<b.plastic<<','<<b.projection<<','<<b.detachment<<','<<b.residual<<','<<b.maxPointResidual<<','<<b.active<<','<<b.born<<','<<b.dead<<','<<b.sliding<<'\n';
 }
};
int main(int argc,char**argv){try{
 if(argc!=8)throw std::invalid_argument("SDK SCENE STEPS OUTPUT FRAME BEAM CONTACT");int steps=std::stoi(argv[3]);if(steps<1||steps>16000)throw std::invalid_argument("bounded16000steps");std::ifstream old(argv[4]);if(old)throw std::runtime_error("refuse old journal");
 sofa::simulation::graph::init();sofa::simpleapi::init();sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");for(int i=5;i<8;++i)if(!sofa::simpleapi::importPlugin(argv[i]))throw std::runtime_error("plugin load");auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("scene load");sofa::simulation::node::initRoot(root.get());auto*body=root->getChild("Multilayer");if(!body)throw std::runtime_error("body");
 auto journal=sofa::core::objectmodel::New<Journal>();auto*ctx=static_cast<sofa::core::objectmodel::BaseContext*>(body);for(auto*f:ctx->getObjects<sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>>(sofa::core::objectmodel::BaseContext::Local))if(f->getClassName()=="CurvedMaterialContact")journal->contact=f;if(!journal->contact)throw std::runtime_error("contact scope");journal->out.open(argv[4]);if(!journal->out)throw std::runtime_error("output");journal->out<<std::setprecision(17)<<"time,step,U0,U1,endpoint_material_spring_work,plastic,derived_endpoint_projection,detachment,residual,max_point_residual,active,born,dead,sliding\n";root->addObject(journal);
 for(int i=0;i<steps;++i)sofa::simulation::node::animate(root.get());
 if(journal->ends!=unsigned(steps))throw std::runtime_error("journal once per step");
 std::cout<<std::setprecision(17)<<"RETURN_AUDIT {\"steps\":"<<steps<<",\"max_residual\":"<<journal->maxResidual<<",\"plastic\":"<<journal->plastic<<",\"projection\":"<<journal->projection<<",\"detachment\":"<<journal->detachment<<",\"births\":"<<journal->born<<",\"deaths\":"<<journal->dead<<"}\n";
 sofa::simulation::node::unload(root);journal.reset();root.reset();sofa::simulation::Simulation::theSimulation.reset();sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
 }catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<'\n';return 1;}}
