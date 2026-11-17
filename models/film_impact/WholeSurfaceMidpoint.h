#pragma once
#include "SurfaceEvent.h"
#include "ManyRowImpact.h"
#include "FilmProjection.h"
#include "../film_native_contact/CoupledContactStep.h"
#include "../film_rail_tendon/ControlProfile.h"
namespace regrip_film_impact {
struct EventControl {
 double maximum=0,ramp=4,release=6,end=8;bool c2=true;
 regrip_film_rail::ControlProfile::Sample sample(double time)const{return regrip_film_rail::ControlProfile::evaluate(time,maximum,ramp,release,end,c2);}
};
struct ConstraintInventoryRow {
 unsigned triangle=0,feature=0;int stage=0; // 1:BE position solve,2:velocity projection
 SurfacePoint normal{};std::array<double,3>barycentric{};
 double gap=0,impulse=0,normalBefore=0,normalAfter=0;
 Eigen::RowVectorXd jacobian;
};
struct WholeSurfaceStep {
 std::vector<SurfacePoint>position,velocity,eventPosition,preVelocity,postVelocity;
 std::optional<SurfaceEvent>event;std::optional<ManyRowImpact>impact;Eigen::MatrixXd jacobian;
 double forceTime=0,tension=0,tensionRate=0,eventTension=0,minimumGap=0;
 bool remainderRequiresContact=false,sustained=false;
 double constraintImpulse=0,projectionImpulse=0,projectionLoss=0,positionResidual=0;
 Eigen::RowVectorXd eventFractionIncomingDerivative;
 std::optional<double>absoluteEventStartTimeDerivative;
 std::vector<ConstraintInventoryRow>constraintRows;
};
inline WholeSurfaceStep wholeSurfaceMidpoint(const regrip_film_native::CoupledPlaneStep&m,
 const std::vector<std::array<unsigned,3>>&triangles,SurfacePoint center,double radius,
 double beginTime,const EventControl&control,bool deferSustained=false){
 using namespace regrip_film_native;
 auto rest=m.model.rest();WholeSurfaceStep out;out.forceTime=beginTime+m.h/2;
 auto applied=control.sample(out.forceTime);out.tension=applied.tension;out.tensionRate=applied.rate;
 CoupledContactStep midpoint(m.model,m.mass,m.h/2,m.damping,out.tension,m.previous,m.previousVelocity,{},true,true);
 auto middle=midpoint.solve(m.previousVelocity);
 QuadraticSurfacePath path{rest,std::vector<Point>(rest.size()),std::vector<Point>(rest.size())};
 for(unsigned i=0;i<rest.size();++i)for(unsigned d=0;d<3;++d){
  path.a0[i][d]+=m.previous[i][d];path.a1[i][d]=m.h*m.previousVelocity[i][d];
  path.a2[i][d]=m.h*(middle.velocity[i][d]-m.previousVelocity[i][d]);
 }
 out.event=earliestSurfaceEvent(path,triangles,center,radius);
 auto freeEnd=[&](const std::vector<Point>&q,const std::vector<Point>&v,double h,double t){
  CoupledContactStep step(m.model,m.mass,h/2,m.damping,control.sample(t+h/2).tension,q,v,{},true,true);
  auto result=step.solve(v);for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d){
   result.displacement[i][d]=2*result.displacement[i][d]-q[i][d];result.velocity[i][d]=2*result.velocity[i][d]-v[i][d];
  }return result;
 };
 if(!out.event){out.position=middle.displacement;out.velocity=middle.velocity;
  for(unsigned i=0;i<rest.size();++i)for(unsigned d=0;d<3;++d){out.position[i][d]=2*out.position[i][d]-m.previous[i][d];out.velocity[i][d]=2*out.velocity[i][d]-m.previousVelocity[i][d];}
 }else{
  double a=out.event->fraction;out.eventPosition=m.previous;out.preVelocity=m.previousVelocity;
  for(unsigned i=0;i<rest.size();++i)for(unsigned d=0;d<3;++d){
   out.eventPosition[i][d]+=a*(path.a1[i][d]+a*path.a2[i][d]);out.preVelocity[i][d]+=2*a*path.a2[i][d]/m.h;
  }
  out.eventTension=control.sample(beginTime+a*m.h).tension;
  out.jacobian.resize(out.event->rows.size(),m.freeSize);
  for(unsigned k=0;k<out.event->rows.size();++k){auto row=out.event->rows[k];std::vector<Point>p;
   for(unsigned i:row.support)p.push_back(add(rest[i],out.eventPosition[i]));
   auto e=regrip_film_sphere::ClosestPrimitive::evaluate(p,center,radius);std::vector<Point>g(rest.size());
   for(unsigned j=0;j<9;++j)g[row.support[j/3]][j%3]+=e.gap.g[j];out.jacobian.row(k)=filmRow(m,g);
  }
  out.impact=manyRowImpact(filmMass(m),out.jacobian,m.pack(out.preVelocity),1e-10);
  bool uniqueBranch=true;
  for(int k=1;k<out.jacobian.rows();++k)if((out.jacobian.row(k).array()!=out.jacobian.row(0).array()).any())uniqueBranch=false;
  if(uniqueBranch){
   auto y=midpoint.mechanics.pack(middle.velocity);auto e=midpoint.mechanics.evaluate(y);
   Eigen::LDLT<Eigen::MatrixXd> factor(e.tangent);
   if(factor.info()!=Eigen::Success||factor.vectorD().minCoeff()<=0)throw std::runtime_error("surface event tangent not SPD");
   Eigen::MatrixXd V=factor.solve(filmMass(m));Eigen::MatrixXd Q=m.h*((a-a*a)*Eigen::MatrixXd::Identity(m.freeSize,m.freeSize)+a*a*V);
   Eigen::VectorXd pathRate=m.h*m.pack(out.preVelocity);double denominator=(out.jacobian.row(0)*pathRate)(0);
   if(denominator>=0)throw std::domain_error("nontransversal whole-surface event derivative");
   out.eventFractionIncomingDerivative=-(out.jacobian.row(0)*Q)/denominator;
   Eigen::VectorXd forceT=Eigen::VectorXd::Zero(m.freeSize);
   m.model.elements(middle.displacement,1,[&](const Element&el){if(el.kind!=2)return;for(unsigned j=0;j<3*el.ids.size();++j){unsigned ia=3*el.ids[j/3]+j%3;int i=m.index[ia];if(i>=0)forceT(i)+=m.weight[ia]*el.energy.g[j];}});
   Eigen::VectorXd Vtime=factor.solve(-m.h/2*forceT*out.tensionRate);
   double fractionTime=-(out.jacobian.row(0)*(m.h*a*a*Vtime))(0)/denominator;
   out.absoluteEventStartTimeDerivative=1+m.h*fractionTime;
  }
  out.postVelocity=m.expand(out.impact->state.velocity);
  double remainder=m.h*(1-a);
  if(remainder>0){auto result=freeEnd(out.eventPosition,out.postVelocity,remainder,beginTime+a*m.h);out.position=std::move(result.displacement);out.velocity=std::move(result.velocity);}
  else{out.position=out.eventPosition;out.velocity=out.postVelocity;}
 }
 out.minimumGap=std::numeric_limits<double>::infinity();
 for(auto triangle:triangles){std::vector<Point>p;for(unsigned i:triangle)p.push_back(add(rest[i],out.position[i]));
  out.minimumGap=std::min(out.minimumGap,regrip_film_sphere::ClosestPrimitive::evaluate(p,center,radius).gap.v);
 }
 if(out.minimumGap< -1e-10){
  if(deferSustained)out.remainderRequiresContact=true;
  else throw std::domain_error("whole-surface remainder requires sustained contact;state NOT committed");
 }
 return out;
}
}
