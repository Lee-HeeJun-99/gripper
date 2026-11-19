// Sampled analytical missing-inertia input;NOT an ODE/contact solver or implicit force tangent.
#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/component/mechanicalload/ConstantForceField.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip {
using sofa::core::objectmodel::BaseComponent;using sofa::core::objectmodel::BaseLink;
class NativeInertiaInput:public BaseComponent {
public:
 using R=sofa::defaulttype::Rigid3Types;using V=sofa::defaulttype::Vec3Types;
 using Body=sofa::core::behavior::MechanicalState<R>;using Points=sofa::core::behavior::MechanicalState<V>;using Force=sofa::component::mechanicalload::ConstantForceField<R>;
 SOFA_CLASS(NativeInertiaInput,BaseComponent);
 sofa::core::objectmodel::SingleLink<NativeInertiaInput,Body,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> body;
 sofa::core::objectmodel::SingleLink<NativeInertiaInput,Points,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> points;
 sofa::core::objectmodel::SingleLink<NativeInertiaInput,Force,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> force;
 sofa::core::objectmodel::Data<double> mass;
 sofa::core::objectmodel::Data<std::string> filename;std::ofstream f;
 NativeInertiaInput():body(initLink("body","COM rigid state,read only")),points(initLink("points","Equal-mass Native quadrature positions,read only")),force(initLink("force","Exclusive Native ConstantForceField input")),mass(initData(&mass,0.0,"mass","Explicit research total mass in kg")),filename(initData(&filename,std::string(),"filename","Sampled physical input journal")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();if(!body||!points||!force||mass.getValue()<=0||std::ifstream(filename.getValue()))throw std::runtime_error("explicit valid input links/mass/unique journal required");f.open(filename.getValue());f<<std::setprecision(17)<<"input_time_s,omega_world_rad_s,angular_momentum_Nms,applied_torque_Nm,power_W,COM_offset_m\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(!dynamic_cast<sofa::simulation::AnimateBeginEvent*>(e))return;
  const auto& q=body->read(sofa::core::vec_id::read_access::position)->getValue();const auto& v=body->read(sofa::core::vec_id::read_access::velocity)->getValue();const auto& p=points->read(sofa::core::vec_id::read_access::position)->getValue();
  if(q.size()!=1||v.size()!=1||p.empty())throw std::runtime_error("single COM rigid reference only");
  const auto w=v[0].getVOrientation();V::Deriv L{},offset{};
  for(const auto& x:p){const auto r=x-q[0].getCenter();offset+=r/double(p.size());L+=sofa::type::cross(r,sofa::type::cross(w,r))*(mass.getValue()/p.size());}
  if(offset.norm()>1e-12)throw std::runtime_error("mass quadrature is not COM centred");
  const auto torque=-sofa::type::cross(w,L);R::Deriv input{};input.getVOrientation()=torque;
  force->d_forces.setValue(R::VecDeriv(1,input));
  f<<getContext()->getTime()<<",\""<<w<<"\",\""<<L<<"\",\""<<torque<<"\","<<sofa::type::dot(torque,w)<<",\""<<offset<<"\"\n";f.flush();
 }
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char* getModuleName(){return "ReGripInertiaInput";}
__attribute__((visibility("default"))) const char* getModuleVersion(){return "1.0";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Sampled analytical gyroscopic input to Native ConstantForceField;NO state writes or solver replacement").add<regrip::NativeInertiaInput>());}
}
