#pragma once
#include "WholeSurfaceMidpoint.h"
#include "../film_sphere_contact/CandidateClosure.h"
#include "MidpointPosition.h"
namespace regrip_film_impact {
// Independent dissipative BE-position / mass-metric velocity-projection split.
// Position uses existing variational mechanics/candidate closure. Velocity is
// NOT assigned zero: a separate unilateral impulse QP supplies its change.
// Its kinetic projection loss is a numerical constraint-enforcement inventory,
// NOT a new physical collision atom,Coulomb heat or viscous damping.
inline WholeSurfaceStep sustainedSurface(const regrip_film_native::CoupledPlaneStep&m,
 const std::vector<std::array<unsigned,3>>&triangles,SurfacePoint center,double radius,
 double beginTime,const EventControl&control,bool midpointContact=false){
 using namespace regrip_film_native;using namespace regrip_film_sphere;
 auto initialRest=m.model.rest();
 for(auto t:triangles){std::vector<Point>p;for(unsigned i:t)p.push_back(add(initialRest[i],m.previous[i]));auto e=ClosestPrimitive::evaluate(p,center,radius);
  if(e.gap.v<=1e-10){double rate=0;for(unsigned a=0;a<9;++a)rate+=e.gap.g[a]*m.previousVelocity[t[a/3]][a%3];
   if(rate< -1e-10)throw std::domain_error("initial inward contact requires explicit zero-time impact;not a sustained correction");}
 }
 auto endControl=control.sample(beginTime+m.h);
 CoupledContactStep mechanics(m.model,m.mass,m.h,m.damping,endControl.tension,m.previous,m.previousVelocity,{},true,true);
 auto accepted=midpointContact?midpointPosition(m,triangles,center,radius,control.sample(beginTime+m.h/2).tension):CandidateClosure::solve(mechanics,center,radius,triangles,m.previousVelocity,true,nullptr,8,true);
 WholeSurfaceStep out;out.position=accepted.mechanical.displacement;out.velocity=accepted.mechanical.velocity;
 auto applied=control.sample(beginTime+m.h*(midpointContact?.5:1));
 out.sustained=true;out.forceTime=beginTime+m.h*(midpointContact?.5:1);out.tension=applied.tension;out.tensionRate=applied.rate;
 out.positionResidual=accepted.mechanical.residual;out.constraintImpulse=accepted.mechanical.lambda.sum();
 std::vector<Eigen::RowVectorXd>rows;auto rest=m.model.rest();out.minimumGap=std::numeric_limits<double>::infinity();
 auto inventory=[&](unsigned id,const auto&e,int stage,double impulse){
  std::vector<Point>g(rest.size());for(unsigned a=0;a<9;++a)g[triangles[id][a/3]][a%3]+=e.gap.g[a];
  Point point{e.point[0].v,e.point[1].v,e.point[2].v};auto delta=sub(point,center);double length=std::sqrt(dot(delta,delta));
  if(!(length>0))throw std::domain_error("undefined sustained normal");
  std::vector<Point>p;for(unsigned i:triangles[id])p.push_back(add(rest[i],out.position[i]));
  auto ab=sub(p[1],p[0]),ac=sub(p[2],p[0]),ap=sub(point,p[0]);double aa=dot(ab,ab),bb=dot(ab,ac),cc=dot(ac,ac),den=aa*cc-bb*bb;
  if(!(den>0))throw std::domain_error("degenerate sustained barycentric basis");
  double b=(cc*dot(ab,ap)-bb*dot(ac,ap))/den,c=(aa*dot(ac,ap)-bb*dot(ab,ap))/den;
  ConstraintInventoryRow row;row.triangle=id;row.feature=e.feature;row.stage=stage;row.gap=e.gap.v;row.normal=scale(delta,1/length);row.barycentric={1-b-c,b,c};row.impulse=impulse;row.jacobian=filmRow(m,g);
  row.normalBefore=(row.jacobian*m.pack(m.previousVelocity))(0);row.normalAfter=(row.jacobian*m.pack(out.velocity))(0);return row;
 };
 for(unsigned k=0;k<accepted.rows.size();++k){int id=accepted.triangle[k];if(id<0)throw std::runtime_error("sustained inventory has unowned predictor row");
  std::vector<Point>p;for(unsigned i:triangles[id])p.push_back(add(rest[i],out.position[i]));auto e=ClosestPrimitive::evaluate(p,center,radius);
  out.constraintRows.push_back(inventory(id,e,1,accepted.mechanical.lambda(k)));
 }
 std::vector<ConstraintInventoryRow>projectionRows;
 for(unsigned id=0;id<triangles.size();++id){auto triangle=triangles[id];std::vector<Point>p;for(unsigned i:triangle)p.push_back(add(rest[i],out.position[i]));auto e=ClosestPrimitive::evaluate(p,center,radius);
  out.minimumGap=std::min(out.minimumGap,e.gap.v);
  if(e.gap.v<=1e-10){auto row=inventory(id,e,2,0);row.normalBefore=row.normalAfter;rows.push_back(row.jacobian);projectionRows.push_back(std::move(row));}
 }
 if(!rows.empty()){
  Eigen::MatrixXd J(rows.size(),m.freeSize);for(unsigned i=0;i<rows.size();++i)J.row(i)=rows[i];
  auto projected=manyRowImpact(filmMass(m),J,m.pack(out.velocity),1e-10);
  out.projectionImpulse=projected.state.impulse.sum();out.projectionLoss=projected.state.energyLoss;
  out.velocity=m.expand(projected.state.velocity);
  for(unsigned k=0;k<projectionRows.size();++k){auto&row=projectionRows[k];row.impulse=projected.state.impulse(k);row.normalAfter=projected.state.normalVelocity(k);out.constraintRows.push_back(std::move(row));}
 }
 if(out.minimumGap< -1e-10)throw std::runtime_error("sustained endpoint gap gate");
 return out;
}
inline WholeSurfaceStep wholeSurfaceContactStep(const regrip_film_native::CoupledPlaneStep&m,
 const std::vector<std::array<unsigned,3>>&triangles,SurfacePoint center,double radius,
 double beginTime,const EventControl&control,bool midpointContact=false){
 using namespace regrip_film_native;auto rest=m.model.rest();double initialGap=std::numeric_limits<double>::infinity();
 for(auto t:triangles){std::vector<Point>p;for(unsigned i:t)p.push_back(add(rest[i],m.previous[i]));initialGap=std::min(initialGap,regrip_film_sphere::ClosestPrimitive::evaluate(p,center,radius).gap.v);}
 if(initialGap< -1e-10)throw std::domain_error("initial surface penetration outside declared gap gate");
 if(initialGap<=1e-10)return sustainedSurface(m,triangles,center,radius,beginTime,control,midpointContact);
 auto out=wholeSurfaceMidpoint(m,triangles,center,radius,beginTime,control,true);
 if(out.remainderRequiresContact){double elapsed=m.h*out.event->fraction,remaining=m.h-elapsed;
  CoupledPlaneStep after(m.model,m.mass,remaining,m.damping,control.sample(beginTime+elapsed).tension,out.eventPosition,out.postVelocity,std::vector<Point>(rest.size()),0);
  auto contact=sustainedSurface(after,triangles,center,radius,beginTime+elapsed,control,midpointContact);
  out.position=std::move(contact.position);out.velocity=std::move(contact.velocity);out.minimumGap=contact.minimumGap;out.sustained=true;
  out.constraintImpulse=contact.constraintImpulse;out.projectionImpulse=contact.projectionImpulse;out.projectionLoss=contact.projectionLoss;out.positionResidual=contact.positionResidual;
  out.constraintRows=std::move(contact.constraintRows);
  out.forceTime=contact.forceTime;out.tension=contact.tension;out.tensionRate=contact.tensionRate;
  out.remainderRequiresContact=false;
 }
 return out;
}
}
