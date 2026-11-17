#pragma once
#include "../film_coupled_contact/CoupledOwnerClass.h"
#include <sofa/core/objectmodel/Context.h>
namespace regrip_coupled_adaptive {
// Genuine physical interval refinement,NOT merely a different output cadence.
// Start from the declared initial state,not from saved positions/velocities.
// Every interval of a measured adaptive grid is divided by1/2/4. No error
// estimator or forecast is rerun;all physical solves use the existing owner.
class FrozenCoupledGridODE final:public regrip_coupled::CoupledSphereODE {
public:
 SOFA_CLASS(FrozenCoupledGridODE,regrip_coupled::CoupledSphereODE);
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>>gridTicks{initData(&gridTicks,"gridTicks","Strictly increasing integer accepted-grid end ticks")};
 sofa::core::objectmodel::Data<unsigned>tickDenominator{initData(&tickDenominator,1u,"tickDenominator","Integer physical grid denominator")};
 sofa::core::objectmodel::Data<unsigned>gridFactor{initData(&gridFactor,1u,"gridFactor","Divide EACH physical interval by1/2/4")};
 sofa::core::objectmodel::Data<double>gridDuration{initData(&gridDuration,.001,"gridDuration","Physical interval duration seconds")};
 std::ofstream macro,grid;bool completed=false;
 void init()override{
  CoupledSphereODE::init();unsigned previous=0,factor=gridFactor.getValue(),den=tickDenominator.getValue();const auto&ticks=gridTicks.getValue();if((factor!=1&&factor!=2&&factor!=4)||ticks.empty()||den==0||den>1048576||gridDuration.getValue()<=0||gridDuration.getValue()>.001||ticks.size()*factor>1600)throw std::runtime_error("bounded frozen dyadic coupon grid required");for(unsigned t:ticks){if(t<=previous||t>den)throw std::runtime_error("nonmonotone frozen grid");previous=t;}if(previous!=den)throw std::runtime_error("incomplete frozen grid");
  for(const auto*suffix:{".macro_states.csv",".grid.csv"})if(std::ifstream(filename.getValue()+suffix))throw std::runtime_error("frozen journals exist");states.flush();std::ifstream input(filename.getValue()+".states.csv");std::string header;std::getline(input,header);macro.open(filename.getValue()+".macro_states.csv");macro<<header<<'\n';grid.open(filename.getValue()+".grid.csv");grid<<std::setprecision(17)<<"begin,dt,end,source_interval,subdivision\n";
 }
 void solve(const sofa::core::ExecParams*params,SReal dt,sofa::core::MultiVecCoordId xId,sofa::core::MultiVecDerivId vId)override{
  auto*context=dynamic_cast<sofa::core::objectmodel::Context*>(getContext());if(!context||completed||context->getTime()!=0||dt!=gridDuration.getValue())throw std::runtime_error("frozen grid is one fresh complete coupon;no state replay");
  struct Restore{sofa::core::objectmodel::Context*c;double dt;~Restore(){c->setTime(0);c->setDt(dt);}}restore{context,dt};unsigned previous=0,factor=gridFactor.getValue();double denominator=double(tickDenominator.getValue())*factor;std::streampos finalOffset;
  for(unsigned i=0;i<gridTicks.getValue().size();++i){unsigned end=gridTicks.getValue()[i],interval=end-previous;
   for(unsigned j=0;j<factor;++j){double t=gridDuration.getValue()*double(previous*factor+j*interval)/denominator,h=gridDuration.getValue()*interval/denominator;context->setTime(t);context->setDt(h);finalOffset=states.tellp();CoupledSphereODE::solve(params,h,xId,vId);grid<<t<<','<<h<<','<<t+h<<','<<i<<','<<j<<'\n';}previous=end;
  }
  states.flush();grid.flush();std::ifstream input(filename.getValue()+".states.csv");input.seekg(finalOffset);std::string line;if(!std::getline(input,line)||line.empty())throw std::runtime_error("missing actual frozen-grid final state");macro<<line<<'\n';macro.flush();completed=true;
 }
};
}
