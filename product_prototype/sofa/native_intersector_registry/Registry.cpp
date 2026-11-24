// Public registry queries ONLY; no intersector registration or mechanical writes.
#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/collision/Intersection.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <fstream>
class ReGripIntersectorRegistry:public sofa::core::objectmodel::BaseComponent {
public:
 SOFA_CLASS(ReGripIntersectorRegistry,sofa::core::objectmodel::BaseComponent);
 sofa::core::objectmodel::Data<std::string> filename;
 bool recorded=false;
 ReGripIntersectorRegistry():filename(initData(&filename,std::string(),"filename","Unique installed intersector lookup journal")){f_listening.setValue(true);}
 void handleEvent(sofa::core::objectmodel::Event*event)override {
  if(recorded||!dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event))return;
  if(std::ifstream(filename.getValue()))throw std::runtime_error("exclusive registry output required");
  std::ofstream f(filename.getValue());f<<"intersection,model0,model1,class0,class1,supported,swap,intersector\n";
  auto models=getContext()->getObjects<sofa::core::CollisionModel>(sofa::core::objectmodel::BaseContext::SearchDown);
  for(auto* intersection:getContext()->getObjects<sofa::core::collision::Intersection>(sofa::core::objectmodel::BaseContext::SearchDown))
   for(auto* a:models)for(auto* b:models){
    if(a->getPathName().find("/wire/wireSurface/")!=0||b->getPathName().find("/finiteEyelet/")!=0)continue;
    bool swap=false;auto* method=intersection->findIntersector(a,b,swap);
    f<<'"'<<intersection->getClassName()<<"\",\""<<a->getPathName()<<"\",\""<<b->getPathName()<<"\",\""<<a->getClassName()<<"\",\""<<b->getClassName()<<"\","<<(method!=nullptr)<<','<<swap<<",\""<<(method?method->name():"NULL")<<"\"\n";
   }
  recorded=true;
 }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripIntersectorRegistry";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Public installed intersector query only; no physical implementation").add<ReGripIntersectorRegistry>());}
}
