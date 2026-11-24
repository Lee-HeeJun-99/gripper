#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <array>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <cmath>
#include <algorithm>
namespace regrip {
using sofa::core::objectmodel::BaseObject;using sofa::core::objectmodel::BaseLink;
class NativeCableLatch:public BaseObject {
public:
 SOFA_CLASS(NativeCableLatch,BaseObject);
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 sofa::core::objectmodel::SingleLink<NativeCableLatch,BaseObject,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> cable0,cable1;
 sofa::core::objectmodel::Data<double> start;
 sofa::core::objectmodel::Data<double> final0,final1,end;
 sofa::core::objectmodel::Data<std::string> filename;
 std::array<double,2> rest{},target{},applied{};bool active=false,verified=false;std::ofstream log;
 NativeCableLatch():cable0(initLink("cable0","Native cable public input")),cable1(initLink("cable1","Native cable public input")),start(initData(&start,.6,"start","First end-time at which previous accepted geometric length is held")),final0(initData(&final0,-1.,"final0","Optional independently defined final shortening m;negative keeps latched length")),final1(initData(&final1,-1.,"final1","Optional independently defined final shortening m;negative keeps latched length")),end(initData(&end,1.,"end","End of optional C2 input shortening ramp")),filename(initData(&filename,std::string(),"filename","Exclusive actual input journal")){f_listening.setValue(true);}
 double number(BaseObject*b,const char*name){auto*d=dynamic_cast<sofa::core::objectmodel::Data<double>*>(b->findData(name));if(!d)throw std::runtime_error("Expected native scalar data");return d->getValue();}
 double length(BaseObject*b){
  auto*s=dynamic_cast<State*>(b->getContext()->getMechanicalState());auto*p=dynamic_cast<sofa::core::objectmodel::Data<sofa::type::Vec3d>*>(b->findData("pullPoint"));if(!s||!p)throw std::runtime_error("Explicit mapped Vec3 native cable path required");
  const auto&q=s->read(sofa::core::vec_id::read_access::position)->getValue();std::istringstream ids(b->findData("indices")->getValueString());unsigned i,count=0;auto previous=p->getValue();double sum=0.;while(ids>>i){if(i>=q.size())throw std::runtime_error("Cable index out of range");sum+=(q[i]-previous).norm();previous=q[i];++count;}if(count!=q.size())throw std::runtime_error("Coupon requires all mapped cable points explicitly indexed");return sum;
 }
 void init()override{BaseObject::init();if(!cable0||!cable1||std::ifstream(filename.getValue()))throw std::runtime_error("Unique linked input latch required");unsigned i=0;for(auto*b:{cable0.get(),cable1.get()})rest[i++]=length(b);log.open(filename.getValue());log<<std::setprecision(17)<<"time_s,latched,target0_m,target1_m,geometric0_m,geometric1_m,force0_Ns,force1_Ns\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(e)){
   // Cross-sibling mapped paths may not be initialized at this object's
   // bwdInit. Verify AFTER graph initialization, before any dynamics.
   if(!verified){unsigned i=0;for(auto*b:{cable0.get(),cable1.get()}){rest[i]=length(b);double native=number(b,"cableInitialLength");if(std::abs(native-rest[i])>1e-12){std::ostringstream error;error<<std::setprecision(17)<<"Initialized cable length mismatch native="<<native<<" geometric="<<rest[i];throw std::runtime_error(error.str());}++i;}verified=true;}
   const double end=getContext()->getTime()+getContext()->getDt();
   if(end>=start.getValue()&&!active){unsigned i=0;for(auto*b:{cable0.get(),cable1.get()}){target[i]=rest[i]-length(b);if(target[i]<0)throw std::runtime_error("Cannot latch a longer-than-reference path in this experiment");++i;}active=true;}
   if(active){unsigned i=0;for(auto*b:{cable0.get(),cable1.get()}){const double final=i?final1.getValue():final0.getValue();double u=0.;if(final>=0){if(final<target[i]||this->end.getValue()<=start.getValue())throw std::runtime_error("Invalid closing target/ramp interval");u=std::max(0.,std::min(1.,(end-start.getValue())/(this->end.getValue()-start.getValue())));u=u*u*u*(10+u*(-15+6*u));}applied[i]=target[i]+u*((final>=0?final:target[i])-target[i]);std::ostringstream value;value<<std::setprecision(17)<<applied[i++];if(!b->findData("valueType")->read("displacement")||!b->findData("value")->read(value.str()))throw std::runtime_error("Native length input rejected");}}
  }
  if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(e)){log<<getContext()->getTime()<<','<<active<<',';if(active)log<<applied[0]<<','<<applied[1];else log<<"NULL,NULL";log<<','<<rest[0]-length(cable0.get())<<','<<rest[1]-length(cable1.get())<<','<<number(cable0.get(),"force")<<','<<number(cable1.get(),"force")<<'\n';log.flush();}
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCableLatch";}
__attribute__((visibility("default")))const char*getModuleVersion(){return "0.1";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Input ONLY:force-to-held-native-geometric-cable-length,no state/forcefield/ODE modifications").add<regrip::NativeCableLatch>());}
}
