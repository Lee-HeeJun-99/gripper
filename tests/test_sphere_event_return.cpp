#include "../models/general_vector_history/SphereEventReturn.h"
#include <iostream>
using namespace regrip_history;
int main(){try{
 V before{0,1.03,0},after{0,1.01,.02};Vec<First> endpoint{};
 for(int j=0;j<3;++j)endpoint[j]=First(after[j])+First::variable(j);
 auto r=regrip_general_history::sphereEventReturn(before,{},endpoint,1.02,.001,.0003,128);
 if(!r.birth||r.death||r.entry<=0||r.entry>=1)throw std::runtime_error("birth classification");
 double fd=0;
 for(int j=0;j<3;++j){auto p=after,m=after;p[j]+=1e-7;m[j]-=1e-7;
 auto a=regrip_general_history::sphereEventReturn(before,{},constantV<First>(p),1.02,.001,.0003,128);
 auto b=regrip_general_history::sphereEventReturn(before,{},constantV<First>(m),1.02,.001,.0003,128);
 for(int v=0;v<3;++v)fd=std::max(fd,std::abs((a.elastic[v].v-b.elastic[v].v)/2e-7-r.elastic[v].g[j]));}
 double balance=r.storedEnergy.v-r.work.v+r.plasticLoss.v+r.projection.v;
 auto transit=regrip_general_history::sphereEventReturn({-1.2,.8,0},{},constantV<First>(V{1.2,.8,0}),1.02,.001,.0003,128);
 if(!transit.birth||!transit.death||transit.storedEnergy.v!=0||transit.plasticLoss.v<0||fd>1e-7||std::abs(balance)>1e-18)throw std::runtime_error("event derivative/energy/transit");
 double cycle=-transit.work.v+transit.plasticLoss.v+transit.projection.v+transit.detachmentInventory.v;
 if(std::abs(cycle)>1e-17)throw std::runtime_error("cycle energy");
 auto Q=regrip3d::exp({.4,-.6,.2});auto rotated=regrip_general_history::sphereEventReturn(regrip3d::rotate(Q,before),{},constantV<First>(regrip3d::rotate(Q,after)),1.02,.001,.0003,128);
 V ev{};for(int j=0;j<3;++j)ev[j]=r.elastic[j].v;auto expected=regrip3d::rotate(Q,ev);
 for(int j=0;j<3;++j)if(std::abs(expected[j]-rotated.elastic[j].v)>1e-13)throw std::runtime_error("event objectivity");
 auto none=regrip_general_history::sphereEventReturn({0,1.1,0},{},constantV<First>(V{.01,1.1,0}),1.02,.001,.0003,128);
 if(none.birth||none.death||none.plasticLoss.v!=0)throw std::runtime_error("noncontact");
 bool rejected=false;try{regrip_general_history::sphereEventReturn({-2,1,0},{},constantV<First>(V{2,1,0}),1,.001,.0003,128);}catch(const std::domain_error&){rejected=true;}
 if(!rejected)throw std::runtime_error("grazing must reject undefined derivative");
 std::cout<<"PASS birth_fraction="<<r.entry<<" FD_absolute="<<fd<<" birth_identity="<<balance<<" transit_identity="<<cycle<<"\n";
 return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
