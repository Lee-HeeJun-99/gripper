#include "../models/yield_front_history/VectorReturn.h"
#include "../models/closure/Quadrature.h"
#include <iomanip>
#include <iostream>
using namespace regrip_vector_history;
int main(){try{
 const R k=.001L,v=.2L,a=3e-6L,b=1e-5L,T=.01L,s=k*v-a;
 const R xmax=s*T/b;
 // Independent analytical integral over x in[0,1] of
 // integral_(t_y)^T c(x,t)*(v-a/k)dt, t_y=b*x/(k*v-a).
 const R exact=(v-a/k)*(b*T*xmax*xmax/2-b*b*xmax*xmax*xmax/(3*s)+a*T*T*xmax/2-a*b*b*xmax*xmax*xmax/(6*s*s));
 std::cout<<std::setprecision(18)<<"steps,endpoint_D,event_integrated_D,exact_D,endpoint_relative,event_relative\n";
 for(unsigned count:{20u,40u,80u}){
  R h=T/count,D=0,event=0;
  for(unsigned n=1;n<=count;++n){
   R t0=(n-1)*h,t1=n*h,front0=s*t0/b,front1=s*t1/b;
   for(auto interval:{std::pair<R,R>{0,front0},{front0,front1}}){
    if(interval.second<=interval.first)continue;
    for(auto [node,w]:regrip_closure::gauss(8)){
     R x=(interval.first+interval.second)/2+(interval.second-interval.first)/2*node;
     R c0=b*x+a*t0,c1=b*x+a*t1,e0=std::min(v*t0,c0/k);
     auto r=radialReturn({e0,0,0},{v*h,0,0},{0,0,1},k,c1);
     R weight=(interval.second-interval.first)/2*w;
     D+=weight*r.loss;
     if(r.slip){
      // Unique scalar collinear event. NOT a general3D force/Jacobian rule.
      R denominator=(k*v-a)*h;
      if(denominator<=0)throw std::runtime_error("nonunique scalar yield event");
      R alpha=std::max(R(0),(c0-k*e0)/denominator);
      if(alpha>1)throw std::runtime_error("yield event outside step");
      R yieldCapacity=c0+alpha*a*h;
      event+=weight*(yieldCapacity+c1)/2*norm(r.plastic);
     }
    }
   }
  }
  R endpointError=std::abs(D-exact)/exact,eventError=std::abs(event-exact)/exact;
  if(eventError>1e-12L)throw std::runtime_error("analytical event work mismatch");
  std::cout<<count<<','<<D<<','<<event<<','<<exact<<','<<endpointError<<','<<eventError<<'\n';
 }
 return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
