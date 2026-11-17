#include "FilmEventImpulse.h"
#include "FilmRestartHistory.h"
#include "IsolatedFilmImpactStep.h"
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/simulation/MechanicalOperations.h>
#include <fstream>
#include <iomanip>
#include <memory>
namespace regrip_film_impact {
// A zero-time, explicitly supplied event-state API owner. Deliberately NOT a
// continuous birth detector or full film timestep replacement. One event only.
class FilmSuppliedEventImpulse:public sofa::core::objectmodel::BaseObject {
public:
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 using Link=sofa::core::objectmodel::BaseLink;
 SOFA_CLASS(FilmSuppliedEventImpulse,sofa::core::objectmodel::BaseObject);
 sofa::core::objectmodel::SingleLink<FilmSuppliedEventImpulse,State,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK> root;
 sofa::core::objectmodel::SingleLink<FilmSuppliedEventImpulse,sofa::core::objectmodel::BaseObject,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK> field;
 sofa::core::objectmodel::Data<unsigned> node;
 sofa::core::objectmodel::Data<double> radius;
 sofa::core::objectmodel::Data<sofa::type::Vec3> center;
 sofa::core::objectmodel::Data<std::string> filename;
 bool done=false;std::ofstream journal;
 FilmSuppliedEventImpulse():root(initLink("root","Independent displacement state")),field(initLink("field","Actual FilmRailTendon")),
 node(initData(&node,0u,"node","Single supplied event material node;NOT triangle closure")),
 radius(initData(&radius,1.,"radius","Supplied fixed sphere radius incl buffer")),
 center(initData(&center,sofa::type::Vec3(0,0,0),"center","Supplied fixed sphere center")),
 filename(initData(&filename,std::string(),"filename","Exclusive supplied-event impulse journal")){f_listening.setValue(true);}
 template<class T>T parameter(const char*name)const{
  auto*data=dynamic_cast<sofa::core::objectmodel::Data<T>*>(field->findData(name));
  if(!data)throw std::runtime_error("actual film event parameter missing");return data->getValue();
 }
 void init()override{
  BaseObject::init();if(!root||!field||field->getClassName()!="FilmRailTendon"||getContext()->getGravity().norm()!=0)
   throw std::runtime_error("supplied film event requires explicit actual film links and zero gravity");
  if(getContext()->getTime()!=0)throw std::runtime_error("supplied event reference starts at zero only");
  if(filename.getValue().empty()||std::ifstream(filename.getValue()))throw std::runtime_error("film event journal exists/empty");
  journal.open(filename.getValue());if(!journal)throw std::runtime_error("film event journal open");
  journal<<std::setprecision(17)<<"event_time,node,gap,pre_normal,post_normal,impulse,effective_mass,momentum_residual,impact_loss,history_beta,query_pure\n";
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(done||!dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event))return;
  if(getContext()->getTime()!=0)throw std::runtime_error("supplied initial-event time mismatch");
  sofa::simulation::common::MechanicalOperations initial(sofa::core::ExecParams::defaultInstance(),getContext());
  initial.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  auto*local=dynamic_cast<State*>(field->getContext()->getMechanicalState());auto*actualMass=field->getContext()->getMass();
  if(!local||!actualMass)throw std::runtime_error("supplied event actual state/mass missing");
  regrip_film_native::Assembly model(parameter<unsigned>("nx"));model.guideIntervals=parameter<unsigned>("guideIntervals");
  model.guideOffset=parameter<double>("guideOffset");model.bondK=parameter<double>("bondStiffness");model.rootGuideSecondOrder=parameter<bool>("rootGuideSecondOrder");
  const auto&x=local->read(sofa::core::vec_id::read_access::position)->getValue();
  const auto&v=local->read(sofa::core::vec_id::read_access::velocity)->getValue();
  std::vector<regrip_film_rail::Point>q(x.size()),before(v.size()),zero(x.size());std::vector<double>mass(x.size());
  if(x.size()!=model.size())throw std::runtime_error("film API geometry mismatch");
  for(unsigned i=0;i<x.size();++i){mass[i]=actualMass->getElementMass(i);for(unsigned d=0;d<3;++d){q[i][d]=x[i][d];before[i][d]=v[i][d];}}
  regrip_film_native::CoupledPlaneStep mechanics(model,mass,getContext()->getDt(),0,0,q,before,zero,0);
  auto c=center.getValue();regrip_film_rail::Point point{c[0],c[1],c[2]};
  auto result=filmEventImpulse(mechanics,q,before,{{node.getValue()}},point,radius.getValue(),1e-10,1e-12);
  auto repeat=filmEventImpulse(mechanics,q,before,{{node.getValue()}},point,radius.getValue(),1e-10,1e-12);
  if(result.postVelocity!=repeat.postVelocity||result.reduced.impulse!=repeat.reduced.impulse)throw std::runtime_error("film impact query purity");
  FilmRestartHistory restart(q,before);restart.impact(q,before,result.postVelocity,0);
  auto velocity=root->read(sofa::core::vec_id::read_access::velocity)->getValue();
  for(unsigned a=0;a<mechanics.index.size();++a)if(mechanics.index[a]>=0&&mechanics.weight[a]==1)
   velocity[a/3][a%3]=result.postVelocity[a/3][a%3];
  root->write(sofa::core::vec_id::write_access::velocity)->setValue(velocity);
  sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());
  mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  const auto&accepted=local->read(sofa::core::vec_id::read_access::velocity)->getValue();
  for(unsigned i=0;i<accepted.size();++i)for(unsigned d=0;d<3;++d)
   if(accepted[i][d]!=result.postVelocity[i][d])throw std::runtime_error("actual mapped impact state differs from kernel");
  Eigen::VectorXd pre=mechanics.pack(before);double rate=(result.jacobian*pre)(0);
  double effective=1/(result.jacobian*filmMass(mechanics).llt().solve(result.jacobian.transpose()))(0,0);
  auto p=model.rest()[node.getValue()];for(unsigned d=0;d<3;++d)p[d]+=q[node.getValue()][d]-point[d];
  double gap=std::sqrt(regrip_film_rail::dot(p,p))-radius.getValue();
  journal<<0<<','<<node.getValue()<<','<<gap<<','<<rate<<','<<result.reduced.normalVelocity(0)<<','<<result.reduced.impulse(0)<<','<<effective<<','<<result.reduced.momentumResidual<<','<<result.reduced.energyLoss<<','<<restart.reference(getContext()->getDt()).beta<<",1\n";
  journal.flush();done=true;
 }
};
// Independent one-timestep prototype with detected (subintegrated) birth and
// post-impact BE restart. Only a certified externally isolated point event is
// supported. It MUST NOT be used as a whole-surface/full-cycle replacement.
class FilmIsolatedEventStep final:public FilmSuppliedEventImpulse {
public:
 SOFA_CLASS(FilmIsolatedEventStep,FilmSuppliedEventImpulse);
 sofa::core::objectmodel::Data<bool> isolatedSequence{initData(&isolatedSequence,false,"isolatedSequence","At most80 cold-start steps with ONE isolated point impact and contact-free remainder;NOT full contact")};
 sofa::core::objectmodel::Data<bool> midpointRestart{initData(&midpointRestart,false,"midpointRestart","Separate second-order implicit midpoint startup/restart contrast;original BE default preserved")};
 sofa::core::objectmodel::Data<unsigned> maximumSequenceSteps{initData(&maximumSequenceSteps,80u,"maximumSequenceSteps","Profile-bounded reference count,up to160;not a physical tolerance")};
 std::unique_ptr<IsolatedFilmSequence> sequence;unsigned steps=0;std::ofstream endpoints;
 std::vector<regrip_film_rail::Point>beginPosition,beginVelocity;
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){
   if(maximumSequenceSteps.getValue()>160||maximumSequenceSteps.getValue()==0||
      (!isolatedSequence.getValue()&&(done||getContext()->getTime()!=0))||steps>=maximumSequenceSteps.getValue()||getContext()->getDt()>.0011)
    throw std::runtime_error("isolated prototype step/duration policy");
   sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());
   mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
   auto*local=dynamic_cast<State*>(field->getContext()->getMechanicalState());if(!local)throw std::runtime_error("isolated event local state");
   const auto&q=local->read(sofa::core::vec_id::read_access::position)->getValue();const auto&v=local->read(sofa::core::vec_id::read_access::velocity)->getValue();
   beginPosition.resize(q.size());beginVelocity.resize(v.size());for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d){beginPosition[i][d]=q[i][d];beginVelocity[i][d]=v[i][d];}return;
  }
  if((done&&!isolatedSequence.getValue())||!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;
  if(parameter<double>("maximumTension")!=0)throw std::runtime_error("isolated timestep reference currently requires zero prescribed tendon tension");
  regrip_film_native::Assembly model(parameter<unsigned>("nx"));model.guideIntervals=parameter<unsigned>("guideIntervals");
  model.guideOffset=parameter<double>("guideOffset");model.bondK=parameter<double>("bondStiffness");model.rootGuideSecondOrder=parameter<bool>("rootGuideSecondOrder");
  auto*mass=field->getContext()->getMass();if(!mass)throw std::runtime_error("isolated event mass");
  std::vector<double>masses(model.size());for(unsigned i=0;i<masses.size();++i)masses[i]=mass->getElementMass(i);
  // This reference uses the same documented c=2 mass damping as the source
  // scene. Reject any actual ODE parameter mismatch rather than silently fit it.
  auto*ode=getContext()->get<sofa::core::objectmodel::BaseObject>(std::string("ode"));
  auto*damping=ode?dynamic_cast<sofa::core::objectmodel::Data<double>*>(ode->findData("rayleighMass")):nullptr;
  if(!damping||damping->getValue()!=2)throw std::runtime_error("isolated prototype requires matching actual mass damping2");
  regrip_film_native::CoupledPlaneStep mechanics(model,masses,getContext()->getDt(),2,0,beginPosition,beginVelocity,std::vector<regrip_film_rail::Point>(model.size()),0);
  auto c=center.getValue();regrip_film_rail::Point point{c[0],c[1],c[2]};
  IsolatedFilmImpactStep result;bool hit=true;double eventTime=0;
  if(isolatedSequence.getValue()){
   if(!sequence)sequence=std::make_unique<IsolatedFilmSequence>(mechanics,node.getValue(),point,radius.getValue(),midpointRestart.getValue());
   if(sequence->history.position!=beginPosition||sequence->history.velocity!=beginVelocity)
    throw std::runtime_error("actual accepted state differs from event sequence owner");
   auto value=sequence->advance(getContext()->getDt());hit=bool(value);
   if(value){result=std::move(*value);eventTime=sequence->history.lastJump->time;}
   result.position=sequence->history.position;result.velocity=sequence->history.velocity;
   auto p=regrip_film_rail::add(model.rest().at(node.getValue()),result.position.at(node.getValue()));
   result.remainingGap=regrip_film_sphere::ClosestPrimitive::evaluate({p},point,radius.getValue()).gap.v;
  }else{result=isolatedFilmImpactStep(mechanics,node.getValue(),point,radius.getValue(),midpointRestart.getValue());eventTime=result.birth.time;}
  auto x=root->read(sofa::core::vec_id::read_access::position)->getValue();auto v=root->read(sofa::core::vec_id::read_access::velocity)->getValue();
  for(unsigned a=0;a<mechanics.index.size();++a)if(mechanics.index[a]>=0&&mechanics.weight[a]==1){x[a/3][a%3]=result.position[a/3][a%3];v[a/3][a%3]=result.velocity[a/3][a%3];}
  root->write(sofa::core::vec_id::write_access::position)->setValue(x);root->write(sofa::core::vec_id::write_access::velocity)->setValue(v);
  sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());
  mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  auto*local=dynamic_cast<State*>(field->getContext()->getMechanicalState());const auto&actual=local->read(sofa::core::vec_id::read_access::position)->getValue();
  for(unsigned i=0;i<actual.size();++i)for(unsigned d=0;d<3;++d)if(actual[i][d]!=result.position[i][d])throw std::runtime_error("isolated event mapped position mismatch");
  if(hit){Eigen::VectorXd pre=mechanics.pack(result.birth.velocity);double before=(result.impact.jacobian*pre)(0);
   double effective=1/(result.impact.jacobian*filmMass(mechanics).llt().solve(result.impact.jacobian.transpose()))(0,0);
   journal<<eventTime<<','<<node.getValue()<<','<<result.birth.gap<<','<<before<<','<<result.impact.reduced.normalVelocity(0)<<','<<result.impact.reduced.impulse(0)<<','<<effective<<','<<result.impact.reduced.momentumResidual<<','<<result.impact.reduced.energyLoss<<",1,null\n";journal.flush();}
  if(!endpoints.is_open()){
   std::string path=filename.getValue()+".endpoint.csv";if(std::ifstream(path))throw std::runtime_error("isolated endpoint journal exists");
   endpoints.open(path);endpoints<<std::setprecision(17)<<"time,gap,shell_energy,attachment_energy,kinetic_energy,local_displacement,local_velocity\n";
  }
  double shell=0,attachment=0,kinetic=0;model.elements(result.position,0,[&](const regrip_film_rail::Element&e){if(e.kind==0)shell+=e.energy.v;if(e.kind==1)attachment+=e.energy.v;});
  for(unsigned i=0;i<masses.size();++i)kinetic+=.5*masses[i]*regrip_film_rail::dot(result.velocity[i],result.velocity[i]);
  endpoints<<getContext()->getTime()<<','<<result.remainingGap<<','<<shell<<','<<attachment<<','<<kinetic<<",\"";
  for(const auto&p:result.position){for(double value:p)endpoints<<value<<' ';}endpoints<<"\",\"";
  for(const auto&p:result.velocity){for(double value:p)endpoints<<value<<' ';}endpoints<<"\"\n";endpoints.flush();
  done=true;++steps;
 }
};
void registerFilmSuppliedEventImpulse(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Supplied zero-time film event impulse API reference;NOT contact birth/full dynamic solver").add<FilmSuppliedEventImpulse>());}
void registerFilmIsolatedEventStep(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Isolated point event/impulse/remainder prototype;NOT whole-surface or full-cycle contact").add<FilmIsolatedEventStep>());}
}
