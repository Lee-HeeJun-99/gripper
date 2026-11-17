#pragma once
#include "ProjectedImpact.h"
#include "RestartHistory.h"
#include <optional>
namespace regrip_film_impact {
struct PlaneFlight {
 Eigen::Vector3d position,velocity;
 std::optional<double> fraction;
 double impulse=0,loss=0,momentumResidual=0,preNormal=0,postNormal=0;
};
// Exact free-flight + instantaneous plane impact + exact remaining free-flight.
// No forces, acceleration, constraints or film deformation are represented here.
inline PlaneFlight planeFlight(Eigen::Vector3d x,Eigen::Vector3d v,
 const Eigen::Vector3d&normal,double offset,double mass,double h,double restitution) {
 if(!x.allFinite()||!v.allFinite()||!normal.allFinite()||
    std::abs(normal.squaredNorm()-1)>1e-14||!std::isfinite(offset)||
    !std::isfinite(mass)||mass<=0||!std::isfinite(h)||h<=0)
  throw std::invalid_argument("ballistic plane inputs");
 double gap=normal.dot(x)-offset,rate=normal.dot(v);
 if(gap<0)throw std::domain_error("initial plane penetration;not an impact correction");
 PlaneFlight out;out.position=x+h*v;out.velocity=v;
 if(rate>=0||gap+h*rate>0)return out;
 double tau=-gap/rate;
 auto r=solve(mass*Eigen::Matrix3d::Identity(),normal.transpose(),v,restitution,1e-12,1e-12);
 Eigen::Vector3d event=x+tau*v;
 out.position=event+(h-tau)*r.velocity;out.velocity=r.velocity;out.fraction=tau/h;
 out.impulse=r.impulse(0);out.loss=r.energyLoss;out.momentumResidual=r.momentumResidual;
 out.preNormal=rate;out.postNormal=normal.dot(out.velocity);return out;
}
}
