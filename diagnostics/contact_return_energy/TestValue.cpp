#include "Audit.h"
#include <sofa/core/behavior/Mass.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/component/statecontainer/MechanicalObject.h>
#include "../../models/contact_birth/MaterialCells.h"
#include "../../models/curved_contact/Map.h"
#include "CurveClassOnly.inc"
#include <iostream>
int main(){try{
 using namespace regrip_integrated;using State=sofa::component::statecontainer::MechanicalObject<Types>;
 double maxAbsolute=0,maxRelative=0;unsigned count=0;
 for(unsigned shape=0;shape<3;++shape){
  auto state=sofa::core::objectmodel::New<State>();state->resize(3);Types::VecCoord x(3);
  x[0].getCenter()={-.5,1.03,0};x[1].getCenter()={.5,1.03,0};for(auto&p:x)p.getOrientation()={0,0,0,1};state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);state->write(sofa::core::vec_id::write_access::position)->setValue(x);
  auto f=sofa::core::objectmodel::New<CurvedMaterialContact>(state.get());f->segments.setValue({0,1});f->objectIndex.setValue(2);f->shape.setValue(shape);f->radius.setValue(1.);f->halfHeight.setValue(1.);f->pointRadius.setValue(.02);f->mu.setValue(.3);f->lineStiffness.setValue(1.);f->tangentLineStiffness.setValue(1.);f->historySpacing.setValue(.02);f->prepare(x);
  for(unsigned i=0;i<200;++i){
   double y=1.01+.018*std::sin(.07*i),z=.02*std::sin(.11*i);x[0].getCenter()={-.5,y,z};x[1].getCenter()={.5,y,z};auto a=exp(V{0,.01*std::sin(.03*i),.01*std::sin(.04*i)}),b=exp(V{0,.01*std::cos(.05*i),-.01*std::sin(.04*i)}),o=exp(V{0,.01*std::sin(.02*i),0});for(int j=0;j<4;++j){x[0].getOrientation()[j]=a[j];x[1].getOrientation()[j]=b[j];x[2].getOrientation()[j]=o[j];}
   state->write(sofa::core::vec_id::write_access::position)->setValue(x);double old=f->committedPlastic;sofa::core::MechanicalParams mp;
   double ad=f->getPotentialEnergy(&mp,*state->read(sofa::core::vec_id::read_access::position)),value=f->computeValue(x).a.energy;
   double error=std::abs(ad-value),relative=ad?error/std::abs(ad):(value==0?0:INFINITY);maxAbsolute=std::max(maxAbsolute,error);maxRelative=std::max(maxRelative,relative);
   if(error>1e-15||relative>1e-10||f->committedPlastic!=old)throw std::runtime_error("value-only energy differs or query commits");
   if(curveReturnedEnergy(f.get())!=value)throw std::runtime_error("actual hidden bridge value differs");f->commit(x);++count;
  }
 }
 std::cout<<"PASS actual energy API states="<<count<<" max_absolute="<<maxAbsolute<<" max_relative="<<maxRelative<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
