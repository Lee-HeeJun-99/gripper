#pragma once
#include "IsolatedContactTransfer.h"
namespace regrip_three_resume {
// Restricted symmetric endpoint-negative target detector. NOT a globally
// earliest whole nonlinear trajectory CCD:interior-only births can be missed.
// It rejects asymmetric,ambiguous,non-face or multi-branch outcomes explicitly.
inline ContactTransfer detectedContactTransfer(const SharedFilmSystem&s,
 const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time,double h){
 std::vector<ContactOwner>old;for(unsigned f=0;f<3;++f){auto r=s.selected(q,f);old.push_back({f,r.triangle,r.feature});if(r.feature!=6||(f&&r.triangle!=old[0].triangle))throw std::runtime_error("restricted detected transfer needs symmetric smooth-face initial owners");}
 auto trial=regrip_collocation::persistentRows(s.shared.M,2,q,v,time,h,[&](const auto&x,double t){return s.force(x,regrip_film_rail::ControlProfile::evaluate(t,.0001,.01,.02,.03,true).tension);},[&](const auto&x){return ownedGeometry(s,x,old);});
 unsigned target=0;for(unsigned f=0;f<3;++f){auto r=s.selected(trial.q,f);if(r.triangle==old[f].triangle||r.feature!=6||r.gap>=0)throw std::runtime_error("no signed new-face endpoint candidate;different event isolation required");if(f==0)target=r.triangle;else if(r.triangle!=target)throw std::runtime_error("asymmetric detected target;general row owner required");}
 return isolatedContactTransfer(s,q,v,time,h,old[0].triangle,target);
}
}
