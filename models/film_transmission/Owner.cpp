#include "Kernel.h"
#include "Gauss.h"
#include <sofa/core/behavior/OdeSolver.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/behavior/BaseForceField.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/MechanicalOperations.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/core/objectmodel/BaseNode.h>
#include <set>
#include <fstream>
#include <iomanip>
namespace regrip_transmission {
class FilmTransmissionODE:public sofa::core::behavior::OdeSolver {
public:
 SOFA_CLASS(FilmTransmissionODE,sofa::core::behavior::OdeSolver);
 using Film=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<FilmTransmissionODE,Film,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>root{initLink("root","Actual independent displacement state")};
 sofa::core::objectmodel::SingleLink<FilmTransmissionODE,sofa::core::objectmodel::BaseObject,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>field{initLink("field","Actual FilmRailTendon")};
 sofa::core::objectmodel::Data<std::string>filename{initData(&filename,std::string(),"filename","Exclusive actual-state journal")};
 sofa::core::objectmodel::Data<std::string>massFilename{initData(&massFilename,std::string(),"massFilename","Hash-verified original1002 public nodal mass snapshot")};
 sofa::core::objectmodel::Data<unsigned>maxSteps{initData(&maxSteps,8u,"maxSteps","Profiled finite coupon budget <=2000")};
 unsigned count=0;double last=-1;std::ofstream journal,stageJournal;
 virtual double interval(double,double dt)const{return dt;}
 virtual Step advance(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass)const{return step(m,q,v,time,h,mass);}
 template<class T>T parameter(const char*key)const{auto*d=dynamic_cast<sofa::core::objectmodel::Data<T>*>(field->findData(key));if(!d)throw std::runtime_error("actual transmission parameter missing");return d->getValue();}
 void init()override{
  OdeSolver::init();if(!root||!field||field->getClassName()!="FilmRailTendon"||getContext()->getGravity().norm()!=0||maxSteps.getValue()==0||maxSteps.getValue()>2000||getContext()->getTime()!=0)throw std::runtime_error("separate single-film rest/zero-gravity coupon required");
  if(getContext()->getObjects<sofa::core::behavior::OdeSolver>(sofa::core::objectmodel::BaseContext::SearchDown).size()!=1||getContext()->getObjects<sofa::core::behavior::BaseMass>(sofa::core::objectmodel::BaseContext::SearchDown).size()!=1)throw std::runtime_error("single actual projected-mass/ODE coupon only");
  for(auto*f:getContext()->getObjects<sofa::core::behavior::BaseForceField>(sofa::core::objectmodel::BaseContext::SearchDown))if(f!=field.get()&&!dynamic_cast<sofa::core::behavior::BaseMass*>(f))throw std::runtime_error("extra physical forces not supported");
  if(parameter<unsigned>("nx")!=21||parameter<unsigned>("guideIntervals")!=4||!parameter<bool>("rootGuideSecondOrder")||!parameter<bool>("c2Control")||parameter<double>("maximumTension")!=.0001||parameter<double>("rampTime")!=.01||parameter<double>("releaseBegin")!=.02||parameter<double>("releaseEnd")!=.03)throw std::runtime_error("qualified transmission control/root/model mismatch");
  model(parameter<double>("bondStiffness"),parameter<double>("guideOffset"));if(filename.getValue().empty()||std::ifstream(filename.getValue())||std::ifstream(filename.getValue()+".stages.csv"))throw std::runtime_error("transmission journal exists/empty");journal.open(filename.getValue());journal<<std::setprecision(17)<<"time,dt,momentum_residual,evaluations,T_mid,T_end,q,v\n";stageJournal.open(filename.getValue()+".stages.csv");stageJournal<<std::setprecision(17)<<"macro,stage,time,weight,T,q,v\n";
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  double time=getContext()->getTime();if(++count>maxSteps.getValue()||time<=last||dt!=getContext()->getDt())throw std::runtime_error("once-per-step transmission clock/budget");last=time;double h=interval(time,dt);
  sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  auto*local=dynamic_cast<Film*>(field->getContext()->getMechanicalState());auto*mass=field->getContext()->getMass();if(!local||!mass)throw std::runtime_error("actual transmission local state/mass missing");auto m=model(parameter<double>("bondStiffness"),parameter<double>("guideOffset"));auto mm=publicMass(massFilename.getValue());const auto&x=local->read(sofa::core::vec_id::read_access::position)->getValue();const auto&vel=local->read(sofa::core::vec_id::read_access::velocity)->getValue();std::vector<Point>q(x.size()),v(x.size());
  if(x.size()!=m.size())throw std::runtime_error("actual transmission size");for(unsigned i=0;i<x.size();++i){if(mass->getElementMass(i)!=mm[i])throw std::runtime_error("exact public transmission mass differs");for(unsigned d=0;d<3;++d){q[i][d]=x[i][d];v[i][d]=vel[i][d];if(count==1&&(q[i][d]!=0||v[i][d]!=0))throw std::runtime_error("single coupon must start at rest");}}
  auto map=mechanics(m,q,v,h,0,mm);if(map.expand(map.pack(q))!=q||map.expand(map.pack(v))!=v)throw std::runtime_error("actual root map differs");auto after=advance(m,q,v,time,h,mm);
  auto rx=root->read(sofa::core::vec_id::read_access::position)->getValue(),rv=root->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned a=0;a<map.index.size();++a)if(map.index[a]>=0&&map.weight[a]==1){rx[a/3][a%3]=after.q[a/3][a%3];rv[a/3][a%3]=after.v[a/3][a%3];}root->write(sofa::core::vec_id::write_access::position)->setValue(rx);root->write(sofa::core::vec_id::write_access::velocity)->setValue(rv);mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  const auto&actual=local->read(sofa::core::vec_id::read_access::position)->getValue();const auto&av=local->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d)if(actual[i][d]!=after.q[i][d]||av[i][d]!=after.v[i][d])throw std::runtime_error("exact actual transmission commit/map failed");
  journal<<time+dt<<','<<h<<','<<after.residual<<','<<after.evaluations<<','<<control().sample(time+h/2).tension<<','<<control().sample(time+dt).tension;quote(journal,after.q);quote(journal,after.v);journal<<'\n';journal.flush();
  if(after.highOrder)for(unsigned i=0;i<2;++i){stageJournal<<count<<','<<i<<','<<after.stageTime[i]<<','<<h/2<<','<<after.stageT[i];quote(stageJournal,after.stageQ[i]);quote(stageJournal,after.stageV[i]);stageJournal<<'\n';}stageJournal.flush();
 }
};
class FilmTransmissionAlignedODE:public FilmTransmissionODE {
public:
 SOFA_CLASS(FilmTransmissionAlignedODE,FilmTransmissionODE);
 sofa::core::objectmodel::Data<double>endTime{initData(&endTime,.0008,"endTime","Exact common coupon observation endpoint;NO state/time overwrite")};
 double nominal=0;
 FilmTransmissionAlignedODE(){f_listening.setValue(true);}
 double interval(double time,double dt)const override{return (time+dt)-time;}
 void init()override{FilmTransmissionODE::init();nominal=getContext()->getDt();if(!(endTime.getValue()>0&&endTime.getValue()<=.05)||nominal!=endTime.getValue()/maxSteps.getValue())throw std::runtime_error("explicit common-target numerical plan required");}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;double time=getContext()->getTime(),used=getContext()->getDt();if(count==0||time!=last+used)throw std::runtime_error("aligned transmission actual clock differs");
  double next=count+1==maxSteps.getValue()?endTime.getValue()-time:used;if(!(next>0&&next<=2*nominal)||(count==maxSteps.getValue()&&time!=endTime.getValue()))throw std::runtime_error("common-target final interval invalid");
  auto*root=dynamic_cast<sofa::core::objectmodel::BaseNode*>(getContext());std::set<sofa::core::objectmodel::BaseNode*>seen;std::function<void(sofa::core::objectmodel::BaseNode*)>apply=[&](auto*n){if(!seen.insert(n).second)return;if(n->getContext()->getTime()!=time)throw std::runtime_error("child clock mismatch;not overwritten");n->getContext()->setDt(next);for(auto*c:n->getChildren())apply(c);};if(!root)throw std::runtime_error("aligned node missing");apply(root);if(seen.size()!=4)throw std::runtime_error("single-film context topology differs");
 }
};
class FilmTransmissionGaussODE:public FilmTransmissionAlignedODE {
public:
 SOFA_CLASS(FilmTransmissionGaussODE,FilmTransmissionAlignedODE);
 Step advance(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass)const override{return stepGauss(m,q,v,time,h,mass);}
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripFilmTransmission";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Independent actual single FilmRailTendon nonlinear transmission;NO object/contact/grasp;reuse validated free midpoint").add<regrip_transmission::FilmTransmissionODE>());f->registerObjects(sofa::core::ObjectRegistrationData("Separate exact-endpoint coupon with public next-dt schedule;no time/q/v projection").add<regrip_transmission::FilmTransmissionAlignedODE>());f->registerObjects(sofa::core::ObjectRegistrationData("Separate Gauss-Legendre order4 single-film transmission;not contact/full time/grasp qualified").add<regrip_transmission::FilmTransmissionGaussODE>());}
}
