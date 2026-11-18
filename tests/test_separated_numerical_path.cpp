#include "../models/film_routed_contact/SeparatedPath.h"
#include <iostream>
using namespace regrip_film_impact;
int main(){try{
 std::vector<std::array<unsigned,3>>tri{{0,1,2}};
 QuadraticSurfacePath p{{{-1,-1,2},{1,-1,2},{0,1,2}},{{0,0,1},{0,0,1},{0,0,1}},{{0,0,0},{0,0,0},{0,0,0}}};
 if(!regrip_routed_contact::separatedNumericalPath(p,tri,{0,0,0},1).clear)throw std::runtime_error("separating plane not certified");
 // Both endpoints clear, interior penetrates: must NOT exclude.
 for(auto&v:p.a1)v={0,0,-6};for(auto&v:p.a2)v={0,0,6};
 if(regrip_routed_contact::separatedNumericalPath(p,tri,{0,0,0},1).clear)throw std::runtime_error("interior collision missed");
 // Curved clear path whose whole-interval Bernstein control is negative.
 for(auto&v:p.a0)v[2]=2.1;
 for(auto&v:p.a1)v={0,0,-4};for(auto&v:p.a2)v={0,0,4};
 auto r=regrip_routed_contact::separatedNumericalPath(p,tri,{0,0,0},1);
 if(!r.clear)throw std::runtime_error("curved supporting proof required");
 if(!regrip_routed_contact::rotatingPlaneClear(p,tri[0],{0,0,0},1,0,1,6))throw std::runtime_error("polynomial face witness failed");
 // Exact tangent is not strict separation.
 for(auto&v:p.a0)v[2]=2;
 if(regrip_routed_contact::separatedNumericalPath(p,tri,{0,0,0},1).clear)throw std::runtime_error("tangent excluded");
 QuadraticSurfacePath edge{{{2,-1,0},{2,1,0},{3,0,0}},{{0,0,0},{0,0,0},{0,0,0}},{{0,0,0},{0,0,0},{0,0,0}}};
 if(!regrip_routed_contact::rotatingPlaneClear(edge,tri[0],{0,0,0},1,0,1,3))throw std::runtime_error("polynomial edge witness failed");
 edge.a0={{2,0,0},{3,1,0},{3,-1,0}};
 if(!regrip_routed_contact::rotatingPlaneClear(edge,tri[0],{0,0,0},1,0,1,0))throw std::runtime_error("polynomial vertex witness failed");
 std::cout<<"PASS strict interval supporting planes;interior hit/tangent not excluded\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
