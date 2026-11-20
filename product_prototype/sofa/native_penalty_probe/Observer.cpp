#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/core/behavior/OdeSolver.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/component/collision/response/contact/PenalityContactForceField.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip {
class NativePenaltyJournal:public sofa::core::objectmodel::BaseComponent {
public:
 SOFA_CLASS(NativePenaltyJournal,sofa::core::objectmodel::BaseComponent);
 using FF=sofa::component::collision::response::contact::PenalityContactForceField<sofa::defaulttype::Vec3Types>;
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 sofa::core::objectmodel::SingleLink<NativePenaltyJournal,State,sofa::core::objectmodel::BaseLink::FLAG_STOREPATH|sofa::core::objectmodel::BaseLink::FLAG_STRONGLINK> point;
 sofa::core::objectmodel::Data<std::string> filename;std::ofstream f,p;
 NativePenaltyJournal():point(initLink("point","Optional actual Vec3 state/force slot,read only")),filename(initData(&filename,std::string(),"filename","Unique read-only contact metadata snapshot")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();if(std::ifstream(filename.getValue()))throw std::runtime_error("existing penalty journal");f.open(filename.getValue());f<<std::setprecision(17)<<"time_s,forcefield,row,ks_N_per_m,contact_distance_m,stored_penetration_snapshot_m,stored_force_expression_NOT_FORCE_EVALUATION_N,accepted_geometric_gap_m,normal\n";}
 void bwdInit()override{BaseComponent::bwdInit();std::ofstream schema(filename.getValue()+".solver.csv");schema<<"component,data,value\n";for(auto*o:getContext()->getObjects<sofa::core::objectmodel::BaseComponent>(sofa::core::objectmodel::BaseContext::SearchDown))if(dynamic_cast<sofa::core::behavior::OdeSolver*>(o)||o->getClassName()=="NewtonRaphsonSolver")for(auto*d:o->getDataFields())schema<<std::quoted(o->getClassName())<<','<<std::quoted(d->getName())<<','<<std::quoted(d->getValueString())<<'\n';if(point){p.open(filename.getValue()+".point.csv");p<<std::setprecision(17)<<"time_s,q,v,force_slot,Newton_status,Newton_residualGraph\n";}}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  for(auto*ff:getContext()->getObjects<FF>(sofa::core::objectmodel::BaseContext::SearchDown)){
   auto p=ff->getMState1()->readPositions();auto q=ff->getMState2()->readPositions();unsigned row=0;
   for(const auto&c:ff->getContact()){const auto g=(q[c.m2]-p[c.m1])*c.norm-c.dist;f<<getContext()->getTime()<<",\""<<ff->getPathName()<<"\","<<row++<<','<<c.ks<<','<<c.dist<<','<<c.pen<<','<<(c.pen>0?c.ks*c.pen:0)<<','<<g<<",\""<<c.norm<<"\"\n";}
  }f.flush();
  if(point){p<<getContext()->getTime()<<",\""<<point->readPositions().ref()<<"\",\""<<point->readVelocities().ref()<<"\",\""<<point->read(sofa::core::vec_id::read_access::force)->getValue()<<'"';std::string status="NOT_MEASURED",graph="NOT_MEASURED";for(auto*o:getContext()->getObjects<sofa::core::objectmodel::BaseComponent>(sofa::core::objectmodel::BaseContext::SearchDown))if(o->getClassName()=="NewtonRaphsonSolver"){status=o->findData("status")->getValueString();graph=o->findData("residualGraph")->getValueString();}p<<','<<std::quoted(status)<<','<<std::quoted(graph)<<'\n';p.flush();}
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripPenaltyProbe";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only Native penalty forcefield data;no state or solver changes").add<regrip::NativePenaltyJournal>());}
}
