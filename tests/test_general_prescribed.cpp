#include "../models/general_vector_history/Owner.h"
#include "../models/general_vector_history/AdaptiveMaterialRule.h"
#include "../models/curved_contact/Map.h"
#include <iomanip>
#include <iostream>
using namespace regrip_general_history;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("steps argument");unsigned steps=std::stoul(argv[1]);if(!steps||steps>128)throw std::invalid_argument("bounded steps");
 Owner owner;Owner::Physics physics;Pose object;double dt=.01/steps,cumulative=0;
 auto geometry=[](double t){Pose a,b;a.p={-.3,1.01-.01*t,.2*t};b.p={.3,1.01-.01*t,.2*t};a.q=regrip3d::exp({0,0,.01*t});b.q=regrip3d::exp({0,0,-.01*t});return [a,b](double s){Pose p;p.p=regrip_curved::position(a,b,s,.6);return p;};};
 Owner::Geometry before=geometry(0);
 // Match SOFA prepare(): establish initially active,zero-extension contact.
 // Without this transaction the fixture starts from empty contact history,
 // a DIFFERENT initial-value problem (preserved failed time01 campaign).
 auto initial=owner.trial(before,before,object,object,physics);owner.commit(initial);
 std::cout<<std::setprecision(17)<<"time,plastic_increment,plastic_cumulative,stored_energy,normal_force\n";
 for(unsigned step=1;step<=steps;++step){
  Owner::Geometry current=geometry(step*dt);
  auto result=[&](double s){return regrip_birthlaw::value(current(s),object,owner.at(s),before(s).p,0,1,5,.02,.001,.001,.3);};
  auto density=[&](double s){auto r=result(s);std::array<double,11> v{};v[0]=r.normalForce;v[1]=r.elasticEnergy;v[2]=r.plasticDissipation;return v;};
  auto rule=adaptiveMaterialRule(30,.6,density);double D=0,U=0,Fn=0;
  for(auto [s,w]:rule){auto r=result(s);D+=w*r.plasticDissipation;U+=w*r.elasticEnergy;Fn+=w*r.normalForce;}
  cumulative+=D;auto trial=owner.trial(before,current,object,object,physics);owner.commit(trial);before=current;
  std::cout<<step*dt<<','<<D<<','<<cumulative<<','<<U<<','<<Fn<<'\n';
 }
 return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
