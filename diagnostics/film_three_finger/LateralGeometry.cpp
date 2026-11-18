#include "../../models/film_lateral_tendon/Route.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include <iostream>
#include <iomanip>
using namespace regrip_lateral_tendon;
Eigen::Vector3d vec(const Vec<AD>&x){return {x[0].v,x[1].v,x[2].v};}
double segment(const Eigen::Vector3d&a,const Eigen::Vector3d&b,const Eigen::Vector3d&c){Eigen::Vector3d d=b-a;if(!(d.squaredNorm()>0))throw std::runtime_error("collapsed physical segment");double t=std::clamp((c-a).dot(d)/d.squaredNorm(),0.,1.);return (a+t*d-c).norm();}
int main(){try{
 Assembly m(21);m.guideOffset=5;m.guideIntervals=4;m.rootGuideSecondOrder=true;auto rest=m.rest();std::vector<Point>zero(m.size());regrip_three_finger::Layout layout;auto center=layout.bodyCenter+Eigen::Vector3d(0,0,.0001);std::cout<<std::setprecision(17)<<"lateral_mm,wire_centreline_gap_mm,guide_arm_centreline_gap_mm,rest_combined_length_mm,unit_closing_mode_work_Nmm,core_volume_three_fingers_mm3\n";
 for(double lateral:{0.,6.}){double wire=1e9,arms=1e9,work=0;
  for(unsigned f=0;f<3;++f)for(unsigned part:{1u,2u}){std::vector<Eigen::Vector3d>points;for(unsigned k=0;k<=4;++k){unsigned i=5*k;Assembly::Local local(m.guideIds(part,i),rest);auto guidePoint=vec(guide(m,local,part,i,lateral)),base=vec(m.guide(local,part,i,0));Eigen::Vector3d g=layout.mount[f].origin+layout.mount[f].R*guidePoint,b=layout.mount[f].origin+layout.mount[f].R*base;points.push_back(g);arms=std::min(arms,segment(b,g,center)-30.);}for(unsigned k=1;k<points.size();++k)wire=std::min(wire,segment(points[k-1],points[k],center)-30.);}
  route(m,zero,1,lateral,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)if(a%3==2){double x=rest[e.ids[a/3]][0];double displacement=-x*x/(2*m.L);work-=e.energy.g[a]*displacement;}});
  std::cout<<lateral<<','<<wire<<','<<arms<<','<<length(m,zero,lateral)<<','<<work<<','<<3*m.volume()<<'\n';
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
