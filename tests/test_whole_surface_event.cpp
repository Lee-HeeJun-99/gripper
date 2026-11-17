#include "../models/film_impact/SurfaceEvent.h"
#include "../models/film_impact/ManyRowImpact.h"
#include <iostream>
using namespace regrip_film_impact;
void check(bool b){if(!b)throw std::runtime_error("whole-surface reference mismatch");}
int main(){try{
 std::vector<std::array<unsigned,3>>triangles{{0,1,2}};
 for(auto points:{std::vector<SurfacePoint>{{2,-3,-3},{2,3,-3},{2,0,3}},
  std::vector<SurfacePoint>{{2,-1,0},{2,1,0},{2,0,1}},std::vector<SurfacePoint>{{2,0,0},{2,1,0},{2,0,1}}}){
  QuadraticSurfacePath path{points,std::vector<SurfacePoint>(3,{-4,0,0}),std::vector<SurfacePoint>(3)};
  auto event=earliestSurfaceEvent(path,triangles,{0,0,0},1);check(event&&std::abs(event->fraction-.25)<1e-9);
  check(event->fraction-event->clearUntil<=1e-10&&event->rows.size()==1);
  auto a=event->rows[0].barycentric;check(std::abs(a[0]+a[1]+a[2]-1)<1e-12);
 }
 QuadraticSurfacePath curved{{{2,-3,-3},{2,3,-3},{2,0,3}},std::vector<SurfacePoint>(3,{-8,0,0}),std::vector<SurfacePoint>(3,{8,0,0})};
 auto hit=earliestSurfaceEvent(curved,triangles,{0,0,0},1);check(hit&&std::abs(hit->fraction-(1-std::sqrt(.5))/2)<1e-9);
 auto earlier=curved;earlier.a2.assign(3,{});earlier.a1.assign(3,{-4,0,0});
 // Triangle0 is later, triangle1 earlier. Both endpoints are noncontact for
 // the earlier triangle. The whole search must not use Native row ordering.
 auto one=earlier;for(auto p:one.a0){p[0]+=1;earlier.a0.insert(earlier.a0.begin(),p);}
 earlier.a1.assign(6,{-4,0,0});earlier.a2.assign(6,{});
 auto first=earliestSurfaceEvent(earlier,{{0,1,2},{3,4,5}},{0,0,0},1);
 check(first&&std::abs(first->fraction-.25)<1e-9&&first->rows[0].triangle==1);
 auto simultaneous=earliestSurfaceEvent(one,{{0,1,2},{0,1,2}},{0,0,0},1);check(simultaneous&&simultaneous->rows.size()==2);
 // Distinct opposing sphere features, not duplicate triangles at one vertex.
 QuadraticSurfacePath opposed{{{2,-.1,0},{2,.1,0},{2,0,.1},{-2,-.1,0},{-2,0,.1},{-2,.1,0}},
  {{-4,0,0},{-4,0,0},{-4,0,0},{4,0,0},{4,0,0},{4,0,0}},std::vector<SurfacePoint>(6)};
 auto doubleHit=earliestSurfaceEvent(opposed,{{0,1,2},{3,4,5}},{0,0,0},1);
 check(doubleHit&&doubleHit->rows.size()==2&&std::abs(doubleHit->fraction-.25)<1e-9);
 check(doubleHit->rows[0].normal[0]*doubleHit->rows[1].normal[0]<-.99);
 auto rotated=one;
 auto rotation=[](SurfacePoint p){return SurfacePoint{-p[1],p[0],p[2]};};
 for(auto&p:rotated.a0){p=rotation(p);p[0]+=7;p[1]-=2;p[2]+=3;}
 for(auto&p:rotated.a1)p=rotation(p);for(auto&p:rotated.a2)p=rotation(p);
 auto rigid=earliestSurfaceEvent(rotated,triangles,{7,-2,3},1);
 check(rigid&&std::abs(rigid->fraction-.25)<1e-9&&std::abs(rigid->rows[0].normal[1]-1)<1e-12);
 // Strictly separated high tangential motion: the old global-speed advance
 // exhausts its finite budget, whereas a swept separating plane proves clear.
 auto tangential=one;for(auto&p:tangential.a0)p[0]=1.0001;
 tangential.a1.assign(3,{0,1000000,0});
 check(!earliestSurfaceEvent(tangential,triangles,{0,0,0},1));
 bool oldBudget=false;try{earliestSurfaceEvent(tangential,triangles,{0,0,0},1,1e-10,1e-10,false);}catch(const std::runtime_error&){oldBudget=true;}check(oldBudget);
 bool rejected=false;auto grazing=curved;grazing.a1.assign(3,{-4,0,0});grazing.a2.assign(3,{4,0,0});
 try{earliestSurfaceEvent(grazing,triangles,{0,0,0},1);}catch(const std::runtime_error&){rejected=true;}check(rejected);
 rejected=false;try{earliestSurfaceEvent(one,{{0,0,0}},{0,0,0},1);}catch(const std::runtime_error&){rejected=true;}check(rejected);
 auto plus=one,minus=one;for(auto&p:plus.a0)p[0]+=1e-4;for(auto&p:minus.a0)p[0]-=1e-4;
 double fd=(earliestSurfaceEvent(plus,triangles,{0,0,0},1)->fraction-earliestSurfaceEvent(minus,triangles,{0,0,0},1)->fraction)/2e-4;
 check(std::abs(fd-.25)<1e-6);
 Eigen::MatrixXd M=Eigen::MatrixXd::Identity(3,3),J(3,3);J<<1,0,0,1,1,0,0,0,1;
 Eigen::Vector3d incoming(-2,-1,-.5);auto exact=solve(M,J,incoming,0,1e-11,1e-12);auto many=manyRowImpact(M,J,incoming,1e-11);
 check((exact.velocity-many.state.velocity).norm()<1e-9&&many.state.momentumResidual<1e-12&&many.state.energyLoss>=0);
 Eigen::MatrixXd redundant(256,3);for(int i=0;i<256;++i)redundant.row(i)=J.row(i%3);
 auto large=manyRowImpact(M,redundant,incoming,1e-11);check((large.state.velocity-exact.velocity).norm()<1e-9&&large.rank==3);
 for(int trial=0;trial<20;++trial){
  Eigen::Matrix3d A;A<<2,.1*trial,.2,.3,1.5,.1,.2,.1,1;
  Eigen::Matrix3d mass=A.transpose()*A;
  auto reference=solve(mass,J,incoming,0,1e-11,1e-12);
  auto iterative=manyRowImpact(mass,J,incoming,1e-11);
  Eigen::MatrixXd reversed=J.colwise().reverse().eval();
  auto reordered=manyRowImpact(mass,reversed,incoming,1e-11);
  check((reference.velocity-iterative.state.velocity).norm()<1e-8);
  check((reordered.state.velocity-iterative.state.velocity).norm()<1e-8);
 }
 std::cout<<"PASS whole quadratic surface vertex/edge/face/interior hit/ordering/simultaneous/grazing rejection/FD and256-row unregularized impact;NOT continuous exact ODE, sustained contact or grasp\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
