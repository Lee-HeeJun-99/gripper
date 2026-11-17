#include "SharedFilmSystem.h"
#include "../film_rail_tendon/ControlProfile.h"
#include "../film_coupled_contact/CoupledOwnerClass.h"
#include <sofa/helper/logging/Messaging.h>
namespace regrip_three_finger {
// Actual narrow REST/T=0 contact IVP. No claim of closing/lift/grasp.
class ThreeFilmPersistentODE:public CoupledSphereODE {
public:
 SOFA_CLASS(ThreeFilmPersistentODE,CoupledSphereODE);
 sofa::core::objectmodel::SingleLink<ThreeFilmPersistentODE,Film,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>root1{initLink("root1","Second actual independent displacement state")},root2{initLink("root2","Third actual independent displacement state")};
 sofa::core::objectmodel::SingleLink<ThreeFilmPersistentODE,sofa::core::objectmodel::BaseObject,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>field1{initLink("field1","Second actual FilmRailTendon")},field2{initLink("field2","Third actual FilmRailTendon")};
 std::ofstream accepted,rowJournal,policy;
 sofa::core::objectmodel::Data<std::string>ownerCostFilename{initData(&ownerCostFilename,std::string(),"ownerCostFilename","Opt-in passive inclusive owner costs;empty disables")};
 sofa::core::objectmodel::Data<std::string>publicMassFilename{initData(&publicMassFilename,std::string(),"publicMassFilename","Opt-in exact actual public nodal mass/inertia journal;empty disables")};
 sofa::core::objectmodel::Data<bool>reuseJournalRows{initData(&reuseJournalRows,false,"reuseJournalRows","Opt-in reuse of EXACT rows already computed at this journal state;never across states")};
 regrip_film::PassiveProfile ownerMeter;std::ofstream ownerCosts;
 bool ready=false;
 ThreeFilmPersistentODE(){radius.setValue(30.01);}
 virtual bool drivenPilot()const{return false;}
 virtual bool exactDistanceOrder()const{return false;}
 template<class T>static T read(sofa::core::objectmodel::BaseObject*f,const char*name){auto*d=dynamic_cast<sofa::core::objectmodel::Data<T>*>(f->findData(name));if(!d)throw std::runtime_error("actual three-film parameter missing");return d->getValue();}
 void init()override{
  try{
  sofa::core::behavior::OdeSolver::init();
  if(!ownerCostFilename.getValue().empty()){if(std::ifstream(ownerCostFilename.getValue()))throw std::runtime_error("owner cost journal exists");ownerCosts.open(ownerCostFilename.getValue());if(!ownerCosts)throw std::runtime_error("owner cost journal cannot open");ownerCosts<<"time,metric,count,inclusive_seconds\n"<<std::setprecision(17);ownerMeter.enabled=true;}
  if(!publicMassFilename.getValue().empty()&&std::ifstream(publicMassFilename.getValue()))throw std::runtime_error("public mass journal exists");
  if(!root||!root1||!root2||!field||!field1||!field2||!body||body->getSize()!=1||getContext()->getGravity().norm()!=0||maxSteps.getValue()==0||maxSteps.getValue()>(exactDistanceOrder()?64:32)||rayleighMass.getValue()!=2||radius.getValue()!=30.01)throw std::runtime_error("three-film explicit links/zero gravity/profiled32steps/R30.01 research IVP required");
  if(getContext()->getObjects<sofa::core::behavior::OdeSolver>(sofa::core::objectmodel::BaseContext::SearchDown).size()!=1||getContext()->getObjects<sofa::core::behavior::BaseMass>(sofa::core::objectmodel::BaseContext::SearchDown).size()!=4||!body->getContext()->getObjects<sofa::core::behavior::BaseProjectiveConstraintSet>(sofa::core::objectmodel::BaseContext::Local).empty())throw std::runtime_error("sole three-film ODE,four actual masses,FREE body required");
  for(auto*f:{field.get(),field1.get(),field2.get()}){
   if(f->getClassName()!="FilmRailTendon"||read<unsigned>(f,"nx")!=21||read<unsigned>(f,"guideIntervals")!=4||read<double>(f,"guideOffset")!=5||read<double>(f,"bondStiffness")!=.001||!read<bool>(f,"rootGuideSecondOrder")||read<double>(f,"maximumTension")!=(drivenPilot()?.0001:0))throw std::runtime_error("actual fixed three-film research parameters differ;NOT general closing owner");
   if(drivenPilot()&&(!read<bool>(f,"c2Control")||read<double>(f,"rampTime")!=.01||read<double>(f,"releaseBegin")!=.02||read<double>(f,"releaseEnd")!=.03||(!exactDistanceOrder()&&maxSteps.getValue()!=8)||(exactDistanceOrder()&&maxSteps.getValue()!=8&&maxSteps.getValue()!=16&&maxSteps.getValue()!=32&&maxSteps.getValue()!=64)))throw std::runtime_error("explicit independently profiled10ms C2 pilot grid required");
  }
  for(auto*f:getContext()->getObjects<sofa::core::behavior::BaseForceField>(sofa::core::objectmodel::BaseContext::SearchDown))if(f!=field.get()&&f!=field1.get()&&f!=field2.get()&&!dynamic_cast<sofa::core::behavior::BaseMass*>(f))throw std::runtime_error("unsupported three-film external force field");
  for(auto suffix:{".states.csv",".rows.csv",".policy.csv"})if(filename.getValue().empty()||std::ifstream(filename.getValue()+suffix))throw std::runtime_error("three-film journal exists/empty");
  accepted.open(filename.getValue()+".states.csv");rowJournal.open(filename.getValue()+".rows.csv");policy.open(filename.getValue()+".policy.csv");for(auto*f:{&accepted,&rowJournal,&policy})*f<<std::setprecision(17);
  accepted<<"time,minimum_gap,momentum_residual,normal_velocity_residual,iterations,evaluations,q,v\n";rowJournal<<"time,owner_finger,triangle,feature,gap,force,normal_velocity,nx,ny,nz,px,py,pz,jacobian,stage_q,stage_v\n";policy<<"component,films,rigid_bodies,maximum_steps,external_Fx,external_Fy,external_Fz,rayleigh_mass,radius\n"<<getClassName()<<",3,1,"<<maxSteps.getValue()<<','<<externalForce.getValue()[0]<<','<<externalForce.getValue()[1]<<','<<externalForce.getValue()[2]<<','<<rayleighMass.getValue()<<','<<radius.getValue()<<'\n';policy.flush();ready=true;d_componentState.setValue(sofa::core::objectmodel::ComponentState::Valid);
  }catch(const std::exception&e){d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);msg_error(this)<<"Three-film initialization rejected: "<<e.what();}
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  {regrip_film::PassiveProfile::Scope timer(ownerMeter,"coupled_step");solveStep(dt);}
  if(ownerCosts){for(const auto&entry:ownerMeter.metrics)ownerCosts<<getContext()->getTime()+dt<<','<<entry.first<<','<<entry.second.count<<','<<entry.second.seconds<<'\n';ownerCosts.flush();}
 }
 void solveStep(SReal dt){
  if(!ready){msg_error(this)<<"Invalid three-film component: no integration or accepted commit";return;}
  if(++count>maxSteps.getValue()||dt!=getContext()->getDt()||!(dt>0)||getContext()->getTime()<=last||getContext()->getTime()+dt>(drivenPilot()?.01:1e-4)+1e-14)throw std::runtime_error("three-film explicit profiled REST-initialized window only");last=getContext()->getTime();
  sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  auto system=[&]{regrip_film::PassiveProfile::Scope timer(ownerMeter,"shared_model_construction");return SharedFilmSystem(Layout(),Eigen::Vector3d(externalForce.getValue()[0],externalForce.getValue()[1],externalForce.getValue()[2]),true,true,ownerMeter.enabled?&ownerMeter:nullptr);}();system.exactUnresolved=exactDistanceOrder();const unsigned nf=system.shared.nf,nb=3*nf;Eigen::VectorXd q=system.initial,v=Eigen::VectorXd::Zero(q.size());
  std::array<Film*,3>roots={root.get(),root1.get(),root2.get()},locals;std::array<sofa::core::objectmodel::BaseObject*,3>fields={field.get(),field1.get(),field2.get()};
  system.shared.M.setZero();
  for(unsigned f=0;f<3;++f){auto&s=system.shared.films[f];locals[f]=dynamic_cast<Film*>(fields[f]->getContext()->getMechanicalState());auto*mass=fields[f]->getContext()->getMass();if(!locals[f]||!mass)throw std::runtime_error("actual three-film local state/mass missing");const auto&x=locals[f]->read(sofa::core::vec_id::read_access::position)->getValue();const auto&velocity=locals[f]->read(sofa::core::vec_id::read_access::velocity)->getValue();if(x.size()!=s.film.model.size())throw std::runtime_error("three-film size mismatch");std::vector<Point>xx(x.size()),vv(x.size());
   for(unsigned i=0;i<x.size();++i){double actualMass=mass->getElementMass(i);if(!(actualMass>0)||std::abs(actualMass-s.film.mass[i])>1e-13*s.film.mass[i])throw std::runtime_error("actual three-film mass differs from qualified reference");for(unsigned d=0;d<3;++d){xx[i][d]=x[i][d];vv[i][d]=velocity[i][d];unsigned a=3*i+d;if(s.film.index[a]>=0)system.shared.M(f*nf+s.film.index[a],f*nf+s.film.index[a])+=actualMass*s.film.weight[a]*s.film.weight[a];}}
   q.segment(f*nf,nf)=s.film.pack(xx);v.segment(f*nf,nf)=s.film.pack(vv);if(count==1&&(xx!=s.before.q||s.film.pack(vv).norm()!=0))throw std::runtime_error("actual three-film coupon must START at REST,not an unqualified trajectory");
  }
  auto bx=body->read(sofa::core::vec_id::read_access::position)->getValue();auto bv=body->read(sofa::core::vec_id::read_access::velocity)->getValue();sofa::linearalgebra::FullMatrix<double>Mb(6,6);Mb.clear();body->getContext()->getMass()->getElementMass(0,&Mb);
  for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j){double expected=i==j?(i<3?.0001:.036):0;if(std::abs(Mb.element(i,j)-expected)>1e-14*std::max(1e-20,std::abs(expected)))throw std::runtime_error("actual FREE sphere mass/isotropic inertia differs");system.shared.M(nb+i,nb+j)=Mb.element(i,j);}
  if(count==1&&!publicMassFilename.getValue().empty()){
   std::ofstream out(publicMassFilename.getValue());if(!out)throw std::runtime_error("cannot open public mass journal");out<<std::setprecision(17)<<system.shared.films[0].film.model.size()<<'\n';
   for(unsigned f=0;f<3;++f){auto*mass=fields[f]->getContext()->getMass();for(unsigned i=0;i<system.shared.films[f].film.model.size();++i)out<<mass->getElementMass(i)<<' ';out<<'\n';}out<<Mb.element(0,0)<<' '<<Mb.element(3,3)<<'\n';
  }
  for(unsigned d=0;d<3;++d){q(nb+d)=bx[0].getCenter()[d];v(nb+d)=bv[0].getVCenter()[d];v(nb+3+d)=bv[0].getVOrientation()[d];}if(count==1&&((q.segment<3>(nb)-system.layout.bodyCenter).norm()>1e-12||v.norm()!=0))throw std::runtime_error("actual three-film initial IVP differs");
  auto applied=[&](double t){return drivenPilot()?regrip_film_rail::ControlProfile::evaluate(t,read<double>(field.get(),"maximumTension"),read<double>(field.get(),"rampTime"),read<double>(field.get(),"releaseBegin"),read<double>(field.get(),"releaseEnd"),read<bool>(field.get(),"c2Control")).tension:0.;};
  auto result=[&]{regrip_film::PassiveProfile::Scope timer(ownerMeter,"implicit_stage_solve");return regrip_collocation::persistentRows(system.shared.M,rayleighMass.getValue(),q,v,last,dt,[&](const auto&x,double t){return system.force(x,applied(t));},[&](const auto&x){return system.geometry(x);});}();double gap=system.clearance(result.q);if(drivenPilot())for(const auto&s:result.stages)gap=std::min(gap,system.clearance(s.q));if(gap< -1e-10||!result.q.allFinite()||!result.v.allFinite())throw std::runtime_error("three-film accepted whole clearance/finite gate");
  for(unsigned f=0;f<3;++f){const auto&s=system.shared.films[f];auto xx=s.film.expand(result.q.segment(f*nf,nf)),vv=s.film.expand(result.v.segment(f*nf,nf));auto x=roots[f]->read(sofa::core::vec_id::read_access::position)->getValue();auto velocity=roots[f]->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned a=0;a<s.film.index.size();++a)if(s.film.index[a]>=0&&s.film.weight[a]==1){x[a/3][a%3]=xx[a/3][a%3];velocity[a/3][a%3]=vv[a/3][a%3];}roots[f]->write(sofa::core::vec_id::write_access::position)->setValue(x);roots[f]->write(sofa::core::vec_id::write_access::velocity)->setValue(velocity);}
  for(unsigned d=0;d<3;++d){bx[0].getCenter()[d]=result.q(nb+d);bv[0].getVCenter()[d]=result.v(nb+d);bv[0].getVOrientation()[d]=result.v(nb+3+d);}Eigen::Vector3d angle=result.q.tail<3>();Eigen::Quaterniond orientation(bx[0].getOrientation()[3],bx[0].getOrientation()[0],bx[0].getOrientation()[1],bx[0].getOrientation()[2]);if(angle.norm()>0)orientation=Eigen::Quaterniond(Eigen::AngleAxisd(angle.norm(),angle/angle.norm()))*orientation;for(unsigned d=0;d<4;++d)bx[0].getOrientation()[d]=orientation.coeffs()(d);body->write(sofa::core::vec_id::write_access::position)->setValue(bx);body->write(sofa::core::vec_id::write_access::velocity)->setValue(bv);mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  for(unsigned f=0;f<3;++f){auto expected=system.local(result.q,f).q;auto velocity=system.shared.films[f].film.expand(result.v.segment(f*nf,nf));const auto&actual=locals[f]->read(sofa::core::vec_id::read_access::position)->getValue();const auto&av=locals[f]->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned i=0;i<expected.size();++i)for(unsigned d=0;d<3;++d)if(actual[i][d]!=expected[i][d]||av[i][d]!=velocity[i][d])throw std::runtime_error("actual three-film mapped commit differs");}
  const auto&actualBody=body->read(sofa::core::vec_id::read_access::position)->getValue()[0];const auto&actualVelocity=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];for(unsigned d=0;d<3;++d)if(actualBody.getCenter()[d]!=result.q(nb+d)||actualVelocity.getVCenter()[d]!=result.v(nb+d)||actualVelocity.getVOrientation()[d]!=result.v(nb+3+d))throw std::runtime_error("actual FREE body commit differs");for(unsigned d=0;d<4;++d)if(actualBody.getOrientation()[d]!=orientation.coeffs()(d))throw std::runtime_error("actual FREE body orientation commit differs");
  for(unsigned k=0;k<3;++k){const auto&position=k?result.stages[k-1].q:q;const auto&velocity=k?result.stages[k-1].v:v;std::array<Row,3>snapshot;auto geo=system.geometry(position,reuseJournalRows.getValue()?&snapshot:nullptr);for(unsigned f=0;f<3;++f){auto row=reuseJournalRows.getValue()?std::move(snapshot[f]):system.selected(position,f);Eigen::Vector3d normal=system.layout.mount[f].R*row.normal;Eigen::Vector3d point=system.layout.mount[f].origin+system.layout.mount[f].R*row.contact;rowJournal<<last+dt*(k==0?0:k==1?.5:1)<<','<<f<<','<<row.triangle<<','<<row.feature<<','<<row.gap<<','<<(k?result.stages[k-1].force(f):result.initialForce(f))<<','<<geo.J.row(f).dot(velocity);for(double x:normal)rowJournal<<','<<x;for(double x:point)rowJournal<<','<<x;quote(rowJournal,geo.J.row(f));quote(rowJournal,position);quote(rowJournal,velocity);rowJournal<<'\n';}}
  accepted<<last+dt<<','<<gap<<','<<result.momentumResidual<<','<<result.velocityResidual<<','<<result.iterations<<','<<result.evaluations;quote(accepted,result.q);quote(accepted,result.v);accepted<<'\n';accepted.flush();rowJournal.flush();
 }
};
// Separate explicit scope. The original T0 owner retains all of its guards.
class ThreeFilmDrivenODE:public ThreeFilmPersistentODE {
public:
 SOFA_CLASS(ThreeFilmDrivenODE,ThreeFilmPersistentODE);
 bool drivenPilot()const override{return true;}
};
class ThreeFilmDrivenExactODE final:public ThreeFilmDrivenODE {
public:
 SOFA_CLASS(ThreeFilmDrivenExactODE,ThreeFilmDrivenODE);
 bool exactDistanceOrder()const override{return true;}
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripThreeFilmContact";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){
 f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL actual3film/oneFREEsphere REST T0 persistent contact;NOT grasp").add<regrip_three_finger::ThreeFilmPersistentODE>());
 f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL shared C2 three-film10ms pilot;NOT grasp").add<regrip_three_finger::ThreeFilmDrivenODE>());
 f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL shared C2 exact-rational unresolved distance order;NOT grasp").add<regrip_three_finger::ThreeFilmDrivenExactODE>());
}
}
