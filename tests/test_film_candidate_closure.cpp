#include "../models/film_sphere_contact/CandidateClosure.h"
#include <iostream>
using namespace regrip_film_sphere;
int main(){try{
 Assembly m(5);std::vector<Point> q(m.size()),v(m.size());
 std::vector<CandidateClosure::Triangle> tris{{m.id(0,3,2),m.id(0,4,2),m.id(0,4,3)}};
 // No predictor rows. The initial surface violates the declared buffer.
 CoupledContactStep base(m,m.masses(),.005,2,0,q,v,{},true,true);
 auto r=CandidateClosure::solve(base,{92,14,-8},8.01,tris,v,true);
 if(r.added!=1||r.sweeps!=2||r.minimumGap < -1e-10||r.rows.size()!=1||r.triangle[0]!=0||r.mechanical.lambda(0)<=0)throw std::runtime_error("missing triangle was not discovered/resolved");
 if(!base.planes.empty()||base.mechanics.previous!=q)throw std::runtime_error("closure mutated input");
 auto fast=CandidateClosure::solve(base,{92,14,-8},8.01,tris,v,true,nullptr,8,true);
 if(fast.mechanical.displacement!=r.mechanical.displacement||fast.mechanical.velocity!=r.mechanical.velocity||fast.mechanical.lambda!=r.mechanical.lambda)throw std::runtime_error("broadphase changed actual state/impulse");
 for(unsigned i=0;i<100;++i){std::vector<Point>p{{0,0,0},{1,.01*i,0},{.01*i,1,.1}};Point c{.071*i-2,.039*i-1,.011*i+.5};double bound=CandidateClosure::boxLowerBound(p,c,.2),exact=ClosestPrimitive::evaluate(p,c,.2).gap.v;if(bound>exact+1e-14)throw std::runtime_error("nonconservative clearance bound");}
 bool reject=false;try{CandidateClosure::solve(base,{92,14,-8},8.01,tris,v,true,nullptr,1);}catch(const std::runtime_error&){reject=true;}if(!reject)throw std::runtime_error("closure committed unconverged sweep");
 reject=false;try{CandidateClosure::solve(base,{92,14,-8},8.01,{{0,0,0}},v,true);}catch(const std::runtime_error&){reject=true;}if(!reject)throw std::runtime_error("degenerate triangle accepted");
 std::cout<<"PASS missing candidate,independent row,full endpoint clearance,query purity,budget/degenerate rejection;NOT CCD or SOFA certification\n";
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
