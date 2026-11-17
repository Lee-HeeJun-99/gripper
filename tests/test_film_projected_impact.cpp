#include "../models/film_impact/FilmProjection.h"
#include "../models/film_impact/PrimitiveBirth.h"
#include "../models/film_impact/FilmEventImpulse.h"
#include "../models/film_impact/FilmRestartHistory.h"
#include <iostream>
using namespace regrip_film_impact;
using namespace regrip_film_native;
void check(bool b){if(!b)throw std::runtime_error("film impact reference mismatch");}
int main(){try{
 Assembly model(5);auto mass=model.masses();std::vector<Point> zero(model.size()),J(model.size());
 CoupledPlaneStep mechanics(model,mass,.01,2,0,zero,zero,J,0);
 auto M=filmMass(mechanics);Eigen::MatrixXd B=Eigen::MatrixXd::Zero(3*model.size(),mechanics.freeSize);
 Eigen::VectorXd physicalMass(3*model.size());
 for(unsigned a=0;a<mechanics.index.size();++a){physicalMass(a)=mass[a/3];if(mechanics.index[a]>=0)B(a,mechanics.index[a])=mechanics.weight[a];}
 check((M-projectedMass(B,physicalMass)).norm()==0);
 auto tip=model.id(0,4,2);J[tip][2]=1;
 Eigen::VectorXd incoming=Eigen::VectorXd::Zero(mechanics.freeSize);incoming(mechanics.index[3*tip+2])=-3;
 auto impact=solve(M,filmRow(mechanics,J),incoming,0,1e-12,1e-20);
 check(impact.velocity.norm()<1e-12&&impact.momentumResidual<1e-20&&impact.impulse(0)>0);
 auto eventVelocity=mechanics.expand(incoming);auto rest=model.rest();
 Point center=rest[tip];center[2]-=1;
 auto event=filmEventImpulse(mechanics,zero,eventVelocity,{{tip}},center,1,1e-10,1e-12);
 check(event.reduced.velocity.norm()<1e-12&&event.reduced.impulse(0)==impact.impulse(0));
 FilmRestartHistory history(zero,zero);auto q1=zero;q1[tip][2]=.1;
 history.accept(q1,eventVelocity,.01);auto reference=history.reference(.01);
 check(reference.beta==CoupledBDFHistory::beta&&reference.position==CoupledBDFHistory::extrapolate(q1,zero));
 history.impact(zero,eventVelocity,event.postVelocity,.123);
 check(history.reference(.01).beta==1&&history.lastJump->preVelocity==eventVelocity);
 history.accept(zero,event.postVelocity,.003);check(history.reference(.01).beta==1);
 history.accept(zero,event.postVelocity,.01);check(history.reference(.01).beta==CoupledBDFHistory::beta);
 // Face/edge/vertex support, including separated endpoints with an interior hit.
 for(auto shape:{std::vector<Point>{{2,-3,-3},{2,3,-3},{2,0,3}},
                 std::vector<Point>{{2,-3,0},{2,3,0}},std::vector<Point>{{2,0,0}}}){
  std::vector<Point>delta(shape.size(),Point{-4,0,0});auto birth=primitiveBirth(shape,delta,{0,0,0},1);
  check(birth&&std::abs(birth->fraction-.25)<1e-10&&birth->pathDerivative<0);
 }
 // Nonintersecting motion and explicit degenerate-geometry rejection.
 check(!primitiveBirth({{2,0,0}},{{1,0,0}},{0,0,0},1));
 bool rejected=false;try{primitiveBirth({{2,0,0},{2,0,0},{2,0,0}},{{-4,0,0},{-4,0,0},{-4,0,0}},{0,0,0},1);}catch(const std::runtime_error&){rejected=true;}check(rejected);
 std::cout<<"PASS actual film root mass/J projection and affine face/edge/vertex birth;NOT dynamic triangle CCD or SOFA film impact\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
