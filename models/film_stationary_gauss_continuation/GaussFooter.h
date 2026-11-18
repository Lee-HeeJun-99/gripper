#pragma once
#include "../film_stationary_release/FreeFooter.h"
namespace regrip_stationary_gauss {
// New typed Gauss clock domain. The old FREE reader's50ms guard is untouched.
inline regrip_stationary_release::FreeProvenance readFooter(std::istream&in,double time){
 using regrip_stationary_release::FreeProvenance;std::string label,origin;unsigned count;FreeProvenance p;
 in>>label>>count;if(!in||label!="FREE_ACTIVE_COUNT"||count!=0)throw std::runtime_error("explicit Gauss FREE active set required");
 in>>label>>count;if(!in||label!="RELEASED_FACE_GEOMETRY"||count!=3)throw std::runtime_error("three released observations required");
 for(unsigned f=0;f<3;++f){unsigned finger,triangle,feature;in>>finger>>triangle>>feature;if(!in||finger!=f||triangle!=116||feature!=6)throw std::runtime_error("Gauss released-face provenance differs");}
 in>>label>>p.begin>>p.end;if(!in||label!="RELEASE_INTERVAL"||!(p.begin>.0267&&p.begin<.0269&&p.end==p.begin+.0002&&p.end<=time))throw std::runtime_error("exact original release interval required");
 in>>label>>p.lastImpact;if(!in||label!="LAST_IMPACT_TIME"||!(p.lastImpact>0&&p.lastImpact<=p.begin))throw std::runtime_error("known impact provenance required");
 in>>label>>origin;if(!in||label!="INITIAL_CONDITION"||origin!="STATIONARY_SEPARATED")throw std::runtime_error("stationary origin required");
 double clock;in>>label>>clock;if(!in||label!="ACCUMULATED_TIME"||clock!=time||!std::isfinite(time)||time<.05||time>.0564)throw std::runtime_error("exact bounded Gauss FREE clock required");return p;
}
}
