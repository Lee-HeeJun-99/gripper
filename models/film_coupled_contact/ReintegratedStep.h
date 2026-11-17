#pragma once
#include "ReintegratedBirth.h"
namespace regrip_coupled {
// ISOLATED BRACKET PROTOTYPE. The dense numerical path supplies a candidate;
// a strict endpoint-family entering bracket and matching features are required.
// Matching does NOT prove global earliest CCD of the endpoint family.
inline Result reintegratedStep(const System&system,double time,const EventControl&control){
 if(system.clearance(system.before)<=1e-10)return system.advance(time,control);
 auto out=system.smooth(time,control,false);
 auto candidate=earliestSurfaceEvent(system.relativePath(out.state),system.triangles,{0,0,0},system.radius);
 if(!candidate){if(out.minimumGap< -1e-10)throw std::runtime_error("reintegrated prototype missed endpoint clearance");return out;}
 auto root=resolveCoupledBirthBracket(system,time,control);
 Eigen::VectorXd physicalNormal=root.J*system.pack(root.state);
 if(physicalNormal.size()==0||!physicalNormal.allFinite()||physicalNormal.maxCoeff()>=-1e-10)throw std::domain_error("endpoint-family prototype lacks strictly approaching physical event velocity;no artificial impulse");
 for(const auto&row:root.rows){bool match=false;for(const auto&r:candidate->rows)if(r.triangle==row.triangle&&r.feature==row.feature)match=true;if(!match)throw std::runtime_error("endpoint family differs from isolated dense candidate;global earliest proof missing");}
 out.event=SurfaceEvent{root.time/system.film.h,0,root.evaluations,{}};
 for(unsigned k=0;k<root.rows.size();++k){const auto&row=root.rows[k];auto support=system.triangles[row.triangle];auto rest=system.film.model.rest();std::vector<Point>p;for(unsigned id:support)p.push_back(sub(add(rest[id],root.state.q[id]),point(root.state.body.center)));
  auto e=system.primitive(root.state,row.triangle);Point x{e.point[0].v,e.point[1].v,e.point[2].v};auto ab=sub(p[1],p[0]),ac=sub(p[2],p[0]),ap=sub(x,p[0]);double aa=dot(ab,ab),bb=dot(ab,ac),cc=dot(ac,ac),den=aa*cc-bb*bb;if(!(den>0))throw std::runtime_error("reintegrated owner degenerate barycentric support");double b=(cc*dot(ab,ap)-bb*dot(ac,ap))/den,c=(aa*dot(ac,ap)-bb*dot(ab,ap))/den;
  out.event->rows.push_back({k,row.triangle,row.feature,row.gap,system.film.h*root.familyRates(k),support,{1-b-c,b,c},point(row.normal)});
 }
 out.eventJ=root.J;out.eventIncomingSensitivity=root.timeIncoming/system.film.h;out.absoluteEventStartSensitivity=root.absoluteStartSensitivity;
 out.eventState=root.state;out.preImpact=root.state;out.impact=manyRowImpact(system.M,root.J,system.pack(root.state),1e-10);out.postImpact=root.state;system.velocity(out.postImpact,out.impact->state.velocity);out.state=out.postImpact;
 out.forceTime=time+root.time/2;out.tension=control.sample(out.forceTime).tension;out.evaluations+=root.mechanicalEvaluations;out.acceptedReuses+=root.acceptedReuses;
 double remaining=system.film.h-root.time;
 if(remaining>0){CoupledPlaneStep m(system.film.model,system.film.mass,remaining,system.film.damping,control.sample(time+root.time).tension,out.postImpact.q,out.postImpact.v,std::vector<Point>(out.postImpact.q.size()),0);System remainder(m,system.triangles,out.postImpact.body,system.radius,system.strictNewton,system.reuseAccepted,system.midpointContact,system.absoluteNewtonResidual,system.contactSolveGap);auto contact=remainder.smooth(time+root.time,control,true);out.state=contact.state;out.contactRows=contact.contactRows;out.constraintImpulse=contact.constraintImpulse;out.residual=contact.residual;out.sustained=contact.sustained;out.forceTime=contact.forceTime;out.tension=contact.tension;out.evaluations+=contact.evaluations;out.acceptedReuses+=contact.acceptedReuses;
  std::vector<Row>rows;for(unsigned id=0;id<system.triangles.size();++id)if(system.primitive(out.state,id).gap.v<=1e-10)rows.push_back(system.geometry(out.state,id));
  if(!rows.empty()){Eigen::MatrixXd J(rows.size(),system.n);for(unsigned i=0;i<rows.size();++i)J.row(i)=rows[i].gradient;auto projection=manyRowImpact(system.M,J,system.pack(out.state),1e-10);system.velocity(out.state,projection.state.velocity);out.projectionLoss=projection.state.energyLoss;out.projectionDefect=projection.momentumEnergyDefect;out.projection=projection;out.projectionRows=std::move(rows);}
 }
 out.minimumGap=system.clearance(out.state);if(out.minimumGap< -1e-10)throw std::runtime_error("reintegrated accepted whole endpoint clearance gate");return out;
}
}
