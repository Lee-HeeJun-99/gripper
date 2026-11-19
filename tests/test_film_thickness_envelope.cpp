#include "../models/film_precise_static/SphereEquilibrium.h"
#include <iostream>
int main(){try{
 using namespace regrip_precise_static;
 double maxGradient=0,maxHessian=0,maxObjectivity=0;
 // Fixed smooth vertex,edge,face branches,not C1 feature boundaries.
 std::vector<Point> tri{{0,0,0},{3,0,0},{0,3,0}};
 for(Point c:std::vector<Point>{{-1,-1,2},{1,-1,2},{1,1,2}}){
  auto base=regrip_film_sphere::ClosestPrimitive::evaluate(tri,c,1.);
  auto thick=regrip_film_sphere::ClosestPrimitive::evaluate(tri,c,1.025);
  if(std::abs((base.gap.v-thick.gap.v)-.025)>1e-14)throw std::runtime_error("constant offset value");
  for(unsigned a=0;a<9;++a){if(base.gap.g[a]!=thick.gap.g[a])throw std::runtime_error("offset changed gradient");
   auto p=tri,m=tri;double h=1e-5;p[a/3][a%3]+=h;m[a/3][a%3]-=h;
   auto ep=regrip_film_sphere::ClosestPrimitive::evaluate(p,c,1.025),em=regrip_film_sphere::ClosestPrimitive::evaluate(m,c,1.025);
   maxGradient=std::max(maxGradient,std::abs((ep.gap.v-em.gap.v)/(2*h)-thick.gap.g[a]));
   for(unsigned b=0;b<9;++b){if(base.gap.h[regrip_film::N*a+b]!=thick.gap.h[regrip_film::N*a+b])throw std::runtime_error("offset changed Hessian");maxHessian=std::max(maxHessian,std::abs((ep.gap.g[b]-em.gap.g[b])/(2*h)-thick.gap.h[regrip_film::N*b+a]));}
  }
  // Proper rigid rotation plus translation.
  auto transform=[](Point x){return Point{-x[1]+7,x[0]-3,x[2]+4};};auto moved=tri;for(auto&x:moved)x=transform(x);
  maxObjectivity=std::max(maxObjectivity,std::abs(regrip_film_sphere::ClosestPrimitive::evaluate(moved,transform(c),1.025).gap.v-thick.gap.v));
  // For every point y in triangle and |d|<=halfThickness, reverse triangle
  // inequality gives |y+d-c|-Rbuffer >= gap_envelope. Sample normal extrusion.
  for(unsigned i=0;i<=10;++i)for(unsigned j=0;i+j<=10;++j)for(double z:{-.025,.025}){
   Point y{3*i/10.,3*j/10.,z};double d=std::sqrt((y[0]-c[0])*(y[0]-c[0])+(y[1]-c[1])*(y[1]-c[1])+(y[2]-c[2])*(y[2]-c[2]))-1.;if(d+1e-14<thick.gap.v)throw std::runtime_error("conservative extrusion bound");
  }
 }
 bool rejected=false;try{regrip_film_sphere::ClosestPrimitive::evaluate({{0,0,0},{1,0,0},{2,0,0}},{0,0,2},1);}catch(const std::runtime_error&){rejected=true;}
 if(!rejected||maxGradient>1e-8||maxHessian>1e-8||maxObjectivity>1e-12)throw std::runtime_error("unchanged geometry derivative/objectivity gates failed");
 std::cout.precision(17);std::cout<<"{\"status\":\"PASS\",\"gradient_fd\":"<<maxGradient<<",\"Hessian_fd\":"<<maxHessian<<",\"rigid_gap_error\":"<<maxObjectivity<<",\"degenerate_rejected\":true,\"scope\":\"conservative fixed-thickness geometry only;not dynamic contact\"}\n";
 return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
