#include "../models/contact_history/MaterialHistory.h"
#include <iostream>
#include <iomanip>
// An audit counterexample,NOT a claim that the coupled trajectory injects
// energy overall. Stiffness-proportional damping uses beta*J_force*v.
int main(){try{
 using namespace regrip_history;Pose p,o;p.p={1.01,0,0};double beta=.1;
 auto normal=evaluateContact(p,o,{},0,1,1,.02,1,1,0);
 double tangentRayleighPower=beta*normal.wrench.jacobian[12*1+1];
 if(!(tangentRayleighPower>0))throw std::runtime_error("normal curvature counterexample changed");
 p.p={0,1.01,0};History a;a.active=true;a.local=p.p;a.normal={0,1,0};double cap=.3*(.02-(1.01-1));
 a.elastic={std::nextafter(cap,0.),0,0};auto b=a;b.elastic[0]=std::nextafter(cap,INFINITY);
 auto left=evaluateContact(p,o,a,2,1,1,.02,1,1,.3),right=evaluateContact(p,o,b,2,1,1,.02,1,1,.3);
 double jump=std::abs(left.wrench.jacobian[0]-right.wrench.jacobian[0]);
 if(jump<.5||std::abs(left.wrench.force[0]-right.wrench.force[0])>1e-15)throw std::runtime_error("yield one-sided derivative counterexample");
 std::cout<<std::setprecision(17)<<"AUDIT normal_contact_stiffness_Rayleigh_power="<<tangentRayleighPower<<" (positive work,not dissipation)\n";
 std::cout<<"AUDIT yield_force_difference="<<std::abs(left.wrench.force[0]-right.wrench.force[0])<<" Jacobian_jump="<<jump<<";nonsmooth derivative is legitimate,but not automatically a physical viscosity\n";
 std::cout<<"PASS counterexamples reproduced;coupled damping PSD remains NOT RUN\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
