// Reuse guarded links/material/API initialization without changing the old
// persistent owner. This separate research DLL registers ONLY its new owner.
#define REGRIP_THREE_FILM_EMBEDDED
#include "../film_three_finger/ThreeFilmOwner.cpp"
#include "BracketedBirth.h"
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/core/objectmodel/BaseNode.h>
#include <set>
namespace regrip_three_event {
class ThreeFilmBracketedEventODE:public regrip_three_finger::ThreeFilmDrivenODE {
public:
 SOFA_CLASS(ThreeFilmBracketedEventODE,regrip_three_finger::ThreeFilmDrivenODE);
 bool exactDistanceOrder()const override{return true;}
 sofa::core::objectmodel::Data<bool>firstIntervalJournal{initData(&firstIntervalJournal,false,"firstIntervalJournal","Opt-in actual free/impact/remainder stage inventory;no force/state law change")};
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!ready){msg_error(this)<<"Event owner invalid;no commit";return;}
  if(count++!=0||dt!=.0002||getContext()->getTime()!=0)throw std::runtime_error("isolated externally bracketed event coupon:ONE200us step only,NOT general closing");
  for(auto suffix:{".event.csv",".impact_rows.csv",".first_interval.csv"})if(std::ifstream(filename.getValue()+suffix))throw std::runtime_error("event output exists;use exclusive new output paths");
  sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  SharedFilmSystem system(Layout(),Eigen::Vector3d(0,0,-.001),true,true);system.exactUnresolved=true;
  unsigned nf=system.shared.nf,nb=3*nf;Eigen::VectorXd q=system.initial,v=Eigen::VectorXd::Zero(q.size());system.shared.M.setZero();
  std::array<Film*,3>roots={root.get(),root1.get(),root2.get()},locals;
  std::array<sofa::core::objectmodel::BaseObject*,3>fields={field.get(),field1.get(),field2.get()};
  for(unsigned f=0;f<3;++f){auto&s=system.shared.films[f];locals[f]=dynamic_cast<Film*>(fields[f]->getContext()->getMechanicalState());auto*mass=fields[f]->getContext()->getMass();if(!locals[f]||!mass)throw std::runtime_error("event actual local mass/state missing");const auto&x=locals[f]->read(sofa::core::vec_id::read_access::position)->getValue();const auto&vel=locals[f]->read(sofa::core::vec_id::read_access::velocity)->getValue();if(x.size()!=s.film.model.size())throw std::runtime_error("event film size mismatch");std::vector<Point>xx(x.size()),vv(x.size());
   for(unsigned i=0;i<x.size();++i){double m=mass->getElementMass(i);if(!(m>0)||std::abs(m-s.film.mass[i])>1e-13*s.film.mass[i])throw std::runtime_error("event public mass differs from research fixture");s.film.mass[i]=m;for(unsigned d=0;d<3;++d){xx[i][d]=x[i][d];vv[i][d]=vel[i][d];unsigned a=3*i+d;int k=s.film.index[a];if(k>=0)system.shared.M(f*nf+k,f*nf+k)+=m*s.film.weight[a]*s.film.weight[a];}}
   q.segment(f*nf,nf)=s.film.pack(xx);v.segment(f*nf,nf)=s.film.pack(vv);if(xx!=s.before.q||v.segment(f*nf,nf).norm()!=0)throw std::runtime_error("event fixture must have initially unstrained stationary films");
  }
  auto bx=body->read(sofa::core::vec_id::read_access::position)->getValue();auto bv=body->read(sofa::core::vec_id::read_access::velocity)->getValue();sofa::linearalgebra::FullMatrix<double>mass(6,6);mass.clear();body->getContext()->getMass()->getElementMass(0,&mass);
  for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j){double expected=i==j?(i<3?.0001:.036):0;if(std::abs(mass.element(i,j)-expected)>1e-14*std::max(1e-20,std::abs(expected)))throw std::runtime_error("event sphere public mass/inertia fixture differs");system.shared.M(nb+i,nb+j)=mass.element(i,j);}
  for(unsigned d=0;d<3;++d){q(nb+d)=bx[0].getCenter()[d];v(nb+d)=bv[0].getVCenter()[d];v(nb+3+d)=bv[0].getVOrientation()[d];}
  auto expected=system.initial;expected(nb+2)+=.0001;Eigen::VectorXd incoming=Eigen::VectorXd::Zero(q.size());incoming(nb+2)=-1;
  if((q-expected).norm()>1e-14||(v-incoming).norm()!=0||externalForce.getValue()!=sofa::type::Vec3(0,0,-.001))throw std::runtime_error("separated prescribed initial velocity event fixture differs;NOT C2 closing from REST");
  EventControl control{read<double>(field.get(),"maximumTension"),read<double>(field.get(),"rampTime"),read<double>(field.get(),"releaseBegin"),read<double>(field.get(),"releaseEnd"),read<bool>(field.get(),"c2Control")};
  auto birth=bracketedBirth(system,q,v,0,.00005,.0002,control);auto result=regrip_collocation::persistentRows(system.shared.M,2,birth.before.q,birth.impact.state.velocity,birth.time,dt-birth.time,[&](const auto&x,double t){return system.force(x,control.sample(t).tension);},[&](const auto&x){return system.geometry(x);});double gap=system.clearance(result.q);for(const auto&s:result.stages)gap=std::min(gap,system.clearance(s.q));if(gap< -1e-10)throw std::runtime_error("event remaining-step whole-stage clearance failed");
  if(firstIntervalJournal.getValue()){
   std::ofstream out(filename.getValue()+".first_interval.csv");out<<std::setprecision(17)<<"stage,time,weight_s,tension_N,normal_power_Nmm_s,lambda_N,q,v\n";
   auto record=[&](const char*name,double time,double weight,const Eigen::VectorXd&position,const Eigen::VectorXd&velocity,const Eigen::VectorXd&lambda,const Eigen::MatrixXd&J){out<<name<<','<<time<<','<<weight<<','<<control.sample(time).tension<<','<<(lambda.size()?lambda.dot(J*velocity):0)<<',';for(int i=0;i<lambda.size();++i)out<<(i?" ":"")<<lambda(i);for(const auto*values:{&position,&velocity}){out<<',';for(int i=0;i<values->size();++i)out<<(i?" ":"")<<(*values)(i);}out<<'\n';};
   Eigen::VectorXd none;Eigen::MatrixXd noRows(0,q.size());double tau=birth.time,remaining=dt-tau;Eigen::VectorXd middle=(v+birth.before.v)/2;middle.segment<3>(nb)=(v.segment<3>(nb)+tau/2*system.external/system.shared.M(nb,nb))/(1+tau);middle.tail<3>()=v.tail<3>()/(1+tau);Eigen::VectorXd middleQ=q+tau/2*middle;
   record("initial",0,0,q,v,none,noRows);record("free_midpoint",tau/2,tau,middleQ,middle,none,noRows);record("pre_impact",tau,0,birth.before.q,birth.before.v,none,noRows);record("post_impact",tau,0,birth.before.q,birth.impact.state.velocity,none,noRows);
   auto initialGeometry=system.geometry(birth.before.q);record("contact_initial",tau,remaining/6,birth.before.q,birth.impact.state.velocity,result.initialForce,initialGeometry.J);record("contact_midpoint",tau+remaining/2,2*remaining/3,result.stages[0].q,result.stages[0].v,result.stages[0].force,result.stages[0].geometry.J);record("contact_end",dt,remaining/6,result.q,result.v,result.stages[1].force,result.stages[1].geometry.J);out.flush();
  }
  for(unsigned f=0;f<3;++f){auto&s=system.shared.films[f];auto xx=s.film.expand(result.q.segment(f*nf,nf)),vv=s.film.expand(result.v.segment(f*nf,nf));auto x=roots[f]->read(sofa::core::vec_id::read_access::position)->getValue();auto vel=roots[f]->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned a=0;a<s.film.index.size();++a)if(s.film.index[a]>=0&&s.film.weight[a]==1){x[a/3][a%3]=xx[a/3][a%3];vel[a/3][a%3]=vv[a/3][a%3];}roots[f]->write(sofa::core::vec_id::write_access::position)->setValue(x);roots[f]->write(sofa::core::vec_id::write_access::velocity)->setValue(vel);}
  for(unsigned d=0;d<3;++d){bx[0].getCenter()[d]=result.q(nb+d);bv[0].getVCenter()[d]=result.v(nb+d);bv[0].getVOrientation()[d]=result.v(nb+3+d);}Eigen::Vector3d angle=result.q.tail<3>();Eigen::Quaterniond orientation(bx[0].getOrientation()[3],bx[0].getOrientation()[0],bx[0].getOrientation()[1],bx[0].getOrientation()[2]);if(angle.norm()>0)orientation=Eigen::Quaterniond(Eigen::AngleAxisd(angle.norm(),angle/angle.norm()))*orientation;for(unsigned d=0;d<4;++d)bx[0].getOrientation()[d]=orientation.coeffs()(d);body->write(sofa::core::vec_id::write_access::position)->setValue(bx);body->write(sofa::core::vec_id::write_access::velocity)->setValue(bv);mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  for(unsigned f=0;f<3;++f){auto xx=system.shared.films[f].film.expand(result.q.segment(f*nf,nf)),vv=system.shared.films[f].film.expand(result.v.segment(f*nf,nf));const auto&ax=locals[f]->read(sofa::core::vec_id::read_access::position)->getValue();const auto&av=locals[f]->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned i=0;i<xx.size();++i)for(unsigned d=0;d<3;++d)if(ax[i][d]!=xx[i][d]||av[i][d]!=vv[i][d])throw std::runtime_error("event actual mapped q/v commit mismatch");}
  const auto&actual=body->read(sofa::core::vec_id::read_access::position)->getValue()[0];const auto&actualV=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];for(unsigned d=0;d<3;++d)if(actual.getCenter()[d]!=result.q(nb+d)||actualV.getVCenter()[d]!=result.v(nb+d)||actualV.getVOrientation()[d]!=result.v(nb+3+d))throw std::runtime_error("event actual FREE body commit mismatch");
  std::ofstream journal(filename.getValue()+".event.csv");journal<<std::setprecision(17)<<"event_time,gap,rows,rank,momentum,energy_loss,minimum_vn,impulse,qminus,vminus,vplus,qend,vend\n"<<birth.time<<','<<birth.gap<<','<<birth.rows.size()<<','<<birth.impact.rank<<','<<birth.momentumResidual<<','<<birth.impact.state.energyLoss<<','<<birth.impact.state.normalVelocity.minCoeff()<<',';auto vector=[&](const Eigen::VectorXd&x){for(int i=0;i<x.size();++i)journal<<(i?" ":"")<<x(i);};vector(birth.impact.state.impulse);journal<<',';vector(birth.before.q);journal<<',';vector(birth.before.v);journal<<',';vector(birth.impact.state.velocity);journal<<',';vector(result.q);journal<<',';vector(result.v);journal<<'\n';journal.flush();
  std::ofstream rows(filename.getValue()+".impact_rows.csv");rows<<std::setprecision(17)<<"time,owner,owner_finger,triangle,feature,gap,normal_before,normal_after,impulse_Ns,nx,ny,nz,px,py,pz,jacobian\n";
  for(unsigned i=0;i<birth.rows.size();++i){const auto&r=birth.rows[i];auto row=system.shared.films[r.finger].geometry(system.local(birth.before.q,r.finger),r.triangle);Eigen::Vector3d normal=system.layout.mount[r.finger].R*row.normal,point=system.layout.mount[r.finger].origin+system.layout.mount[r.finger].R*row.contact;rows<<birth.time<<','<<i<<','<<r.finger<<','<<r.triangle<<','<<r.feature<<','<<r.gap<<','<<r.normalBefore<<','<<r.normalAfter<<','<<birth.impact.state.impulse(i);for(unsigned d=0;d<3;++d)rows<<','<<normal(d);for(unsigned d=0;d<3;++d)rows<<','<<point(d);rows<<',';for(int k=0;k<birth.J.cols();++k)rows<<(k?" ":"")<<birth.J(i,k);rows<<'\n';}rows.flush();
  accepted<<dt<<','<<gap<<','<<result.momentumResidual<<','<<result.velocityResidual<<','<<result.iterations<<','<<result.evaluations<<',';auto state=[&](const auto&x){for(int i=0;i<x.size();++i)accepted<<(i?" ":"")<<x(i);};state(result.q);accepted<<',';state(result.v);accepted<<'\n';accepted.flush();
 }
};
// Keep the isolated-event owner intact. AFTER its accepted event/remainder,
// reuse the existing actual public-mass persistent owner at the next real
// SOFA clock. Its compressive-row/whole-stage guards remain unchanged.
// This is NOT release/re-impact handling:those branches still reject.
class ThreeFilmEventContinuationODE:public ThreeFilmBracketedEventODE {
public:
 SOFA_CLASS(ThreeFilmEventContinuationODE,ThreeFilmBracketedEventODE);
 void solve(const sofa::core::ExecParams*p,SReal dt,sofa::core::MultiVecCoordId x,sofa::core::MultiVecDerivId v)override{
  if(dt!=.0002||maxSteps.getValue()!=8)throw std::runtime_error("profiled eight200us macro contact continuation only");
  if(count==0)ThreeFilmBracketedEventODE::solve(p,dt,x,v);
  else regrip_three_finger::ThreeFilmPersistentODE::solve(p,dt,x,v);
 }
};
class ThreeFilmVariableContinuationODE:public ThreeFilmBracketedEventODE {
public:
 SOFA_CLASS(ThreeFilmVariableContinuationODE,ThreeFilmBracketedEventODE);
 void solve(const sofa::core::ExecParams*p,SReal dt,sofa::core::MultiVecCoordId x,sofa::core::MultiVecDerivId v)override{
  if(maxSteps.getValue()!=32||(count==0?dt!=.0002:(dt!=.0002&&dt!=.0001&&dt!=.00005))||getContext()->getTime()+dt>.0016+1e-14)throw std::runtime_error("bounded200us COMMON impact then200/100/50us persistent refinement only");
  if(count==0)ThreeFilmBracketedEventODE::solve(p,dt,x,v);
  else regrip_three_finger::ThreeFilmPersistentODE::solve(p,dt,x,v);
 }
};
// Separate profiled first C2 peak scope,not a silent extension of the tested
// 1.6ms owner. Sustained row/release/whole-surface guards are still enforced.
class ThreeFilmFirstPeakODE:public ThreeFilmBracketedEventODE {
public:
 SOFA_CLASS(ThreeFilmFirstPeakODE,ThreeFilmBracketedEventODE);
 void solve(const sofa::core::ExecParams*p,SReal dt,sofa::core::MultiVecCoordId x,sofa::core::MultiVecDerivId v)override{
  if(maxSteps.getValue()!=64||dt!=.0002||getContext()->getTime()+dt>.01+1e-14)throw std::runtime_error("separately profiled fifty200us steps to FIRST C2 peak only");
  if(count==0)ThreeFilmBracketedEventODE::solve(p,dt,x,v);
  else regrip_three_finger::ThreeFilmPersistentODE::solve(p,dt,x,v);
 }
};
// Public API scheduler,NOT a force/state observer:changes NEXT macro dt only
// after the common impact step has ended. Records actual time and used dt.
class ThreeFilmPostImpactClock:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(ThreeFilmPostImpactClock,sofa::core::objectmodel::BaseObject);
 sofa::core::objectmodel::Data<unsigned>refinement{initData(&refinement,1u,"refinement","1/2/4 next-step refinement;first impact remains200us")};
 sofa::core::objectmodel::Data<bool>synchronizeChildren{initData(&synchronizeChildren,false,"synchronizeChildren","Explicit new clock version:public NEXT dt on all child contexts before next AnimateBegin;old root-only mode retained")};
 sofa::core::objectmodel::Data<std::string>filename{initData(&filename,std::string(),"filename","Exclusive actual dt schedule journal")};
 std::ofstream out;double previous=0;unsigned calls=0;bool ready=false;
 ThreeFilmPostImpactClock(){f_listening.setValue(true);}
 void init()override{sofa::core::objectmodel::BaseObject::init();if((refinement.getValue()!=1&&refinement.getValue()!=2&&refinement.getValue()!=4)||filename.getValue().empty()||std::ifstream(filename.getValue())||getContext()->getDt()!=.0002){msg_error(this)<<"invalid explicit post-impact clock";return;}out.open(filename.getValue());out<<std::setprecision(17)<<"time,used_dt,next_dt,synchronized_contexts,minimum_next_dt,maximum_next_dt\n";ready=true;}
 void handleEvent(sofa::core::objectmodel::Event*e)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;if(!ready)throw std::runtime_error("invalid clock;no silent scheduling");double end=getContext()->getTime(),used=getContext()->getDt(),next=.0002/refinement.getValue();if(std::abs(end-previous-used)>1e-14||end>.0016+1e-14||++calls>1+7*refinement.getValue())throw std::runtime_error("actual post-impact macro clock mismatch");previous=end;getContext()->setDt(next);unsigned contexts=1;double minimum=getContext()->getDt(),maximum=minimum;
  if(synchronizeChildren.getValue()){auto*root=dynamic_cast<sofa::core::objectmodel::BaseNode*>(getContext());if(!root)throw std::runtime_error("explicit scene node needed for child clock synchronization");std::set<sofa::core::objectmodel::BaseNode*>visited;std::function<void(sofa::core::objectmodel::BaseNode*)>apply=[&](auto*node){if(!visited.insert(node).second)return;node->getContext()->setDt(next);minimum=std::min(minimum,node->getContext()->getDt());maximum=std::max(maximum,node->getContext()->getDt());for(auto*child:node->getChildren())apply(child);};apply(root);contexts=visited.size();if(minimum!=next||maximum!=next)throw std::runtime_error("child context rejected explicit NEXT dt");}
  out<<end<<','<<used<<','<<next<<','<<contexts<<','<<minimum<<','<<maximum<<'\n';out.flush();}
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripThreeFilmEvent";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL externally isolated three-film/free sphere event and compressive remainder;NOT general CCD/grasp").add<regrip_three_event::ThreeFilmBracketedEventODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL event followed by reused eight200us actual persistent steps;NOT release/re-impact/grasp").add<regrip_three_event::ThreeFilmEventContinuationODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL common impact and variable post-contact dt;NOT full event refinement").add<regrip_three_event::ThreeFilmVariableContinuationODE>());f->registerObjects(sofa::core::ObjectRegistrationData("Public next-step post-impact dt scheduler;NO force/state writes").add<regrip_three_event::ThreeFilmPostImpactClock>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL fifty200us steps to first C2 peak;NOT hold/release/grasp").add<regrip_three_event::ThreeFilmFirstPeakODE>());}
}
