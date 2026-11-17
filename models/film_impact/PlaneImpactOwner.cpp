#include "PlaneFlight.h"
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/behavior/BaseForceField.h>
#include <sofa/core/behavior/OdeSolver.h>
#include <sofa/core/BaseMapping.h>
#include <sofa/core/behavior/BaseProjectiveConstraintSet.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip_film_impact {
void registerFilmSuppliedEventImpulse(sofa::core::ObjectFactory*);
void registerFilmIsolatedEventStep(sofa::core::ObjectFactory*);
class BallisticPlaneImpact final:public sofa::core::objectmodel::BaseObject {
public:
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 using Link=sofa::core::objectmodel::BaseLink;
 SOFA_CLASS(BallisticPlaneImpact,sofa::core::objectmodel::BaseObject);
 sofa::core::objectmodel::SingleLink<BallisticPlaneImpact,State,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK> body;
 sofa::core::objectmodel::Data<double> restitution;
 sofa::core::objectmodel::Data<std::string> filename;
 Eigen::Vector3d beginX,beginV;double beginTime=0,last=-1,mass=0;
 std::ofstream journal;RestartHistory history;
 BallisticPlaneImpact():body(initLink("body","One unmapped point;not a film owner")),
 restitution(initData(&restitution,0.,"restitution","Explicit Newton restitution assumption")),
 filename(initData(&filename,std::string(),"filename","Exclusive actual event/state journal")){f_listening.setValue(true);}
 void init()override{
  BaseObject::init();if(!body||body->getSize()!=1||getContext()->getGravity().norm()!=0)
   throw std::runtime_error("ballistic reference requires one point and zero gravity");
  if(!std::isfinite(restitution.getValue())||restitution.getValue()<0||restitution.getValue()>1)
   throw std::runtime_error("restitution must be in[0,1]");
  if(!getContext()->getObjects<sofa::core::behavior::OdeSolver>(sofa::core::objectmodel::BaseContext::SearchDown).empty())
   throw std::runtime_error("reference is the sole integrator;external ODE solver rejected");
  if(!getContext()->getObjects<sofa::core::BaseMapping>(sofa::core::objectmodel::BaseContext::SearchDown).empty()||
     !getContext()->getObjects<sofa::core::behavior::BaseProjectiveConstraintSet>(sofa::core::objectmodel::BaseContext::SearchDown).empty())
   throw std::runtime_error("ballistic reference rejects mappings/projective constraints;use projected-film law instead");
  for(auto*f:getContext()->getObjects<sofa::core::behavior::BaseForceField>(sofa::core::objectmodel::BaseContext::SearchDown))
   if(!dynamic_cast<sofa::core::behavior::BaseMass*>(f))throw std::runtime_error("ballistic reference excludes external/internal forces");
  auto*m=body->getContext()->getMass();if(!m)throw std::runtime_error("actual mass required");mass=m->getElementMass(0);
  if(!(mass>0)||!std::isfinite(mass))throw std::runtime_error("positive actual mass required");
  if(filename.getValue().empty()||std::ifstream(filename.getValue()))throw std::runtime_error("impact journal exists/empty");
  journal.open(filename.getValue());if(!journal)throw std::runtime_error("impact journal open");
  journal<<std::setprecision(17)<<"time,dt,event_time,pre_normal,post_normal,impulse,impact_loss,momentum_residual,x,y,z,vx,vy,vz,history_invalidated\n";
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){
   const auto&x=body->read(sofa::core::vec_id::read_access::position)->getValue()[0];
   const auto&v=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];
   for(unsigned d=0;d<3;++d){beginX(d)=x[d];beginV(d)=v[d];}beginTime=getContext()->getTime();return;
  }
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;
  double time=getContext()->getTime(),h=getContext()->getDt();if(time==last)return;last=time;
  auto r=planeFlight(beginX,beginV,Eigen::Vector3d(1,0,0),0,mass,h,restitution.getValue());
  // Query purity: two kernel queries must have identical values before commit.
  auto repeat=planeFlight(beginX,beginV,Eigen::Vector3d(1,0,0),0,mass,h,restitution.getValue());
  if(r.position!=repeat.position||r.velocity!=repeat.velocity||r.impulse!=repeat.impulse)
   throw std::runtime_error("impure impact query");
  auto x=body->read(sofa::core::vec_id::read_access::position)->getValue();
  auto v=body->read(sofa::core::vec_id::read_access::velocity)->getValue();
  for(unsigned d=0;d<3;++d){x[0][d]=r.position(d);v[0][d]=r.velocity(d);}
  body->write(sofa::core::vec_id::write_access::position)->setValue(x);
  body->write(sofa::core::vec_id::write_access::velocity)->setValue(v);
  if(r.fraction)history.impact();else history.acceptSmoothStep(h);
  journal<<time<<','<<h<<',';if(r.fraction)journal<<beginTime+h*(*r.fraction);else journal<<"null";
  if(r.fraction)journal<<','<<r.preNormal<<','<<r.postNormal;else journal<<",null,null";
  journal<<','<<r.impulse<<','<<r.loss<<','<<r.momentumResidual;
  for(unsigned d=0;d<3;++d)journal<<','<<r.position(d);
  for(unsigned d=0;d<3;++d)journal<<','<<r.velocity(d);
  journal<<','<<bool(r.fraction)<<'\n';journal.flush();
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripImpactReference";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){
 regrip_film_impact::registerFilmSuppliedEventImpulse(f);
 regrip_film_impact::registerFilmIsolatedEventStep(f);
 f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL exact force-free point-plane impact integrator;NOT film dynamics").add<regrip_film_impact::BallisticPlaneImpact>());
}
}
