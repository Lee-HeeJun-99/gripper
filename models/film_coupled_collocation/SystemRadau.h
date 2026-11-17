#pragma once
#include "SingleRowRadau.h"
#include "../film_coupled_contact/CoupledSphere.h"
namespace regrip_coupled {
struct RadauAdvance {Result result;regrip_collocation::RadauResult stages;};
// One already-touching,feature-preserving persistent branch. No impact,
// candidate-birth or release is silently substituted with this bilateral DAE.
inline RadauAdvance singleRowRadauStep(const System&s,double time,const EventControl&control,bool lobatto=false){
 unsigned id=0;double gap=std::numeric_limits<double>::infinity();for(unsigned i=0;i<s.triangles.size();++i)if(s.primitive(s.before,i).gap.v<gap){gap=s.primitive(s.before,i).gap.v;id=i;}
 unsigned feature=s.geometry(s.before,id).feature;unsigned evaluations=0;
 auto state=[&](const Eigen::VectorXd&x){State z=s.before;z.q=s.film.expand(x.head(s.nf));z.body.center=x.segment<3>(s.nf);return z;};
 auto geometry=[&](const Eigen::VectorXd&x){auto row=s.geometry(state(x),id);if(row.feature!=feature)throw std::domain_error("single-row Radau feature transition;needs another branch");return regrip_collocation::Geometry{row.gap,row.gradient,row.hessian};};
 auto force=[&](const Eigen::VectorXd&x,double t){++evaluations;auto z=state(x);regrip_collocation::Force f{Eigen::VectorXd::Zero(s.n),Eigen::MatrixXd::Zero(s.n,s.n)};f.value.segment<3>(s.nf)=s.before.body.force;
  s.film.model.elements(z.q,control.sample(t).tension,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=s.film.index[ga];if(i<0)continue;f.value(i)-=s.film.weight[ga]*e.energy.g[a];for(unsigned z=0;z<3*e.ids.size();++z){unsigned gz=3*e.ids[z/3]+z%3;int k=s.film.index[gz];if(k>=0)f.negativeTangent(i,k)+=s.film.weight[ga]*s.film.weight[gz]*e.energy.h[N*a+z];}}});return f;};
 Eigen::VectorXd q=Eigen::VectorXd::Zero(s.n);q.head(s.nf)=s.film.pack(s.before.q);q.segment<3>(s.nf)=s.before.body.center;
 auto collocation=regrip_collocation::singleRowRadau(s.M,s.film.damping,q,s.pack(s.before),time,s.film.h,force,geometry,false,lobatto);
 Result out;out.state=state(collocation.q);s.velocity(out.state,collocation.v);Eigen::Vector3d angle=collocation.q.tail<3>();if(angle.norm()>0)out.state.body.orientation=Eigen::Quaterniond(Eigen::AngleAxisd(angle.norm(),angle/angle.norm()))*s.before.body.orientation;
 out.minimumGap=s.clearance(out.state);if(out.minimumGap< -1e-10)throw std::domain_error("Radau whole-surface endpoint gap;new rows need coupled active-set solve");
 out.residual=collocation.momentumResidual;out.sustained=true;out.forceTime=time+s.film.h;out.tension=control.sample(out.forceTime).tension;out.evaluations=evaluations;out.constraintImpulse.resize(lobatto?3:2);
 if(lobatto){out.contactRows.push_back(s.geometry(s.before,id));out.contactTimes.push_back(time);out.constraintImpulse(0)=s.film.h/6*collocation.initialForce;}
 for(unsigned k=0;k<2;++k){out.contactRows.push_back(s.geometry(state(collocation.stages[k].q),id));out.contactTimes.push_back(collocation.stages[k].time);out.constraintImpulse(k+unsigned(lobatto))=s.film.h*(lobatto?(k==0?2./3:1./6):(k==0?.75:.25))*collocation.stages[k].force;}
 return {std::move(out),std::move(collocation)};
}
}
