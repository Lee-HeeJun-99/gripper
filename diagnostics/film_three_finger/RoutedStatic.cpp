#include "../../models/film_routed_tendon/Step.h"
// Reuse SAME independent Newton/line-search/load continuation,not a new solver.
inline regrip_transmission::Parts routedStaticParts(const regrip_film_native::CoupledPlaneStep&m,const std::vector<regrip_film_rail::Point>&q,double T){return regrip_routed_tendon::parts(m,q,T,4.5);}
#define parts routedStaticParts
#include "TransmissionStatic.cpp"
#undef parts
