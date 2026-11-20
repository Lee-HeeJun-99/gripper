#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/Mapping.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip {
using sofa::core::objectmodel::BaseComponent;using sofa::core::objectmodel::BaseLink;
class NativeMappingAcceleration:public BaseComponent {
public:
 using In=sofa::defaulttype::Rigid3Types;using Out=sofa::defaulttype::Vec3Types;
 using Map=sofa::core::Mapping<In,Out>;
 using Body=sofa::core::behavior::MechanicalState<In>;
 using Points=sofa::core::behavior::MechanicalState<Out>;
 SOFA_CLASS(NativeMappingAcceleration,BaseComponent);
 sofa::core::objectmodel::SingleLink<NativeMappingAcceleration,Map,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> mapping;
 sofa::core::objectmodel::SingleLink<NativeMappingAcceleration,Body,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> body;
 sofa::core::objectmodel::SingleLink<NativeMappingAcceleration,Points,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> points;
 sofa::core::objectmodel::Data<std::string> filename;std::ofstream f;
 NativeMappingAcceleration():mapping(initLink("mapping","Actual Native rigid mapping,API called on temporary output only")),body(initLink("body","Actual parent rigid state,read only")),points(initLink("points","Actual mapped mass positions,read only")),filename(initData(&filename,std::string(),"filename","Exclusive acceleration API journal")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();if(!mapping||!body||!points||std::ifstream(filename.getValue()))throw std::runtime_error("explicit links and unique filename required");f.open(filename.getValue());f<<std::setprecision(17)<<"time_s,point_index,api_acceleration_m_s2,expected_centripetal_m_s2\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  const auto& q=body->read(sofa::core::vec_id::read_access::position)->getValue();const auto* v=body->read(sofa::core::vec_id::read_access::velocity);const auto& p=points->read(sofa::core::vec_id::read_access::position)->getValue();
  if(q.size()!=1||v->getValue().size()!=1)throw std::runtime_error("single rigid reference only");
  // Neither input state nor its acceleration/force vectors are written.
  sofa::core::objectmodel::Data<In::VecDeriv> zeroParentAcceleration;
  sofa::core::objectmodel::Data<Out::VecDeriv> temporaryChildAcceleration;
  zeroParentAcceleration.setValue(In::VecDeriv(1));temporaryChildAcceleration.setValue(Out::VecDeriv(p.size()));
  mapping->computeAccFromMapping(sofa::core::MechanicalParams::defaultInstance(),temporaryChildAcceleration,*v,zeroParentAcceleration);
  const auto w=v->getValue()[0].getVOrientation();
  for(size_t k=0;k<p.size();++k){const auto r=p[k]-q[0].getCenter();const auto expected=sofa::type::cross(w,sofa::type::cross(w,r));f<<getContext()->getTime()<<','<<k<<",\""<<temporaryChildAcceleration.getValue()[k]<<"\",\""<<expected<<"\"\n";}f.flush();
 }
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char* getModuleName(){return "ReGripMappingAcceleration";}
__attribute__((visibility("default"))) const char* getModuleVersion(){return "1.0";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only public mapping composite acceleration API probe using temporary output").add<regrip::NativeMappingAcceleration>());}
}
