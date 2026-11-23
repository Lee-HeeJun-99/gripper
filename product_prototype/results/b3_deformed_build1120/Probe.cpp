#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/linearalgebra/FullMatrix.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <cmath>

// Diagnostic only: private force buffers, no actual state/force/ODE writes.
// Native force caches are touched: trajectory purity MUST be checked externally.
class ReGripDeformedProbe:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(ReGripDeformedProbe,sofa::core::objectmodel::BaseObject);
 using Types=sofa::defaulttype::Vec3Types;
 using State=sofa::core::behavior::MechanicalState<Types>;
 using Field=sofa::core::behavior::ForceField<Types>;
 using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<ReGripDeformedProbe,State,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK> body;
 sofa::core::objectmodel::SingleLink<ReGripDeformedProbe,Field,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK> elastic;
 sofa::core::objectmodel::Data<std::string> filename;
 sofa::core::objectmodel::Data<double> sampleTime;
 bool done=false;
 ReGripDeformedProbe():body(initLink("body","Observed actual state")),elastic(initLink("elastic","Existing Native FEM")),filename(initData(&filename,std::string(),"filename","Exclusive diagnostic prefix")),sampleTime(initData(&sampleTime,0.1,"sampleTime","Accepted output time")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||!elastic||std::ifstream(filename.getValue()+".fd.csv"))throw std::runtime_error("unique explicit diagnostic required");}
 void handleEvent(sofa::core::objectmodel::Event*ev)override{
  if(done||!dynamic_cast<sofa::simulation::AnimateEndEvent*>(ev)||getContext()->getTime()+1e-14<sampleTime.getValue())return;
  done=true;
  const auto q=body->read(sofa::core::vec_id::read_access::position)->getValue();
  const auto v=body->read(sofa::core::vec_id::read_access::velocity)->getValue();
  Types::VecDeriv direction(q.size());double sum=0;
  for(unsigned i=0;i<q.size()*3;++i){double x=std::sin(double(i+1));direction[i/3][i%3]=x;sum+=x*x;}
  for(auto&d:direction)d/=std::sqrt(sum);
  sofa::core::MechanicalParams params;
  auto evaluate=[&](double h){Field::DataVecCoord x;Field::DataVecDeriv velocity,force;auto displaced=q;
   for(unsigned i=0;i<q.size();++i)displaced[i]+=direction[i]*h;
   x.setValue(displaced);velocity.setValue(v);force.setValue(Types::VecDeriv(q.size()));
   elastic->addForce(&params,force,x,velocity);return force.getValue();};
  const auto f=evaluate(0);
  unsigned offset=0,n=q.size()*3;sofa::linearalgebra::FullMatrix<double>K(n,n);K.clear();elastic->addKToMatrix(&K,-1.,offset);
  std::ofstream matrix(filename.getValue()+".matrix.csv");matrix<<std::setprecision(17)<<"i,j,K_N_per_m\n";
  for(unsigned i=0;i<n;++i)for(unsigned j=0;j<n;++j)if(K.element(i,j)!=0)matrix<<i<<','<<j<<','<<K.element(i,j)<<'\n';
  std::ofstream fd(filename.getValue()+".fd.csv");fd<<std::setprecision(17)<<"time_s,epsilon_m,error_N_per_m,fd_norm_N_per_m\n";
  for(double h:{1e-7,1e-8,1e-9}){auto plus=evaluate(h),minus=evaluate(-h);double error=0,norm=0;
   for(unsigned i=0;i<n;++i){double expected=0;for(unsigned j=0;j<n;++j)expected-=K.element(i,j)*direction[j/3][j%3];double d=(plus[i/3][i%3]-minus[i/3][i%3])/(2*h);error+=(d-expected)*(d-expected);norm+=d*d;}
   fd<<getContext()->getTime()<<','<<h<<','<<std::sqrt(error)<<','<<std::sqrt(norm)<<'\n';}
  const auto restored=evaluate(0);double forceError=0;for(unsigned i=0;i<f.size();++i)forceError+=(restored[i]-f[i]).norm2();
  std::ofstream state(filename.getValue()+".state.csv");state<<std::setprecision(17)<<"time_s,force_cache_repeat_error_N,q,v\n"<<getContext()->getTime()<<','<<std::sqrt(forceError)<<",\""<<q<<"\",\""<<v<<"\"\n";
  if(q!=body->read(sofa::core::vec_id::read_access::position)->getValue()||v!=body->read(sofa::core::vec_id::read_access::velocity)->getValue())throw std::runtime_error("probe changed actual state");
 }
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripDeformedProbe";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only diagnostic,not physical solver").add<ReGripDeformedProbe>());}
}
