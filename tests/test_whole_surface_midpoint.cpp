#include "../models/film_impact/WholeSurfaceMidpoint.h"
#include "../models/film_impact/SustainedSurface.h"
#include <iostream>
using namespace regrip_film_impact;using namespace regrip_film_native;
int main(){try{
 Assembly model(5);auto mass=model.masses();std::vector<Point>q(model.size()),v(model.size()),zero(model.size());unsigned tip=model.id(0,4,2);v[tip][2]=-3;
 std::vector<std::array<unsigned,3>>triangles;
 for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<model.nx;++i)for(unsigned j=0;j+1<model.parts[part].ny;++j){
  unsigned a=model.id(part,i,j),b=model.id(part,i+1,j),c=model.id(part,i,j+1),d=model.id(part,i+1,j+1);
  triangles.push_back({a,b,c});triangles.push_back({b,d,c});
 }
 Point center=model.rest()[tip];center[2]-=1.001;CoupledPlaneStep m(model,mass,.001,2,0,q,v,zero,0);EventControl control;
 auto result=wholeSurfaceMidpoint(m,triangles,center,1,0,control);
 if(!result.event||!result.impact||result.minimumGap< -1e-10||result.impact->state.momentumResidual>1e-20)throw std::runtime_error("whole film midpoint event");
 control.maximum=.001;auto s=control.sample(.7);auto exact=ControlProfile::evaluate(.7,.001,4,6,8,true);
 if(s.tension!=exact.tension||s.rate!=exact.rate||s.acceleration!=exact.acceleration)throw std::runtime_error("shared C2 input");
 double delta=1e-5;double fd=(control.sample(.7+delta).tension-control.sample(.7-delta).tension)/(2*delta);
 if(std::abs(fd-s.rate)>1e-12)throw std::runtime_error("shared C2 derivative");
 auto c2event=wholeSurfaceMidpoint(m,triangles,center,1,.7,control,true);
 auto shiftedPlus=wholeSurfaceMidpoint(m,triangles,center,1,.7+delta,control,true);
 auto shiftedMinus=wholeSurfaceMidpoint(m,triangles,center,1,.7-delta,control,true);
 if(!c2event.event||!shiftedPlus.event||!shiftedMinus.event||!c2event.absoluteEventStartTimeDerivative)throw std::runtime_error("C2 isolated event branch");
 double eventFD=1+m.h*(shiftedPlus.event->fraction-shiftedMinus.event->fraction)/(2*delta);
 if(std::abs(eventFD-*c2event.absoluteEventStartTimeDerivative)>1e-7)throw std::runtime_error("C2 event-time IFT FD");
 std::cout<<"C2 event absolute-time sensitivity FD error "<<std::abs(eventFD-*c2event.absoluteEventStartTimeDerivative)<<'\n';
 auto contactCenter=model.rest()[tip];contactCenter[2]-=1;
 CoupledPlaneStep touching(model,mass,.00001,2,0,q,zero,zero,0);EventControl noLoad;
 auto held=wholeSurfaceContactStep(touching,triangles,contactCenter,1,0,noLoad);
 if(!held.sustained||held.minimumGap< -1e-10||held.projectionLoss<0)throw std::runtime_error("sustained rest identity");
 // Release is driven by an outward initial velocity, not by changing gap.
 auto outward=zero;outward[tip][2]=.1;CoupledPlaneStep separating(model,mass,.00001,2,0,q,outward,zero,0);
 auto released=wholeSurfaceContactStep(separating,triangles,contactCenter,1,0,noLoad);
 if(released.minimumGap<0||released.constraintImpulse!=0)throw std::runtime_error("unloaded release");
 std::cout<<"PASS independent whole-film midpoint event fraction "<<result.event->fraction<<" owned rows "<<result.event->rows.size()<<" end gap "<<result.minimumGap<<" impulse residual "<<result.impact->state.momentumResidual<<";NOT sustained contact or full C2 closing\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
