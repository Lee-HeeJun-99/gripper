#include "../models/integrated/Kernels.h"
#include <iostream>
#include <iomanip>
#include <cmath>
// Stored U(s,z) has no explicit dependence on the yield capacity. Candidate
// getPotentialEnergy after RETURN is not fixed-state parameter differentiation.
int main(){try{
 const double k=10,s=.2;double z=0,totalD=0,totalProjection=0;
 std::cout<<std::setprecision(17)<<"capacity,stored_before,returned_after,plastic_D,derived_projection,residual\n";
 for(double cap:{2.,1.,.1,0.,.5,3.}){
  double old=s-z,U0=.5*k*old*old;auto r=regrip_integrated::slider(s,z,k,cap);double e=s-r.plastic,U1=.5*k*e*e,projection=.5*k*(e-old)*(e-old),residual=U1-U0+r.dissipation+projection;
  if(std::abs(residual)>1e-15||r.dissipation<0||projection<0)throw std::runtime_error("capacity-change energy identity");
  std::cout<<cap<<','<<U0<<','<<U1<<','<<r.dissipation<<','<<projection<<','<<residual<<'\n';z=r.plastic;totalD+=r.dissipation;totalProjection+=projection;
 }
 if(std::abs(totalD+totalProjection-.2)>1e-15)throw std::runtime_error("released stored energy not accounted");
 return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
