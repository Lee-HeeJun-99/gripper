#pragma once
#include <Eigen/Dense>
#include <optional>
#include <stdexcept>
#include <cmath>
namespace regrip_film_impact {
struct Birth {double fraction;Eigen::Vector3d normal;};
// Exact for an explicitly AFFINE relative point trajectory, not a deforming
// triangle CCD or dense output of BDF2. Both endpoints may be separated.
inline std::optional<Birth> affineSphereBirth(const Eigen::Vector3d&relativeStart,
 const Eigen::Vector3d&relativeIncrement,double radius) {
 if(!relativeStart.allFinite()||!relativeIncrement.allFinite()||!std::isfinite(radius)||radius<=0)
  throw std::invalid_argument("sphere birth input");
 double a=relativeIncrement.squaredNorm(),c=relativeStart.squaredNorm()-radius*radius;
 if(c<0)throw std::domain_error("initial overlap is not a contact birth");
 if(c==0){double slope=relativeStart.dot(relativeIncrement);
  if(slope==0)throw std::domain_error("grazing/nontransversal initial contact");
  if(slope<0)return Birth{0,relativeStart/radius};return std::nullopt;}
 if(a==0)return std::nullopt;
 double b=2*relativeStart.dot(relativeIncrement),discriminant=b*b-4*a*c;
 if(discriminant<0)return std::nullopt;
 if(discriminant==0){double alpha=-b/(2*a);if(alpha>=0&&alpha<=1)
   throw std::domain_error("grazing event has no unique implicit birth derivative");return std::nullopt;}
 double q=-.5*(b+std::copysign(std::sqrt(discriminant),b));
 double alpha=std::min(q/a,c/q);
 if(alpha<0||alpha>1)return std::nullopt;
 Eigen::Vector3d point=relativeStart+alpha*relativeIncrement;
 if(point.dot(relativeIncrement)>=0)throw std::domain_error("not an entering root");
 return Birth{alpha,point.normalized()};
}
// IFT with start fixed, endpoint q1 variable: dx(alpha)/dq1=alpha I.
inline Eigen::RowVector3d birthEndpointDerivative(const Birth&event,const Eigen::Vector3d&increment){
 double denominator=event.normal.dot(increment);
 if(denominator==0)throw std::domain_error("singular birth derivative");
 return -event.fraction*event.normal.transpose()/denominator;
}
}
