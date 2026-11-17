#include "../models/film_sphere_contact/ClosestPrimitive.h"
#include <iostream>
#include <iomanip>
// Prescribed gap-preserving rotating/sliding segment. Actual nearest-point
// kernel, not a free-dynamics solution. Tests quadrature of normal virtual work.
using regrip_film::Point;
std::vector<Point> path(double time){
 double theta=.4*time,s=-time;Point n{std::sin(theta),0,std::cos(theta)},t{std::cos(theta),0,-std::sin(theta)};
 std::vector<Point> points;
 for(double edge:{-3.,3.}){Point p;for(int d=0;d<3;++d)p[d]=n[d]+(s+edge)*t[d];points.push_back(p);}return points;
}
int main(){
 using regrip_film_sphere::ClosestPrimitive;
 double previous=0;
 std::cout<<std::setprecision(17);
 for(unsigned steps:{20u,40u,80u,160u}){
  double work=0,midwork=0,maxgap=0;
  for(unsigned i=0;i<steps;++i){double a=double(i)/steps,b=double(i+1)/steps;
   auto x0=path(a),x1=path(b),xm=path((a+b)/2);
   auto end=ClosestPrimitive::evaluate(x1,{0,0,0},1.);
   auto mid=ClosestPrimitive::evaluate(xm,{0,0,0},1.);
   maxgap=std::max(maxgap,std::abs(end.gap.v));
   for(unsigned k=0;k<6;++k){double dx=x1[k/3][k%3]-x0[k/3][k%3];work+=end.gap.g[k]*dx;midwork+=mid.gap.g[k]*dx;}
  }
  if(maxgap>1e-13||!(work<0)||std::abs(midwork)>1e-12)return 1;
  if(previous!=0&&std::abs(work/previous-.5)>.01)return 2;
  previous=work;
  std::cout<<steps<<","<<work<<","<<midwork<<","<<maxgap<<"\n";
 }
 std::cout<<"PASS prescribed persistent-gap work counterexample;NOT dynamics or integration correction\n";
}
