#pragma once
#include "../film_three_finger/SharedFilmSystem.h"
namespace regrip_force_value {
// Same full AD2 element energy/gradient. Only the UNUSED global Hessian
// allocation/assembly is omitted. Not the previously rejected gradient-only AD.
inline Eigen::VectorXd value(const regrip_three_finger::SharedFilmSystem&s,
 const Eigen::VectorXd&x,double tension){
 const unsigned nf=s.shared.nf,n=s.shared.M.rows();Eigen::VectorXd out=Eigen::VectorXd::Zero(n);out.segment<3>(3*nf)=s.external;
 for(unsigned f=0;f<3;++f){const auto&film=s.shared.films[f];auto state=s.local(x,f);
  film.film.model.elements(state.q,tension,[&](const regrip_film_rail::Element&e){for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=film.film.index[ga];if(i<0)continue;out(f*nf+i)-=film.film.weight[ga]*e.energy.g[a];}},s.meter);
 }return out;
}
}
