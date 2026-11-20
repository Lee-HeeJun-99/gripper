#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/collision/NarrowPhaseDetection.h>
#include <sofa/core/collision/DetectionOutput.h>
#include <sofa/core/CollisionModel.h>
#include <sofa/component/collision/geometry/LineCollisionModel.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip {
using sofa::core::objectmodel::BaseComponent;using sofa::core::objectmodel::BaseLink;
class NativeFeatureRows:public BaseComponent {
public:
 SOFA_CLASS(NativeFeatureRows,BaseComponent);
 sofa::core::objectmodel::SingleLink<NativeFeatureRows,sofa::core::collision::NarrowPhaseDetection,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> narrow;
 sofa::core::objectmodel::Data<std::string> filename;std::ofstream f;
 NativeFeatureRows():narrow(initLink("narrow","Actual Native detection output,read only")),filename(initData(&filename,std::string(),"filename","Unique feature journal")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();if(!narrow||std::ifstream(filename.getValue()))throw std::runtime_error("unique linked feature journal required");f.open(filename.getValue());f<<std::setprecision(17)<<"time_s,model0,model1,pair_index,element0,element1,contact_id,point0,point1,normal,value,deltaT,line0_vertex0,line0_vertex1,line1_vertex0,line1_vertex1\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  for(const auto& pair:narrow->getDetectionOutputs()){
   // Checked RTTI cross-cast to the common public vector base;no layout reinterpretation.
   const auto* outputs=dynamic_cast<const sofa::type::vector<sofa::core::collision::DetectionOutput>*>(pair.second);
   if(!outputs)throw std::runtime_error("unsupported native detection output vector type");
   unsigned k=0;for(const auto& c:*outputs){
    f<<getContext()->getTime()<<",\""<<pair.first.first->getPathName()<<"\",\""<<pair.first.second->getPathName()<<"\","<<k++<<','<<c.elem.first.getIndex()<<','<<c.elem.second.getIndex()<<','<<c.id<<",\""<<c.point[0]<<"\",\""<<c.point[1]<<"\",\""<<c.normal<<"\","<<c.value<<','<<c.deltaT;
    for(const auto& element:{c.elem.first,c.elem.second}){
     using Model=sofa::component::collision::geometry::LineCollisionModel<sofa::defaulttype::Vec3Types>;
     if(auto* model=dynamic_cast<Model*>(element.getCollisionModel())){sofa::component::collision::geometry::Line line(model,element.getIndex());f<<','<<line.i1()<<','<<line.i2();}
     else f<<",-1,-1";
    }f<<'\n';
   }
  }f.flush();
 }
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char* getModuleName(){return "ReGripFeatureRows";}
__attribute__((visibility("default"))) const char* getModuleVersion(){return "1.0";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only Native detection feature/line endpoint identities").add<regrip::NativeFeatureRows>());}
}
