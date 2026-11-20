#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/component/solidmechanics/spring/SpringForceField.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip {
class NativeSpringEnergyJournal: public sofa::core::objectmodel::BaseComponent {
public:
 SOFA_CLASS(NativeSpringEnergyJournal,sofa::core::objectmodel::BaseComponent);
 using FF=sofa::component::solidmechanics::spring::SpringForceField<sofa::defaulttype::Vec3Types>;
 sofa::core::objectmodel::Data<std::string> filename;
 std::ofstream out;
 NativeSpringEnergyJournal():filename(initData(&filename,std::string(),"filename","Unique actual Native potential API journal")){f_listening.setValue(true);}
 void init() override {
  BaseComponent::init();
  if(std::ifstream(filename.getValue())) throw std::runtime_error("existing spring energy output");
  out.open(filename.getValue());
  out<<std::setprecision(17)<<"time_s,forcefield,actual_native_potential_J\n";
 }
 void handleEvent(sofa::core::objectmodel::Event* event) override {
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)) return;
  for(auto* ff:getContext()->getObjects<FF>(sofa::core::objectmodel::BaseContext::SearchDown))
   out<<getContext()->getTime()<<','<<std::quoted(ff->getPathName())<<','<<ff->getPotentialEnergy(sofa::core::MechanicalParams::defaultInstance())<<'\n';
  out.flush();
 }
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char* getModuleName(){return "ReGripSpringEnergy";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory* f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only actual Native spring potential API;no state updates").add<regrip::NativeSpringEnergyJournal>());}
}
