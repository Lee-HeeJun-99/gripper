#include "../../models/film_routed_tendon/Step.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include "../../models/film_sphere_contact/ClosestPrimitive.h"
#include <iomanip>
#include <iostream>
using namespace regrip_routed_tendon;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("samples,amplitude,output required");auto m=model();double amplitude=std::stod(argv[2]);validate(m,amplitude);auto rest=m.rest();regrip_three_finger::Layout layout;auto c=layout.mount[0].R.transpose()*(layout.bodyCenter-layout.mount[0].origin);Point center{c[0],c[1],c[2]};std::ifstream in(argv[1]);unsigned n;in>>n;if(!in||n<1||n>2000)throw std::runtime_error("bounded geometry samples");std::ofstream out(argv[3]);out<<std::setprecision(17)<<"time_s,triangle_buffer_gap_mm,wire_centreline_physical_gap_mm,violated_triangles,total_triangles,wire_length_mm\n";
 for(unsigned k=0;k<n;++k){double t;in>>t;auto x=rest;for(auto&p:x)for(unsigned d=0;d<3;++d){double q;in>>q;p[d]+=q;}if(!in)throw std::runtime_error("geometry payload incomplete");double gap=1e9,wiregap=1e9,L=0;unsigned count=0,total=0;
  for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<m.nx;++i)for(unsigned j=0;j+1<m.parts[part].ny;++j){unsigned a=m.id(part,i,j),b=m.id(part,i+1,j),c=m.id(part,i,j+1),d=m.id(part,i+1,j+1);for(auto ids:{std::array<unsigned,3>{a,b,c},std::array<unsigned,3>{b,d,c}}){auto e=regrip_film_sphere::ClosestPrimitive::evaluate({x[ids[0]],x[ids[1]],x[ids[2]]},center,layout.bufferRadius);gap=std::min(gap,e.gap.v);if(e.gap.v< -1e-10)++count;++total;}}
  for(unsigned part:{1u,2u}){std::vector<Point>g;for(unsigned k=0;k<=m.guideIntervals;++k){unsigned i=(m.nx-1)*k/m.guideIntervals;Assembly::Local local(m.guideIds(part,i),x);auto p=m.guide(local,part,i,-offset(m,i,amplitude));g.push_back({p[0].v,p[1].v,p[2].v});}for(unsigned k=0;k<m.guideIntervals;++k){wiregap=std::min(wiregap,regrip_film_sphere::ClosestPrimitive::evaluate({g[k],g[k+1]},center,layout.bodyRadius).gap.v);auto d=sub(g[k],g[k+1]);L+=std::sqrt(dot(d,d));}}
  out<<t<<','<<gap<<','<<wiregap<<','<<count<<','<<total<<','<<L<<'\n';out.flush();}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
