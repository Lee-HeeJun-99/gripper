#include "ValueEnergy.h"
#include "value_models/film_rail_tendon/Kernel.h"
namespace regrip_value_energy {
std::array<double,2>evaluate(const Parameters&p,const std::vector<std::array<double,3>>&q){
 regrip_value_film_rail::Assembly model(p.nx);model.guideIntervals=p.guideIntervals;model.guideOffset=p.guideOffset;model.bondK=p.bondK;model.rootGuideSecondOrder=p.rootGuideSecondOrder;std::array<double,2>out{};
 model.elements(q,0,[&](const regrip_value_film_rail::Element&e){if(e.kind==0)out[0]+=e.energy.v;if(e.kind==1)out[1]+=e.energy.v;});return out;
}
}
