#pragma once
#include "../film_coupled_contact/ReintegratedStep.h"
#include "../film_coupled_collocation/SystemRadau.h"
namespace regrip_coupled {
struct CombinedAdvance {Result result;std::optional<RadauAdvance>persistent;double persistentStart=0;};
// Integration PROTOTYPE,not global earliest CCD or release. To preserve the
// validated event-atom code WITHOUT rewriting it,the separated branch also
// evaluates the old midpoint remainder as an explicit baseline validator.
// That unused state/force/projection is NOT applied. Its REAL evaluations are
// counted. Removal of this redundant computation needs equivalence evidence.
inline CombinedAdvance combinedStep(const System&s,double time,const EventControl&control,bool sparseStage=false){
 if(s.clearance(s.before)<=1e-10){auto contact=singleRowRadauStep(s,time,control,true,sparseStage);return {contact.result,std::move(contact),time};}
 auto event=reintegratedStep(s,time,control);
 if(!event.event)return {std::move(event),std::nullopt,0};
 double birth=time+s.film.h*event.event->fraction,remaining=s.film.h*(1-event.event->fraction);
 if(!(remaining>0))return {std::move(event),std::nullopt,0};
 CoupledPlaneStep film(s.film.model,s.film.mass,remaining,s.film.damping,control.sample(birth).tension,event.postImpact.q,event.postImpact.v,std::vector<Point>(event.postImpact.q.size()),0);
 System remainder(film,s.triangles,event.postImpact.body,s.radius,s.strictNewton,s.reuseAccepted,true,s.absoluteNewtonResidual,s.contactSolveGap);
 auto contact=singleRowRadauStep(remainder,birth,control,true,sparseStage);
 event.state=contact.result.state;event.contactRows=contact.result.contactRows;event.contactTimes=contact.result.contactTimes;event.constraintImpulse=contact.result.constraintImpulse;
 event.projection.reset();event.projectionRows.clear();event.projectionLoss=0;event.projectionDefect=0; // No endpoint projection in the new accepted path.
 event.minimumGap=contact.result.minimumGap;event.residual=contact.result.residual;event.sustained=true;event.forceTime=contact.result.forceTime;event.tension=contact.result.tension;
 event.evaluations+=contact.result.evaluations;event.acceptedReuses+=contact.result.acceptedReuses;
 return {std::move(event),std::move(contact),birth};
}
}
