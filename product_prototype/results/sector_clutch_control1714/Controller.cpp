// Sensor-triggered cable clutch only. No mechanical-state/contact/solver writes.
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <limits>
#include <cmath>
class NativeSectorClutch:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(NativeSectorClutch,sofa::core::objectmodel::BaseObject);
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using BL=sofa::core::objectmodel::BaseLink;
 using Vec=sofa::type::Vec3d;
 sofa::core::objectmodel::SingleLink<NativeSectorClutch,State,BL::FLAG_STOREPATH|BL::FLAG_STRONGLINK> body;
 sofa::core::objectmodel::SingleLink<NativeSectorClutch,BaseObject,BL::FLAG_STOREPATH|BL::FLAG_STRONGLINK> sequence;
 sofa::core::objectmodel::Data<sofa::type::vector<Vec>> vertices;
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> owners;
 sofa::core::objectmodel::Data<Vec> normal0,normal1;
 sofa::core::objectmodel::Data<double> threshold;
 sofa::core::objectmodel::Data<bool> enabled;
 sofa::core::objectmodel::Data<std::string> filename;
 bool latched=false;
 std::ofstream file;
 NativeSectorClutch():body(initLink("body","Read-only accepted rigid frames")),sequence(initLink("sequence","Only maximumForceN is writable")),vertices(initData(&vertices,"vertices","Actual finite hardware vertices in rigid-parent coordinates")),owners(initData(&owners,"owners","Rigid parent per vertex")),normal0(initData(&normal0,Vec(),"normal0","First outward sector normal")),normal1(initData(&normal1,Vec(),"normal1","Second outward sector normal")),threshold(initData(&threshold,.0001,"threshold","Existing contactDistance/2, metres")),enabled(initData(&enabled,false,"enabled","False is a passive sensor control")),filename(initData(&filename,std::string(),"filename","Exclusive sensor/command journal")){f_listening.setValue(true);}
 double gap()const {
  const auto&q=body->read(sofa::core::vec_id::read_access::position)->getValue();
  double value=std::numeric_limits<double>::infinity();
  for(unsigned k=0;k<owners.getValue().size();++k){
   const auto& f=q.at(owners.getValue()[k]);
   const Vec x=f.getCenter()+f.getOrientation().rotate(vertices.getValue()[k]);
   for(const Vec n:{normal0.getValue(),normal1.getValue()})value=std::min(value,-sofa::type::dot(x,n));
  }
  if(!std::isfinite(value))throw std::runtime_error("nonfinite sector sensor");
  return value;
 }
 void init()override {
  BaseObject::init();
  if(!body||!sequence||vertices.getValue().empty()||vertices.getValue().size()!=owners.getValue().size()||std::ifstream(filename.getValue()))throw std::runtime_error("explicit geometry/unique journal required");
  if(!dynamic_cast<sofa::core::objectmodel::Data<double>*>(sequence->findData("maximumForceN")))throw std::runtime_error("typed native force sequence required");
  if(gap()<=threshold.getValue())throw std::runtime_error("initial sector safety preflight failed");
  file.open(filename.getValue());file<<std::setprecision(17)<<"time_s,accepted_sector_gap_m,latched,next_maximumForce_N\n";
 }
 void handleEvent(sofa::core::objectmodel::Event*e)override {
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  const double g=gap();
  if(enabled.getValue()&&g<=threshold.getValue())latched=true;
  auto*d=dynamic_cast<sofa::core::objectmodel::Data<double>*>(sequence->findData("maximumForceN"));
  // End-event update is explicitly for the NEXT existing sequence begin event.
  if(latched)d->setValue(0.);
  file<<getContext()->getTime()<<','<<g<<','<<latched<<','<<d->getValue()<<'\n';file.flush();
 }
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char* getModuleName(){return "ReGripSectorClutch";}
__attribute__((visibility("default"))) const char* getModuleVersion(){return "1";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Accepted-state finite-envelope cable safety clutch;not a solver").add<NativeSectorClutch>());}
}
