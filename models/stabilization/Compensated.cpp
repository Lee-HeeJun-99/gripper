#include "Compensated.h"
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <vector>
#include <fstream>
#include <iomanip>
#include <cmath>
class CompensatedEulerPositions final:public sofa::core::objectmodel::BaseComponent{
public:
 SOFA_CLASS(CompensatedEulerPositions,sofa::core::objectmodel::BaseComponent);
 using Types=sofa::defaulttype::Rigid3Types;
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> excluded;
 sofa::core::objectmodel::Data<std::string> filename;
 sofa::core::behavior::MechanicalState<Types>*state=nullptr;std::vector<double>before;std::vector<long double>carry;std::ofstream file;unsigned steps=0;size_t corrections=0;
 CompensatedEulerPositions():excluded(initData(&excluded,"excludedIndices","Fixed roots; this component is NOT used on grasp objects")),filename(initData(&filename,std::string("compensation.csv"),"filename","Numerical integration diagnostics")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();state=dynamic_cast<sofa::core::behavior::MechanicalState<Types>*>(getContext()->getMechanicalState());std::ifstream old(filename.getValue());if(!state||old){msg_error()<<"Invalid compensated integration state/output";state=nullptr;return;}file.open(filename.getValue());file<<std::setprecision(17)<<"time,max_carry_mm,coordinate_corrections\n";}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!state)return;
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){const auto&x=state->read(sofa::core::vec_id::read_access::position)->getValue();before.resize(3*x.size());if(carry.size()!=before.size())carry.assign(before.size(),0);for(size_t i=0;i<x.size();++i)for(int j=0;j<3;++j)before[3*i+j]=x[i].getCenter()[j];}
  if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)&&before.size()==3*state->getSize()){
   auto*data=state->write(sofa::core::vec_id::write_access::position);const auto&v=state->read(sofa::core::vec_id::read_access::velocity)->getValue();auto*x=data->beginEdit();double maxCarry=0;
   for(size_t i=0;i<x->size();++i){if(std::find(excluded.getValue().begin(),excluded.getValue().end(),i)!=excluded.getValue().end())continue;for(int j=0;j<3;++j){double old=(*x)[i].getCenter()[j];long double increment=static_cast<long double>(v[i][j])*getContext()->getDt();double next=regrip_compensated::update(before[3*i+j],old,increment,carry[3*i+j]);if(next!=old)++corrections;(*x)[i].getCenter()[j]=next;maxCarry=std::max(maxCarry,double(std::abs(carry[3*i+j])));}}
   data->endEdit();if(++steps%2000==0)file<<getContext()->getTime()<<','<<maxCarry<<','<<corrections<<'\n';
  }
 }
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripCompensated";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Compensated Euler position accumulation; no target/force correction").add<CompensatedEulerPositions>());}
}
