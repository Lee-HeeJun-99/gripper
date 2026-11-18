// Separate persistent-contact owner. No old count spoofing,force or state projection.
#define REGRIP_THREE_FILM_EMBEDDED
#include "../film_three_finger/ThreeFilmOwner.cpp"
#include <sofa/core/objectmodel/BaseNode.h>
#include <sofa/core/objectmodel/Context.h>
#include <set>
namespace regrip_three_resume {
using namespace regrip_three_finger;
class ThreeFilmResumeODE:public ThreeFilmDrivenODE {
public:
 SOFA_CLASS(ThreeFilmResumeODE,ThreeFilmDrivenODE);
 sofa::core::objectmodel::Data<std::string>checkpoint{initData(&checkpoint,std::string(),"checkpoint","Immutable complete persistent-state input")};
 sofa::core::objectmodel::Data<std::string>identity{initData(&identity,std::string(),"identity","Runner-verified SHA256 provenance token")};
 sofa::core::objectmodel::Data<double>endTime{initData(&endTime,.01,"endTime","Explicit forecast-bounded physical endpoint <=30ms")};
 bool restored=false;unsigned priorSteps=0;double initialTime=0,savedDt=0;
 bool exactDistanceOrder()const override{return true;}
 bool requiresRestStart()const override{return false;}
 double physicalEndLimit()const override{return endTime.getValue();}
 virtual std::string inputCheckpointMagic()const{return "REGRIP_PERSISTENT_V1";}
 virtual std::string outputCheckpointMagic()const{return "REGRIP_PERSISTENT_V1";}
 virtual void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&v){
  for(unsigned f=0;f<3;++f){unsigned tri,feature;in>>tri>>feature;auto row=s.selected(q,f);if(!in||tri!=row.triangle||feature!=row.feature)throw std::runtime_error("resume accepted contact owner differs");}
  if(s.clearance(q)<-1e-10||(s.geometry(q).J*v).cwiseAbs().maxCoeff()>1e-10)throw std::runtime_error("resume persistent gap/velocity condition failed");
 }
 virtual void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&s,const Eigen::VectorXd&q,double){for(unsigned f=0;f<3;++f){auto row=s.selected(q,f);out<<row.triangle<<' '<<row.feature<<'\n';}}
 void clocks(double time,double dt){
  auto*node=dynamic_cast<sofa::core::objectmodel::BaseNode*>(getContext());if(!node)throw std::runtime_error("resume requires scene node");
std::set<sofa::core::objectmodel::BaseNode*>seen;std::function<void(sofa::core::objectmodel::BaseNode*)>visit=[&](auto*n){if(!seen.insert(n).second)return;auto*c=dynamic_cast<sofa::core::objectmodel::Context*>(n->getContext());if(!c)throw std::runtime_error("resume requires public mutable Context");c->setTime(time);n->getContext()->setDt(dt);if(n->getContext()->getTime()!=time||n->getContext()->getDt()!=dt)throw std::runtime_error("resume context clock rejected");for(auto*c:n->getChildren())visit(c);};visit(node);
  if(seen.size()!=11)throw std::runtime_error("resume scene topology changed");
 }
 void bwdInit()override{
  ThreeFilmDrivenODE::bwdInit();if(!ready)throw std::runtime_error("resume parent validation failed");
  std::ifstream in(checkpoint.getValue());std::string magic,token;in>>magic>>initialTime>>savedDt>>priorSteps>>token;
if(!in||magic!=inputCheckpointMagic()||identity.getValue().size()!=64||token!=identity.getValue()||(savedDt!=.0002&&savedDt!=.0001&&savedDt!=.00005)||!(initialTime>0)||endTime.getValue()> .03||endTime.getValue()<=initialTime)throw std::runtime_error("resume header/provenance/time rejected");
  SharedFilmSystem system(Layout(),{0,0,-.001},true,true);system.exactUnresolved=true;unsigned nf=system.shared.nf,n=system.initial.size();
  Eigen::VectorXd q(n),v(n);for(auto*z:{&q,&v})for(int i=0;i<z->size();++i)in>>(*z)(i);Eigen::Vector4d quaternion;for(double&x:quaternion)in>>x;
  if(!q.allFinite()||!v.allFinite()||!quaternion.allFinite()||std::abs(quaternion.squaredNorm()-1)>1e-14||q.tail<3>().norm()!=0)throw std::runtime_error("resume finite/quaternion/local-chart validation");
  std::array<Film*,3>roots={root.get(),root1.get(),root2.get()};std::array<sofa::core::objectmodel::BaseObject*,3>fields={field.get(),field1.get(),field2.get()};
  for(unsigned f=0;f<3;++f){auto*mass=fields[f]->getContext()->getMass();for(unsigned i=0;i<system.shared.films[f].film.model.size();++i){double m;in>>m;if(!in||m!=mass->getElementMass(i))throw std::runtime_error("resume exact public nodal mass differs");}}
  sofa::linearalgebra::FullMatrix<double>mb(6,6);mb.clear();body->getContext()->getMass()->getElementMass(0,&mb);for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j){double m;in>>m;if(!in||m!=mb.element(i,j))throw std::runtime_error("resume public rigid mass/inertia differs");}
  for(unsigned f=0;f<3;++f){const auto&s=system.shared.films[f].film;for(unsigned a=0;a<s.index.size();++a){int index;double weight;in>>index>>weight;if(!in||index!=s.index[a]||weight!=s.weight[a])throw std::runtime_error("resume root mapping differs");}}
  readContactCheckpoint(in,system,q,v);
  std::string extra;if(in>>extra)throw std::runtime_error("resume trailing data");
  // Contact type was validated before physical writes by the explicit owner hook.
  for(unsigned f=0;f<3;++f){const auto&s=system.shared.films[f].film;auto x=roots[f]->read(sofa::core::vec_id::read_access::position)->getValue(),vel=roots[f]->read(sofa::core::vec_id::read_access::velocity)->getValue();for(auto&p:x)for(unsigned d=0;d<3;++d)p[d]=0;for(auto&p:vel)for(unsigned d=0;d<3;++d)p[d]=0;for(unsigned a=0;a<s.index.size();++a)if(s.index[a]>=0&&s.weight[a]==1){x[a/3][a%3]=q(f*nf+s.index[a]);vel[a/3][a%3]=v(f*nf+s.index[a]);}roots[f]->write(sofa::core::vec_id::write_access::position)->setValue(x);roots[f]->write(sofa::core::vec_id::write_access::velocity)->setValue(vel);}
  auto bx=body->read(sofa::core::vec_id::read_access::position)->getValue();auto bv=body->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned d=0;d<3;++d){bx[0].getCenter()[d]=q(3*nf+d);bv[0].getVCenter()[d]=v(3*nf+d);bv[0].getVOrientation()[d]=v(3*nf+3+d);}for(unsigned d=0;d<4;++d)bx[0].getOrientation()[d]=quaternion(d);body->write(sofa::core::vec_id::write_access::position)->setValue(bx);body->write(sofa::core::vec_id::write_access::velocity)->setValue(bv);
  clocks(initialTime,savedDt);sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  // Validate mapped children immediately,not only after the first solve.
  for(unsigned f=0;f<3;++f){auto*local=dynamic_cast<Film*>(fields[f]->getContext()->getMechanicalState());const auto&x=local->read(sofa::core::vec_id::read_access::position)->getValue();const auto&vel=local->read(sofa::core::vec_id::read_access::velocity)->getValue();auto expected=system.local(q,f).q,ev=system.shared.films[f].film.expand(v.segment(f*nf,nf));for(unsigned i=0;i<x.size();++i)for(unsigned d=0;d<3;++d)if(x[i][d]!=expected[i][d]||vel[i][d]!=ev[i][d])throw std::runtime_error("resume mapped state not exact");}
  restored=true;
 }
 void save(double time){
  SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;unsigned nf=s.shared.nf;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());std::array<sofa::core::objectmodel::BaseObject*,3>fields={field.get(),field1.get(),field2.get()};
  for(unsigned f=0;f<3;++f){auto*local=dynamic_cast<Film*>(fields[f]->getContext()->getMechanicalState());const auto&x=local->read(sofa::core::vec_id::read_access::position)->getValue();const auto&vel=local->read(sofa::core::vec_id::read_access::velocity)->getValue();std::vector<Point>xx(x.size()),vv(x.size());for(unsigned i=0;i<x.size();++i)for(unsigned d=0;d<3;++d){xx[i][d]=x[i][d];vv[i][d]=vel[i][d];}q.segment(f*nf,nf)=s.shared.films[f].film.pack(xx);v.segment(f*nf,nf)=s.shared.films[f].film.pack(vv);}
  const auto&bx=body->read(sofa::core::vec_id::read_access::position)->getValue()[0];const auto&bv=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];for(unsigned d=0;d<3;++d){q(3*nf+d)=bx.getCenter()[d];v(3*nf+d)=bv.getVCenter()[d];v(3*nf+3+d)=bv.getVOrientation()[d];}
  std::string path=filename.getValue()+".checkpoint_"+std::to_string(priorSteps+count)+".txt";if(std::ifstream(path))throw std::runtime_error("checkpoint already exists");std::ofstream out(path);out<<std::setprecision(17)<<outputCheckpointMagic()<<' '<<time<<' '<<savedDt<<' '<<priorSteps+count<<'\n'<<identity.getValue()<<'\n';for(const auto*z:{&q,&v})out<<z->transpose()<<'\n';for(unsigned d=0;d<4;++d)out<<bx.getOrientation()[d]<<' ';out<<'\n';
  for(unsigned f=0;f<3;++f){auto*m=fields[f]->getContext()->getMass();for(unsigned i=0;i<s.shared.films[f].film.model.size();++i)out<<m->getElementMass(i)<<' ';out<<'\n';}sofa::linearalgebra::FullMatrix<double>mb(6,6);mb.clear();body->getContext()->getMass()->getElementMass(0,&mb);for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)out<<mb.element(i,j)<<' ';out<<'\n';for(unsigned f=0;f<3;++f){const auto&m=s.shared.films[f].film;for(unsigned a=0;a<m.index.size();++a)out<<m.index[a]<<' '<<m.weight[a]<<' ';out<<'\n';}writeContactCheckpoint(out,s,q,time);if(!out)throw std::runtime_error("checkpoint write failed");
 }
 void solve(const sofa::core::ExecParams*p,SReal dt,sofa::core::MultiVecCoordId x,sofa::core::MultiVecDerivId v)override{
  if(!restored||dt!=savedDt||(count==0&&getContext()->getTime()!=initialTime))throw std::runtime_error("resume initialization/clock not validated");
  ThreeFilmPersistentODE::solve(p,dt,x,v);save(last+dt);
 }
};
}
#ifndef REGRIP_THREE_RESUME_EMBEDDED
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripThreeFilmResume";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL exact persistent checkpoint transfer;legacy sampled-work origin NOT restored;NOT grasp").add<regrip_three_resume::ThreeFilmResumeODE>());}
}
#endif
