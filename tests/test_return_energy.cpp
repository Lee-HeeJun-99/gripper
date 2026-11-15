#include "../models/contact_energy/ReturnAudit.h"
#include <iostream>
#include <random>
using namespace regrip_return_audit;
int main(){try{
 std::mt19937_64 rng(20261116);std::uniform_real_distribution<double>u(-1,1);
 unsigned sticks=0,slips=0,births=0,deaths=0;double maxResidual=0;
 for(unsigned i=0;i<2000;++i){
  History h;V before{0,1.01,0};Pose p,o;o.q={0,0,0,1};p.q=o.q;
  if(i%5){h.active=true;h.local=before;h.normal={0,1,0};h.elastic={.005*u(rng),0,.005*u(rng)};}
  else{before={0,1.03,0};++births;}
  p.p={.008*u(rng),i%17?1.01:1.04,.008*u(rng)};
  auto r=regrip_birthlaw::value(p,o,h,before,0,1,1,.02,.7,.8,.2);
  auto b=evaluate(h,r,before,0,1,1,.02,.8);
  maxResidual=std::max(maxResidual,std::abs(b.residual));
  if(b.plastic<0||b.projection<0||b.detachment<0)throw std::runtime_error("negative loss");
  if(r.next.active){if(r.next.sliding)++slips;else ++sticks;}else ++deaths;
  if(std::abs(b.residual)>2e-18)throw std::runtime_error("radial-return energy identity");
 }
 if(!sticks||!slips||!births||!deaths)throw std::runtime_error("missing branch coverage");
 std::cout<<"PASS states=2000 sticks="<<sticks<<" slips="<<slips<<" births="<<births<<" deaths="<<deaths<<" max_residual="<<maxResidual<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
