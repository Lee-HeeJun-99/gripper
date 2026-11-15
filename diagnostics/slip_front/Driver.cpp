#include <sofa/simpleapi/SimpleApi.h>
#include <sofa/simpleapi/init.h>
#include <sofa/simulation/graph/init.h>
#include <sofa/simulation/Node.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/helper/system/FileRepository.h>
#include <sofa/core/behavior/Mass.h>
#include "../../models/contact_birth/MaterialCells.h"
#include "../../models/curved_contact/Map.h"
#include "CurveClassOnly.inc"
#include <fstream>
#include <iomanip>
#include <iostream>
using Types=sofa::defaulttype::Rigid3Types;
using Contact=regrip_integrated::CurvedMaterialContact;
class Probe:public sofa::core::objectmodel::BaseObject{
public:
 SOFA_CLASS(Probe,sofa::core::objectmodel::BaseObject);
 Contact*contact=nullptr;unsigned nodes=0,steps=0,next=0;std::ofstream out;
 std::vector<double>targets{.9,1,1.1,1.2,7.05,7.1,7.15,7.2,7.25,7.3,7.4,7.5,8,15.05,15.1,15.15,15.2,15.3,15.4,16.1};
 Probe(){f_listening.setValue(true);}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;
  ++steps;
  double t=getContext()->getTime();if(next>=targets.size()||t<targets[next]-.25*getContext()->getDt())return;
  if(std::abs(t-targets[next])>.25*getContext()->getDt())throw std::runtime_error("missed actual trace epoch");
  unsigned epoch=contact->steps;double plastic=contact->committedPlastic;
  const auto&x=contact->getMState()->read(sofa::core::vec_id::read_access::position)->getValue();auto s=contact->computeValue(x);
  if(epoch!=contact->steps||plastic!=contact->committedPlastic)throw std::runtime_error("probe query committed history");
  double sum=0;
  for(const auto&p:s.points){auto&g=contact->grids.at(p.edge);unsigned a=contact->segments.getValue()[2*p.edge];double material=(a%nodes+p.s)*100/(nodes-1),e=std::sqrt(regrip_integrated::dot(p.r.next.elastic,p.r.next.elastic));
   sum+=p.weight*p.r.plasticDissipation;
   out<<t<<','<<steps<<','<<p.edge<<','<<material<<','<<p.weight<<','<<p.r.normalForce<<','<<p.r.capacity<<','<<e<<','<<p.r.plasticDissipation<<','<<p.weight*p.r.plasticDissipation<<','<<p.r.next.sliding<<','<<contact->old(p.edge,p.s).active<<','<<g.count<<'\n';
  }
  if(sum!=s.D)throw std::runtime_error("trace point sum differs from actual snapshot");
  out.flush();std::cout<<std::setprecision(17)<<"SLIP_FRONT time="<<t<<" active="<<s.points.size()<<" sliding="<<s.slips<<" actual_increment="<<s.D<<'\n';++next;
 }
};
int main(int argc,char**argv){try{
 if(argc!=9)throw std::invalid_argument("SDK SCENE STEPS OUTPUT FRAME BEAM CONTACT NODES");
 int steps=std::stoi(argv[3]);unsigned nodes=std::stoul(argv[8]);if(steps<1||steps>160000||(nodes!=21&&nodes!=41))throw std::invalid_argument("bounded probe scope");
 std::ifstream old(argv[4]);if(old)throw std::runtime_error("refuse old trace");
 sofa::simulation::graph::init();sofa::simpleapi::init();sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");
 for(int i=5;i<8;++i)if(!sofa::simpleapi::importPlugin(argv[i]))throw std::runtime_error("plugin");
 auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("scene");sofa::simulation::node::initRoot(root.get());auto*body=root->getChild("Multilayer");if(!body)throw std::runtime_error("body");
 auto probe=sofa::core::objectmodel::New<Probe>();probe->nodes=nodes;
 for(auto*f:static_cast<sofa::core::objectmodel::BaseContext*>(body)->getObjects<sofa::core::behavior::ForceField<Types>>(sofa::core::objectmodel::BaseContext::Local))if(f->getClassName()=="CurvedMaterialContact"){
  if(probe->contact)throw std::runtime_error("multiple contacts");
  auto*c=static_cast<Contact*>(f);
  if(f->findData("historySpacing")!=&c->historySpacing||f->findData("objectIndex")!=&c->objectIndex||f->findData("filename")!=&c->filename)throw std::runtime_error("frozen project-class ABI mismatch");probe->contact=c;
 }
 if(!probe->contact||probe->contact->objectIndex.getValue()!=6*nodes)throw std::runtime_error("explicit six-layer point scope");
 probe->out.open(argv[4]);if(!probe->out)throw std::runtime_error("trace output");probe->out<<std::setprecision(17)<<"time,step,edge,ideal_reference_mm,weight_mm,normal_density,capacity_density,elastic_norm_mm,plastic_density,weighted_plastic,sliding,previously_active,material_count\n";
 sofa::core::objectmodel::BaseComponent::SPtr helper;for(auto obj:body->object)if(obj->getClassName()=="CompensatedBeamTranslations")helper=obj;
 if(!helper||!body->removeObject(helper)||!body->addObject(probe,sofa::core::objectmodel::TypeOfInsertion::AtBegin)||!body->addObject(helper,sofa::core::objectmodel::TypeOfInsertion::AtBegin))throw std::runtime_error("public pre-Commit stage insertion");
 if(body->object[0].get()!=helper.get()||body->object[1].get()!=probe.get())throw std::runtime_error("probe is not after structural accumulation");
 for(int i=0;i<steps;++i)sofa::simulation::node::animate(root.get());
 if(probe->steps!=unsigned(steps)||probe->contact->steps!=unsigned(steps))throw std::runtime_error("once-per-step owner/probe mismatch");
 std::cout<<"POINT_TRACE {\"steps\":"<<steps<<",\"snapshots\":"<<probe->next<<",\"query_history_changes\":0}\n";
 sofa::simulation::node::unload(root);probe.reset();root.reset();sofa::simulation::Simulation::theSimulation.reset();sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
 }catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<'\n';return 1;}}
