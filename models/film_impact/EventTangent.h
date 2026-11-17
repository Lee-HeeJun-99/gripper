#pragma once
#include "BracketedFilmBirth.h"
namespace regrip_film_impact {
// Smooth single-active-row derivative through numerical birth + plastic impact.
// Initial q0/mass fixed; columns are reduced incoming velocities. No derivative
// is asserted across contact-feature changes, grazing or activation changes.
inline Eigen::MatrixXd singleEventVelocityTangent(
 const regrip_film_native::CoupledPlaneStep&mechanics,const BracketedFilmBirth&birth,
 unsigned node,regrip_film_rail::Point center,double radius){
 using namespace regrip_film_native;
 auto impact=filmEventImpulse(mechanics,birth.position,birth.velocity,{{node}},center,radius,1e-10,1e-12);
 double p=impact.reduced.impulse(0);if(!(p>0))throw std::domain_error("single-event tangent requires strict active impulse");
 auto position=add(mechanics.model.rest().at(node),birth.position.at(node));
 auto e=regrip_film_sphere::ClosestPrimitive::evaluate({position},center,radius);
 Eigen::MatrixXd K=Eigen::MatrixXd::Zero(mechanics.freeSize,mechanics.freeSize);
 for(unsigned a=0;a<3;++a)for(unsigned b=0;b<3;++b){unsigned ia=3*node+a,ib=3*node+b;
  if(mechanics.index[ia]>=0&&mechanics.index[ib]>=0)
   K(mechanics.index[ia],mechanics.index[ib])+=mechanics.weight[ia]*mechanics.weight[ib]*e.gap.h[N*a+b];
 }
 Eigen::MatrixXd dC=K*birth.positionIncomingDerivative;
 Eigen::LLT<Eigen::MatrixXd>factor(filmMass(mechanics));
 Eigen::VectorXd inverseC=factor.solve(impact.jacobian.transpose()),pre=mechanics.pack(birth.velocity);
 double W=(impact.jacobian*inverseC)(0);if(!(W>0))throw std::domain_error("singular effective impact mass");
 Eigen::MatrixXd tangent=birth.velocityIncomingDerivative;
 for(unsigned j=0;j<mechanics.freeSize;++j){
  double dW=2*dC.col(j).dot(inverseC);
  double dp=-(dW*p+dC.col(j).dot(pre)+(impact.jacobian*birth.velocityIncomingDerivative.col(j))(0))/W;
  tangent.col(j)+=factor.solve(dC.col(j)*p+impact.jacobian.transpose()*dp);
 }
 return tangent;
}
}
