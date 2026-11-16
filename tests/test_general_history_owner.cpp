#include "../models/general_vector_history/Owner.h"
#include "../models/curved_contact/Map.h"
#include <iostream>
using namespace regrip_general_history;
void check(bool ok,const char *why){if(!ok)throw std::runtime_error(why);}
int main(){try{
 Owner owner(64); Owner::Physics physics;
 auto geometry=[](int step){return [step](double s){Pose p;
   // Material coordinate fixed; sphere patch moves and normals rotate.
   p.p={.9*(s-.5)+.001*step,1.04-.004*step,.002*step};return p;};};
 Pose object;std::array<History,97> reference{};double error=0,D=0,detach=0;
 Owner::Geometry before=geometry(0);
 for(int step=1;step<=30;++step){
  auto after=geometry(step<=15?step:30-step);
  auto trial=owner.trial(before,after,object,object,physics);
  for(unsigned i=0;i<reference.size();++i){double s=(i+.5)/reference.size();
   auto r=regrip_birthlaw::value(after(s),object,reference[i],before(s).p,physics.shape,physics.radius,physics.height,physics.skin,physics.kn,physics.kt,physics.mu);
   auto old=owner.at(s);check(old.elastic==reference[i].elastic,"independent point prefix");
   auto next=trial.next(s);check(next.elastic==r.next.elastic&&next.active==r.next.active,"query/commit law");
   D+=r.plasticDissipation/reference.size();
   if(old.active&&!next.active)detach+=.5*physics.kt*regrip3d::dot(old.elastic,old.elastic)/reference.size();
   reference[i]=r.next;
  }
  auto epoch=owner.epoch();owner.commit(trial);check(owner.epoch()==epoch+1,"one commit");
  bool rejected=false;try{owner.commit(trial);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"stale commit rejected");
  for(unsigned i=0;i<reference.size();++i){double s=(i+.5)/reference.size();auto a=owner.at(s),b=owner.at(s);check(a.elastic==b.elastic,"pure repeated query");
   for(int j=0;j<3;++j)error=std::max(error,std::abs(a.elastic[j]-reference[i].elastic[j]));}
  before=after;
 }
 check(error==0&&D>=0&&detach>=0,"exact reference and nonnegative inventories");
 check(!owner.at(.5).active,"death resets history");
 Owner::Geometry recontact=[](double s){Pose p;p.p={.1*(s-.5),1.01,.001};return p;};
 auto birth=owner.trial(before,recontact,object,object,physics);owner.commit(birth);check(owner.at(.5).active,"recontact");
 // Independent arbitrary-abscissa query, not a grid node or sample ID.
 check(owner.at(.3141592653589793).active,"arbitrary material coordinate");
 std::cout<<"PASS moving sphere material owner states="<<30*97<<" error="<<error<<" D="<<D<<" detachment_inventory="<<detach<<"\n";
 return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
