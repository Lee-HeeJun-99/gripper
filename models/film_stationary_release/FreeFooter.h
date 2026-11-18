#pragma once
#include <istream>
#include <ostream>
#include <stdexcept>
#include <string>
#include <cmath>
namespace regrip_stationary_release {
struct FreeProvenance {double begin=0,end=0,lastImpact=0;};
// Observation geometry is not a live contact set or a fabricated row lifetime.
inline FreeProvenance readFreeFooter(std::istream&in,double time){
 std::string label,origin;unsigned count;FreeProvenance p;
 in>>label>>count;if(!in||label!="FREE_ACTIVE_COUNT"||count!=0)throw std::runtime_error("explicit stationary FREE active set required");
 in>>label>>count;if(!in||label!="RELEASED_FACE_GEOMETRY"||count!=3)throw std::runtime_error("three released face observations required");
 for(unsigned f=0;f<3;++f){unsigned finger,triangle,feature;in>>finger>>triangle>>feature;if(!in||finger!=f||triangle!=116||feature!=6)throw std::runtime_error("released face provenance differs");}
 in>>label>>p.begin>>p.end;if(!in||label!="RELEASE_INTERVAL"||!(p.begin>.0267&&p.begin<.0269&&p.end==p.begin+.0002&&p.end<=time))throw std::runtime_error("exact accumulated release interval required");
 in>>label>>p.lastImpact;if(!in||label!="LAST_IMPACT_TIME"||!(p.lastImpact>0&&p.lastImpact<=p.begin))throw std::runtime_error("known global impact provenance required");
 in>>label>>origin;if(!in||label!="INITIAL_CONDITION"||origin!="STATIONARY_SEPARATED")throw std::runtime_error("stationary origin required");
 double clock;in>>label>>clock;if(!in||label!="ACCUMULATED_TIME"||clock!=time||!std::isfinite(time)||time>.05)throw std::runtime_error("exact stationary free physical clock required");return p;
}
inline void writeFreeFooter(std::ostream&out,const FreeProvenance&p,double time){
 out<<"FREE_ACTIVE_COUNT 0\nRELEASED_FACE_GEOMETRY 3\n";for(unsigned f=0;f<3;++f)out<<f<<" 116 6\n";
 out<<"RELEASE_INTERVAL "<<p.begin<<' '<<p.end<<"\nLAST_IMPACT_TIME "<<p.lastImpact<<"\nINITIAL_CONDITION STATIONARY_SEPARATED\nACCUMULATED_TIME "<<time<<'\n';
}
}
