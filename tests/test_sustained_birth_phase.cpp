#include "../models/film_impact/ManyRowImpact.h"
#include <iostream>
#include <iomanip>
// Exact shared-mass counterexample: an old contact separates when a second
// contact is born inside the step. No stiffness, damping or solver truncation.
int main(){
 using namespace regrip_film_impact;
 Eigen::Matrix3d M=Eigen::Vector3d(1,1,2).asDiagonal();
 Eigen::Matrix<double,2,3> J;J<<1,0,-1,0,1,-1;
 Eigen::Vector3d before(0,-1,0);
 auto exact=manyRowImpact(M,J,before,1e-13);
 if(std::abs(exact.state.impulse(1)-2./3)>1e-12||exact.state.impulse(0)!=0)return 1;
 std::cout<<std::setprecision(17);
 for(double phase:{.1,.25,.5,.75,.9}){
  // Endpoint midpoint gap equation g0+h*J*v0+h*W*lambda=0.
  double lambda=(1-phase)*2./3;
  Eigen::Vector3d endpoint=before+M.inverse()*J.row(1).transpose()*(2*lambda);
  double normal=(J*endpoint)(1);
  if(std::abs(normal-(1-2*phase))>1e-12)return 2;
  if((M*(endpoint-before)-J.row(1).transpose()*(2*lambda)).norm()>1e-12)return 3;
  // With h=1, exact event-flight position equals endpoint constrained position.
  Eigen::Vector3d positionMidpoint=.5*(before+endpoint);
  Eigen::Vector3d positionEvent=phase*before+(1-phase)*exact.state.velocity;
  if((positionMidpoint-positionEvent).norm()>1e-12)return 4;
  std::cout<<phase<<","<<normal<<","<<2*lambda<<","<<exact.state.impulse(1)<<"\n";
 }
 std::cout<<"PASS counterexample reproduced; endpoint position/momentum do NOT certify plastic impact velocity\n";
}
