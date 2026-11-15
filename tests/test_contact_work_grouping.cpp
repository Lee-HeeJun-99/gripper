#include "../models/contact_energy/ReturnAudit.h"
#include <random>
#include <iostream>
#include <iomanip>
int main(){try{
 using namespace regrip_history;std::mt19937 rng(1511);std::uniform_real_distribution<double>u(-1,1);double maximum=0;
 for(unsigned shape=0;shape<3;++shape)for(unsigned i=0;i<200;++i){
  Pose p,o;p.p=shape==0?V{1.01,0,0}:shape==1?V{1.01,.1,0}:V{.1,1.01,.1};
  auto n=regrip_birthlaw::value(p,o,{},p.p,shape,1,1,.02,1,1,0);History old;old.active=true;old.local=p.p;old.normal=n.next.normal;
  V e{u(rng)*1e-4,u(rng)*1e-4,u(rng)*1e-4};old.elastic=sub(e,scale(old.normal,dot(old.normal,e)));
  auto f0=regrip_birthlaw::evaluate(p,o,old,p.p,shape,1,1,.02,1,1,.3),n0=regrip_birthlaw::evaluate(p,o,{},p.p,shape,1,1,.02,1,1,0);
  V d{u(rng)*.004,u(rng)*.004,u(rng)*.004};if(i==0)d=scale(old.normal,.02);auto q=p;q.p=add(p.p,d);
  auto f1=regrip_birthlaw::evaluate(q,o,old,p.p,shape,1,1,.02,1,1,.3),n1=regrip_birthlaw::evaluate(q,o,{},p.p,shape,1,1,.02,1,1,0);
  auto b=regrip_return_audit::evaluate(old,f1,p.p,shape,1,1,.02,1);
  double wf=0,wn=0,jf=0,jn=0;for(int r=0;r<3;++r){wf+=f0.wrench.force[r]*d[r];wn+=n0.wrench.force[r]*d[r];for(int c=0;c<3;++c){jf+=d[r]*f0.wrench.jacobian[12*r+c]*d[c];jn+=d[r]*n0.wrench.jacobian[12*r+c]*d[c];}}
  double Rn=n1.wrench.energy-n0.wrench.energy+wn+.5*jn,Pn=-.5*jn,Rt=b.endpointWork+(wf-wn)+(jf-jn);
  double Rc=(f1.wrench.energy-b.newEnergy)-(f0.wrench.energy-b.oldEnergy)+b.endpointWork+wf+jf;
  maximum=std::max(maximum,std::abs(Rc-(Rn-Pn+Rt)));
  if(maximum>1e-17||b.plastic<0||b.detachment<0)throw std::runtime_error("independent contact grouping identity");
 }
 std::cout<<std::setprecision(17)<<"PASS600 Sphere/Cylinder/Box contact work groupings,including separation,max_residual="<<maximum<<";no force/Jacobian change\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
