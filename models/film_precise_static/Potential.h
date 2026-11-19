#pragma once
#include "../film_precise_tendon/Route.h"
namespace regrip_precise_static {
// Dead-load tendon potential, NOT stored elastic cable energy or path work.
// Sum the SAME element energies before rounding a 200mm total cable length.
inline double tendonPotential(const regrip_film_rail::Assembly&m,const std::vector<regrip_film::Point>&q,double T,double lateral){
 long double value=0;regrip_precise_tendon::route(m,q,T,lateral,[&](const regrip_film_rail::Element&e){value+=static_cast<long double>(e.energy.v);});return double(value);
}
}
