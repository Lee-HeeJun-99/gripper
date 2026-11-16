#include "../models/general_vector_history/MovingReturn.h"
#include <iostream>
using namespace regrip_history;
int main(){try{
 V e{.001,.0002,0},n{0,0,1},du{.008,.003,.001},end{.2,.1,1};double cap=2.8e-6,k=.001;
 Vec<First>d{},normal{};for(int j=0;j<3;++j){d[j]=First(du[j])+First::variable(j);normal[j]=First(end[j])+First::variable(3+j);}
 auto r=regrip_general_history::movingReturn(e,n,d,normal,k,3e-6,First(cap)+First::variable(6),128);
 double fd=0;for(int j=0;j<7;++j){auto p=du,m=du,pn=end,mn=end;double pc=cap,mc=cap,h=j==6?1e-11:1e-7;
  if(j<3){p[j]+=h;m[j]-=h;}else if(j<6){pn[j-3]+=h;mn[j-3]-=h;}else{pc+=h;mc-=h;}
  auto a=regrip_general_history::movingReturn(e,n,constantV<First>(p),constantV<First>(pn),k,3e-6,First(pc),128);
  auto b=regrip_general_history::movingReturn(e,n,constantV<First>(m),constantV<First>(mn),k,3e-6,First(mc),128);
  for(int v=0;v<3;++v){double diff=(a.elastic[v].v-b.elastic[v].v)/(2*h);fd=std::max(fd,std::abs(diff-r.elastic[v].g[j])/std::max(1.,std::abs(diff)));}}
 double residual=r.storedEnergy.v-.5*k*dot(e,e)-r.work.v+r.plasticLoss.v+r.projection.v;
 auto Q=regrip3d::exp({.4,-.6,.2});auto rotated=regrip_general_history::movingReturn(regrip3d::rotate(Q,e),regrip3d::rotate(Q,n),constantV<First>(regrip3d::rotate(Q,du)),constantV<First>(regrip3d::rotate(Q,end)),k,3e-6,First(cap),128);
 V ev{};for(int j=0;j<3;++j)ev[j]=r.elastic[j].v;auto expected=regrip3d::rotate(Q,ev);double covariance=0;for(int j=0;j<3;++j)covariance=std::max(covariance,std::abs(expected[j]-rotated.elastic[j].v));
 if(fd>1e-6||std::abs(residual)>1e-18||covariance>1e-13||r.plasticLoss.v<0)throw std::runtime_error("moving return derivative/energy/objectivity");
 std::cout<<"PASS FD="<<fd<<" discrete_identity="<<residual<<" covariance="<<covariance<<"\n";
 for(unsigned s:{32u,64u,128u,256u}){auto v=regrip_general_history::movingReturn(e,n,constantV<First>(du),constantV<First>(end),k,3e-6,First(cap),s);std::cout<<"substeps="<<s<<" D="<<v.plasticLoss.v<<" e="<<v.elastic[0].v<<","<<v.elastic[1].v<<","<<v.elastic[2].v<<"\n";}
 return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
