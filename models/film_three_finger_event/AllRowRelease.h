#pragma once
#include "BlockFree.h"
namespace regrip_three_event {
struct AllRowRelease {FreeState state;Eigen::VectorXd bilateralReaction,freeNormalAcceleration;double endpointGap;};
// Narrow ALL-row zero-force release branch. No partial active set,impulse,
// position projection,or continuation across a detected re-impact is claimed.
// Caller must separately certify the released interval's surface path.
inline AllRowRelease allRowRelease(const SharedFilmSystem&s,const Eigen::VectorXd&q,
 const Eigen::VectorXd&v,double time,double h,const EventControl&control,double damping=2){
 auto g=s.geometry(q);if(g.gap.cwiseAbs().maxCoeff()>1e-10||(g.J*v).cwiseAbs().maxCoeff()>1e-10)throw std::domain_error("all-row release requires initially touching tangent state");Eigen::LLT<Eigen::MatrixXd>mass(s.shared.M);if(mass.info()!=Eigen::Success)throw std::domain_error("release mass not SPD");auto applied=control.sample(time);auto force=s.force(q,applied.tension);Eigen::VectorXd acceleration=mass.solve(force.value-damping*s.shared.M*v),normal=g.J*acceleration;for(int i=0;i<normal.size();++i)normal(i)+=v.dot(g.H[i]*v);Eigen::MatrixXd W=g.J*mass.solve(g.J.transpose());Eigen::FullPivLU<Eigen::MatrixXd>factor(W);if(!factor.isInvertible())throw std::domain_error("release branch needs independent rows;no regularization");Eigen::VectorXd reaction=factor.solve(-normal);
 if(reaction.maxCoeff()>=0||normal.minCoeff()<=0)throw std::domain_error("not an all-row separating acceleration branch;partial active set required");
 auto after=freeMidpoint(s,q,v,time,h,control,damping);double gap=s.clearance(after.q);if(gap< -1e-10||(s.geometry(after.q).J*after.v).minCoeff()< -1e-10)throw std::domain_error("release endpoint re-contact/closure;no state commit");return {std::move(after),std::move(reaction),std::move(normal),gap};
}
}
