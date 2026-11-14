// Existing validated implementation included unchanged in an isolated plugin.
#include "Integrated.inc"
namespace regrip_integrated {
class ForceAudit final:public sofa::core::objectmodel::BaseComponent{
public:
 SOFA_CLASS(ForceAudit,sofa::core::objectmodel::BaseComponent);
 sofa::core::objectmodel::Data<std::string> filename;
 sofa::core::objectmodel::Data<unsigned> stride;
 sofa::core::objectmodel::Data<double> after;
 sofa::core::behavior::MechanicalState<Types>*state=nullptr;
 std::ofstream file;unsigned steps=0;
 ForceAudit():filename(initData(&filename,std::string("forces.txt"),"filename","Per-field unprojected force audit")),stride(initData(&stride,20u,"stride","Sampling stride")),after(initData(&after,0.,"after","Start recording time")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();state=dynamic_cast<sofa::core::behavior::MechanicalState<Types>*>(getContext()->getMechanicalState());
  std::ifstream existing(filename.getValue());if(!state||!stride.getValue()||existing){msg_error()<<"Invalid audit/output";return;}file.open(filename.getValue());file<<std::setprecision(17);}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!file||!state||!stride.getValue()||!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||++steps%stride.getValue()||getContext()->getTime()<after.getValue()-1e-10)return;
  auto*x=state->read(sofa::core::vec_id::read_access::position);Inherit::DataVecDeriv zero,f;zero.setValue(Types::VecDeriv(state->getSize()));sofa::core::MechanicalParams mp;
  file<<"T "<<getContext()->getTime()<<'\n';
  for(auto*ff:getContext()->getObjects<Inherit>(sofa::core::objectmodel::BaseContext::Local)){
   f.setValue(Types::VecDeriv(state->getSize()));ff->addForce(&mp,f,*x,zero);file<<"F "<<ff->getClassName()<<' '<<ff->getName()<<' '<<f.getValue()<<'\n';
  }
  file<<"ENGINE "<<state->read(sofa::core::vec_id::read_access::force)->getValue()<<'\n';file.flush();
 }
};
}
extern "C" {
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripStabilization";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){registerIntegratedObjects(f);f->registerObjects(sofa::core::ObjectRegistrationData("Independent per-field static residual audit").add<regrip_integrated::ForceAudit>());}
}
