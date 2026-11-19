#pragma once
#ifndef REGRIP_FILM_EXTENDED_AD
#error "Separate experimental module requires extended AD in every translation unit"
#endif
#include "../film_precise_tendon/Route.h"
#include "../film_transmission/Gauss.h"
namespace regrip_extended_precision {
inline regrip_transmission::Parts parts(const regrip_transmission::CoupledPlaneStep&m,const std::vector<regrip_film::Point>&q,double T,double lateral){
 using namespace regrip_transmission;
 static_assert(sizeof(regrip_film::ADScalar)>sizeof(double),"extended local arithmetic required");
 const int n=m.freeSize;using Vector=Eigen::Matrix<long double,Eigen::Dynamic,1>;using Matrix=Eigen::Matrix<long double,Eigen::Dynamic,Eigen::Dynamic>;
 Vector force=Vector::Zero(n),attachment=Vector::Zero(n),tendon=Vector::Zero(n);Matrix stiffness=Matrix::Zero(n,n);long double skin=0,rails=0,bond=0;
 double cable=regrip_precise_tendon::elements(m.model,q,T,lateral,[&](const regrip_film_rail::Element&e){
  if(e.kind==0){if(e.ids.front()<105)skin+=e.energy.v;else rails+=e.energy.v;}else if(e.kind==1)bond+=e.energy.v;
  for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=m.index[ga];if(i<0)continue;long double f=-static_cast<long double>(m.weight[ga])*e.energy.g[a];force(i)+=f;if(e.kind==1)attachment(i)+=f;if(e.kind==2)tendon(i)+=f;
   for(unsigned b=0;b<3*e.ids.size();++b){unsigned gb=3*e.ids[b/3]+b%3;int j=m.index[gb];if(j>=0)stiffness(i,j)+=static_cast<long double>(m.weight[ga])*m.weight[gb]*e.energy.h[regrip_film::N*a+b];}}
 });
 Parts out{force.cast<double>(),attachment.cast<double>(),tendon.cast<double>(),stiffness.cast<double>()};out.skin=double(skin);out.rails=double(rails);out.bond=double(bond);out.cable=cable;return out;
}
}
