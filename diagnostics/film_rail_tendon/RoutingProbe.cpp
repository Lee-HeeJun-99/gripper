#include "../../models/film_rail_tendon/Kernel.h"
#include <iostream>
#include <iomanip>
using namespace regrip_film_rail;
// Virtual-work probe, not a static/dynamic solution or wrapping prediction.
int main(){std::cout<<std::setprecision(17)<<"offset_mm,curvature_generator_derivative,axial_generator_derivative,net_force_z,net_moment_y\n";
 for(double offset:{-.2,.2,1.,2.,5.}){Assembly m;m.guideOffset=offset;auto r=m.rest();std::vector<Point>u(m.size());double curvature=0,axial=0;Point F{},M{};
  m.elements(u,.001,[&](const Element&e){if(e.kind!=2)return;for(unsigned a=0;a<3*e.ids.size();++a){unsigned i=e.ids[a/3],j=a%3;auto x=r[i];double mode=j==0?-(x[2]+.075)*x[0]:j==2?.5*x[0]*x[0]:0;curvature+=e.energy.g[a]*mode;axial+=j==0?e.energy.g[a]*x[0]:0;Point f{};f[j]=-e.energy.g[a];F=add(F,f);M=add(M,cross(x,f));}});
  std::cout<<offset<<','<<curvature<<','<<axial<<','<<F[2]<<','<<M[1]<<'\n';
  if(!std::isfinite(curvature)||std::abs(F[2])>1e-12||std::abs(M[1])>1e-12)return 1;
 }
}
