#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/collision/NarrowPhaseDetection.h>
#include <sofa/core/collision/DetectionOutput.h>
#include <sofa/core/CollisionModel.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/component/constraint/lagrangian/model/UnilateralLagrangianConstraint.h>
#include <sofa/simulation/events/BuildConstraintSystemEndEvent.h>
#include <sofa/simulation/CollisionEndEvent.h>
#include <fstream>
#include <iomanip>
class ReGripContactProvenance:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(ReGripContactProvenance,sofa::core::objectmodel::BaseObject);
 using Link=sofa::core::objectmodel::BaseLink;
 using Constraint=sofa::component::constraint::lagrangian::model::UnilateralLagrangianConstraint<sofa::defaulttype::Vec3Types>;
 sofa::core::objectmodel::SingleLink<ReGripContactProvenance,sofa::core::collision::NarrowPhaseDetection,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>narrow;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<double>startTime,endTime;
 sofa::core::objectmodel::Data<bool>atCollisionEnd;
 std::ofstream features,children;
 ReGripContactProvenance():narrow(initLink("narrow","Read-only actual detection outputs")),filename(initData(&filename,std::string(),"filename","Unique output prefix")),startTime(initData(&startTime,0.,"startTime","Read-only sampling window start")),endTime(initData(&endTime,.00121,"endTime","Read-only sampling window end")),atCollisionEnd(initData(&atCollisionEnd,false,"atCollisionEnd","Read detector ONLY before constraint assembly;no child Jacobian available at this phase")){f_listening.setValue(true);}
 void init()override{
  BaseObject::init();if(!narrow||std::ifstream(filename.getValue()+".features.csv"))throw std::runtime_error("unique linked provenance output required");
  if(startTime.getValue()<0||endTime.getValue()<startTime.getValue()||endTime.getValue()-startTime.getValue()>.005)throw std::runtime_error("bounded sampling window <=5ms required");
  features.open(filename.getValue()+".features.csv");children.open(filename.getValue()+".children.csv");features<<std::setprecision(17);children<<std::setprecision(17);
  features<<"previous_time_s,model0,model1,index,element0,element1,contact_id,point0,point1,normal,value\n";
  children<<"previous_time_s,constraint,state,side,row,column,point,J\n";
 }
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  const bool collision=atCollisionEnd.getValue();
  if((collision?!dynamic_cast<sofa::simulation::CollisionEndEvent*>(e):!dynamic_cast<sofa::simulation::BuildConstraintSystemEndEvent*>(e))||getContext()->getTime()<startTime.getValue()||getContext()->getTime()>endTime.getValue())return;
  double t=getContext()->getTime();
  for(const auto&pair:narrow->getDetectionOutputs()){
   if(!pair.second)continue;
   const auto*out=dynamic_cast<const sofa::type::vector<sofa::core::collision::DetectionOutput>*>(pair.second);
   if(!out)throw std::runtime_error("unsupported public detector vector");
   unsigned k=0;for(const auto&c:*out)features<<t<<",\""<<pair.first.first->getPathName()<<"\",\""<<pair.first.second->getPathName()<<"\","<<k++<<','<<c.elem.first.getIndex()<<','<<c.elem.second.getIndex()<<','<<c.id<<",\""<<c.point[0]<<"\",\""<<c.point[1]<<"\",\""<<c.normal<<"\","<<c.value<<'\n';
  }
  if(collision){features.flush();return;} // No access to not-yet-built constraint rows.
  for(auto*c:getContext()->getObjects<Constraint>(sofa::core::objectmodel::BaseContext::SearchDown)){
   unsigned side=0;for(auto*base:{c->getMechModel1(),c->getMechModel2()}){
    auto*state=dynamic_cast<sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>*>(base);
    if(!state)throw std::runtime_error("missing typed Vec3 contact child state");
    const auto&q=state->read(sofa::core::vec_id::read_access::position)->getValue();
    const auto&J=state->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();
    for(auto r=J.begin();r!=J.end();++r)for(auto col=r.begin();col!=r.end();++col){
     if(col.index()>=q.size())throw std::runtime_error("invalid child Jacobian column");
     children<<t<<",\""<<c->getPathName()<<"\",\""<<state->getPathName()<<"\","<<side<<','<<r.index()<<','<<col.index()<<",\""<<q[col.index()]<<"\",\""<<col.val()<<"\"\n";
    }++side;
   }
  }features.flush();children.flush();
 }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripContactProvenance";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only detector features and actual child constraint rows;no metadata mutation").add<ReGripContactProvenance>());}
}
