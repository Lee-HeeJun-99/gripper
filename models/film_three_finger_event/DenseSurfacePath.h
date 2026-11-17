#pragma once
#include "BlockFree.h"
#include "../film_impact/SurfaceEvent.h"
namespace regrip_three_event {
struct SharedSurfacePath {
 regrip_film_impact::QuadraticSurfacePath path;
 std::vector<std::array<unsigned,3>> triangles;
 std::vector<std::pair<unsigned,unsigned>> owners;
};
// Relative triangle/sphere path of the ONE free-midpoint interval,not frame
// interpolation and not the partial-interval nonlinear endpoint family.
inline SharedSurfacePath denseSurfacePath(const SharedFilmSystem&s,const Eigen::VectorXd&q0,
 const Eigen::VectorXd&v0,const FreeState&endpoint,double h){
 if(!(h>0)||q0.size()!=endpoint.q.size()||v0.size()!=q0.size())throw std::invalid_argument("three-film dense path dimensions");
 SharedSurfacePath out;unsigned nf=s.shared.nf,body=3*nf;Eigen::VectorXd vm=(v0+endpoint.v)/2;
 for(unsigned f=0;f<3;++f){const auto&film=s.shared.films[f].film;auto rest=film.model.rest(),q=film.expand(q0.segment(f*nf,nf)),v=film.expand(v0.segment(f*nf,nf)),middle=film.expand(vm.segment(f*nf,nf));unsigned offset=out.path.a0.size();
  for(unsigned i=0;i<q.size();++i){Eigen::Vector3d first=s.layout.world(f,add(rest[i],q[i]))-q0.segment<3>(body),rate=s.layout.mount[f].R*vector(v[i])-v0.segment<3>(body),curvature=s.layout.mount[f].R*(vector(middle[i])-vector(v[i]))-(vm.segment<3>(body)-v0.segment<3>(body));out.path.a0.push_back(point(first));out.path.a1.push_back(point(h*rate));out.path.a2.push_back(point(h*curvature));}
  for(unsigned t=0;t<s.shared.films[f].triangles.size();++t){auto triangle=s.shared.films[f].triangles[t];for(auto&i:triangle)i+=offset;out.triangles.push_back(triangle);out.owners.emplace_back(f,t);}
 }out.path.validate();return out;
}
}
