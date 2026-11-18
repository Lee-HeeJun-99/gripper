#include "../../models/film_transmission/Kernel.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include "../../models/film_sphere_contact/ClosestPrimitive.h"
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("samples,output required");using namespace regrip_transmission;auto m=model();auto rest=m.rest();regrip_three_finger::Layout layout;auto c=layout.mount[0].R.transpose()*(layout.bodyCenter-layout.mount[0].origin);Point center{c[0],c[1],c[2]};std::ifstream in(argv[1]);unsigned n;in>>n;if(n>2000||n<1)throw std::runtime_error("bounded surface samples required");std::ofstream out(argv[2]);out<<std::setprecision(17)<<"input,minimum_buffer_gap_mm,minimum_physical_midsurface_gap_mm,triangle,feature,violated_buffer_triangles,total_triangles\n";
 for(unsigned k=0;k<n;++k){double parameter;in>>parameter;std::vector<Point>x=rest;for(auto&p:x)for(unsigned d=0;d<3;++d){double q;in>>q;p[d]+=q;}if(!in)throw std::runtime_error("invalid shape input");double minimum=std::numeric_limits<double>::infinity();unsigned triangle=0,feature=0,count=0,id=0;
  for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<m.nx;++i)for(unsigned j=0;j+1<m.parts[part].ny;++j){unsigned a=m.id(part,i,j),b=m.id(part,i+1,j),c=m.id(part,i,j+1),d=m.id(part,i+1,j+1);for(auto ids:{std::array<unsigned,3>{a,b,c},std::array<unsigned,3>{b,d,c}}){auto e=regrip_film_sphere::ClosestPrimitive::evaluate({x[ids[0]],x[ids[1]],x[ids[2]]},center,layout.bufferRadius);if(e.gap.v<minimum){minimum=e.gap.v;triangle=id;feature=e.feature;}if(e.gap.v< -1e-10)++count;++id;}}
  out<<parameter<<','<<minimum<<','<<minimum+layout.bufferRadius-layout.bodyRadius<<','<<triangle<<','<<feature<<','<<count<<','<<id<<'\n';
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
