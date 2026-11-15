#include "../models/conservative_beam/EnergyKernel.h"
#include <iostream>
#include <iomanip>
#include <random>
using namespace regrip_beam;
void check(bool b,const char*s){if(!b)throw std::runtime_error(s);}
V times(V a,double t){for(auto&v:a)v*=t;return a;}
V spatialStep(Q to,Q from){for(int j=0;j<3;++j)from[j]*=-1;auto q=multiply(to,from);if(q[3]<0)for(auto&x:q)x=-x;double s=std::sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]);double f=s<1e-14?2:2*std::atan2(s,q[3])/s;return {f*q[0],f*q[1],f*q[2]};}
int main(){try{
 Pose a0,b0;b0.p={10,0,0};Properties p{183,60,60,8,10,11};double ef=0,jf=0,mf=0;
 std::mt19937 gen(7321);std::uniform_real_distribution<double>d(-1,1);
 for(int z=0;z<40;++z){Pose a=a0,b=b0;a.q=exp(V{.5*d(gen),.5*d(gen),.5*d(gen)});b.q=multiply(a.q,exp(V{1.1*d(gen),1.1*d(gen),1.1*d(gen)}));for(int j=0;j<3;++j)b.p[j]+=d(gen);auto r=evaluate(a,b,a0,b0,p);
  for(int k=0;k<12;++k){auto ap=a,am=a,bp=b,bm=b;if(k<6){ap=increment(a,k,1e-6);am=increment(a,k,-1e-6);}else{bp=increment(b,k-6,1e-6);bm=increment(b,k-6,-1e-6);}auto rp=evaluate(ap,bp,a0,b0,p),rm=evaluate(am,bm,a0,b0,p);ef=std::max(ef,std::abs((rp.energy-rm.energy)/2e-6+r.force[k]));for(int i=0;i<12;++i)jf=std::max(jf,std::abs((rp.force[i]-rm.force[i])/2e-6-r.jacobian[12*i+k]));}
  auto m=add(add(V{r.force[3],r.force[4],r.force[5]},V{r.force[9],r.force[10],r.force[11]}),cross(sub(b.p,a.p),V{r.force[6],r.force[7],r.force[8]}));for(auto v:m)mf=std::max(mf,std::abs(v));
 }
 auto work=[&](int n){Pose path[5]={b0,b0,b0,b0,b0};path[1].p={10.2,.1,-.2};path[1].q=exp(V{.3,.2,-.1});path[2].p={9.8,.4,.2};path[2].q=exp(V{-.2,.5,.3});path[3].p={10.1,-.2,.1};path[3].q=exp(V{.2,-.1,.4});double sum=0;
  for(int s=0;s<4;++s){auto dp=sub(path[s+1].p,path[s].p);auto w=spatialStep(path[s+1].q,path[s].q);for(int i=0;i<n;++i){double t=(i+.5)/n;Pose b;b.p=add(path[s].p,times(dp,t));b.q=multiply(exp(times(w,t)),path[s].q);auto r=evaluate(a0,b,a0,b0,p);sum+=(r.force[6]*dp[0]+r.force[7]*dp[1]+r.force[8]*dp[2]+r.force[9]*w[0]+r.force[10]*w[1]+r.force[11]*w[2])/n;}}return sum;};
 double w32=work(32),w128=work(128);check(ef<1e-5&&jf<1e-5&&mf<1e-9,"large deformation FD/moment");check(std::abs(w128)<std::abs(w32)*.1&&std::abs(w128)<.001,"noncommuting SO3 closed path convergence");std::cout<<std::setprecision(17)<<"PASS large40 energyFD="<<ef<<" jacobianFD="<<jf<<" moment="<<mf<<" closed32="<<w32<<" closed128="<<w128<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
