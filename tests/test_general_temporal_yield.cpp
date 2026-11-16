#include "../models/general_vector_history/TemporalYield.h"
#include <iomanip>
#include <iostream>
using namespace regrip_history;
int main(){try{
 double rootError=0,derivativeError=0;unsigned count=0;
 for(unsigned i=0;i<256;++i){double angle=.013*i;V e{.0005*std::cos(angle),.0005*std::sin(angle),0};
  V d{.006*std::cos(angle+.3),.006*std::sin(angle+.3),0};double k=.001,c0=2e-6,c1=2.1e-6;
  Vec<First> increment;for(int j=0;j<3;++j)increment[j]=First(d[j])+First::variable(j);
  auto capacity=First(c1)+First::variable(3);auto a=regrip_general_history::firstYield(e,increment,k,c0,capacity);
  auto trial=add(e,scale(d,a.v));double c=c0+a.v*(c1-c0);
  rootError=std::max(rootError,std::abs(k*std::sqrt(dot(trial,trial))-c));
  for(int j=0;j<4;++j){double h=j==3?1e-11:1e-8;auto dp=d,dm=d;double cp=c1,cm=c1;
   if(j<3){dp[j]+=h;dm[j]-=h;}else{cp+=h;cm-=h;}
   auto p=regrip_general_history::firstYield(e,constantV<First>(dp),k,c0,First(cp));
   auto m=regrip_general_history::firstYield(e,constantV<First>(dm),k,c0,First(cm));
   double fd=(p.v-m.v)/(2*h);derivativeError=std::max(derivativeError,std::abs(fd-a.g[j])/std::max(1.,std::abs(a.g[j])));
  }++count;
 }
 if(rootError>1e-18||derivativeError>1e-7)throw std::runtime_error("vector first-yield IFT/root mismatch");
 bool rejected=false;try{regrip_general_history::firstYield({0,0,0},constantV<First>({0,0,0}),.001,2e-6,First(2e-6));}catch(const std::domain_error&){rejected=true;}
 if(!rejected)throw std::runtime_error("no-event branch not rejected");
 std::cout<<std::setprecision(17)<<"PASS vector temporal first-yield states="<<count<<" root="<<rootError<<" IFT_relative="<<derivativeError<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
