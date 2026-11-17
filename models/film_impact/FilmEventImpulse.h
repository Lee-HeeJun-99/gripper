#pragma once
#include "FilmProjection.h"
#include "../film_sphere_contact/ClosestPrimitive.h"
namespace regrip_film_impact {
struct FilmEventImpulse {
 ImpactResult reduced;
 std::vector<regrip_film_rail::Point> postVelocity,nodalImpulse;
 Eigen::MatrixXd jacobian;
};
// Input MUST be the externally resolved state at ONE event time. No stored
// endpoint interpolation is silently substituted. Geometry is checked at that
// supplied state; caller owns birth-time accuracy and simultaneous-row closure.
inline FilmEventImpulse filmEventImpulse(const regrip_film_native::CoupledPlaneStep&mechanics,
 const std::vector<regrip_film_rail::Point>&qEvent,
 const std::vector<regrip_film_rail::Point>&vEvent,
 const std::vector<std::vector<unsigned>>&supports,
 regrip_film_rail::Point center,double radius,double gapTolerance,double velocityTolerance){
 using namespace regrip_film_rail;
 if(qEvent.size()!=mechanics.model.size()||vEvent.size()!=qEvent.size()||supports.empty()||supports.size()>16||
    !std::isfinite(radius)||radius<=0||!std::isfinite(gapTolerance)||gapTolerance<0)
  throw std::invalid_argument("film event dimensions/radius/gap tolerance");
 auto rest=mechanics.model.rest();std::vector<std::vector<Point>>gradients;
 Eigen::MatrixXd J(supports.size(),mechanics.freeSize);
 for(unsigned k=0;k<supports.size();++k){std::vector<Point>p;
  for(unsigned node:supports[k])p.push_back(add(rest.at(node),qEvent.at(node)));
  auto e=regrip_film_sphere::ClosestPrimitive::evaluate(p,center,radius);
  if(std::abs(e.gap.v)>gapTolerance)throw std::domain_error("impact row is not at supplied event geometry");
  std::vector<Point>g(rest.size());for(unsigned a=0;a<3*p.size();++a)g[supports[k][a/3]][a%3]+=e.gap.g[a];
  J.row(k)=filmRow(mechanics,g);gradients.push_back(std::move(g));
 }
 Eigen::VectorXd before=mechanics.pack(vEvent);auto expanded=mechanics.expand(before);
 // A velocity outside the declared root mapping must not be silently projected.
 for(unsigned i=0;i<expanded.size();++i)for(unsigned d=0;d<3;++d)
  if(expanded[i][d]!=vEvent[i][d])throw std::domain_error("event velocity violates exact root mapping");
 FilmEventImpulse out;out.reduced=solve(filmMass(mechanics),J,before,0,velocityTolerance,0);
 out.jacobian=J;out.postVelocity=mechanics.expand(out.reduced.velocity);out.nodalImpulse.resize(rest.size());
 for(unsigned k=0;k<supports.size();++k)for(unsigned i=0;i<rest.size();++i)
  out.nodalImpulse[i]=add(out.nodalImpulse[i],scale(gradients[k][i],out.reduced.impulse(k)));
 return out;
}
}
