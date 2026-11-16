#include "../models/general_vector_history/Owner.h"
#include "../models/general_vector_history/AdaptiveMaterialRule.h"
#include <iostream>
int main(){try{
 using namespace regrip_history;Pose object;
 auto density=[&](double s){Pose p;p.p={.6*(s-.5),1.01,0};
  auto r=regrip_birthlaw::value(p,object,{},p.p,0,1,5,.02,.001,.001,.3);
  auto f=add(scale(r.next.normal,r.normalForce),scale(r.next.elastic,-.001));auto torque=cross(p.p,scale(r.next.elastic,-.001));
  std::array<double,11>v{};v[0]=r.normalForce;v[1]=r.elasticEnergy;v[2]=r.plasticDissipation;
  for(int j=0;j<3;++j){v[3+j]=std::abs(f[j]);v[6+j]=std::abs(torque[j]);}return v;};
 auto rule=regrip_general_history::adaptiveMaterialRule(30,.6,density);
 std::cout<<"PASS geometry rule points="<<rule.size()<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
