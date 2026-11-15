#include "Audit.h"
#include <sofa/core/behavior/Mass.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include "../../models/contact_birth/MaterialCells.h"
#include "../../models/curved_contact/Map.h"
#include "../../models/contact_energy/ReturnAudit.h"
#include "CurveClassOnly.inc"
#include <set>
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
