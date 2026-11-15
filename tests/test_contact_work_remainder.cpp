#include "../models/contact_energy/ReturnAudit.h"
#include <iostream>
#include <iomanip>
// Independent constrained planar point:actual BEGIN force/J versus material
// endpoint return work. A signed work defect is not classified as heat.
int main(){try{
 using namespace regrip_history;Pose p,o;p.p={0,1.01,0};History old;old.active=true;old.local=p.p;old.normal={0,1,0};
 double maximum=0;
 for(double delta:{.001,.01,-.001,-.01}){
  auto begin=regrip_birthlaw::evaluate(p,o,old,p.p,2,1,1,.02,1,1,.3);
  auto q=p;q.p[0]+=delta;auto end=regrip_birthlaw::evaluate(q,o,old,p.p,2,1,1,.02,1,1,.3);
  auto b=regrip_return_audit::evaluate(old,end,p.p,2,1,1,.02,1);
  double nodal=begin.wrench.force[0]*delta+begin.wrench.jacobian[0]*delta*delta;
  double mapped=b.endpointWork+nodal;
  double identity=b.newEnergy-b.oldEnergy+nodal+b.plastic+b.projection+b.detachment-mapped;
  maximum=std::max(maximum,std::abs(identity));
  if(std::abs(identity)>1e-18||b.plastic<0||b.projection<0)throw std::runtime_error("contact mapped-work identity");
  if(end.next.sliding&&mapped>=0)throw std::runtime_error("yield crossing must retain signed temporal work defect");
  if(!end.next.sliding&&std::abs(mapped)>1e-18)throw std::runtime_error("linear stick Euler identity");
 }
 std::cout<<std::setprecision(17)<<"PASS independent mapped contact work,stick/slip signs,max_residual="<<maximum<<";not global energy certification\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
