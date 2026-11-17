#pragma once
#include "BlockFree.h"
#include "../film_impact/ManyRowImpact.h"
namespace regrip_three_event {
struct BirthRow {unsigned finger,triangle,feature;double gap,normalBefore,normalAfter;};
struct BracketedBirth {
 double time,lowerTime,gap,momentumResidual;
 FreeState before;
 regrip_film_impact::ManyRowImpact impact;
 Eigen::MatrixXd J;
 std::vector<BirthRow> rows;
};
// Strict EXTERNALLY ISOLATED endpoint-family bracket. This does not certify
// globally earliest nonlinear event or swept CCD. Both q and v are reintegrated
// from the original separated state at each partial midpoint interval.
inline BracketedBirth bracketedBirth(const SharedFilmSystem&s,const Eigen::VectorXd&q,
 const Eigen::VectorXd&v,double start,double lo,double hi,const EventControl&control,
 double damping=2,double timeTolerance=1e-13,double gapTolerance=1e-12){
 if(!(lo>0&&hi>lo&&hi<=.001&&timeTolerance>0&&gapTolerance>0)||s.clearance(q)<=0)
  throw std::invalid_argument("strict separated three-film externally isolated birth bracket required");
 auto left=freeMidpoint(s,q,v,start,lo,control,damping),right=freeMidpoint(s,q,v,start,hi,control,damping);
 double gl=s.clearance(left.q),gr=s.clearance(right.q);
 if(!(gl>0&&gr<=0))throw std::domain_error("endpoint-family birth bracket is not signed;no impact accepted");
 for(unsigned k=0;k<80&&hi-lo>timeTolerance;++k){double mid=(lo+hi)/2;auto state=freeMidpoint(s,q,v,start,mid,control,damping);double g=s.clearance(state.q);if(g>0){lo=mid;left=std::move(state);gl=g;}else{hi=mid;right=std::move(state);gr=g;}}
 right=freeMidpoint(s,q,v,start,hi,control,damping,true);gr=s.clearance(right.q);
 if(hi-lo>timeTolerance||std::abs(gr)>gapTolerance)throw std::runtime_error("three-film birth root not resolved;no state commit");
 const unsigned nf=s.shared.nf,n=q.size(),body=3*nf;std::vector<Eigen::RowVectorXd>gradients;std::vector<BirthRow>rows;
 for(unsigned f=0;f<3;++f){auto state=s.local(right.q,f);const auto&film=s.shared.films[f];
  for(unsigned t=0;t<film.triangles.size();++t){double gap=film.primitive(state,t).gap.v;if(std::abs(gap)>gapTolerance)continue;
   auto row=film.geometry(state,t);Eigen::RowVectorXd J=Eigen::RowVectorXd::Zero(n);J.segment(f*nf,nf)=row.gradient.head(nf).transpose();J.segment<3>(body)=row.gradient.segment<3>(nf).transpose()*s.layout.mount[f].R.transpose();
   if(row.gradient.tail<3>().norm()!=0)throw std::domain_error("sphere normal must have zero angular Jacobian");
   double rate=J.dot(right.positionFamilyRate),vn=J.dot(right.v);
   if(rate>=0||vn>=0)continue;
   if(gap>0&&gap/(-rate)>timeTolerance)continue;
   // Shared-edge duplicates are retained as real rows;rank and multiplier
   // nonuniqueness are reported rather than adding artificial compliance.
   gradients.push_back(J);rows.push_back({f,t,row.feature,gap,vn,0});
  }
 }
 if(rows.empty())throw std::domain_error("resolved event has no physically entering shared rows");
 Eigen::MatrixXd J(rows.size(),n);for(unsigned i=0;i<rows.size();++i)J.row(i)=gradients[i];
 auto impact=regrip_film_impact::manyRowImpact(s.shared.M,J,right.v,1e-10);
 if(impact.state.momentumResidual>1e-17)throw std::runtime_error("three-film impact momentum gate1e-17 Ns");
 for(unsigned i=0;i<rows.size();++i)rows[i].normalAfter=impact.state.normalVelocity(i);
 return {start+hi,start+lo,gr,impact.state.momentumResidual,std::move(right),std::move(impact),std::move(J),std::move(rows)};
}
}
