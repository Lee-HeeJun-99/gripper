#pragma once
#include "ContactRows.h"
#include "../film_rail_tendon/ControlProfile.h"
namespace regrip_three_resume {
struct ContactTransfer {
 regrip_collocation::RowsResult pre,post;
 regrip_film_impact::ManyRowImpact impact;
 std::vector<ContactOwner>old,all,active;
 regrip_collocation::RowGeometry eventGeometry;
 double fractionTime=0,bracketWidth=0,minimumGap=0;
 unsigned rootEvaluations=0;
 Eigen::Vector3d rootImpulse=Eigen::Vector3d::Zero(),rootMoment=Eigen::Vector3d::Zero();
 double linearBalance=0,angularBalance=0;
};
// Explicitly isolated117 birth,not general CCD or full active-set dynamics.
// Reuses qualified Lobatto and ManyRowImpact;no state/force projection.
inline ContactTransfer isolatedContactTransfer(const SharedFilmSystem&s,
 const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time,double h){
 ContactTransfer out;std::vector<ContactOwner>newborn;for(unsigned f=0;f<3;++f){auto row=s.selected(q,f);out.old.push_back({f,row.triangle,row.feature});auto other=s.shared.films[f].geometry(s.local(q,f),117);newborn.push_back({f,117,other.feature});if(row.triangle!=124||row.feature!=6||other.feature!=6)throw std::runtime_error("isolated124->117 fixture owner differs");}
 auto force=[&](const auto&x,double t){return s.force(x,regrip_film_rail::ControlProfile::evaluate(t,.0001,.01,.02,.03,true).tension);};auto geo=[&](const auto&x){return ownedGeometry(s,x,out.old);};auto advance=[&](double interval){return regrip_collocation::persistentRows(s.shared.M,2,q,v,time,interval,force,geo);};
 auto initialNew=ownedGeometry(s,q,newborn);auto whole=advance(h);double right=ownedGeometry(s,whole.q,newborn).gap.minCoeff();if(initialNew.gap.minCoeff()<=0||right>=0)throw std::runtime_error("identified117 birth bracket not signed");double lo=0,hi=h;out.rootEvaluations=1;
 for(unsigned k=0;k<48&&hi-lo>1e-13;++k){double mid=(lo+hi)/2;auto r=advance(mid);++out.rootEvaluations;double g=ownedGeometry(s,r.q,newborn).gap.minCoeff();if(g>0)lo=mid;else hi=mid;}
 out.fractionTime=(lo+hi)/2;out.bracketWidth=hi-lo;out.pre=advance(out.fractionTime);++out.rootEvaluations;auto ng=ownedGeometry(s,out.pre.q,newborn);if(ng.gap.cwiseAbs().maxCoeff()>1e-10||s.clearance(out.pre.q)<-1e-10)throw std::runtime_error("simultaneous/root whole clearance rejected");
 out.all=out.old;out.all.insert(out.all.end(),newborn.begin(),newborn.end());out.eventGeometry=ownedGeometry(s,out.pre.q,out.all);out.impact=regrip_film_impact::manyRowImpact(s.shared.M,out.eventGeometry.J,out.pre.v,1e-10);Eigen::VectorXd vn=out.eventGeometry.J*out.impact.state.velocity;for(unsigned k=0;k<out.all.size();++k)if(std::abs(vn(k))<=1e-10)out.active.push_back(out.all[k]);
 out.post=regrip_collocation::persistentRows(s.shared.M,2,out.pre.q,out.impact.state.velocity,time+out.fractionTime,h-out.fractionTime,force,[&](const auto&x){return ownedGeometry(s,x,out.active);});out.minimumGap=s.clearance(out.post.q);for(const auto&stage:out.pre.stages)out.minimumGap=std::min(out.minimumGap,s.clearance(stage.q));for(const auto&stage:out.post.stages)out.minimumGap=std::min(out.minimumGap,s.clearance(stage.q));if(out.minimumGap< -1e-10)throw std::runtime_error("transfer whole-stage gap fails");
 // Unreduced nodal impulse and actual projected mass recover fixed-root
 // impulse inventory. This is NOT root-reaction work or a fitted balance.
 const unsigned nf=s.shared.nf,nb=3*nf;Eigen::Vector3d total=Eigen::Vector3d::Zero(),angular=total;
 for(unsigned f=0;f<3;++f){const auto&system=s.shared.films[f];auto local=s.local(out.pre.q,f);auto rest=system.film.model.rest();auto before=system.film.expand(out.pre.v.segment(f*nf,nf)),after=system.film.expand(out.impact.state.velocity.segment(f*nf,nf));std::vector<Eigen::Vector3d>nodal(rest.size(),Eigen::Vector3d::Zero());for(unsigned k=0;k<out.all.size();++k)if(out.all[k].finger==f){auto e=system.primitive(local,out.all[k].triangle);auto support=system.triangles[out.all[k].triangle];for(unsigned a=0;a<9;++a)nodal[support[a/3]](a%3)+=out.impact.state.impulse(k)*e.gap.g[a];}
  for(unsigned i=0;i<rest.size();++i){Eigen::Vector3d dp=s.layout.mount[f].R*(system.film.mass[i]*(vector(after[i])-vector(before[i]))),reaction=dp-s.layout.mount[f].R*nodal[i],x=s.layout.world(f,add(rest[i],local.q[i]));total+=dp;angular+=x.cross(dp);out.rootImpulse+=reaction;out.rootMoment+=x.cross(reaction);}}
Eigen::Vector3d dp=s.shared.M(nb,nb)*(out.impact.state.velocity.segment<3>(nb)-out.pre.v.segment<3>(nb));total+=dp;angular+=out.pre.q.segment<3>(nb).cross(dp)+s.shared.M(nb+3,nb+3)*(out.impact.state.velocity.tail<3>()-out.pre.v.tail<3>());out.linearBalance=(total-out.rootImpulse).norm();out.angularBalance=(angular-out.rootMoment).norm();if(out.linearBalance>1e-17||out.angularBalance>1e-16)throw std::runtime_error("transfer world momentum/root impulse balance failed");return out;
}
}
