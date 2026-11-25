// Read-only accepted-state cable geometric sensor, not forcefield/controller.
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
class NativeCableRate:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(NativeCableRate,sofa::core::objectmodel::BaseObject);
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using BL=sofa::core::objectmodel::BaseLink;using Vec=sofa::type::Vec3d;
 sofa::core::objectmodel::SingleLink<NativeCableRate,State,BL::FLAG_STOREPATH|BL::FLAG_STRONGLINK> body;
 sofa::core::objectmodel::Data<sofa::type::vector<Vec>> local;
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> owners;
 sofa::core::objectmodel::Data<Vec> origin;
 sofa::core::objectmodel::Data<std::string> filename;
 std::ofstream file;
 NativeCableRate():body(initLink("body","Read-only rigid frames")),local(initData(&local,"local","Actual local cable points")),owners(initData(&owners,"owners","Actual mapping owners")),origin(initData(&origin,Vec(),"origin","Stationary pullPoint only")),filename(initData(&filename,std::string(),"filename","Unique journal")){f_listening.setValue(true);}
 void init()override{
  BaseObject::init();if(!body||local.getValue().empty()||local.getValue().size()!=owners.getValue().size()||std::ifstream(filename.getValue()))throw std::runtime_error("explicit read-only geometry and new journal required");
  file.open(filename.getValue());file<<std::setprecision(17)<<"time_s,length_m,rate_m_s\n";
 }
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  const auto&q=body->read(sofa::core::vec_id::read_access::position)->getValue();
  const auto&v=body->read(sofa::core::vec_id::read_access::velocity)->getValue();
  Vec previous=origin.getValue(),previousV;double length=0,rate=0;
  for(unsigned j=0;j<owners.getValue().size();++j){
   const auto k=owners.getValue()[j];const Vec arm=q.at(k).getOrientation().rotate(local.getValue()[j]);
   const Vec point=q.at(k).getCenter()+arm;
   const Vec velocity=v.at(k).getVCenter()+sofa::type::cross(v.at(k).getVOrientation(),arm);
   const Vec delta=point-previous;const double norm=delta.norm();if(norm<=0)throw std::runtime_error("zero cable segment");
   length+=norm;rate+=sofa::type::dot(delta,velocity-previousV)/norm;previous=point;previousV=velocity;
  }
  file<<getContext()->getTime()<<','<<length<<','<<rate<<'\n';file.flush();
 }
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripCableRate";}
__attribute__((visibility("default"))) const char*getModuleVersion(){return "1";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only accepted cable kinematics").add<NativeCableRate>());}
}
