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
 auto repeated=wholeSurfaceContactStep(touching,triangles,contactCenter,1,0,noLoad);
 if(held.position!=repeated.position||held.velocity!=repeated.velocity||held.constraintRows.size()!=repeated.constraintRows.size())throw std::runtime_error("sustained query impurity");
 double positionSum=0,velocitySum=0;
 for(const auto&r:held.constraintRows){
  if(r.jacobian.size()!=touching.freeSize||std::abs(r.barycentric[0]+r.barycentric[1]+r.barycentric[2]-1)>1e-12)throw std::runtime_error("owned row inventory");
  if(r.stage==1)positionSum+=r.impulse;else if(r.stage==2)velocitySum+=r.impulse;else throw std::runtime_error("unowned stage");
 }
 if(positionSum!=held.constraintImpulse||velocitySum!=held.projectionImpulse)throw std::runtime_error("constraint row impulse inventory mismatch");
 auto midpointHeld=wholeSurfaceContactStep(touching,triangles,contactCenter,1,0,noLoad,true);
 if(midpointHeld.position!=held.position||midpointHeld.velocity!=held.velocity)throw std::runtime_error("constrained midpoint unloaded identity");
 // Release is driven by an outward initial velocity, not by changing gap.
 auto outward=zero;outward[tip][2]=.1;CoupledPlaneStep separating(model,mass,.00001,2,0,q,outward,zero,0);
 auto released=wholeSurfaceContactStep(separating,triangles,contactCenter,1,0,noLoad);
 if(released.minimumGap<0||released.constraintImpulse!=0)throw std::runtime_error("unloaded release");
 auto midpointRelease=wholeSurfaceContactStep(separating,triangles,contactCenter,1,0,noLoad,true);
 if(midpointRelease.minimumGap<0||midpointRelease.constraintImpulse!=0)throw std::runtime_error("midpoint outward release");
 // Algebraic position-kernel check with deliberately inward initial velocity.
 // This is NOT a valid sustained-owner initial state (that owner rejects it
 // until a zero-time physical impact law has been applied).
 bool loadedContact=false;
 for(double side:{-1.,1.}){
  auto sphere=model.rest()[tip];sphere[2]+=side;
  auto inputVelocity=zero;inputVelocity[tip][2]=-.1;
  CoupledPlaneStep loaded(model,mass,.001,2,.00001,q,inputVelocity,zero,0);
  auto accepted=midpointPosition(loaded,triangles,sphere,1,.00001);
  auto vmid=(.5*(loaded.pack(accepted.mechanical.velocity)+loaded.pack(inputVelocity))).eval();
  CoupledPlaneStep midpointStage(model,mass,.0005,2,.00001,q,inputVelocity,zero,0);
  Eigen::VectorXd residual=2*midpointStage.evaluate(vmid).gradient;
  for(unsigned k=0;k<accepted.rows.size();++k){residual-=filmRow(loaded,accepted.rows[k].J).transpose()*accepted.mechanical.lambda(k);loadedContact|=accepted.mechanical.lambda(k)>0;}
  if(residual.norm()>1e-14)throw std::runtime_error("midpoint physical impulse factor/momentum residual");
 }
 if(!loadedContact)throw std::runtime_error("loaded midpoint test never exercised contact");
 auto inward=zero;inward[tip][2]=-.1;CoupledPlaneStep unsupported(model,mass,.001,2,0,q,inward,zero,0);
 bool rejected=false;try{wholeSurfaceContactStep(unsupported,triangles,contactCenter,1,0,noLoad,true);}catch(const std::domain_error&){rejected=true;}
 if(!rejected)throw std::runtime_error("unhandled zero-time impact silently accepted");
 std::cout<<"PASS independent whole-film midpoint event fraction "<<result.event->fraction<<" owned rows "<<result.event->rows.size()<<" end gap "<<result.minimumGap<<" impulse residual "<<result.impact->state.momentumResidual<<";NOT sustained contact or full C2 closing\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
