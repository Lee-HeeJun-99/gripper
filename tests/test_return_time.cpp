#include "../models/integrated/Kernels.h"
#include <iostream>
#include <iomanip>
#include <cmath>
// Independent planar monotone example with linearly varying normal capacity.
// Existing endpoint return is used without changing the production friction law.
int main(){try{
 constexpr double k=10,speed=.2,c0=.4,rate=.08;
 const double yield=c0/(k*speed-rate),plasticRate=speed-rate/k;
 const double exact=plasticRate*(c0*(1-yield)+.5*rate*(1-yield*yield));
 double previousError=0;
 std::cout<<std::setprecision(17)<<"steps,endpoint_D,event_integrated_D,reference_D,endpoint_relative_error\n";
 for(unsigned n:{10u,20u,40u,80u,160u,320u}){
  double z=0,endpoint=0,eventIntegral=0;
  for(unsigned i=1;i<=n;++i){double t0=double(i-1)/n,t1=double(i)/n,cap0=c0+rate*t0,cap1=c0+rate*t1;
   auto r=regrip_integrated::slider(speed*t1,z,k,cap1);double dp=r.plastic-z;
   endpoint+=r.dissipation;
   if(dp>0){double denominator=k*speed*(t1-t0)-(cap1-cap0);if(denominator<=0)throw std::runtime_error("non-monotone yield event");double alpha=(cap0-k*(speed*t0-z))/denominator;alpha=std::clamp(alpha,0.,1.);double capStart=cap0+alpha*(cap1-cap0);eventIntegral+=.5*(capStart+cap1)*dp;}
   z=r.plastic;
  }
  double error=std::abs(endpoint-exact)/exact;
  if(std::abs(eventIntegral-exact)>1e-14||error==0||(previousError&&error>=previousError))throw std::runtime_error("endpoint return time convergence");
  std::cout<<n<<','<<endpoint<<','<<eventIntegral<<','<<exact<<','<<error<<'\n';previousError=error;
 }
 return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
