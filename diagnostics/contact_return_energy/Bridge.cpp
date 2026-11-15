#include "Audit.h"
#include <sofa/core/behavior/Mass.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include "../../models/contact_birth/MaterialCells.h"
#include "../../models/curved_contact/Map.h"
#include "../../models/contact_energy/ReturnAudit.h"
#include "CurveClassOnly.inc"
#include <set>
using AuditContact=regrip_integrated::CurvedMaterialContact;
AuditContact*checkedContact(sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*f){
 if(f->getClassName()!="CurvedMaterialContact")throw std::runtime_error("normal contact audit class");auto*c=static_cast<AuditContact*>(f);
 if(f->findData("historySpacing")!=&c->historySpacing||f->findData("objectIndex")!=&c->objectIndex||f->findData("filename")!=&c->filename)throw std::runtime_error("normal contact audit ABI");return c;
}
extern "C" NormalInventory curveNormalSnapshot(sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*f){
 using namespace regrip_integrated;auto*c=checkedContact(f);const auto&x=c->getMState()->read(sofa::core::vec_id::read_access::position)->getValue();NormalInventory out;out.force.resize(x.size());unsigned object=c->objectIndex.getValue();auto po=c->pose(x[object]);
 for(unsigned e=0;e<c->grids.size();++e){const auto&g=c->grids[e];auto selected=c->bounds(c->interval(x,e),g.count);unsigned a=c->segments.getValue()[2*e],b=c->segments.getValue()[2*e+1];double w=g.length/g.count;
  for(int i=selected.first;i<=selected.last;++i){double s=(i+.5)/g.count;auto pp=c->point(x,e,s);auto r=regrip_history::evaluateContact(pp,po,{},c->shape.getValue(),c->radius.getValue(),c->halfHeight.getValue(),c->pointRadius.getValue(),c->lineStiffness.getValue(),c->tangentLineStiffness.getValue(),0.);if(!r.next.active)continue;
   auto mapped=regrip_curved::map(c->pose(x[a]),c->pose(x[b]),s,g.length,r.wrench);unsigned ids[18];for(unsigned j=0;j<6;++j){ids[j]=6*a+j;ids[j+6]=6*b+j;ids[j+12]=6*object+j;}
   out.energy+=w*r.wrench.energy;for(unsigned j=0;j<18;++j){out.force[ids[j]/6][ids[j]%6]+=w*mapped.force[j];for(unsigned k=0;k<18;++k)if(mapped.jacobian[18*j+k])out.jacobian.push_back({ids[j],ids[k],w*mapped.jacobian[18*j+k]});}
  }
 }return out;
}
extern "C" double curveNormalEnergy(sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*f){
 auto*c=checkedContact(f);const auto&x=c->getMState()->read(sofa::core::vec_id::read_access::position)->getValue();double energy=0;auto o=c->pose(x[c->objectIndex.getValue()]);
 for(unsigned e=0;e<c->grids.size();++e){const auto&g=c->grids[e];auto range=c->bounds(c->interval(x,e),g.count);for(int i=range.first;i<=range.last;++i){auto p=c->point(x,e,(i+.5)/g.count);auto r=regrip_history::value(p,o,{},c->shape.getValue(),c->radius.getValue(),c->halfHeight.getValue(),c->pointRadius.getValue(),c->lineStiffness.getValue(),c->tangentLineStiffness.getValue(),0);energy+=g.length/g.count*r.wrench.energy;}}
 return energy;
}
extern "C" ReturnInventory auditCurveReturn(sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*f){
 using Contact=regrip_integrated::CurvedMaterialContact;
 if(f->getClassName()!="CurvedMaterialContact")throw std::runtime_error("audit contact class");
 auto*c=static_cast<Contact*>(f);
 if(f->findData("historySpacing")!=&c->historySpacing||f->findData("objectIndex")!=&c->objectIndex||f->findData("filename")!=&c->filename)throw std::runtime_error("audit compiled project ABI");
 const auto&x=c->getMState()->read(sofa::core::vec_id::read_access::position)->getValue();
 auto snapshot=c->computeValue(x);ReturnInventory total;std::set<std::pair<unsigned,unsigned>>present;
 auto add=[&](const regrip_return_audit::Balance&b,double w){
  total.oldEnergy+=w*b.oldEnergy;total.newEnergy+=w*b.newEnergy;total.endpointWork+=w*b.endpointWork;total.plastic+=w*b.plastic;total.projection+=w*b.projection;total.detachment+=w*b.detachment;total.residual+=w*b.residual;total.maxPointResidual=std::max(total.maxPointResidual,std::abs(b.residual));
 };
 for(const auto&p:snapshot.points){unsigned edge=p.edge;double s=p.s;const auto&g=c->grids.at(edge);unsigned id=std::lround(s*g.count-.5);if(id>=g.count||!present.insert({edge,id}).second)throw std::runtime_error("audit immutable point ID");
  auto h=c->old(edge,s);auto b=regrip_return_audit::evaluate(h,p.r,c->beforeLocal(edge,s),c->shape.getValue(),c->radius.getValue(),c->halfHeight.getValue(),c->pointRadius.getValue(),c->tangentLineStiffness.getValue());add(b,p.weight);++total.active;if(!h.active)++total.born;if(p.r.next.sliding)++total.sliding;
 }
 for(unsigned e=0;e<c->grids.size();++e){const auto&g=c->grids[e];for(unsigned id:g.active)if(!present.count({e,id})){
  regrip_birthlaw::ContactResult inactive;auto b=regrip_return_audit::evaluate(g.state[id],inactive,{},c->shape.getValue(),c->radius.getValue(),c->halfHeight.getValue(),c->pointRadius.getValue(),c->tangentLineStiffness.getValue());add(b,g.length/g.count);++total.dead;
 }}
 if(std::abs(total.newEnergy-snapshot.elastic)>1e-19||std::abs(total.plastic-snapshot.D)>1e-19)throw std::runtime_error("audit differs from actual snapshot energy/return");
 return total;
}
