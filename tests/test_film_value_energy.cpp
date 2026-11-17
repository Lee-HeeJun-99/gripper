#include "../models/film_rail_tendon/Kernel.h"
#include "../models/film_value_energy/ValueEnergy.h"
#include <chrono>
#include <iostream>
int main(){try{using namespace regrip_film_rail;double normalSeconds=0,valueSeconds=0;unsigned states=0;
 for(unsigned nx:{5u,21u}){Assembly model(nx);model.guideOffset=5;auto rest=model.rest();std::vector<std::vector<Point>>packets;
  for(unsigned k=0;k<24;++k){auto q=std::vector<Point>(model.size());for(unsigned i=0;i<q.size();++i){q[i][0]=.00001*k*std::sin(rest[i][0]);q[i][1]=.00003*k*std::cos(rest[i][1]);q[i][2]=-.1*k*std::pow(rest[i][0]/100,2)+.01*k*std::sin(rest[i][1]);}packets.push_back(q);}
  regrip_value_energy::Parameters p{nx,model.guideIntervals,model.guideOffset,model.bondK,model.rootGuideSecondOrder};std::vector<std::array<double,2>>expected;
  auto t=std::chrono::steady_clock::now();for(const auto&q:packets){std::array<double,2>energy{};model.elements(q,0,[&](const Element&e){if(e.kind==0)energy[0]+=e.energy.v;if(e.kind==1)energy[1]+=e.energy.v;});expected.push_back(energy);}normalSeconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
  t=std::chrono::steady_clock::now();for(unsigned k=0;k<packets.size();++k){auto value=regrip_value_energy::evaluate(p,packets[k]);if(value!=expected[k])throw std::runtime_error("value/AD2 stored energies NOT bit exact");++states;}valueSeconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
 }
 std::cout<<"PASS "<<states<<" finite deformed states,stored shell/attachment energies bit exact;normal_AD2_s "<<normalSeconds<<" value_s "<<valueSeconds<<" measured_speedup "<<normalSeconds/valueSeconds<<";NOT force/Hessian replacement\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
