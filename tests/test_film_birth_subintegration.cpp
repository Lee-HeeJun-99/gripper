#include "../models/film_impact/BracketedFilmBirth.h"
#include "../models/film_impact/IsolatedFilmImpactStep.h"
#include "../models/film_impact/EventTangent.h"
#include <iostream>
using namespace regrip_film_impact;using namespace regrip_film_native;
int main(){try{
 Assembly model(5);auto mass=model.masses();std::vector<Point>q(model.size()),v(model.size()),zero(model.size());
 unsigned tip=model.id(0,4,2);v[tip][2]=-3;Point center=model.rest()[tip];center[2]-=1.001;
 CoupledPlaneStep original(model,mass,.001,2,0,q,v,zero,0);
 auto event=resolveFilmBirthBracket(original,{tip},center,1);
 auto impulse=filmEventImpulse(original,event.position,event.velocity,{{tip}},center,1,1e-10,1e-12);
 if(!(event.time>0&&event.time<original.h&&event.gapRate<0)||std::abs(impulse.reduced.normalVelocity(0))>1e-12||impulse.reduced.energyLoss<=0)
  throw std::runtime_error("subintegrated film event/impact");
 unsigned column=original.index[3*tip+2];double epsilon=1e-4;auto vp=v,vm=v;vp[tip][2]+=epsilon;vm[tip][2]-=epsilon;
 CoupledPlaneStep plus(model,mass,.001,2,0,q,vp,zero,0),minus(model,mass,.001,2,0,q,vm,zero,0);
 auto p=resolveFilmBirthBracket(plus,{tip},center,1),m=resolveFilmBirthBracket(minus,{tip},center,1);
 double fd=(p.time-m.time)/(2*epsilon),analytic=event.timeIncomingDerivative(column);
 if(std::abs(fd-analytic)>1e-8)throw std::runtime_error("subintegration root IFT FD");
 auto tangent=singleEventVelocityTangent(original,event,tip,center,1);
 auto pi=filmEventImpulse(plus,p.position,p.velocity,{{tip}},center,1,1e-10,1e-12);
 auto mi=filmEventImpulse(minus,m.position,m.velocity,{{tip}},center,1,1e-10,1e-12);
 Eigen::VectorXd fdVelocity=(pi.reduced.velocity-mi.reduced.velocity)/(2*epsilon);
 double tangentError=(fdVelocity-tangent.col(column)).norm();
 if(tangentError>1e-6)throw std::runtime_error("birth+impulse consistent tangent FD");
 std::cout<<"event tangent absolute FD error "<<tangentError<<'\n';
 auto full=isolatedFilmImpactStep(original,tip,center,1);
 if(full.remainingGap<0||full.position.size()!=model.size())throw std::runtime_error("isolated impact remainder");
 for(unsigned steps:{20u,40u,80u}){
  IsolatedFilmSequence sequence(original,tip,center,1);unsigned count=0;double eventTime=0;
  for(unsigned i=0;i<steps;++i){double start=sequence.time;auto hit=sequence.advance(.001/steps);
   if(hit){++count;eventTime=start+hit->birth.time;}}
  if(count!=1)throw std::runtime_error("isolated sequence impact count");
  std::cout<<"sequence steps "<<steps<<" event_time "<<eventTime<<" tip "<<sequence.history.position[tip][2]<<'\n';
 }
 // Independent residual identity for midpoint startup: no damping inflation,
 // force evaluated at q_mid, kinematic update uses v_mid, not end velocity.
 IsolatedFilmSequence midpoint(original,tip,center,1,true);double h=.00005;
 if(midpoint.advance(h))throw std::runtime_error("unexpected startup impact");
 auto qmid=q,vmid=v;for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d){
  qmid[i][d]=.5*(q[i][d]+midpoint.history.position[i][d]);
  vmid[i][d]=.5*(v[i][d]+midpoint.history.velocity[i][d]);
  if(std::abs(midpoint.history.position[i][d]-q[i][d]-h*vmid[i][d])>1e-14)throw std::runtime_error("midpoint position identity");
 }
 std::vector<Point>gradient(model.size());model.elements(qmid,0,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)gradient[e.ids[a/3]][a%3]+=e.energy.g[a];});
 Eigen::VectorXd residual=Eigen::VectorXd::Zero(original.freeSize);
 for(unsigned a=0;a<original.index.size();++a)if(original.index[a]>=0){unsigned i=a/3,d=a%3;
  residual(original.index[a])+=original.weight[a]*(mass[i]*(midpoint.history.velocity[i][d]-v[i][d]+h*2*vmid[i][d])+h*gradient[i][d]);
 }
 if(residual.norm()>1e-12)throw std::runtime_error("midpoint momentum identity");
 std::cout<<"PASS independent implicit-film entering bracket:time "<<event.time<<" gap "<<event.gap<<" normal_rate "<<event.gapRate<<" impulse "<<impulse.reduced.impulse(0)<<" IFT "<<analytic<<" FD "<<fd<<";NOT whole-surface CCD or full SOFA timestep\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
